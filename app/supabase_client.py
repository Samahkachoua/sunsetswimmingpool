import os

from dotenv import load_dotenv
from supabase import Client, create_client

load_dotenv()

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def sign_in_admin(email: str, password: str):
    # A dedicated client, kept separate from `supabase` above: signing in
    # mutates a client's session, and if done on the shared client it would
    # silently swap all subsequent queries from the service role (which
    # bypasses RLS) to the logged-in user's role (which is subject to RLS).
    auth_client = create_client(SUPABASE_URL, SUPABASE_KEY)
    return auth_client.auth.sign_in_with_password({"email": email, "password": password})


def get_admin_user(access_token: str):
    auth_client = create_client(SUPABASE_URL, SUPABASE_KEY)
    return auth_client.auth.get_user(access_token)
