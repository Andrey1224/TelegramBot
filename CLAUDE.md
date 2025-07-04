# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Setup and Dependencies
```bash
# Virtual environment setup
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Environment configuration
echo "BOT_TOKEN=YOUR_TOKEN_HERE" > .env
```

### Database Operations
```bash
# Run migrations
alembic upgrade head

# Create new migration
alembic revision --autogenerate -m "description"

# Downgrade migration
alembic downgrade -1
```

### Running the Application
```bash
# Local development
python main.py

# Docker
docker build -t profit-bot .
docker run --env-file .env profit-bot
```

## Architecture Overview

This is a Telegram bot for profit management with support for brands, geography, and managers. The application uses:

- **AsyncIO**: All database operations and Telegram interactions are asynchronous
- **SQLAlchemy + Alembic**: Database ORM with async support and migration management
- **SQLite**: Database with foreign key constraints enabled via PRAGMA
- **python-telegram-bot**: Telegram Bot API wrapper

### Core Data Model
The application revolves around a hierarchical structure:
- `Brand` → has many `Geo` regions and `Manager`s
- `Geo` → belongs to one `Brand`, has many `Report`s and `Fact`s
- `Report` → daily planned amounts per geo/date (unique constraint)
- `Fact` → monthly actual amounts per geo/month (unique constraint)

### Project Structure
- `db/` - Database models, session management, and SQLAlchemy configuration
- `handlers/` - Telegram bot command handlers (start, admin, daily, monthly)
- `services/` - Business logic layer (CRUD operations, reports)
- `migrations/` - Alembic database migration files
- `utils/` - Helper functions (calendar utils, logging)

### Key Configuration
- Database URL: `sqlite+aiosqlite:///./bot.db` (configurable via DATABASE_URL env var)
- Foreign keys are enabled in SQLite via connection event listener
- Bot token loaded from `.env` file or BOT_TOKEN environment variable

### Database Session Pattern
Use `get_db()` async generator in handlers to properly manage database sessions:
```python
async with AsyncSessionLocal() as session:
    # database operations
```