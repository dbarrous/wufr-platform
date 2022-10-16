import logging
import sys
import psycopg2


def rds_connect():

    logger = logging.getLogger()

    logger.setLevel(logging.INFO)
    logger.info("Connecting to RDS")
    try:
        conn = psycopg2.connect(
            host="wufrr.cawbem9fwljk.us-east-1.rds.amazonaws.com",
            port="5432",
            user="wufr_admin",
            password="$Sadiel96",
            database="wufr",
        )
        logger.info("Connected to RDS")
        print("Connected to RDS")
        return conn

    except Exception as e:
        logger.error(f"ERROR: Unexpected error: Could not connect to RDS instance. {e}")
        sys.exit()
