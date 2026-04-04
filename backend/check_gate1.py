import os
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def check_gate1():
    now = datetime.now(timezone.utc)
    
    print("\n" + "="*60)
    print(" GATE 1: WARD AFFINITY AND DISRUPTION IMPACT ENGINE VERIFIER")
    print("="*60)
    
    # Check what wards are currently disrupted
    events_res = supabase.table("zone_disruption_events").select("ward_id").eq("is_active", True).lte("created_at", now.isoformat()).execute()
    # Convert to set because zone_disruption_events contains hourly logs (multiple rows per ward)
    disrupted_ward_ids = list(set([e['ward_id'] for e in events_res.data]))
    
    if not disrupted_ward_ids:
        print("\nNo wards are currently actively disrupted. Gate 1 will ignore everyone.")
        return
        
    print(f"Active Disrupted Wards detected: {len(disrupted_ward_ids)}")

    # Check all active policies
    policies = supabase.table("policies").select("id, worker_id").eq("status", "active").execute().data
    print(f"Evaluating {len(policies)} active workers...\n")
    
    for i, policy in enumerate(policies, 1):
        worker_id = policy['worker_id']
        worker = supabase.table("workers").select("email").eq("id", worker_id).execute().data[0]
        
        # Get cached affinity from database
        affinities = supabase.table("worker_ward_affinity").select("ward_id, affinity_score").eq("worker_id", worker_id).execute().data
        
        if not affinities:
            continue
            
        print(f"[{i}] WORKER: {worker.get('email', worker_id)}")
        print("-" * 40)
        
        disrupted_sum = 0.0
        remaining_sum = 0.0
        
        print("Affinities Breakdown:")
        for aff in affinities:
            w_id = aff['ward_id']
            score = aff['affinity_score']
            ward_name = supabase.table("wards").select("name").eq("id", w_id).execute().data[0]['name']
            
            if w_id in disrupted_ward_ids:
                print(f" ⚠️  {ward_name} (DISRUPTED) : {score:.3f}")
                disrupted_sum += score
            else:
                print(f" ✅  {ward_name} (Clear)     : {score:.3f}")
                remaining_sum += score
                
        print("\nGATE 1 MATHEMATICAL CHECK:")
        print(f" Total Disrupted Affinity : {disrupted_sum:.3f}")
        print(f" Total Remaining Affinity : {remaining_sum:.3f}")
        
        if disrupted_sum >= remaining_sum:
            print(f" 🟢 RESULT: Gate 1 PASSED! ({disrupted_sum:.3f} >= {remaining_sum:.3f})")
            print(" -> Worker relies heavily on disrupted zones and cannot compensate.")
        else:
            print(f" 🔴 RESULT: Gate 1 FAILED. ({disrupted_sum:.3f} < {remaining_sum:.3f})")
            print(" -> Worker can comfortably compensate their income in remaining clear zones.")
            
        print("="*60 + "\n")

if __name__ == "__main__":
    check_gate1()
