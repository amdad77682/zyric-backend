from supabase import create_client, Client
from app.config import get_settings

settings = get_settings()

# Create Supabase client
supabase: Client = create_client(settings.supabase_url, settings.supabase_key)

# Create Supabase client with service role key for admin operations
supabase_admin: Client = create_client(settings.supabase_url, settings.supabase_service_key)
