import csv
import os
import sqlite3
from datetime import datetime


def export_audit_log(db_path: str = "lnt_sovereign.db", output_dir: str = "audit_exports"):
    """
    Exports the hardened decision ledger for SOC-2 / AIDA compliance review.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"lnt_audit_report_{timestamp}.csv"
    filepath = os.path.join(output_dir, filename)

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM decision_audits")
        rows = cursor.fetchall()

        # Get column names
        column_names = [description[0] for description in cursor.description]

        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(column_names)
            writer.writerows(rows)

        conn.close()
        return filepath, len(rows)
    except Exception as e:
        return None, str(e)

if __name__ == "__main__":
    print("🛡️ Initializing Sovereign Audit Export (SOC-2 Readiness)...")
    path, count = export_audit_log()
    if path:
        print(f"✅ Exported {count} verified decisions to: {path}")
    else:
        print(f"❌ Export failed: {count}")
