import psycopg2

try:
    conn = psycopg2.connect(
        host="localhost",
        port="5432",
        database="dbl_challenge",
        user="postgres",
        password="1234"
    )

except psycopg2.Error as e:
    print("Error while connecting to PostgreSQL:", e)
