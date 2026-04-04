import os
import datetime
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
sb = create_client(os.environ.get('SUPABASE_URL'), os.environ.get('SUPABASE_KEY'))

def set_diversity():
    today = datetime.datetime.now().date().isoformat()
    val_map = {
        'Ward East - Mumbai': 0.10,
        'Ward North - Mumbai': 0.45,
        'Ward West - Mumbai': 0.90,
        'Ward South - Mumbai': 1.00,
        'Ward Central - Mumbai': 1.00
    }
    
    wards = sb.table('wards').select('id, name').execute().data
    for w in wards:
        if w['name'] in val_map:
            pct = val_map[w['name']]
            sb.table('peer_activity').update({'percent_working': pct}).eq('ward_id', w['id']).eq('date', today).execute()
            print(f"Updated {w['name']} to {pct*100}%")

    # Trigger Evaluation
    import httpx
    print("Triggering the Engine...")
    try:
        res = httpx.post("http://localhost:8000/api/v1/engine/evaluate", timeout=30.0)
        print(f"Engine replied: {res.status_code}")
    except Exception as e:
        print(f"Engine trigger error: {e}")

if __name__ == "__main__":
    set_diversity()
