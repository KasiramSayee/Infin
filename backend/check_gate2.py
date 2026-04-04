import os
from datetime import datetime, timezone
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def check_gate2():
    now = datetime.now(timezone.utc)
    today_date = now.date().isoformat()
    
    print("\n" + "="*60)
    print(" GATE 2: ZONE PEER COMPARISON (ZPCS) VERIFIER")
    print("="*60)
    
    # 1. Inspect the Peer Activity for today across all wards
    print(f"Current Date: {today_date}")
    peer_res = supabase.table("peer_activity").select("ward_id, percent_working").eq("date", today_date).execute()
    peer_data = {p['ward_id']: p['percent_working'] for p in peer_res.data}
    
    wards_res = supabase.table("wards").select("id, name").execute()
    ward_names = {w['id']: w['name'] for w in wards_res.data}

    print("\nPeer Activity Baseline (Today):")
    for w_id, w_name in ward_names.items():
        working_pct = peer_data.get(w_id, 0.0)
        status = "[DISRUPTED]" if working_pct < 0.50 else "[ NORMAL ]"
        print(f" {status} | {w_name.ljust(20)} : {working_pct:.1%} of peers are working")
    
    print("\n" + "-"*40)
    
    # 2. Evaluate Workers
    workers = supabase.table("workers").select("id, email").execute().data
    print(f"Evaluating {len(workers)} workers for Gate 2 logic...\n")

    for i, worker in enumerate(workers, 1):
        worker_id = worker['id']
        email = worker.get('email', worker_id)
        
        # We need their disrupted wards (from Gate 1 logic)
        # For simplicity in this diagnostic script, we check which wards they have HIGH affinity for that are active
        affinities = supabase.table("worker_ward_affinity").select("ward_id, affinity_score").eq("worker_id", worker_id).execute().data
        
        # Check which wards are ACTUALLY disrupted RIGHT NOW (Latest event per ward)
        # We simulate the Gate 1 logic: only wards with a CURRENTLY active event count.
        disrupted_ids = set()
        for w_id in ward_names.keys():
            latest_res = supabase.table("zone_disruption_events").select("is_active").eq("ward_id", w_id).lte("created_at", now.isoformat()).order("created_at", desc=True).limit(1).execute()
            if latest_res.data and latest_res.data[0]['is_active']:
                disrupted_ids.add(w_id)
        
        worker_disrupted_wards = [a['ward_id'] for a in affinities if a['ward_id'] in disrupted_ids]
        
        if not worker_disrupted_wards:
            print(f"[{i}] WORKER: {email.ljust(25)} | SKIP (No disrupted wards found in Gate 1)")
            continue

        # Calculate Gate 2 manually for this worker
        total_working_pct_weighted = 0.0
        total_weight = 0.0
        applied_wards = []
        for w_id in worker_disrupted_wards:
            working_pct = peer_data.get(w_id, 1.0)
            
            # Find the affinity score for this ward
            ward_weight = 0.0
            for a in affinities:
                if a['ward_id'] == w_id:
                    ward_weight = a['affinity_score']
                    break
                    
            total_working_pct_weighted += (working_pct * ward_weight)
            total_weight += ward_weight
            
            applied_wards.append(f"{ward_names.get(w_id, w_id)} (Affinity: {ward_weight:.2f})")
            
        if total_weight > 0:
            avg_working = total_working_pct_weighted / total_weight
        else:
            avg_working = 1.0 # Fail safe
            
        zpcs_passed = avg_working <= 0.50 # Logic: Pass only if < 50% working
        
        result_icon = "PASS" if zpcs_passed else "REJECT"
        reason = "Disruption confirmed" if zpcs_passed else "Most peers working"
        ward_list_str = ", ".join(applied_wards)
        
        print(f"[{i}] WORKER: {email.ljust(25)} | {result_icon} | Avg: {avg_working:.1%} | Wards: [{ward_list_str}] | {reason}")

    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    check_gate2()
