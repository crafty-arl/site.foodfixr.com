from supabase import create_client, Client
import os
# Initialize Supabase client
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase_client: Client = create_client(url, key)