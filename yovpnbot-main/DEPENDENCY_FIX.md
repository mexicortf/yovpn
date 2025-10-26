# 🔧 Исправление зависимостей

## Проблемы и решения

### ❌ Проблема 1: cryptography==41.0.8 не найден

**Ошибка:**
```
ERROR: Could not find a version that satisfies the requirement cryptography==41.0.8
```

**Причина:** Версия 41.0.8 была yanked (удалена) из PyPI

**Решение:** ✅ Обновлено до `cryptography==43.0.3`

---

### ❌ Проблема 2: Конфликт sqlalchemy

**Ошибка:**
```
The conflict is caused by:
    The user requested sqlalchemy==2.0.25
    databases 0.8.0 depends on sqlalchemy<1.5 and >=1.4.42
```

**Причина:** Пакет `databases` требует старую версию sqlalchemy (<1.5), а в проекте используется 2.0.x

**Решение:** ✅ Убран пакет `databases`, используем нативную поддержку async в SQLAlchemy 2.0

---

## 📦 Обновленные файлы

### `requirements.txt`
- ✅ `cryptography==41.0.8` → `cryptography==43.0.3`
- ✅ Убран `semgrep` (проблемы с зависимостями)
- ✅ Оставлен `sqlalchemy==2.0.23` (нативная async поддержка)

### `requirements_async.txt`
- ✅ `cryptography==41.0.8` → `cryptography==43.0.3`
- ✅ `aiogram==3.2.0` → `aiogram==3.4.1` (обновлено)

---

## 🚀 Установка

### Основной проект:
```bash
pip install -r requirements.txt
```

### Асинхронная версия:
```bash
pip install -r requirements_async.txt
```

### Если все еще есть проблемы:

1. **Обновите pip:**
```bash
pip install --upgrade pip setuptools wheel
```

2. **Очистите кэш:**
```bash
pip cache purge
```

3. **Установите без кэша:**
```bash
pip install --no-cache-dir -r requirements.txt
```

---

## ✅ Проверка установки

```bash
python -c "import cryptography; print(cryptography.__version__)"
python -c "import sqlalchemy; print(sqlalchemy.__version__)"
python -c "import aiogram; print(aiogram.__version__)"
```

Ожидаемый результат:
```
43.0.3
2.0.23
3.4.1
```

---

## 📝 Заметки

### SQLAlchemy 2.0
Используется нативная поддержка async/await без дополнительного пакета `databases`:

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

engine = create_async_engine("sqlite+aiosqlite:///./database.db")
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
```

### Cryptography
Версия 43.0.3 - стабильная и актуальная на октябрь 2025. Поддерживает:
- Python 3.7+
- Все современные алгоритмы шифрования
- Совместима с aiogram и другими библиотеками

---

## 🐛 Известные проблемы

### Semgrep удален
Semgrep может иметь конфликты зависимостей. Если нужен, установите отдельно:
```bash
pip install semgrep
```

### macOS ARM (M1/M2/M3)
Если проблемы с установкой на Apple Silicon:
```bash
arch -arm64 pip install -r requirements.txt
```

---

**Дата исправления:** 21 октября 2025  
**Статус:** ✅ Исправлено
