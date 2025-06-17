import pandas as pd
import ast
import re
from sqlalchemy import create_engine
import plotly.express as px
import dash
from dash import dcc, html, Input, Output

# Connect to database
engine = create_engine("postgresql://dbadmin:BZ6uHRGxki6a7qD@dcpostgres.postgres.database.azure.com:5432/DataChallenge")

# Load the coordinates of points
centroids = pd.read_csv(
    "path/to/full_country_centroids_200.csv",
    header=None,
    names=["country_name", "country_code", "latitude", "longitude"]
)

# Airline to map
airlines = ["klm", "lufthansa", "airfrance", "british_airways", "virginatlantic"]

# Get scores for labels
label_to_score = {
    "Very Negative": -2,
    "Negative": -1,
    "Neutral": 0,
    "Positive": 1,
    "Very Positive": 2
}

def extract_label(val):
    try:
        if isinstance(val, dict):
            return val.get("label")
        if isinstance(val, str):
            match = re.search(r"'label':\s*'([^']+)'", val)
            if match:
                return match.group(1)
    except:
        return None
    return None

# Start the app
app = dash.Dash(__name__)
app.title = "Airline Sentiment Map"
airline_sentiment_data = {}

print("[INIT] Preloading tweet sentiment data...")
# Load the data from the database
try:
    with engine.connect() as conn:
        all_dfs = []

        for airline in airlines:
            print(f"[QUERY] Loading data for @{airline}...")

            params = {
                "airline": airline,
                "mention": f"%@{airline}%"
            }

            query = f"""
                WITH airline_users AS (
                    SELECT id
                    FROM users
                    WHERE LOWER(screen_name) = %(airline)s
                ),
                relevant_tweet_ids AS (
                    SELECT tweets.id
                    FROM tweets
                    JOIN airline_users ON tweets.user_id = airline_users.id

                    UNION

                    SELECT tweets.id
                    FROM tweets
                    WHERE LOWER(tweets.full_text) LIKE %(mention)s

                    UNION

                    SELECT tweets.id
                    FROM tweets
                    WHERE tweets.in_reply_to_status_id IN (
                        SELECT tweets.id
                        FROM tweets
                        JOIN airline_users ON tweets.user_id = airline_users.id
                    )
                )
                SELECT
                    places.country_code,
                    tweets.senti_raw_tabularis,
                    %(airline)s AS airline
                FROM tweets
                JOIN users ON tweets.user_id = users.id
                JOIN places ON tweets.place_id = places.id
                WHERE tweets.id IN (SELECT id FROM relevant_tweet_ids)
            """

            df = pd.read_sql(query, conn, params=params)
            all_dfs.append(df)

        df = pd.concat(all_dfs, ignore_index=True)
        print(f"[INIT] Loaded {len(df)} tweets")

        df["airline"] = df["airline"].str.lower()
        df["country_code"] = df["country_code"].str.upper()
        df["sentiment_label"] = df["senti_raw_tabularis"].apply(extract_label)
        df["sentiment_score"] = df["sentiment_label"].map(label_to_score)

        print("[DEBUG] Airline counts:\n", df["airline"].value_counts())

        for airline in airlines:
            airline_df = df[df["airline"] == airline].dropna(subset=["sentiment_score"])
            if airline_df.empty:
                print(f"[WARN] No sentiment data for {airline}")
                continue

            sentiment = airline_df.groupby("country_code").agg(
                avg_sentiment=("sentiment_score", "mean"),
                tweet_count=("sentiment_score", "count")
            ).reset_index()

            merged = sentiment.merge(centroids, on="country_code", how="inner")
            airline_sentiment_data[airline] = merged
            print(f"[DEBUG] {airline}: {len(merged)} countries loaded")

except Exception as e:
    print(f"[ERROR INIT] Failed to preload airline data: {e}")

# App layout
app.layout = html.Div([
    html.H1("Airline Tweet Sentiment by Country"),
    dcc.Dropdown(
        id="airline-selector",
        options=[{"label": a.upper(), "value": a} for a in airlines],
        value="klm",
        clearable=False
    ),
    dcc.Graph(id="sentiment-map")
])

# Callback for selecting airlines
@app.callback(
    Output("sentiment-map", "figure"),
    Input("airline-selector", "value")
)
def update_map(selected_airline):
    print(f"\n[CALLBACK] Selected airline: {selected_airline}")

    try:
        if selected_airline not in airline_sentiment_data:
            raise ValueError(f"No data for {selected_airline}")

        merged = airline_sentiment_data[selected_airline]

        fig = px.scatter_geo(
            merged,
            lat="latitude",
            lon="longitude",
            color="avg_sentiment",
            hover_name="country_name",
            hover_data={
                "avg_sentiment": True,
                "tweet_count": True,
                "latitude": False,
                "longitude": False,
                "country_name": False
            },
            color_continuous_scale="RdYlGn",
            range_color=[-2, 2],
            projection="natural earth",
            title=f"Sentiment for @{selected_airline.upper()}",
        )

        fig.update_traces(marker=dict(size=6, opacity=1))

        fig.update_geos(
            showcountries=True,
            landcolor="#001f3f",
            showland=True,
            countrycolor="white",
            bgcolor="rgba(0,0,0,0)"
        )
        fig.update_layout(
            geo=dict(showframe=True, showcoastlines=True),
            paper_bgcolor="#000000",
            plot_bgcolor="#000000",
            font_color="white"
        )

        return fig
# Placeholder map in case of an error
    except Exception as e:
        print(f"[ERROR CALLBACK] {e}")
        fallback = pd.DataFrame({
            "country_code": ["US", "GB", "FR"],
            "avg_sentiment": [2, 0, -2],
            "tweet_count": [120, 85, 40],
            "latitude": [37.09, 55.38, 46.60],
            "longitude": [-95.71, -3.43, 1.88],
            "country_name": ["USA", "UK", "France"]
        })
        return px.scatter_geo(
            fallback,
            lat="latitude",
            lon="longitude",
            color="avg_sentiment",
            size=6,
            hover_name="country_name",
            color_continuous_scale="RdYlGn",
            range_color=[-2, 2],
            projection="natural earth",
            title="Fallback Sentiment Map",
            opacity=1.0
        )
        

# Run the app
if __name__ == "__main__":
    print("🚀 Dash app launching...")
    app.run(debug=True,use_reloader=False)
