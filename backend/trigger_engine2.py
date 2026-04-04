import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
client = create_client(url, key)

import main
main.supabase = client

import asyncio
from engine2 import evaluate_claims

async def main_func():
    print("Manually triggering Engine 2 Evaluation...")
    try:
        res = await evaluate_claims(None)
        print("Result:", res)
    except Exception as e:
        import traceback
        with open("trace.txt", "w", encoding="utf-8") as f:
             traceback.print_exc(file=f)
        print("Failed to run evaluate_claims:", e)

if __name__ == "__main__":
    asyncio.run(main_func())
