# daily_report_main.py

from datetime import datetime
import pandas as pd
from config_utils import get_connection, run_query, send_email, EMAIL_RECIPIENTS, logging

# ------------------------------
# Build HTML report
# ------------------------------
def prepare_email_body(results):
    style = """
    <style>
        body { font-family: Calibri, sans-serif; color: #333; }
        h2 { color: #0A66C2; border-bottom: 2px solid #0A66C2; padding-bottom: 4px; }
        h3 { color: #0A66C2; margin-top: 25px; }
        table {
            border-collapse: collapse;
            width: 100%;
            margin-top: 8px;
            margin-bottom: 25px;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 8px 10px;
            text-align: left;
        }
        th {
            background-color: #E8F1FA;
            color: #0A66C2;
            font-weight: 600;
        }
        tr:nth-child(even) { background-color: #F9FBFD; }
        tr:hover { background-color: #F1F6FB; }
        .section {
            margin-bottom: 40px;
        }
        .footer {
            font-size: 13px;
            color: #666;
            margin-top: 30px;
        }
    </style>
    """

    body = f"""
    <html>
    <head>{style}</head>
    <body>
        <h2>📊 Daily Automation Report - {datetime.now().strftime('%d %B %Y')}</h2>
        <p>Hi Team,</p>
        <p>Please find below the summary of today’s automation run.</p>
    """

    for title, df in results.items():
        if df.empty:
            table_html = "<p><i>No records found for this section.</i></p>"
        else:
            table_html = df.to_html(index=False, border=0, classes='dataframe')

        body += f"""
        <div class="section">
            <h3>🔹 {title}</h3>
            {table_html}
        </div>
        """

    body += """
        <div class="footer">
            <p>Kind regards,<br>
            <i>This is an automated email. Please do not reply directly.</i></p>
        </div>
    </body>
    </html>
    """
    return body


# ------------------------------
# Main Logic
# ------------------------------
def main():
    try:
        conn = get_connection()

        queries = {
            "No of Records Received": """
                SELECT COUNT(*) AS record_count
                FROM telikosgov.shipment_info
                WHERE CAST(datedon AS date) = DATE '2025-10-27';
            """,
            "Status Report": """
                SELECT status, charge_status, COUNT(*) AS record_count
                FROM telikosgov.shipment_info
                WHERE CAST(datedon AS date) = DATE '2025-10-27'
                GROUP BY status, charge_status
                ORDER BY record_count DESC;
            """,
            "Charge Wise Report": """
                SELECT charge_cd, status, COUNT(*) AS record_count
                FROM telikosgov.shipment_info
                WHERE CAST(datedon AS date) = DATE '2025-10-27'
                GROUP BY charge_cd, status
                ORDER BY charge_cd;
            """,
            "Charge Codes with No Records": """
                SELECT DISTINCT charge_cd
                FROM (
                    SELECT charge_cd
                    FROM telikosgov.charge_config
                    WHERE is_charge_enabled = 'true'
                      AND product IN ('OCEAN', 'LNS', 'DUAL_CHARGE')
                ) AS input_codes
                WHERE charge_cd NOT IN (
                    SELECT DISTINCT charge_cd
                    FROM telikosgov.shipment_info
                    WHERE CAST(datedon AS date) = DATE '2025-10-27'
                );
            """
        }

        results = {}
        for title, query in queries.items():
            logging.info(f"Running section: {title}")
            df = run_query(conn, query)
            results[title] = df

        conn.close()
        logging.info("Database connection closed.")

        html_body = prepare_email_body(results)
        send_email(
            subject=f"Daily Automation Report - {datetime.now().strftime('%Y-%m-%d')}",
            html_body=html_body,
            to_recipients=EMAIL_RECIPIENTS
        )

    except Exception as e:
        logging.error(f"Unexpected error in main(): {e}")


if __name__ == "__main__":
    main()
