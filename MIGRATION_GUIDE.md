# Running Database Migrations

## Steps to Run Migrations in Supabase

1. **Go to your Supabase Dashboard**
   - Visit: https://app.supabase.com
   - Select your project

2. **Open the SQL Editor**
   - Click on "SQL Editor" in the left sidebar
   - Click "New query"

3. **Run the Combined Migration**
   - Copy the contents from `migrations/000_combined_migration.sql`
   - Paste it into the SQL Editor
   - Click "Run" or press `Ctrl+Enter` (Windows/Linux) or `Cmd+Enter` (Mac)

4. **Verify the Tables**
   - Go to "Table Editor" in the left sidebar
   - You should see three new tables:
     - `users`
     - `password_reset_tokens`
     - `login_history`

## Alternative: Run Individual Migrations

If you prefer to run migrations one by one:

1. Run `001_create_users_table.sql`
2. Run `002_create_password_reset_tokens_table.sql`
3. Run `003_create_login_history_table.sql`

## Configure Your .env File

After running the migrations, make sure to update your `.env` file with your actual Supabase credentials:

```
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-anon-public-key
SUPABASE_SERVICE_KEY=your-service-role-key
JWT_SECRET_KEY=your-secret-key-minimum-32-characters
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

You can find these values in your Supabase Dashboard:
- Go to Project Settings → API
- Copy the Project URL (SUPABASE_URL)
- Copy the `anon` `public` key (SUPABASE_KEY)
- Copy the `service_role` key (SUPABASE_SERVICE_KEY)

## Test the API

Once migrations are complete and .env is configured:

1. The server is already running at: http://localhost:8000
2. View API documentation at: http://localhost:8000/docs
3. Try the endpoints:
   - POST /api/v1/register - Create a new user
   - POST /api/v1/login - Login
   - POST /api/v1/forgot-password - Request password reset
