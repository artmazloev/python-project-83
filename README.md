### Hexlet tests and linter status:
[![Actions Status](https://github.com/artmazloev/python-project-83/actions/workflows/hexlet-check.yml/badge.svg)](https://github.com/artmazloev/python-project-83/actions)


![Ruff Lint](https://github.com/artmazloev/python-project-83/actions/workflows/lint.yml/badge.svg)


[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=artmazloev_python-project-83&metric=sqale_rating)](https://sonarcloud.io/summary/new_code?id=artmazloev_python-project-83)
  


### Описание проекта
Это Flask-приложение для проверки сайтов. Проект позволяет:
- Добавлять URL-адреса
- Проверять доступность сайта (получать статус ответа)
- Сохранять результаты проверок
- Отображать историю проверок на странице сайта
# Page Analyzer (hexlet-code)


**Демонстрация**: [https://python-project-83-hfv6.onrender.com](https://python-project-83-hfv6.onrender.com)

---

## Стек технологий

- Python ≥ 3.10
- Flask
- PostgreSQL
- Gunicorn
- Requests, BeautifulSoup4
- psycopg2-binary
- Линтинг: Ruff
- Деплой: Render.com

---

## Структура проекта

```text
.
├── Makefile             # команды для локального запуска, линтинга и сборки
├── pyproject.toml       # зависимости и настройки проекта
├── .env.example         # образец переменных окружения
├── database.sql         # SQL-скрипт для создания схемы базы данных
├── main.py или package  # точка входа (в вашем случае: page_analyzer:app)
├── page_analyzer/       # пакет приложения:
│   ├── __init__.py      # инициализация Flask-приложения
│   ├── views.py         #
│   ├── models.py        #
│   └── ...              #
└── build.sh             # (если используется) скрипт сборки/деплоя


## Быстрый запуск (локально)

### 1. Клонировать репозиторий

```bash
git clone https://github.com/artmazloev/python-project-83.git
cd python-project-83
```

### 2. Настроить окружение

Создайте `.env` на основе `.env.example`:

```bash
SECRET_KEY=secret_key
DATABASE_URL=postgresql://username:password@localhost:5432/database_name
```

### 3. Установить зависимости

```bash
make install
```

### 4. Инициализировать базу данных

```bash
createdb page_analyzer
psql page_analyzer < database.sql
```

### 5. Запустить приложение (dev)

```bash
make dev
```

Откройте в браузере:
```
http://127.0.0.1:5000/
```

## Запуск в продакшене

### 1. Локально через Gunicorn

```bash
make start
```

По умолчанию порт — `8000`. Изменить порт:

```bash
PORT=5000 make start
```

### 2. Деплой на Render.com

```bash
make render-start
```

Эта команда эквивалентна:

```bash
gunicorn -w 5 -b 0.0.0.0:$PORT page_analyzer:app
```

Render подставит переменную окружения `PORT` и установит зависимости из `pyproject.toml`. Схему БД примените один раз к удалённой БД:

```bash
# пример: локально применить скрипт к удалённой БД Render
psql "<DATABASE_URL_из_Render>" -f database.sql
```

## Полезные команды

| Команда | Описание |
|---------|----------|
| `make lint` | Проверка кода (Ruff) |
| `make lint-fix` | Автоисправление части замечаний (Ruff `--fix`) |
| `make build` | Запуск `./build.sh` (если используется в вашем процессе сборки) |

## Переменные окружения

| Имя | Назначение | Пример |
|-----|------------|--------|
| `SECRET_KEY` | Секретный ключ Flask | `secret_key` |
| `DATABASE_URL` | Строка подключения к PostgreSQL | `postgresql://user:pass@localhost:5432/page_analyzer` |

## Структура проекта (основные файлы)

```
.
├── Makefile          # install/dev/start/render-start/lint/…
├── pyproject.toml    # зависимости и конфигурация (Python ≥3.10)
├── .env.example      # образец переменных окружения
├── database.sql      # схема базы данных
├── page_analyzer/    # модуль/пакет приложения, экспортирует `app`
│   └── __init__.py   # (или иной модуль) с объектом Flask `app`
└── build.sh          # вызывается целью `make build` (если используется)
```