# This file handles project documentation and setup instructions
# it defines quick start guides for local and Docker environments

# Telegram Profit Bot

Telegram бот для управления прибылью с поддержкой брендов, географии и менеджеров.

## Quick Start (venv)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
echo "BOT_TOKEN=PASTE_HERE" > .env
python main.py
```

## Quick Start (Docker)

```bash
docker build -t profit-bot .
docker run --env-file .env profit-bot
```

## Структура проекта

```
telegram-profit-bot/
├── db/                    # Модели и подключение к БД
│   ├── models.py         # Brand, Geo, Manager, Report, Fact
│   └── session.py        # AsyncSession, PRAGMA FK
├── migrations/           # Alembic миграции
├── handlers/            # Telegram хендлеры
├── services/            # Бизнес-логика
├── utils/               # Вспомогательные функции
└── main.py              # Точка входа
```

## База данных

Проект использует SQLite с асинхронным доступом через SQLAlchemy и Alembic для миграций.

### Основные таблицы:
- `brand` - бренды
- `geo` - география (связана с брендами)
- `manager` - менеджеры (связаны с брендами)
- `report` - ежедневные отчёты
- `fact` - месячные факты
