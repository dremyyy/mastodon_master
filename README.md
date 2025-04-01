# mastodon_masters

## How to use/run (OUTDATED/COMING SOON)

 1. Clone Repo
 2. cd /mastodo_streamer
 3. Create a file called ".env" that matches the example.txt file. You need a valid api key for every instance you want to track. Inser the fitting api key for each instance in MASTODON_ACCESS_TOKEN_n. If you dont want to track an instance remove both token and base url from the .env file. Last but not least make sure that NUM_INSTANCES matches the ammount of instances you want to track.
 4. run docker-compose up --build
 5. You can check if flask is running under 'http://localhost:5000/' or the active threads under 'http://localhost:5000/threads'
 6. You can access mongo express under 'http://localhost:8081/' or all the saved data under 'http://localhost:8081/db/mastodon_db/'
 
