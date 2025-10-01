import os
import time
import psycopg2

def main():
    host = os.getenv("POSTGRES_HOST","postgres")
    port = int(os.getenv("POSTGRES_PORT","5432"))
    db = os.getenv("POSTGRES_DB","capacity_manager")
    user = os.getenv("POSTGRES_USER","cm_user")
    password = os.getenv("POSTGRES_PASSWORD","cm_password")

    for _ in range(60):
        try:
            conn = psycopg2.connect(host=host, port=port, dbname=db, user=user, password=password)
            conn.close()
            print("Database ready")
            return
        except Exception as e:
            print(f"Waiting for DB: {e}")
            time.sleep(2)
    raise SystemExit("DB not ready after retries")

if __name__ == "__main__":
    main()
