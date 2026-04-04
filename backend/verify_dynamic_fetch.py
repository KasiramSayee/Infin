import os
import datetime
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
sb = create_client(os.environ.get('SUPABASE_URL'), os.environ.get('SUPABASE_KEY'))

def verify_dynamic_fetch():
    today = datetime.datetime.now().date().isoformat()
    unique_val = 0.0765 # A very specific value
    target_email = "kishore3@gmail.com"
    
    print(f"Targeting worker: {target_email}")
    
    # 1. Find which wards this worker has affinity for
    user_res = sb.table('workers').select('id').eq('email', target_email).execute().data
    worker_id = user_res[0]['id']
    affs = sb.table('worker_ward_affinity').select('ward_id').eq('worker_id', worker_id).execute().data
    ward_ids = [a['ward_id'] for a in affs]
    
    print(f"Updating {len(ward_ids)} associated wards to exactly {unique_val * 100}%...")
    
    # 2. Update peer_activity for ALL those wards to this unique value
    for w_id in ward_ids:
        sb.table('peer_activity').update({'percent_working': unique_val}).eq('ward_id', w_id).eq('date', today).execute()

    # 3. Trigger the Engine
    import httpx
    print("Triggering the Engine and waiting for it to finish...")
    try:
        # Use a synchronous post to ensure it finishes
        res = httpx.post('http://localhost:8000/api/v1/engine/evaluate', timeout=60.0)
        print(f"Engine replied with status: {res.status_code}")
    except Exception as e:
        print(f"Engine trigger error: {e}")

    # 4. Check the claims table for this exact value for THIS worker
    print(f"Checking claims for {target_email}...")
    claims = sb.table('claims').select('*, policies!inner(worker_id, workers!inner(email))').eq('policies.workers.email', target_email).order('created_at', desc=True).limit(1).execute().data
    
    if claims:
        actual_val = claims[0]['gate2_avg_peer_working_pct']
        print(f"Actual Value found in DB: {actual_val}")
        if abs(actual_val - unique_val) < 0.0001:
            print("\nSUCCESS: PROOF OF DYNAMIC FETCH!")
            print(f"The engine picked up your precise database value of {actual_val}!")
        else:
            print(f"\nFAILED: Value {actual_val} does not match {unique_val}.")
    else:
        print("\nFAILED: No claim found for this worker.")

if __name__ == "__main__":
    verify_dynamic_fetch()
