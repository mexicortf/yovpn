#!/bin/bash

# ========================================
# YoVPN Bot - Скрипт установки
# ========================================

set -e

echo "📦 Установка YoVPN Bot..."
echo ""

# Проверка ОС
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "✅ ОС: Linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    echo "✅ ОС: macOS"
else
    echo "⚠️  Неподдерживаемая ОС: $OSTYPE"
fi

# Проверка Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 не установлен"
    echo "📦 Установите Python 3.11 или выше"
    exit 1
fi

python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✅ Python: $python_version"

# Проверка MySQL
if ! command -v mysql &> /dev/null; then
    echo "⚠️  MySQL не установлен"
    echo "📦 Для продакшена требуется MySQL 8.0+"
fi

# Проверка Redis
if ! command -v redis-cli &> /dev/null; then
    echo "⚠️  Redis не установлен (опционально)"
fi

# Создание виртуального окружения
echo ""
echo "🔧 Создание виртуального окружения..."
python3 -m venv venv
source venv/bin/activate

# Установка зависимостей
echo "📥 Установка зависимостей..."
pip install --upgrade pip
pip install -r requirements.txt

# Создание .env
if [ ! -f ".env" ]; then
    echo ""
    echo "📝 Создание .env файла..."
    cp .env.example .env
    
    # Генерация случайного пароля для MySQL
    MYSQL_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
    
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' "s/yovpn_password/$MYSQL_PASSWORD/g" .env
    else
        sed -i "s/yovpn_password/$MYSQL_PASSWORD/g" .env
    fi
    
    echo "✅ .env создан"
    echo "🔐 MySQL пароль: $MYSQL_PASSWORD"
fi

# Создание директорий
echo ""
echo "📁 Создание директорий..."
mkdir -p logs
mkdir -p admin/static/images
mkdir -p database/migrations/versions

echo ""
echo "✅ Установка завершена!"
echo ""
echo "📝 Следующие шаги:"
echo "   1. Отредактируйте .env файл (nano .env)"
echo "   2. Настройте MySQL базу данных"
echo "   3. Примените миграции (alembic upgrade head)"
echo "   4. Запустите бота (./start.sh)"
echo "   5. Запустите админ-панель (./start-admin.sh)"
echo ""
echo "📖 Подробная документация: README.md"
