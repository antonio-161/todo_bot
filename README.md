# ToDo Bot - Telegram бот для управления задачами

Телеграм-бот на aiogram 3.x для управления личными задачами и заметками с использованием PostgreSQL.

## Функциональность

- ✅ Добавление новых задач и заметок
- 📋 Просмотр списка всех задач
- ✅ Отметка задач как выполненных
- 🗑 Удаление задач
- 📱 Удобные inline-клавиатуры для взаимодействия
- 🔄 Автоматическое обновление интерфейса
- 📊 История выполненных задач

## Структура проекта

```
todo_bot/
├── bot.py                 # Основной файл бота
├── config.py              # Конфигурация
├── database.py            # Работа с базой данных
├── states.py              # FSM состояния
├── handlers/              # Обработчики команд
│   ├── __init__.py
│   ├── start.py           # /start команда
│   ├── help.py            # /help команда  
│   ├── new_task.py        # Добавление задач
│   ├── tasks_list.py      # Список задач
│   └── actions.py         # Действия с задачами
├── keyboards/             # Клавиатуры
│   ├── __init__.py
│   ├── inline.py          # Inline клавиатуры
│   └── reply.py           # Reply клавиатуры
├── requirements.txt       # Зависимости Python
├── .env                   # Переменные окружения
├── init_db.sql            # SQL скрипт инициализации БД
├── docker-compose.yml     # Docker Compose конфигурация
├── Dockerfile             # Docker образ бота
└── README.md              # Документация
```

## Установка и запуск

### Метод 1: Локальная установка

#### Предварительные требования
- Python 3.11+
- PostgreSQL 12+
- Telegram Bot Token (получить у @BotFather)

#### Шаги установки

1. **Клонирование проекта**
```bash
git clone <your-repo-url>
cd todo_bot
```

2. **Создание виртуального окружения**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate     # Windows
```

3. **Установка зависимостей**
```bash
pip install -r requirements.txt
```

4. **Настройка PostgreSQL**
```bash
# Создание базы данных
sudo -u postgres createdb todo_bot
sudo -u postgres createuser todo_bot_user -P

# Инициализация схемы
psql -U todo_bot_user -d todo_bot -f init_db.sql
```

5. **Настройка переменных окружения**
```bash
cp .env.example .env
# Отредактируй файл .env с твоими данными
```

6. **Запуск бота**
```bash
python bot.py
```

### Метод 2: Docker Compose (Рекомендуемый)

#### Предварительные требования
- Docker
- Docker Compose

#### Шаги запуска

1. **Клонирование и настройка**
```bash
git clone <your-repo-url>
cd todo_bot
cp .env.example .env
# Отредактируй .env файл
```

2. **Запуск с Docker Compose**
```bash
docker-compose up -d
```

3. **Просмотр логов**
```bash
docker-compose logs -f bot
```

4. **Остановка**
```bash
docker-compose down
```

## Конфигурация

Настрой следующие переменные в файле `.env`:

```env
# Telegram Bot Token
BOT_TOKEN=your_bot_token_here

# PostgreSQL настройки
DB_HOST=localhost
DB_PORT=5432
DB_NAME=todo_bot
DB_USER=your_db_user
DB_PASSWORD=your_db_password
```

## Деплой на продакшен

### VPS/Сервер

1. **Установка зависимостей сервера**
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip postgresql postgresql-contrib nginx
```

2. **Клонирование и настройка проекта**
```bash
cd /opt
sudo git clone <your-repo-url> todo_bot
cd todo_bot
sudo chown -R $USER:$USER /opt/todo_bot
```

3. **Создание systemd сервиса**
```bash
sudo nano /etc/systemd/system/todo-bot.service
```

Содержимое файла:
```ini
[Unit]
Description=ToDo Telegram Bot
After=network.target postgresql.service

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/opt/todo_bot
Environment=PATH=/opt/todo_bot/venv/bin
ExecStart=/opt/todo_bot/venv/bin/python bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

4. **Активация сервиса**
```bash
sudo systemctl daemon-reload
sudo systemctl enable todo-bot
sudo systemctl start todo-bot
```

### Heroku

1. **Подготовка файлов**
```bash
# Создать Procfile
echo "worker: python bot.py" > Procfile
```

2. **Развертывание**
```bash
heroku create your-bot-name
heroku addons:create heroku-postgresql:mini
heroku config:set BOT_TOKEN=your_bot_token
git push heroku main
```

### Railway

1. **Подключение через GitHub**
   - Загрузи код в GitHub
   - Подключи репозиторий в Railway
   
2. **Настройка переменных**
   - Добавь переменные окружения в панели Railway
   - Railway автоматически предоставит PostgreSQL

## Мониторинг и логи

### Локальное развертывание
```bash
# Просмотр логов
tail -f bot.log

# Мониторинг процесса
ps aux | grep python
```

### Docker
```bash
# Логи бота
docker-compose logs -f bot

# Логи базы данных  
docker-compose logs -f postgres

# Мониторинг ресурсов
docker-compose top
```

### Systemd (продакшен)
```bash
# Статус сервиса
sudo systemctl status todo-bot

# Логи сервиса
sudo journalctl -u todo-bot -f

# Перезапуск
sudo systemctl restart todo-bot
```

## Резервное копирование

### База данных
```bash
# Создание бэкапа
pg_dump -U todo_bot_user -h localhost -d todo_bot > backup_$(date +%Y%m%d).sql

# Восстановление
psql -U todo_bot_user -d todo_bot < backup_20240101.sql
```

### Docker
```bash
# Бэкап через Docker
docker-compose exec postgres pg_dump -U todo_bot_user todo_bot > backup.sql
```

## Безопасность

1. **Переменные окружения**
   - Никогда не коммить файл `.env`
   - Используй сложные пароли для БД
   - Регулярно меняй токены

2. **База данных**
   - Ограничь доступ к PostgreSQL
   - Используй SSL соединения в продакшене
   - Регулярно обновляй PostgreSQL

3. **Сервер**
   - Настрой firewall
   - Используй SSH ключи
   - Регулярно обновляй систему

## Масштабирование

### Горизонтальное масштабирование
- Используй Redis для FSM storage вместо MemoryStorage
- Настрой несколько инстансов бота за load balancer

### Оптимизация базы данных
- Добавь индексы для часто используемых запросов
- Используй connection pooling
- Регулярно анализируй производительность запросов

## Поддержка

При возникновении проблем:

1. Проверь логи: `docker-compose logs -f` или `tail -f bot.log`
2. Убедись что все переменные окружения заданы правильно
3. Проверь доступность базы данных
4. Убедись что бот имеет правильный токен

## Лицензия

MIT License - используй свободно в своих проектах.