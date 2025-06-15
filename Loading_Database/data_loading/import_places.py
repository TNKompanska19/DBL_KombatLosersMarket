import os,sys
import json
import pandas as pd
from sqlalchemy import create_engine, Table, MetaData, Text
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.exc import SQLAlchemyError
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from configuration import *

# ─── CONFIG ───────────────────────────────────────────────────────────────────
TABLE_NAME = "places"
CHUNK_SIZE = 9000
# ─────────────────────────────────────────────────────────────────────────────


def process_record(rec):
    """Extract place data from a record."""
    place = rec.get("place")
    if not place:
        return None

    bounding_box = place.get("bounding_box") or {}
    coordinates = bounding_box.get("coordinates")
    box_type = bounding_box.get("type")

    return {
        "id": place.get("id"),
        "place_type": place.get("place_type"),
        "name": place.get("name"),
        "country_code": place.get("country_code"),
        "coordinates": json.dumps(coordinates, ensure_ascii=False) if coordinates else None,
        "type_coordinates": box_type
    }


def insert_batch(engine, table, batch):
    """Insert a batch of records into the database with conflict handling."""
    if not batch:
        return
    try:
        with engine.begin() as conn:
            stmt = pg_insert(table).values(batch)
            stmt = stmt.on_conflict_do_nothing(index_elements=['id'])
            conn.execute(stmt)
        print(f"Inserted {len(batch)} records (skipping duplicates).")
    except SQLAlchemyError as e:
        print(f"Error during DB insert: {e}")


def stream_process_file(filepath, engine, table):
    """Stream a large JSON file line by line."""
    batch = []
    count = 0
    with open(filepath, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                print(f"Skipping invalid JSON line {i} in {os.path.basename(filepath)}")
                continue

            processed = process_record(rec)
            if processed:
                batch.append(processed)
                count += 1

            if len(batch) >= CHUNK_SIZE:
                insert_batch(engine, table, batch)
                batch.clear()

        if batch:
            insert_batch(engine, table, batch)

    print(f"Finished {os.path.basename(filepath)}: {count} records processed.")


def main():
    engine = create_engine(DATABASE_URL)

    # Reflect existing table to support insert with conflict handling
    metadata = MetaData()
    metadata.reflect(bind=engine)
    table = metadata.tables.get(TABLE_NAME)

    if table is None:
        print(f"Table '{TABLE_NAME}' not found in the database.")
        return

    files = sorted(f for f in os.listdir(FOLDER) if f.lower().endswith('.json'))
    print(f"Found {len(files)} JSON files to process.")

    for filename in files:
        filepath = os.path.join(FOLDER, filename)
        print(f"Processing {filename}")
        stream_process_file(filepath, engine, table)

    print("All files processed.")


if __name__ == '__main__':
    main()