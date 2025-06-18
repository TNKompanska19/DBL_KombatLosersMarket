# ----------------- CONFIG ------------------- #
FOLDER = r"E:\TUe\Y1_Q4_DBL_1\data_sample"

# ----------------- CREATE DATABASE CONFIG ---------------------#
DB_ADMIN_URL = "postgresql://postgres:1234@localhost:5432/postgres"
NEW_DB_NAME = "dbl_challenge_test"
DATABASE_URL = f"postgresql://postgres:1234@localhost:5432/{NEW_DB_NAME}"

# Uncomment this to use our cloud hosted database that contains everything pre-made for you:
# DATABASE_URL = "postgresql://dbadmin:BZ6uHRGxki6a7qD@dcpostgres.postgres.database.azure.com:5432/DataChallenge"