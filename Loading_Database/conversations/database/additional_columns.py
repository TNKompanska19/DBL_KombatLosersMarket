import sys,os
import psycopg2
import json
from collections import defaultdict
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..","..")))
from configuration import *

# DB connection
conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

# Alter table
cur.execute("""
    ALTER TABLE public.conversations
    ADD COLUMN IF NOT EXISTS number_of_people INTEGER,
    ADD COLUMN IF NOT EXISTS avg_senti_score FLOAT,
    ADD COLUMN IF NOT EXISTS airline_involved BOOLEAN,
    ADD COLUMN IF NOT EXISTS airline_names TEXT;
""")
conn.commit()

# Mappings
senti_mapping = {
    'Very Negative': 0.0,
    'Negative': 0.25,
    'Neutral': 0.5,
    'Positive': 0.75,
    'Very Positive': 1.0
}

airline_map = {
    56377143: "KLM",
    106062176: "AirFrance",
    18332190: "British_Airways",
    22536055: "AmericanAir",
    124476322: "Lufthansa",
    26223583: "AirBerlin",
    2182373406: "AirBerlin_assist",
    38676903: "easyJet",
    1542862735: "RyanAir",
    253340062: "SingaporeAir",
    218730857: "Qantas",
    45621423: "EtihadAirways",
    20626359: "VirginAtlantic"
}
airline_user_ids = set(airline_map.keys())

# Fetch all tweet + conversation data at once
cur.execute("""
    SELECT c.id, t.user_id, t.senti_raw_tabularis
    FROM public.conversations c
    JOIN public.tweets t ON c.tweet_id = t.id
""")
rows = cur.fetchall()

# Process data grouped by conversation ID
data = defaultdict(list)
for conv_id, user_id, senti_raw in rows:
    data[conv_id].append((user_id, senti_raw))

updates = []

for conv_id, tweets in data.items():
    users = set()
    senti_sum = 0
    senti_count = 0
    airlines = set()

    for user_id, senti_raw in tweets:
        users.add(user_id)

        if user_id in airline_user_ids:
            airlines.add(airline_map[user_id])

        try:
            sentiment = json.loads(senti_raw.replace("'", "\""))
            label = sentiment.get('label')
            score = senti_mapping.get(label, 0.5)
            senti_sum += score
            senti_count += 1
        except Exception:
            continue

    avg_score = senti_sum / senti_count if senti_count else None
    updates.append((
        len(users),
        avg_score,
        bool(airlines),
        ', '.join(sorted(airlines)) if airlines else None,
        conv_id
    ))

# Batch update
batch_size = 1000
for i in range(0, len(updates), batch_size):
    batch = updates[i:i+batch_size]
    args_str = ",".join(
        cur.mogrify("(%s,%s,%s,%s,%s)", rec).decode("utf-8") for rec in batch
    )

    cur.execute(f"""
        UPDATE public.conversations AS c SET
            number_of_people = u.number_of_people,
            avg_senti_score = u.avg_senti_score,
            airline_involved = u.airline_involved,
            airline_names = u.airline_names
        FROM (VALUES {args_str}) AS u(
            number_of_people, avg_senti_score, airline_involved, airline_names, id
        )
        WHERE u.id = c.id
    """)

conn.commit()
cur.close()
conn.close()

print("Fast update completed.")
