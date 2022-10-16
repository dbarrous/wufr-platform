import logging
import sys
import psycopg2
import os 

def rds_connect():

    logger = logging.getLogger()

    logger.setLevel(logging.INFO)
    logger.info("Connecting to RDS")
    try:
        conn = psycopg2.connect(
            host=os,
            port=os.environ('DB_PORT'),
            user=os.environ('DB_USER'),
            password=os.environ('DB_PASSWORD'),
            database=os.environ('DB_NAME'),
        )
        logger.info("Connected to RDS")
        print("Connected to RDS")
        return conn

    except Exception as e:
        logger.error(f"ERROR: Unexpected error: Could not connect to RDS instance. {e}")
        sys.exit()
