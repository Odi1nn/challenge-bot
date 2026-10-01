# 🚀 Челлендж-бот: Путь к iPad

Telegram-бот с мини-приложением для отслеживания домашних заданий.

---

## Структура проекта

```
challenge_bot/
├── main.py           # FastAPI сервер + Telegram бот
├── set_webhook.py    # Скрипт регистрации вебхука (запустить 1 раз)
├── requirements.txt  # Зависимости
├── Procfile          # Для Railway
├── .env              # Токен и URL (не заливать в git!)
└── static/
    └── index.html    # Мини-приложение Telegram
```

---

## ⚡ Деплой на Railway (пошагово, ~10 минут)

### Шаг 1 — Создай бота в Telegram
1. Напиши боту **@BotFather** → `/newbot`
2. Придумай имя и username боту
3. Скопируй токен (вида `1234567890:AAF...`)
4. Токен уже вставлен в `.env` ✅

### Шаг 2 — Зарегистрируйся на Railway
1. Зайди на **[railway.app](https://railway.app)**
2. Нажми **«Login»** → войди через GitHub
3. Если нет GitHub — создай аккаунт на [github.com](https://github.com) (бесплатно, 2 мин)

### Шаг 3 — Залей код на GitHub
1. Зайди на [github.com](https://github.com) → кнопка **«+»** → **New repository**
2. Назови репозиторий `challenge-bot`, нажми **Create repository**
3. Открой папку `challenge_bot` в Finder
4. Открой Терминал в этой папке (правой кнопкой → «Новый терминал по адресу папки»)
5. Выполни команды:
```bash
git init
git add .
git commit -m "init"
git remote add origin https://github.com/ТВО_ИМЯ/challenge-bot.git
git push -u origin main
```

### Шаг 4 — Задеплой на Railway
1. На [railway.app](https://railway.app) → **«New Project»** → **«Deploy from GitHub repo»**
2. Выбери репозиторий `challenge-bot`
3. Railway сам подхватит `Procfile` и запустит сервер
4. Подожди 1-2 минуты пока задеплоится
5. Зайди в **Settings** → **Domains** → нажми **«Generate Domain»**
6. Скопируй URL вида `https://challenge-bot-xxx.railway.app`

### Шаг 5 — Добавь переменные окружения
1. В Railway → вкладка **Variables**
2. Добавь:
   - `BOT_TOKEN` = `8883670945:AAFbNWd2cejSK8N55AZAixuTs0mCLkFqL2A`
   - `WEBAPP_URL` = `https://твой-url.railway.app`
3. Railway сам перезапустит сервер

### Шаг 6 — Зарегистрируй вебхук (1 раз)
В терминале в папке проекта:
```bash
pip install python-dotenv requests
# Отредактируй .env — вставь свой WEBAPP_URL
python set_webhook.py
```
Должен появиться ответ: `{"ok": true, "result": true}`

### Шаг 7 — Настрой бота в BotFather
1. Напиши @BotFather → `/setmenubutton`
2. Выбери своего бота
3. Введи URL мини-приложения: `https://твой-url.railway.app`
4. Введи название кнопки: `📊 Трекер`

---

## 🤖 Команды бота

| Команда | Что делает |
|---------|-----------|
| `/start` | Кнопка открытия трекера |
| `/progress` | Текстовая статистика прогресса |
| `/lives` | Сколько жизней осталось |

---

## 📱 Как пользоваться

- Нажми на квадратик дня → ✅ день засчитан
- Нажми ещё раз → отменить
- **Сегодняшний день** подсвечен фиолетовым
- Будущие дни чуть затемнены
- Кнопка **«Использовать жизнь»** — тратит одну жизнь

---

## 🎨 Особенности

- Тёмная тема, адаптирована под Telegram
- Прогресс-бар + счётчик выполненных дней
- Анимация при нажатии на квадратик
- 🎉 Анимация победы когда все 43 дня выполнены
- Данные хранятся в SQLite базе на сервере
