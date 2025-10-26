#!/bin/bash

# YoVPN Bot - Автоматический установщик
# Версия: 2.0.0

set -e

echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║           YoVPN Bot - Автоматическая установка                  ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Функция для вывода успеха
success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# Функция для вывода ошибки
error() {
    echo -e "${RED}❌ $1${NC}"
}

# Функция для вывода предупреждения
warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Функция для вывода информации
info() {
    echo -e "ℹ️  $1"
}

# Проверка Python
info "Проверка версии Python..."
if ! command -v python3 &> /dev/null; then
    error "Python 3 не установлен"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
info "Найден Python $PYTHON_VERSION"

# Проверка версии Python (требуется 3.9+)
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || [ "$PYTHON_MINOR" -lt 9 ]; then
    error "Требуется Python 3.9 или новее (найден $PYTHON_VERSION)"
    exit 1
fi

success "Python версия корректна ($PYTHON_VERSION)"

# Проверка pip
info "Проверка pip..."
if ! command -v pip3 &> /dev/null; then
    error "pip3 не установлен"
    exit 1
fi

success "pip3 найден"

# Обновление pip
info "Обновление pip, setuptools и wheel..."
python3 -m pip install --upgrade pip setuptools wheel --quiet

success "pip обновлен"

# Выбор типа установки
echo ""
echo "Выберите тип установки:"
echo "1) Минимальная (только необходимые пакеты)"
echo "2) Полная (с dev-инструментами)"
echo "3) Асинхронная версия"
echo ""
read -p "Введите номер (1-3) [1]: " INSTALL_TYPE
INSTALL_TYPE=${INSTALL_TYPE:-1}

case $INSTALL_TYPE in
    1)
        REQUIREMENTS_FILE="requirements-minimal.txt"
        info "Выбрана минимальная установка"
        ;;
    2)
        REQUIREMENTS_FILE="requirements.txt"
        info "Выбрана полная установка"
        ;;
    3)
        REQUIREMENTS_FILE="requirements_async.txt"
        info "Выбрана асинхронная версия"
        ;;
    *)
        error "Неверный выбор"
        exit 1
        ;;
esac

# Проверка наличия файла requirements
if [ ! -f "$REQUIREMENTS_FILE" ]; then
    error "Файл $REQUIREMENTS_FILE не найден"
    exit 1
fi

# Создание виртуального окружения (опционально)
echo ""
read -p "Создать виртуальное окружение? (y/n) [y]: " CREATE_VENV
CREATE_VENV=${CREATE_VENV:-y}

if [ "$CREATE_VENV" = "y" ] || [ "$CREATE_VENV" = "Y" ]; then
    info "Создание виртуального окружения..."
    
    if [ -d "venv" ]; then
        warning "Папка venv уже существует"
        read -p "Удалить и создать заново? (y/n) [n]: " RECREATE_VENV
        if [ "$RECREATE_VENV" = "y" ] || [ "$RECREATE_VENV" = "Y" ]; then
            rm -rf venv
            python3 -m venv venv
            success "Виртуальное окружение пересоздано"
        fi
    else
        python3 -m venv venv
        success "Виртуальное окружение создано"
    fi
    
    # Активация виртуального окружения
    info "Активация виртуального окружения..."
    source venv/bin/activate
    success "Виртуальное окружение активировано"
fi

# Очистка кэша pip
info "Очистка кэша pip..."
python3 -m pip cache purge --quiet 2>/dev/null || true

# Установка зависимостей
echo ""
info "Установка зависимостей из $REQUIREMENTS_FILE..."
echo "Это может занять несколько минут..."
echo ""

if python3 -m pip install -r "$REQUIREMENTS_FILE" --no-cache-dir; then
    success "Все зависимости установлены успешно!"
else
    error "Ошибка при установке зависимостей"
    warning "Попробуйте установить вручную:"
    echo "  pip install -r $REQUIREMENTS_FILE"
    exit 1
fi

# Проверка установки ключевых пакетов
echo ""
info "Проверка установленных пакетов..."

python3 << EOF
import sys

packages_to_check = [
    ('aiogram', '3.4.1'),
    ('sqlalchemy', '2.0.23'),
    ('cryptography', '43.0.3'),
    ('aiohttp', '3.9.1'),
]

all_ok = True
for package_name, expected_version in packages_to_check:
    try:
        module = __import__(package_name)
        version = getattr(module, '__version__', 'unknown')
        print(f"✅ {package_name}: {version}")
    except ImportError as e:
        print(f"❌ {package_name}: не установлен")
        all_ok = False

if all_ok:
    print("\n🎉 Все ключевые пакеты установлены корректно!")
else:
    print("\n⚠️  Некоторые пакеты не установлены")
    sys.exit(1)
EOF

if [ $? -eq 0 ]; then
    success "Проверка пакетов пройдена"
else
    error "Проверка пакетов не пройдена"
    exit 1
fi

# Создание .env файла
echo ""
if [ ! -f ".env" ]; then
    info "Файл .env не найден"
    read -p "Создать .env из примера? (y/n) [y]: " CREATE_ENV
    CREATE_ENV=${CREATE_ENV:-y}
    
    if [ "$CREATE_ENV" = "y" ] || [ "$CREATE_ENV" = "Y" ]; then
        if [ -f ".env.example" ]; then
            cp .env.example .env
            success "Файл .env создан из .env.example"
            warning "Не забудьте заполнить переменные окружения в .env"
        else
            warning ".env.example не найден, создайте .env вручную"
        fi
    fi
else
    success "Файл .env уже существует"
fi

# Инициализация базы данных
echo ""
read -p "Инициализировать базу данных? (y/n) [n]: " INIT_DB
if [ "$INIT_DB" = "y" ] || [ "$INIT_DB" = "Y" ]; then
    info "Инициализация базы данных..."
    
    if command -v alembic &> /dev/null; then
        if [ -d "alembic" ]; then
            alembic upgrade head
            success "База данных инициализирована"
        else
            warning "Папка alembic не найдена, пропускаем миграции"
        fi
    else
        warning "alembic не установлен, пропускаем миграции"
    fi
fi

# Финальное сообщение
echo ""
echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║                  ✅ Установка завершена!                        ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""
success "YoVPN Bot готов к работе!"
echo ""
info "Следующие шаги:"
echo "  1. Настройте .env файл с вашими данными"
echo "  2. Запустите бота: python bot/main.py"
echo "  3. Проверьте документацию: cat INSTALL_GUIDE.md"
echo ""

if [ "$CREATE_VENV" = "y" ] || [ "$CREATE_VENV" = "Y" ]; then
    warning "Не забудьте активировать виртуальное окружение:"
    echo "  source venv/bin/activate"
fi

echo ""
info "Для справки: cat INSTALL_GUIDE.md"
echo ""
