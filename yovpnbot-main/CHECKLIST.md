# ✅ YoVPN WebApp - Launch Checklist

Финальный чек-лист для запуска WebApp в production.

---

## 🎯 Pre-Launch Checklist

### 1. Конфигурация ✅

#### Frontend (.env.local → .env.production)

- [ ] `NEXT_PUBLIC_DEV_MODE=false` ⚠️ ВАЖНО!
- [ ] `NEXT_PUBLIC_API_BASE_URL` - правильный URL API
- [ ] `NEXT_PUBLIC_BASE_URL` - ваш домен
- [ ] `NEXT_PUBLIC_TELEGRAM_BOT_TOKEN` - токен бота
- [ ] Все `NEXT_PUBLIC_*_URL` ссылки на v2raytun обновлены

#### Backend (.env)

- [ ] `TELEGRAM_BOT_TOKEN` - правильный токен
- [ ] `SECRET_KEY` - уникальный ключ (32+ символов)
- [ ] `CORS_ORIGINS` - только ваш домен
- [ ] `MARZBAN_API_URL` - URL Marzban
- [ ] `MARZBAN_USERNAME` и `MARZBAN_PASSWORD`

---

### 2. Безопасность 🔐

- [ ] SECRET_KEY сгенерирован:
  ```bash
  python3 -c "import secrets; print(secrets.token_urlsafe(32))"
  ```
- [ ] .env файлы НЕ в Git (.gitignore проверен)
- [ ] HTTPS настроен (обязательно для Telegram)
- [ ] SSL сертификат валиден
- [ ] CORS origins ограничены
- [ ] Rate limiting настроен (опционально)

---

### 3. Тестирование 🧪

#### Frontend

- [ ] `npm run build` проходит без ошибок
- [ ] `npm run lint` без warnings
- [ ] PWA manifest корректен
- [ ] Service Worker работает
- [ ] Все 3 шага работают
- [ ] Dev Mode отключен в production

#### Backend

- [ ] `pytest` все тесты проходят
- [ ] `/api/health` отвечает
- [ ] HMAC валидация работает
- [ ] Marzban интеграция работает

#### Integration

- [ ] Frontend → Backend связь работает
- [ ] Telegram WebApp открывается
- [ ] init_data валидируется
- [ ] Subscription API работает
- [ ] Deep links открываются

---

### 4. Performance 🚀

- [ ] Lighthouse Score > 90
  - Performance: > 90
  - Accessibility: > 90
  - Best Practices: > 90
  - SEO: > 80

- [ ] Bundle size оптимизирован:
  ```bash
  npm run build
  # Check .next/static размер
  ```

- [ ] Images оптимизированы
- [ ] Fonts загружаются быстро
- [ ] GSAP animations 60 FPS
- [ ] No memory leaks

---

### 5. Документация 📚

- [ ] README.md обновлен
- [ ] WEBAPP_URL в боте обновлен
- [ ] API endpoints задокументированы
- [ ] Environment variables описаны
- [ ] Deployment guide актуален

---

## 🚀 Deployment Checklist

### Vercel (Frontend)

- [ ] Project created
- [ ] GitHub repo connected
- [ ] Build settings:
  - Framework: Next.js
  - Build Command: `cd webapp && npm run build`
  - Output Directory: `webapp/.next`
- [ ] Environment variables добавлены
- [ ] Custom domain настроен
- [ ] SSL certificate активен
- [ ] Deploy successful

### Railway (Backend)

- [ ] Project created
- [ ] GitHub repo connected
- [ ] Root Directory: `api`
- [ ] Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- [ ] Environment variables добавлены
- [ ] Custom domain настроен (опционально)
- [ ] Deploy successful
- [ ] Health check работает

### Nginx (если используется)

- [ ] Nginx установлен
- [ ] Конфигурация создана (`/etc/nginx/sites-available/yovpn`)
- [ ] Symlink создан (`/etc/nginx/sites-enabled/yovpn`)
- [ ] `nginx -t` проходит
- [ ] Nginx перезапущен
- [ ] Reverse proxy работает

### SSL/HTTPS

- [ ] Certbot установлен
- [ ] SSL сертификат получен:
  ```bash
  sudo certbot --nginx -d yourdomain.com
  ```
- [ ] Auto-renewal настроен:
  ```bash
  sudo certbot renew --dry-run
  ```
- [ ] HTTPS redirect работает

---

## 🤖 Bot Integration Checklist

### Telegram Bot

- [ ] WebApp handler зарегистрирован:
  ```python
  from bot.handlers import webapp_handler
  dp.include_router(webapp_handler.router)
  ```

- [ ] WEBAPP_URL обновлен в `bot/handlers/webapp_handler.py`:
  ```python
  WEBAPP_URL = "https://yourdomain.com"
  ```

- [ ] Команды добавлены в меню:
  ```python
  commands = [
      BotCommand(command="start", description="🏠 Главное меню"),
      BotCommand(command="webapp", description="🚀 Активировать подписку"),
      ...
  ]
  await bot.set_my_commands(commands)
  ```

- [ ] Бот перезапущен
- [ ] `/webapp` работает
- [ ] WebApp button появляется
- [ ] WebApp открывается в Telegram

