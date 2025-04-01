import schedule
import time
import subprocess
from datetime import datetime

def run_update():
    print(f"[{datetime.now()}] Running update_analytics.py")
    subprocess.run(["python", "/app/update_analytics.py"])

run_update()

schedule.every().day.at("01:00").do(run_update)

print("Scheduler started. Waiting for next run...")

while True:
    schedule.run_pending()
    time.sleep(30)
