# This file handles project documentation and setup instructions
# it defines quick start guides for local and Docker environments

# Telegram Profit Bot

Telegram бот для управления прибылью з поддержкой брендов, географии и менеджеров.

## Demo

Для демонстрации работы бота с образцовыми данными:

```bash
# Загрузить тестовые данные
sqlite3 bot.db < docs/sample_month_data.sql

# Проверить успешность загрузки
sqlite3 bot.db "SELECT COUNT(*) FROM reports;"  # должно быть ≥ 19

# Сгенерировать месячный отчёт
python -c "
import asyncio
from services.reports import generate_monthly_report
asyncio.run(generate_monthly_report(2025, 1))
"

# Просмотреть готовый отчёт
cat docs/sample_monthly_report.md
```

## ⚠️ Важливо: Міграція String → Date

**Для оновлення з попередніх версій:**
```bash
# Створіть резервну копію БД
cp bot.db bot.db.backup

# Запустіть міграцію для зміни типу поля month з VARCHAR на DATE
alembic upgrade head

# Перевірте результат
sqlite3 bot.db ".schema facts"
```

## Quick Start (venv)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
echo "BOT_TOKEN=PASTE_HERE" > .env
echo "ADMIN_TG_ID=YOUR_ADMIN_ID" >> .env
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

## Daily Workflow

Бот автоматически выполняет ежедневные задачи:

- **18:50** - Отправляет запросы планируемой прибыли всем менеджерам
- **19:30** - Отправляет дневной дайджест администратору

### Особенности:
- Дублирование вводов блокируется (уникальный индекс по office_id + geo_id + date)
- Логирование всех операций в `logs/` с ротацией
- ForceReply для удобного ввода сумм
- Retry логика для Telegram API с exponential backoff
- Поддержка различных форматов ввода сумм (пробелы, запятые, emoji)

## База данных

Проект использует SQLite с асинхронным доступом через SQLAlchemy и Alembic для миграций.

### Основные таблицы:
- `offices` - офисы (ранее brand)
- `geo` - география (связана с офисами)
- `users` - пользователи (ранее manager, связаны с офисами)
- `reports` - ежедневные отчёты
- `facts` - месячные факты (поле month теперь DATE для правильной сортировки)
