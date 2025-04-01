# update_analytics.py
from pymongo import MongoClient
import pandas as pd
from datetime import datetime, timedelta
import pytz
from dotenv import load_dotenv
import os

dotenv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '.env')
load_dotenv(dotenv_path)

mongo_uri = os.getenv('MONGO_URI')
mongo_db_name_A = os.getenv('MONGO_DB_A')
mongo_db_name_B = os.getenv('MONGO_DB_B')


client = MongoClient(mongo_uri)

# Databases
raw_db = client[mongo_db_name_B]        # Raw data
analytics_db = client[mongo_db_name_A]  # Precomputed analytics

# Collection names
collection_names = raw_db.list_collection_names()
postsperday_collection = analytics_db['postsperday']
dailyactiveusers_collection = analytics_db['dailyactiveusers']
averageuseractivity_collection = analytics_db['averageuseractivity']

# Define timezones
utc = pytz.utc
cet = pytz.timezone("Europe/Berlin")

current_utc_date = datetime.now(utc).date()

# Get all unique dates present in `mastodon_db`
existing_dates = set()
for collection_name in collection_names:
    collection = raw_db[collection_name]

    # Get timestamps of all posts
    cursor = collection.find({}, {"_id": 0, "created_at": 1})
    df = pd.DataFrame(list(cursor))

    if not df.empty:
        df["created_at"] = pd.to_datetime(df["created_at"], format="ISO8601").dt.strftime("%Y-%m-%d")
        existing_dates.update(df["created_at"].unique())

# Remove today's date from processing (only process finished days)
existing_dates = {d for d in existing_dates if d < current_utc_date.strftime("%Y-%m-%d")}

# Get all unique dates already in `analytics_db`
analytics_dates_posts = set(postsperday_collection.distinct("date"))
analytics_dates_users = set(dailyactiveusers_collection.distinct("date"))
analytics_dates_avg = set(averageuseractivity_collection.distinct("date"))

# Find missing dates for all three tables (only for finished days)
missing_dates_posts = sorted(existing_dates - analytics_dates_posts)
missing_dates_users = sorted(existing_dates - analytics_dates_users)
missing_dates_avg = sorted(existing_dates - analytics_dates_avg)

# Prepare data for insertion
postsperday_data = []
dailyactiveusers_data = []
averageuseractivity_data = []

for missing_date in sorted(set(missing_dates_posts + missing_dates_users + missing_dates_avg)):  # Combine missing dates
    start_time = datetime.strptime(missing_date, "%Y-%m-%d").replace(tzinfo=utc)
    end_time = start_time + timedelta(days=1)

    for collection_name in collection_names:
        collection = raw_db[collection_name]

        # Count number of posts
        post_count = collection.count_documents({
            "created_at": {"$gte": start_time.isoformat(), "$lt": end_time.isoformat()}
        })

        # Count unique users
        unique_users = len(collection.distinct("user_id", {
            "created_at": {"$gte": start_time.isoformat(), "$lt": end_time.isoformat()}
        }))

        # Calculate average user activity (posts per active user)
        avg_activity = round(post_count / unique_users, 2) if unique_users > 0 else 0

        # Store post count
        if missing_date in missing_dates_posts:
            postsperday_data.append({
                "date": missing_date,
                "instance": collection_name,
                "post_count": post_count
            })

        # Store unique active user count
        if missing_date in missing_dates_users:
            dailyactiveusers_data.append({
                "date": missing_date,
                "instance": collection_name,
                "active_users": unique_users
            })

        # Store average user activity
        if missing_date in missing_dates_avg:
            averageuseractivity_data.append({
                "date": missing_date,
                "instance": collection_name,
                "avg_posts_per_user": avg_activity
            })

# Insert missing records into `analytics_db`
if postsperday_data:
    postsperday_collection.insert_many(postsperday_data)
    print(f"Added {len(missing_dates_posts)} missing days to postsperday.")

if dailyactiveusers_data:
    dailyactiveusers_collection.insert_many(dailyactiveusers_data)
    print(f"Added {len(missing_dates_users)} missing days to dailyactiveusers.")

if averageuseractivity_data:
    averageuseractivity_collection.insert_many(averageuseractivity_data)
    print(f"Added {len(missing_dates_avg)} missing days to averageuseractivity.")

if not postsperday_data and not dailyactiveusers_data and not averageuseractivity_data:
    print("No missing days detected. Analytics up to date.")
