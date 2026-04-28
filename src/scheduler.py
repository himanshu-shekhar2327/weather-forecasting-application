import sys
sys.path.append('src')

from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime
from zones import CITY_DATA
from database import save_to_db
from model_selector import run_selector
from fetch_data import  fetch_recent_weather

def nightly_job():
    print(f'\n Nightly retrain started: {datetime.now()}')

    # Step 1 — fetch and save today's data for all cities
    for city, info in CITY_DATA.items():
        try:
            weather = fetch_recent_weather(
                info['lat'], info['lon'], days=1)
            
            if weather is not None:
                save_to_db(weather, city, info['zone'],
                          info['lat'], info['lon'], info['alt'])
                print(f"  {city} updated")
            else:
                print(f"  {city} — fetch failed, skipping")
        
        except Exception as e:
            print(f"  {city} error: {e}")
            continue

    # Step 2 — retrain all zone models once
    print("\n  Retraining all zone models...")
    run_selector()

    print(f"\n Nightly job complete: {datetime.now()}")
        
    
scheduler = BlockingScheduler()
scheduler.add_job(nightly_job, 'cron', hour=0, minute=0)

print('Scheduler started - nightly retrain at 12:00 AM')
scheduler.start()
        