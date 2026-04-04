import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
sb = create_client(os.environ.get('SUPABASE_URL'), os.environ.get('SUPABASE_KEY'))

claims = sb.table('claims').select('*').execute().data
print(f'Total claims in DB: {len(claims)}')
print("=" * 70)

for c in claims:
    pol = sb.table('policies').select('worker_id').eq('id', c['policy_id']).execute().data
    worker_id = pol[0]['worker_id'] if pol else 'unknown'
    email_res = sb.table('workers').select('email').eq('id', worker_id).execute().data
    email = email_res[0]['email'] if email_res else 'unknown'

    g1 = "PASS" if c.get("gate1_passed") else "FAIL"
    g2 = "PASS" if c.get("zpcs_passed") else "FAIL"
    g3 = "PASS" if c.get("aec_passed") else "FAIL"
    status = c.get("status", "unknown").upper()

    print(f"Worker : {email}")
    print(f"  Gate 1 (Affinity)        : {g1}")
    print(f"  Gate 2 (Peer Comparison) : {g2}")
    print(f"  Gate 3 (Policy Timing)   : {g3}")
    print(f"  Claim Status             : {status}")
    print("-" * 70)
