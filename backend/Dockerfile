FROM mcr.microsoft.com/playwright/python:v1.42.0

RUN apt-get update && apt-get install -y \
    libnss3 \
    libatk-bridge2.0-0 \
    libgtk-3-0 \
    libxss1 \
    libasound2 \
    libgbm-dev \
    fonts-liberation \
    && apt-get clean

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN playwright install --with-deps

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
