# region ==  PART 1: IMPORTS == #
import os,sys
import time
import pandas as pd
import torch
from tqdm import tqdm
from transformers import pipeline
from psycopg2.extras import execute_values
import psycopg2
from datasets import Dataset
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from configuration import *
import warnings

# Remove Pandas warning to use SQLAlchemy
warnings.filterwarnings("ignore", message="pandas only supports SQLAlchemy")

# endregion ==  PART 1: IMPORTS == #

# region == PART 2: CONNECT TO DB

conn = psycopg2.connect(DATABASE_URL)
# Enables autocommit for safer concurrent writes
conn.set_session(autocommit=True)
print("Connected to DB")

with conn.cursor() as cursor:
    cursor.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_name='tweets' AND column_name='senti_raw_tabularis'
            ) THEN
                ALTER TABLE tweets ADD COLUMN senti_raw_tabularis text;
                RAISE NOTICE 'Column senti_raw_tabularis added.';
            ELSE
                RAISE NOTICE 'Column senti_raw_tabularis already exists.';
            END IF;
        END
        $$;
    """)
# endregion ==  PART 2: CONNECT TO DB == #

# region ==  PART 3: SENTIMENT PIPELINE SETUP (CUSTOMIZABLE)== #

# Customize: Force CPU if True, if False - tries to use GPU if available
FORCE_CPU = True
DEVICE_INDEX = 0

device = -1 if FORCE_CPU or not torch.cuda.is_available() else DEVICE_INDEX

# Customize: Change model here if needed
MODEL_NAME = "tabularisai/multilingual-sentiment-analysis"
tabularis = pipeline(
    "sentiment-analysis",
    model=MODEL_NAME,
    device=device,
    batch_size=32  # GPU-optimized batch size
)
print(f"Model loaded on {'CPU' if device == -1 else 'GPU'}")

# endregion ==  PART 3: SENTIMENT PIPELINE SETUP == #

# region ==  PART 4: BATCH SETTINGS (CUSTOMIZABLE) == #

# === Customize per teammate
# === Default setup is made for complete execution
BATCH_SIZE = 6_500_000               # How many tweets this person should process ()
CHUNK_SIZE = 10_000                    # How many tweets to process per DB fetch
BATCH_NUMBER = 0                     # Set 0 for first person, 1 for second, etc.
BATCH_USER = f"user_{BATCH_NUMBER}"  # for logging purposes

# Compute row_num bounds
offset = BATCH_NUMBER * BATCH_SIZE
upper_bound = offset + BATCH_SIZE 
last_row = offset
processed = 0

print(f" Starting BATCH {BATCH_NUMBER} from row_num {last_row + 1}")

# endregion ==  PART 4: BATCH SETTINGS (CUSTOMIZABLES) == #

# region ==  PART 5: FUNCTION TO PERFORM SENTIMENT ANALYSIS ON INPUT BATCH == #

def get_sentiments_batch(text_list):
    #  return setntiment scores for each tweet in the currently processed batch
    try: 
        results = tabularis([text[:512] for text in text_list])
        return [str(res) for res in results]
    # by error return an error message pointing to the faulty batch
    except Exception as e:
        print(f"Error in batch: {e} !")
        return [None] * len(text_list)
# endregion ==  PART 5: FUNCTION TO PERFORM SENTIMENT ANALYSIS ON INPUT BATCH == #

# region ==  PART 6: Load tweets, run model, update DB, log progress == #

while processed < BATCH_SIZE:
    # Extract tweet id, full text and row number into a dataframe for current batch
    query = f"""
        SELECT id, full_text AS text, row_num
        FROM tweets
        WHERE row_num > {last_row} AND row_num <= {upper_bound}
        ORDER BY row_num
        LIMIT {CHUNK_SIZE}
    """
    df = pd.read_sql(query, conn)

    if df.empty:
        print("No more tweets to process.")
        break

    print(f"Loaded {len(df)} tweets from row_num > {last_row}")

    # Perform Sentiment Analysis on current batch and store in the df
    df['senti_raw_tabularis'] = get_sentiments_batch(df['text'].tolist())

    # Upload the batch of sentiment score to the respective tweet in the db
    data_to_update = [(int(row.id), row.senti_raw_tabularis)
                       for row in df.itertuples(index=False)
                       if row.senti_raw_tabularis is not None]

    if data_to_update:
        update_query = """
            UPDATE tweets AS t
            SET senti_raw_tabularis = v.sentiment
            FROM (VALUES %s) AS v(id, sentiment)
            WHERE t.id = v.id
              AND t.senti_raw_tabularis IS NULL;
        """
        # Reconnection mechanism with 3 attempts by default
        for attempt in range(3):
            try:
                with conn.cursor() as cursor:
                    execute_values(cursor, update_query, data_to_update, template="(%s, %s)")
                print(f"Updated rows {last_row}–{last_row + len(data_to_update)}.")
                break
            except Exception as e:
                print(f"Attempt {attempt + 1} failed: {e}")
                if attempt < 2:
                    time.sleep(1)
                else:
                    print("Final update attempt failed.")
    else:
        print("No valid sentiment results in this chunk.")
    
    # Update information for batching
    last_row = df['row_num'].max()
    processed += len(df)

# endregion ==  PART 6: Load tweets, run model, update DB, log progress == #

print(f" Finished Loading Sentiment Analysis BATCH {BATCH_NUMBER}: Processed {processed} tweets.")
