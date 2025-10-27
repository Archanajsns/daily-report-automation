# config_utils.py

import psycopg2
import pandas as pd
import logging
import os
from dotenv import load_dotenv
import win32com.client

# ------------------------------
# Load environment variables
# ------------------------------
load_dotenv()

DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'database': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'port': os.getenv('DB_PORT', 5432)
}

EMAIL_RECIPIENTS = os.getenv('EMAIL_RECIPIENTS', '').split(';')

# ------------------------------
# Logging setup
# ------------------------------
logging.basicConfig(
    filename='../logs/daily_report.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# ------------------------------
# Database connection
# ------------------------------
def get_connection():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        logging.info("✅ Database connection successful")
        return conn
    except Exception as e:
        logging.error(f"❌ Database connection failed: {e}")
        raise

# ------------------------------
# Run SQL query and return DataFrame
# ------------------------------
def run_query(conn, query):
    try:
        logging.info(f"Running query:\n{query}")
        return pd.read_sql(query, conn)
    except Exception as e:
        logging.error(f"❌ Error running query: {e}")
        return pd.DataFrame()

# ------------------------------
# Send Outlook Email
# ------------------------------
def send_email(subject, html_body, to_recipients):
    try:
        outlook = win32com.client.Dispatch("Outlook.Application")
        mail = outlook.CreateItem(0)
        mail.To = ";".join(to_recipients)
        mail.Subject = subject
        mail.HTMLBody = html_body
        mail.Send()
        logging.info("✅ Email sent successfully!")
    except Exception as e:
        logging.error(f"❌ Error sending email: {e}")
