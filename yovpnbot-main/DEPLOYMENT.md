# 🚀 YoVPN WebApp - Deployment Guide

Полное руководство по деплою YoVPN WebApp в production.

## 📋 Содержание

- [Подготовка](#подготовка)
- [Vercel + Railway](#vercel--railway)
- [Docker Compose](#docker-compose)
- [VPS (Ubuntu)](#vps-ubuntu)
- [Cloudflare Pages + Workers](#cloudflare)
- [Post-Deployment](#post-deployment)

---

## 🎯 Подготовка

### 1. Получите домен

Telegram WebApp требует HTTPS, поэтому вам нужен домен:

- Купите домен (Namecheap, GoDaddy, etc.)
- Или используйте бесплатный: Freenom, .pp.ua

### 2. Подготовьте переменные окружения

#### Frontend (.env.production)
```env
NEXT_PUBLIC_API_BASE_URL=https://api.yourdomain.com
NEXT_PUBLIC_BASE_URL=https://yourdomain.com
NEXT_PUBLIC_TELEGRAM_BOT_TOKEN=your_bot_token
NEXT_PUBLIC_DEV_MODE=false

# Download URLs
NEXT_PUBLIC_ANDROID_APK_URL=https://github.com/.../v2raytun-android.apk
NEXT_PUBLIC_IOS_APP_STORE_URL=https://apps.apple.com/app/v2raytun
NEXT_PUBLIC_MACOS_DMG_URL=https://github.com/.../v2raytun-macos.dmg
NEXT_PUBLIC_WINDOWS_EXE_URL=https://github.com/.../v2raytun-windows.exe
NEXT_PUBLIC_ANDROID_TV_APK_URL=https://github.com/.../v2raytun-tv.apk
```

#### Backend (.env.production)
```env
TELEGRAM_BOT_TOKEN=your_bot_token
SECRET_KEY=generate-strong-secret-key-here
CORS_ORIGINS=https://yourdomain.com
MARZBAN_API_URL=https://your-marzban-instance.com
MARZBAN_USERNAME=admin
MARZBAN_PASSWORD=secure-password
```

### 3. Сгенерируйте SECRET_KEY

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## 🌐 Вариант 1: Vercel + Railway

### Frontend на Vercel

#### 1. Подготовка

```bash
cd webapp
npm install -g vercel
```

#### 2. Деплой

```bash
vercel login
vercel --prod
```

#### 3. Настройка переменных в Vercel Dashboard

1. Откройте [vercel.com/dashboard](https://vercel.com/dashboard)
2. Выберите проект
3. Settings → Environment Variables
4. Добавьте все переменные из `.env.production`

#### 4. Настройка домена

1. Settings → Domains
2. Add Domain → введите ваш домен
3. Настройте DNS записи (A или CNAME)

### Backend на Railway

#### 1. Создание проекта

1. Откройте [railway.app](https://railway.app)
2. New Project → Deploy from GitHub repo
3. Выберите ваш репозиторий

#### 2. Настройка

1. Settings → Root Directory → `api`
2. Settings → Start Command → `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

#### 3. Переменные окружения

1. Variables → Add all from `.env.production`
2. Railway автоматически предоставит переменную `$PORT`

#### 4. Домен

1. Settings → Generate Domain
2. Или добавьте свой домен

### Обновление WEBAPP_URL в боте

```python
# bot/handlers/webapp_handler.py
WEBAPP_URL = "https://your-vercel-domain.vercel.app"
```

---

## 🐳 Вариант 2: Docker Compose

### 1. Подготовка сервера

```bash
# SSH в ваш сервер
ssh user@your-server.com

# Установка Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 2. Клонирование репозитория

```bash
git clone https://github.com/yourusername/yovpn.git
cd yovpn
```

### 3. Настройка переменных

```bash
# Создайте .env в корне проекта
nano .env
```

```.env
# Telegram
TELEGRAM_BOT_TOKEN=your_bot_token

# Security
SECRET_KEY=your-secret-key

# Marzban
MARZBAN_API_URL=http://localhost:8080
MARZBAN_USERNAME=admin
MARZBAN_PASSWORD=admin
```

### 4. Запуск

```bash
docker-compose -f docker-compose.webapp.yml up -d
```

### 5. Проверка

```bash
docker-compose -f docker-compose.webapp.yml ps
docker-compose -f docker-compose.webapp.yml logs -f
```

### 6. Настройка Nginx + SSL

```bash
# Установка Certbot
sudo apt install certbot python3-certbot-nginx

# Получение SSL сертификата
sudo certbot --nginx -d yourdomain.com

# Автообновление сертификата
sudo certbot renew --dry-run
```

### 7. Обновление приложения

```bash
git pull
docker-compose -f docker-compose.webapp.yml down
docker-compose -f docker-compose.webapp.yml build
docker-compose -f docker-compose.webapp.yml up -d
```

---

## 💻 Вариант 3: VPS (Ubuntu 22.04)

### 1. Подготовка сервера

```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка зависимостей
sudo apt install -y nodejs npm python3 python3-pip python3-venv nginx certbot python3-certbot-nginx git
```

### 2. Клонирование и настройка

```bash
cd /var/www
sudo git clone https://github.com/yourusername/yovpn.git
sudo chown -R $USER:$USER yovpn
cd yovpn
```

### 3. Frontend

```bash
cd webapp
npm install
npm run build

# Установка PM2 для управления процессами
sudo npm install -g pm2

# Запуск
pm2 start npm --name "webapp" -- start
pm2 save
pm2 startup
```

### 4. Backend

```bash
cd ../api

# Виртуальное окружение
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Запуск с PM2
pm2 start "venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000" --name "api"
pm2 save
```

### 5. Nginx конфигурация

```bash
sudo nano /etc/nginx/sites-available/yovpn
```

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    # WebApp Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_cache_bypass $http_upgrade;
    }

    # API Backend
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # API Docs
    location /docs {
        proxy_pass http://localhost:8000/docs;
        proxy_set_header Host $host;
    }
}
```

```bash
# Активация конфига
sudo ln -s /etc/nginx/sites-available/yovpn /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 6. SSL сертификат

```bash
sudo certbot --nginx -d yourdomain.com
```

### 7. Firewall

```bash
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 22/tcp
sudo ufw enable
```

### 8. Мониторинг

```bash
# PM2 мониторинг
pm2 monit

# Логи
pm2 logs webapp
pm2 logs api

# Автозапуск после перезагрузки
pm2 startup
pm2 save
```

---

## ☁️ Вариант 4: Cloudflare Pages + Workers

### Frontend на Cloudflare Pages

#### 1. Подготовка

```bash
cd webapp
npm run build
```

#### 2. Deploy

1. Откройте [Cloudflare Dashboard](https://dash.cloudflare.com)
2. Pages → Create a project
3. Connect to Git → выберите репозиторий
4. Build settings:
   - Framework: Next.js
   - Build command: `cd webapp && npm run build`
   - Build output: `.next`

#### 3. Environment Variables

Добавьте все переменные из `.env.production`

### Backend на Cloudflare Workers

Это более сложный вариант, требующий адаптации FastAPI под Workers.

---

## ✅ Post-Deployment

### 1. Обновление бота

```python
# bot/handlers/webapp_handler.py
WEBAPP_URL = "https://yourdomain.com"
```

### 2. Регистрация в BotFather

1. Откройте [@BotFather](https://t.me/BotFather)
2. `/mybots` → выберите бота
3. `Bot Settings` → `Menu Button`
4. Введите URL: `https://yourdomain.com`

### 3. Тестирование

```bash
# Проверка доступности
curl https://yourdomain.com
curl https://yourdomain.com/api/health

# Проверка SSL
curl -I https://yourdomain.com

# Скорость загрузки
curl -o /dev/null -s -w 'Total: %{time_total}s\n' https://yourdomain.com
```

### 4. Мониторинг

#### UptimeRobot

1. Зарегистрируйтесь на [UptimeRobot](https://uptimerobot.com)
2. Add New Monitor
3. URL: `https://yourdomain.com/api/health`

#### Google Analytics

```typescript
// webapp/src/app/layout.tsx
<Script
  src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"
  strategy="afterInteractive"
/>
```

### 5. Резервное копирование

```bash
# Автоматический backup (cron)
0 2 * * * /usr/bin/tar -czf /backups/yovpn-$(date +\%Y\%m\%d).tar.gz /var/www/yovpn
```

---

## 🔧 Troubleshooting

### WebApp не загружается

```bash
# Проверка логов
pm2 logs webapp
# или
docker-compose -f docker-compose.webapp.yml logs webapp

# Проверка портов
sudo netstat -tulpn | grep 3000
```

### API не отвечает

```bash
# Проверка статуса
curl http://localhost:8000/api/health

# Проверка логов
pm2 logs api
# или
docker-compose -f docker-compose.webapp.yml logs api
```

### SSL проблемы

```bash
# Проверка сертификата
sudo certbot certificates

# Обновление
sudo certbot renew
```

### CORS ошибки

Проверьте `CORS_ORIGINS` в `.env`:

```env
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

---

## 📊 Performance Tips

### 1. CDN

Используйте Cloudflare для кэширования статики:

```nginx
# nginx.conf
location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

### 2. Compression

```nginx
# nginx.conf
gzip on;
gzip_types text/plain text/css application/json application/javascript;
gzip_min_length 1000;
```

### 3. Database Connection Pooling

```python
# api/app/config.py
DATABASE_POOL_SIZE = 20
DATABASE_MAX_OVERFLOW = 10
```

---

## 🔐 Security Checklist

- [ ] SSL сертификат установлен
- [ ] Firewall настроен
- [ ] SECRET_KEY уникален и безопасен
- [ ] CORS_ORIGINS ограничены
- [ ] Rate limiting настроен
- [ ] Логи ротируются
- [ ] Backup настроен
- [ ] Мониторинг работает

---

## 📞 Support

- Issues: [GitHub Issues](https://github.com/yourusername/yovpn/issues)
- Telegram: @your_support

---

**Happy Deployment! 🚀**
