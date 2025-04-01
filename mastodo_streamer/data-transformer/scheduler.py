import schedule
import time
import subprocess
from datetime import datetime

def run_update():
    print(f"[{datetime.now()}] Running update_analytics.py")
    result = subprocess.run(
        ["python", "/app/update_analytics.py"],
        capture_output=True,
        text=True
    )
    print(result.stdout)
    print(result.stderr)

run_update()

schedule.every().day.at("02:00").do(run_update)

print("Scheduler started. Waiting for next run...")

while True:
    schedule.run_pending()
    time.sleep(30)
