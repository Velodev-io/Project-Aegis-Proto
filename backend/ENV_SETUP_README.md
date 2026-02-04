# Environment Configuration & Database Setup - README

## Quick Setup

### 1. Environment Variables

```bash
# Copy the example file
cp .env.example .env

# Edit .env and fill in your values
nano .env
```

### 2. Database Initialization

```bash
# Using Alembic (recommended for production)
alembic upgrade head

# Or using legacy init (development only)
python database.py
```

### 3. Start the Backend

```bash
python main.py
```

## Environment Variables

See [.env.example](.env.example) for all available configuration options.

### Required for Basic Operation

- `DATABASE_URL` - Database connection string (defaults to SQLite)
- `CORS_ORIGINS` - Allowed frontend origins

### Optional Services

- `OPENAI_API_KEY` - Enable advanced AI scam detection
- `LITHIC_API_KEY` - Enable virtual card management
- `TWILIO_*` - Enable SMS notifications
- `SENDGRID_*` - Enable email notifications

## Database Migrations

See [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) for detailed migration instructions.

### Quick Commands

```bash
# Apply all pending migrations
alembic upgrade head

# Create new migration after model changes
alembic revision --autogenerate -m "Description"

# Rollback last migration
alembic downgrade -1
```

## Security Notes

⚠️ **NEVER commit `.env` to version control!**

- `.env` is in `.gitignore` by default
- Use `.env.example` as a template
- Store production secrets in secure secret management systems
- Rotate API keys regularly

## Troubleshooting

### Database Connection Errors

```bash
# Check database path
echo $DATABASE_URL

# Ensure data directory exists
mkdir -p data

# Reinitialize database
rm data/aegis_trust_vault.db
alembic upgrade head
```

### Missing Environment Variables

The application will use sensible defaults for most variables. Check logs for warnings about missing configuration.
