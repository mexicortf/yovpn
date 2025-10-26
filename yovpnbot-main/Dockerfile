# ========================================
# YoVPN Bot Dockerfile
# Мультистейдж сборка для оптимизации размера
# ========================================

FROM python:3.11-slim as base

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем requirements
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ========================================
# Production Stage
# ========================================
FROM python:3.11-slim

# Устанавливаем только runtime зависимости
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

# Создаем непривилегированного пользователя
RUN useradd -m -u 1000 yovpn

WORKDIR /app

# Копируем установленные пакеты из base stage
COPY --from=base /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=base /usr/local/bin /usr/local/bin

# Копируем код приложения
COPY --chown=yovpn:yovpn . .

# Создаем необходимые директории
RUN mkdir -p logs static/images && \
    chown -R yovpn:yovpn /app

# Переключаемся на непривилегированного пользователя
USER yovpn

# Здоровье контейнера
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# Точка входа определяется в docker-compose.yml
CMD ["python", "-u", "bot/main.py"]
