import os
from datetime import datetime, timezone
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def check_gate3():
    now = datetime.now(timezone.utc)
    
    print("\n" + "="*60)
    print(" GATE 3: ANTI-EXPLOITATION (AEC) VERIFIER")
    print("="*60)
    
    # Evaluate Workers
    workers = supabase.table("workers").select("id, email").execute().data
    print(f"Evaluating {len(workers)} workers for Gate 3 logic...\n")

    for i, worker in enumerate(workers, 1):
        worker_id = worker['id']
        email = worker.get('email', worker_id)
        
        # Get policy
        pol = supabase.table("policies").select("*").eq("worker_id", worker_id).eq("status", "active").execute().data
        if not pol:
            print(f"[{i}] WORKER: {email.ljust(25)} | SKIP (No active policy found)")
            continue
        policy = pol[0]
        
        affinities = supabase.table("worker_ward_affinity").select("ward_id, affinity_score").eq("worker_id", worker_id).execute().data
        
        # Find earliest event for ALL disrupted wards they care about (Gate 1 footprint)
        earliest_event_start = None
        for a in affinities:
            event_res = supabase.table("zone_disruption_events").select("*").eq("ward_id", a['ward_id']).eq("is_active", True).lte("created_at", now.isoformat()).order("created_at", desc=True).limit(1).execute()
            if event_res.data:
                e_start = datetime.fromisoformat(event_res.data[0]['created_at'].replace('Z', '+00:00'))
                if earliest_event_start is None or e_start < earliest_event_start:
                    earliest_event_start = e_start
        
        if not earliest_event_start:
            print(f"[{i}] WORKER: {email.ljust(25)} | SKIP (No active disruptions linked to worker)")
            continue
            
        policy_start = datetime.fromisoformat(str(policy['coverage_start_at']).replace('Z', '+00:00'))
        
        # Enforce timezone comparison
        if not policy_start.tzinfo:
            policy_start = policy_start.replace(tzinfo=timezone.utc)
        if not earliest_event_start.tzinfo:
            earliest_event_start = earliest_event_start.replace(tzinfo=timezone.utc)
            
        aec_passed = policy_start < earliest_event_start
        
        result_icon = "PASS" if aec_passed else "REJECT"
        reason = "Policy active BEFORE disaster" if aec_passed else "Policy bought AFTER disaster!"
        
        # Format neatly
        p_start_str = policy_start.strftime('%Y-%m-%d %H:%M')
        e_start_str = earliest_event_start.strftime('%Y-%m-%d %H:%M')
        
        print(f"[{i}] WORKER: {email.ljust(25)} | {result_icon} | {reason}")
        print(f"    -> Policy Start: {p_start_str} | Disaster Start: {e_start_str}")

    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    check_gate3()
