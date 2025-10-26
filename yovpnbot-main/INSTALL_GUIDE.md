# 📦 Руководство по установке YoVPN Bot

## 🚀 Быстрая установка

### 1️⃣ Клонируйте репозиторий
```bash
git clone <repository-url>
cd yovpnbot
```

### 2️⃣ Создайте виртуальное окружение
```bash
# Python 3.9+
python3 -m venv venv

# Активация (Linux/macOS)
source venv/bin/activate

# Активация (Windows)
venv\Scripts\activate
```

### 3️⃣ Обновите pip
```bash
pip install --upgrade pip setuptools wheel
```

### 4️⃣ Установите зависимости

**Вариант A: Минимальная установка (рекомендуется)**
```bash
pip install -r requirements-minimal.txt
```

**Вариант B: Полная установка (с dev-инструментами)**
```bash
pip install -r requirements.txt
```

**Вариант C: Асинхронная версия**
```bash
pip install -r requirements_async.txt
```

---

## 🐛 Решение проблем

### ❌ Ошибка: `cryptography==41.0.8` не найден

**Решение:**
```bash
# Используйте обновленный requirements.txt
pip install cryptography==43.0.3
```

### ❌ Конфликт зависимостей SQLAlchemy

**Решение:** Используйте обновленные файлы requirements, где убран конфликтующий пакет `databases`

### ❌ Ошибка на macOS (Apple Silicon M1/M2/M3)

**Решение:**
```bash
# Установите через архитектуру ARM64
arch -arm64 pip install -r requirements-minimal.txt

# Или установите Rosetta зависимости
arch -x86_64 pip install -r requirements-minimal.txt
```

### ❌ Ошибка `No matching distribution`

**Решение:**
```bash
# Очистите кэш pip
pip cache purge

# Установите без кэша
pip install --no-cache-dir -r requirements-minimal.txt
```

### ❌ SSL/TLS ошибки

**Решение:**
```bash
# Обновите сертификаты (macOS)
/Applications/Python\ 3.x/Install\ Certificates.command

# Обновите сертификаты (Linux)
sudo apt-get install ca-certificates
sudo update-ca-certificates
```

---

## ✅ Проверка установки

После установки проверьте ключевые пакеты:

```bash
python3 << EOF
import sys
print(f"Python: {sys.version}")

try:
    import aiogram
    print(f"✅ aiogram: {aiogram.__version__}")
except ImportError as e:
    print(f"❌ aiogram: {e}")

try:
    import sqlalchemy
    print(f"✅ SQLAlchemy: {sqlalchemy.__version__}")
except ImportError as e:
    print(f"❌ SQLAlchemy: {e}")

try:
    import cryptography
    print(f"✅ cryptography: {cryptography.__version__}")
except ImportError as e:
    print(f"❌ cryptography: {e}")

try:
    import aiohttp
    print(f"✅ aiohttp: {aiohttp.__version__}")
except ImportError as e:
    print(f"❌ aiohttp: {e}")

print("\n🎉 Все ключевые пакеты установлены!")
EOF
```

**Ожидаемый вывод:**
```
Python: 3.11.x
✅ aiogram: 3.4.1
✅ SQLAlchemy: 2.0.23
✅ cryptography: 43.0.3
✅ aiohttp: 3.9.1

🎉 Все ключевые пакеты установлены!
```

---

## 🔧 Настройка окружения

### 1. Создайте `.env` файл
```bash
cp .env.example .env
```

### 2. Заполните переменные окружения
```bash
# Откройте в редакторе
nano .env

# Или используйте vim
vim .env
```

**Основные переменные:**
```env
BOT_TOKEN=your_bot_token_here
DATABASE_URL=sqlite+aiosqlite:///./database.db
REDIS_URL=redis://localhost:6379
MARZBAN_API_URL=http://your-marzban-url
MARZBAN_USERNAME=admin
MARZBAN_PASSWORD=your_password
```

### 3. Инициализируйте базу данных
```bash
# Создайте миграции
alembic revision --autogenerate -m "Initial migration"

# Примените миграции
alembic upgrade head
```

---

## 🚀 Запуск бота

### Разработка:
```bash
python bot/main.py
```

### Продакшн (с uvloop):
```bash
python run.py
```

### С Docker:
```bash
docker-compose up -d
```

---

## 📊 Требования к системе

### Минимальные:
- **Python:** 3.9+
- **RAM:** 512 MB
- **Disk:** 1 GB
- **OS:** Linux, macOS, Windows

### Рекомендуемые:
- **Python:** 3.11+
- **RAM:** 2 GB
- **Disk:** 5 GB
- **OS:** Ubuntu 22.04 LTS

---

## 🌐 Установка Redis (опционально)

### Ubuntu/Debian:
```bash
sudo apt-get update
sudo apt-get install redis-server
sudo systemctl start redis
sudo systemctl enable redis
```

### macOS:
```bash
brew install redis
brew services start redis
```

### Docker:
```bash
docker run -d -p 6379:6379 redis:alpine
```

---

## 🔐 Установка в виртуальном окружении (рекомендуется)

### 1. Установите virtualenv
```bash
pip install virtualenv
```

### 2. Создайте окружение
```bash
virtualenv venv -p python3.11
```

### 3. Активируйте
```bash
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```

### 4. Установите зависимости
```bash
pip install -r requirements-minimal.txt
```

---

## 📝 Переменные окружения

### Обязательные:
- `BOT_TOKEN` - токен Telegram бота
- `DATABASE_URL` - URL базы данных
- `MARZBAN_API_URL` - URL Marzban API

### Опциональные:
- `REDIS_URL` - URL Redis (по умолчанию: redis://localhost:6379)
- `SENTRY_DSN` - DSN для Sentry (мониторинг)
- `LOG_LEVEL` - уровень логирования (DEBUG, INFO, WARNING, ERROR)
- `ENVIRONMENT` - окружение (development, production)

---

## 🧪 Тестирование установки

```bash
# Запустите тесты
pytest

# С покрытием
pytest --cov=bot --cov-report=html

# Только быстрые тесты
pytest -m "not slow"
```

---

## 📞 Поддержка

Если возникли проблемы:

1. Проверьте `DEPENDENCY_FIX.md`
2. Изучите логи установки
3. Создайте issue в репозитории
4. Обратитесь в поддержку

---

## 📚 Дополнительные ресурсы

- [Документация aiogram](https://docs.aiogram.dev/)
- [Документация SQLAlchemy](https://docs.sqlalchemy.org/)
- [Telegram Bot API](https://core.telegram.org/bots/api)

---

**Обновлено:** 21 октября 2025  
**Версия:** 2.0.0
