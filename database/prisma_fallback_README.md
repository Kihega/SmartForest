# SmartForest — Database & Prisma Guide

## Why two URLs, and why both use the pooler

Supabase exposes Postgres through PgBouncer (the pooler). The raw direct host
`db.[REF].supabase.co:5432` requires a **paid IPv4 add-on** on free-tier projects.

The solution is to use BOTH pooler modes, which are available for free:

| Variable              | Tab in Supabase UI | Port | Used by                     |
|-----------------------|--------------------|------|-----------------------------|
| `DATABASE_URL`        | Transaction        | 6543 | App queries at runtime      |
| `DATABASE_URL_DIRECT` | Session            | 5432 | `prisma db push` / migrate  |

Both URLs point to `aws-0-[region].pooler.supabase.com` — only the port differs.

**Transaction pooler (6543):** Each query may get a different DB connection.
Fast and efficient for read/write app traffic. Append `?pgbouncer=true&connection_limit=1`.

**Session pooler (5432):** One persistent connection per client. Required for
DDL statements (CREATE TABLE, ALTER TABLE) that Prisma migrations use.

### Where to get the URLs
Supabase dashboard → **Settings → Database → Connection string → URI format**

- Click **"Transaction"** tab → copy URI → append `?pgbouncer=true&connection_limit=1`
- Click **"Session"** tab → copy URI → use as-is

---

## First-time setup commands

```bash
cd backend
cp .env.example .env        # edit with your URLs and keys
npm install                 # prisma generate runs automatically via postinstall

# Push schema to DB (creates all tables)
npx prisma db push

# Seed admin user + sample data
npx prisma db seed
```

## Daily commands

| Task                        | Command                       |
|-----------------------------|-------------------------------|
| Apply schema changes        | `npx prisma db push`          |
| Browse data visually        | `npx prisma studio`           |
| Re-run seed                 | `npx prisma db seed`          |
| Regenerate client (after pull) | `npx prisma generate`      |
| Check migration status      | `npx prisma migrate status`   |

## phone column

`phone` is stored in **Supabase user_metadata** (the auth layer).
It does not exist in the `users` DB table by default, which avoids schema
drift with databases created before this column was added.

To add it to the table later:
1. Run `database/migrations/006_add_phone_to_users.sql` in Supabase SQL Editor
2. Uncomment `phone String? @db.VarChar(30)` in `prisma/schema.prisma`
3. Run `npx prisma db push`

## GitHub Secrets required

Go to: GitHub repo → Settings → Secrets and variables → Actions → New secret

| Secret                | Value                                                      |
|-----------------------|------------------------------------------------------------|
| `DATABASE_URL`        | Transaction pooler URI (port 6543) + pgbouncer params      |
| `DATABASE_URL_DIRECT` | Session pooler URI (port 5432)                             |
| `SUPABASE_URL`        | `https://[REF].supabase.co`                                |
| `SUPABASE_ANON_KEY`   | from Supabase → Settings → API                             |
| `SUPABASE_SERVICE_KEY`| from Supabase → Settings → API (service_role key)          |
| `JWT_SECRET`          | any long random string                                     |
| `VITE_API_URL_CLOUD`  | `https://your-render-app.onrender.com/api`                 |

## Manual SQL fallback (if Prisma can't connect at all)

Run these files in order via Supabase SQL Editor:
```
001_create_users.sql
002_create_sensor_readings.sql
003_create_alerts.sql
004_create_devices.sql
005_admin_seed.sql
```