### BotFather

- [ ] Menu Button настроен:
  1. Открыть [@BotFather](https://t.me/BotFather)
  2. `/mybots` → выбрать бота
  3. `Bot Settings` → `Menu Button`
  4. Ввести URL: `https://yourdomain.com`

- [ ] Команды обновлены:
  ```
  /mycommands
  start - 🏠 Главное меню
  webapp - 🚀 Активировать подписку
  subscription - 📊 Моя подписка
  support - 💬 Поддержка
  ```

---

## 🧪 Testing Checklist

### Manual Testing

#### Шаг 1: Platform Selection

- [ ] Страница загружается < 2 секунды
- [ ] Все 5 платформ отображаются
- [ ] Hover эффекты работают
- [ ] Выбор платформы работает
- [ ] Transition к следующему шагу плавный
- [ ] Haptic feedback работает (в Telegram)

#### Шаг 2: Download

- [ ] Правильная платформа отображается
- [ ] Кнопка скачивания работает
- [ ] Ссылка открывается в новой вкладке
- [ ] Progress bar анимируется
- [ ] Shimmer эффект виден
- [ ] Auto-transition работает
- [ ] Back button возвращает назад

#### Шаг 3: Activation

- [ ] Subscription данные загружаются
- [ ] URI корректен
- [ ] Кнопка активации работает
- [ ] URI копируется в clipboard
- [ ] Deep link открывается
- [ ] Success animation показывается
- [ ] Fallback инструкции доступны

### Automated Testing

- [ ] E2E тесты проходят (если есть)
- [ ] Unit тесты > 80% coverage
- [ ] Integration тесты работают
- [ ] Load testing пройден (опционально)

---

## 📊 Monitoring Checklist

### Uptime Monitoring

- [ ] UptimeRobot настроен
- [ ] Мониторинг URL:
  - Frontend: `https://yourdomain.com`
  - Backend: `https://api.yourdomain.com/api/health`
- [ ] Email alerts настроены
- [ ] Telegram alerts настроены (опционально)

### Analytics

- [ ] Google Analytics подключен (опционально):
  ```typescript
  // webapp/src/app/layout.tsx
  <Script src="https://www.googletagmanager.com/gtag/js?id=GA_ID" />
  ```

- [ ] Error tracking:
  - Sentry (рекомендуется)
  - LogRocket (опционально)

### Logs

- [ ] Логи настроены:
  ```bash
  # PM2
  pm2 logs webapp
  pm2 logs api
  
  # Docker
  docker-compose logs -f
  
  # Systemd
  journalctl -u webapp -f
  ```

- [ ] Log rotation настроен
- [ ] Alerting настроен для errors

---

## 🔄 Post-Launch Checklist

### Day 1

- [ ] Мониторинг работает
- [ ] Нет критических errors
- [ ] Users могут активировать подписки
- [ ] Performance в норме
- [ ] Backup создан

### Week 1

- [ ] Собрана обратная связь
- [ ] Мелкие баги исправлены
- [ ] Analytics данные анализированы
- [ ] Performance оптимизирован

### Month 1

- [ ] A/B тесты запущены (опционально)
- [ ] Feature requests собраны
- [ ] Roadmap обновлен
- [ ] Documentation актуализирована

---

## 🆘 Emergency Contacts

### Если что-то сломалось

1. **Проверьте логи:**
   ```bash
   tail -f webapp.log
   tail -f api.log
   ```

2. **Проверьте health check:**
   ```bash
   curl https://api.yourdomain.com/api/health
   ```

3. **Откатите deploy:**
   ```bash
   # Vercel
   vercel rollback
   
   # Railway
   # Dashboard → Deployments → Rollback
   
   # Docker
   docker-compose down
   git checkout previous-commit
   docker-compose up -d
   ```

4. **Свяжитесь с командой:**
   - Telegram: @yovpn_dev
   - Email: dev@yovpn.com
   - GitHub Issues

---

## 📝 Notes

### Полезные команды

```bash
# Проверка статуса
curl https://api.yourdomain.com/api/health

# Проверка SSL
openssl s_client -connect yourdomain.com:443

# Проверка DNS
dig yourdomain.com

# Проверка производительности
curl -o /dev/null -s -w 'Total: %{time_total}s\n' https://yourdomain.com

# Lighthouse audit
npx lighthouse https://yourdomain.com --view

# Bundle analyzer
cd webapp && npm run build && npm run analyze
```

---

## ✅ Final Check

Перед запуском убедитесь что ВСЕ пункты выше отмечены ✅

**Финальный тест:**

1. Откройте бота в Telegram
2. Отправьте `/webapp`
3. Нажмите "🚀 Открыть WebApp"
4. Пройдите все 3 шага
5. Активируйте подписку
6. Проверьте что всё работает!

**Если всё OK →** 🎉 **LAUNCH!**

---

## 📞 Support

- 📖 [README.md](./README.md)
- 🚀 [QUICKSTART.md](./QUICKSTART.md)
- 🌐 [DEPLOYMENT.md](./DEPLOYMENT.md)
- 🐛 [GitHub Issues](https://github.com/yourusername/yovpn/issues)

---

**Good luck! 🚀**
