import psycopg2
from sqlalchemy import create_engine
from sqlalchemy.sql import text

# ----------------- CONFIG --------------------
DB_ADMIN_URL = "postgresql://postgres:1234@localhost:5432/postgres"
NEW_DB_NAME = "dbl_challenge"
NEW_DB_URL = f"postgresql://postgres:1234@localhost:5432/{NEW_DB_NAME}"
# ---------------------------------------------

def create_database():
    try:
        conn = psycopg2.connect(DB_ADMIN_URL)
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute(f"SELECT 1 FROM pg_database WHERE datname = '{NEW_DB_NAME}';")
        exists = cur.fetchone()
        if not exists:
            cur.execute(f"CREATE DATABASE {NEW_DB_NAME};")
            print(f"Database '{NEW_DB_NAME}' created.")
        else:
            print(f"Database '{NEW_DB_NAME}' already exists.")
        cur.close()
        conn.close()
    except Exception as e:
        print("❌ Failed to create database:", e)

def create_tables():
    try:
        conn = psycopg2.connect(NEW_DB_URL)
        conn.autocommit = True
        cur = conn.cursor()
        print("🚧 Creating tables...")

        statements = [
            """
            CREATE TABLE IF NOT EXISTS public.conversations (
                id bigint NOT NULL,
                tweet_id bigint NOT NULL,
                airline_involved boolean,
                CONSTRAINT conversations_pkey PRIMARY KEY (id, tweet_id)
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS public.hashtags (
                id bigint,
                text text
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS public.places (
                id varchar(255) NOT NULL,
                place_type varchar(255),
                name varchar(255),
                country_code varchar(255),
                coordinates jsonb,
                type_coordinates varchar(255),
                CONSTRAINT places_pkey PRIMARY KEY (id)
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS public.symbols (
                id bigint,
                text text
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS public.tweet_hashtags (
                tweet_id bigint,
                hashtag_id bigint,
                indices text
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS public.tweet_symbols (
                tweet_id bigint,
                symbol_id bigint,
                indices text
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS public.tweets (
                id bigint,
                created_at text,
                text text,
                truncated boolean,
                lang text,
                quote_count bigint,
                reply_count bigint,
                retweet_count bigint,
                favorite_count bigint,
                favorited boolean,
                retweeted boolean,
                possibly_sensitive boolean,
                filter_level text,
                in_reply_to_screen_name text,
                is_quote_status boolean,
                user_id bigint,
                place_id text,
                in_reply_to_status_id bigint,
                in_reply_to_user_id bigint,
                quoted_status_id bigint,
                retweeted_status_id bigint,
                full_text text,
                senti_raw_tabularis text,
                row_num bigint
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS public.user_mentions (
                tweet_id bigint,
                user_id bigint,
                screen_name text,
                indices text
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS public.users (
                id bigint NOT NULL,
                screen_name varchar(50) NOT NULL,
                description text,
                protected boolean,
                verified boolean,
                followers_count integer,
                friends_count integer,
                listed_count integer,
                favourites_count integer,
                statuses_count integer,
                created_at text,
                default_profile boolean,
                default_profile_image boolean,
                CONSTRAINT users_pkey PRIMARY KEY (id)
            );
            """,
        ]

        for sql in statements:
            cur.execute(sql)

        print("✅ All tables and indexes created.")
        cur.close()
        conn.close()
    except Exception as e:
        print("❌ Failed to create tables:", e)




if __name__ == "__main__":
    create_database()
    create_tables()
