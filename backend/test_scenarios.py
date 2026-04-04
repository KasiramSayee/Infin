import os
import sys
import datetime
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
sb = create_client(os.environ.get('SUPABASE_URL'), os.environ.get('SUPABASE_KEY'))

def run_scenario(scenario_num):
    today = datetime.datetime.now().date().isoformat()
    
    if scenario_num == 1:
        # Scenario 1: Legitimate Disruption for kishore3@gmail.com in Ward East
        ward_name = "Ward East - Mumbai"
        target_email = "kishore3@gmail.com"
        pct = 0.1
        print(f"Setting up Scenario 1: {ward_name} at {pct*100}% working...")
    elif scenario_num == 2:
        # Scenario 2: Lazy Worker for siddharth@gmail.com in Ward North
        ward_name = "Ward North - Mumbai"
        target_email = "siddharth@gmail.com"
        pct = 0.9
        print(f"Setting up Scenario 2: {ward_name} at {pct*100}% working...")
    else:
        print("Invalid scenario number")
        return

    # 0. Ensure target worker has an active policy
    user_res = sb.table('workers').select('id').eq('email', target_email).execute().data
    if not user_res:
        print(f"User {target_email} not found")
        return
    worker_id = user_res[0]['id']
    
    policy_check = sb.table('policies').select('id').eq('worker_id', worker_id).eq('status', 'active').execute().data
    if not policy_check:
        print(f"Creating mock active policy for {target_email}...")
        sb.table('policies').insert({
            'worker_id': worker_id,
            'status': 'active',
            'coverage_start_at': (datetime.datetime.now() - datetime.timedelta(days=7)).isoformat(),
            'base_income': 1000,
            'floor_income': 700
        }).execute()

    # 1. Update Ward Peer Activity
    ward_res = sb.table('wards').select('id').eq('name', ward_name).execute().data
    if not ward_res:
        print(f"Ward {ward_name} not found")
        return
    ward_id = ward_res[0]['id']

    # 2. Ensure an active disruption event exists for this ward so it passes Gate 1
    event_check = sb.table('zone_disruption_events').select('id').eq('ward_id', ward_id).eq('is_active', True).execute().data
    if not event_check:
        print(f"Creating mock active disruption for {ward_name}...")
        sb.table('zone_disruption_events').insert({
            'ward_id': ward_id,
            'is_active': True,
            'type': 'rain',
            'val': 50.0,
            'created_at': (datetime.datetime.now() - datetime.timedelta(hours=1)).isoformat()
        }).execute()

    # 3. Update Ward Peer Activity
    sb.table('peer_activity').update({'percent_working': pct}).eq('ward_id', ward_id).eq('date', today).execute()

    # Trigger Evaluation
    import httpx
    print("Triggering Engine Evaluation...")
    try:
        res = httpx.post("http://localhost:8000/api/v1/engine/evaluate", timeout=30.0)
        print(f"Engine replied: {res.status_code}")
    except Exception as e:
        print(f"Engine Trigger Failed: {e}")

    # Fetch and Report Result
    claims = sb.table('claims').select('*, policies!inner(worker_id, workers!inner(email))').eq('policies.workers.email', target_email).order('created_at', desc=True).limit(1).execute().data
    if not claims:
        print(f"No claim found for {target_email}")
        return
    
    r = claims[0]
    print("\n" + "="*40)
    print(f"TEST RESULT: SCENARIO {scenario_num}")
    print(f"Worker: {target_email}")
    print(f"Ward: {ward_name}")
    print(f"Peer Working %: {r['gate2_avg_peer_working_pct']:.1%}")
    print(f"Gate 2 Passed: {r['zpcs_passed']}")
    print(f"Overall Status: {r['status']}")
    print("="*40 + "\n")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_scenarios.py <1 or 2>")
    else:
        run_scenario(int(sys.argv[1]))
