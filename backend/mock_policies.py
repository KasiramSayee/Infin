import os
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def mock_policies():
    print("Generating active policies for workers...")
    workers_res = supabase.table("workers").select("id").execute()
    workers = workers_res.data
    
    if not workers:
        print("No workers found.")
        return
        
    now = datetime.now(timezone.utc)
    
    for worker in workers:
        worker_id = worker['id']
        
        # Check if active policy exists
        pol = supabase.table("policies").select("id").eq("worker_id", worker_id).eq("status", "active").execute()
        if not pol.data:
            supabase.table("policies").insert({
                "worker_id": worker_id,
                "policy_cost": 250,
                "expected_daily_earnings": 1000,
                "disruption_probability": 0.05,
                "coverage_start_at": (now - timedelta(days=7)).isoformat(),
                "status": "active",
                "cumulative_weeks_count": 5,
                "cumulative_amount_collected": 1250.0
            }).execute()
            print(f"Created active policy for worker {worker_id}")
        else:
            print(f"Worker {worker_id} already has active policy.")
            
    print("Policy generation complete.")

if __name__ == "__main__":
    mock_policies()
