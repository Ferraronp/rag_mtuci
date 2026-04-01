# RAG МТУСИ

Чат-бот с двухэтапным RAG-пайплайном: ищет информацию в интернете, фильтрует её малой моделью и формулирует ответ большой моделью. Оба этапа используют бесплатные LLM через OpenRouter.

## Как это работает

```
Запрос пользователя
        │
        ▼
[1] Google Search → список URL
        │
        ▼
[2] Playwright (headless Chromium)
    └─ Параллельно загружает страницы
    └─ JS-overrides для обхода антибот-защиты
        │
        ▼
[3] Малая модель — Llama 3.3 Nemotron 49B (OpenRouter, free)
    └─ Текст каждой страницы бьётся на чанки по 4000 токенов (tiktoken)
    └─ Каждый чанк параллельно (до 5 запросов) анализируется:
         ├─ [Да]  — содержит полезную информацию → сохраняется
         └─ [Нет] — нерелевантно → отбрасывается
        │
        ▼
[4] Большая модель — Llama 3.1 Nemotron Ultra 253B (OpenRouter, free)
    └─ Получает все отфильтрованные фрагменты
    └─ Формулирует итоговый ответ с источниками
        │
        ▼
Ответ + список источников (URL)
```

## Стек

- **FastAPI** — бэкенд API
- **Playwright** — парсинг веб-страниц (headless Chromium, обход антибот-защиты)
- **tiktoken** — токенизация текста для нарезки чанков
- **OpenRouter** — доступ к LLM (оба тира бесплатные)
- **Docker Compose** — запуск фронтенда и бэкенда одной командой
- Фронтенд — собирается из `./frontend` (Dockerfile)

## Структура

```
├── backend/
│   ├── main.py          # FastAPI, эндпоинт /search, нарезка чанков
│   ├── llm.py           # Работа с OpenRouter: батч-запросы, retry, две модели
│   ├── parser.py        # Playwright: загрузка и парсинг HTML
│   ├── test.py          # Поиск в Google и извлечение URL
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   └── Dockerfile
└── docker-compose.yml
```

## Быстрый старт

```bash
git clone https://github.com/Ferraronp/rag_mtuci
cd rag_mtuci
```

Вставить OpenRouter API ключ в `backend/llm.py`:
```python
HEADERS = {
    "Authorization": "Bearer <your_openrouter_key>",
    ...
}
```

Запустить:
```bash
docker-compose up --build
```

- Фронтенд: `http://localhost:3000`
- Бэкенд API: `http://localhost:8000`

## API

```
POST /search
Content-Type: application/json

{ "query": "ваш вопрос" }
```

Ответ:
```json
{
  "answer": "...",
  "sources": ["https://...", "https://..."]
}
```

## Зависимости

```
fastapi
uvicorn
playwright
aiohttp
tiktoken
pydantic
```

После установки зависимостей нужно скачать браузер для Playwright:
```bash
playwright install chromium
```
