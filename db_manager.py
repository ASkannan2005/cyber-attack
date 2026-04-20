import psycopg2
from psycopg2 import sql
import datetime

class DBManager:
    def __init__(self, host, database, user, password, port=5432):
        self.config = {
            "host": host,
            "database": database,
            "user": user,
            "password": password,
            "port": port
        }
        self.conn = None

    def connect(self):
        try:
            self.conn = psycopg2.connect(**self.config)
            return True
        except Exception as e:
            print(f"Error connecting to PostgreSQL: {e}")
            return False

    def init_db(self):
        """Creates the traffic_logs table if it doesn't exist."""
        if not self.conn:
            self.connect()
        
        query = """
        CREATE TABLE IF NOT EXISTS traffic_logs (
            id SERIAL PRIMARY KEY,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            duration FLOAT,
            src_bytes FLOAT,
            dst_bytes FLOAT,
            hot FLOAT,
            num_failed_logins FLOAT,
            logged_in FLOAT,
            num_compromised FLOAT,
            num_file_creations FLOAT,
            num_shells FLOAT,
            num_access_files FLOAT,
            is_guest_login FLOAT,
            count FLOAT,
            prediction INTEGER,
            probability FLOAT
        );
        """
        try:
            with self.conn.cursor() as cur:
                cur.execute(query)
                self.conn.commit()
            return True
        except Exception as e:
            print(f"Error initializing DB: {e}")
            return False

    def log_prediction(self, features, prediction, probability):
        """Saves a single prediction result to the DB."""
        if not self.conn:
            self.connect()
            
        query = """
        INSERT INTO traffic_logs (
            duration, src_bytes, dst_bytes, hot, num_failed_logins, logged_in,
            num_compromised, num_file_creations, num_shells, num_access_files,
            is_guest_login, count, prediction, probability
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """
        try:
            values = (
                features['duration'], features['src_bytes'], features['dst_bytes'],
                features['hot'], features['num_failed_logins'], features['logged_in'],
                features['num_compromised'], features['num_file_creations'],
                features['num_shells'], features['num_access_files'],
                features['is_guest_login'], features['count'],
                int(prediction), float(probability)
            )
            with self.conn.cursor() as cur:
                cur.execute(query, values)
                self.conn.commit()
            return True
        except Exception as e:
            print(f"Error logging to DB: {e}")
            return False

    def get_history(self, limit=10):
        """Retrieves recent logs."""
        if not self.conn:
            self.connect()
        
        query = "SELECT * FROM traffic_logs ORDER BY timestamp DESC LIMIT %s;"
        try:
            with self.conn.cursor() as cur:
                cur.execute(query, (limit,))
                return cur.fetchall()
        except Exception as e:
            print(f"Error fetching logs: {e}")
            return []
