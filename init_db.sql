-- Создание базы данных для ToDo бота
-- Выполните этот скрипт перед запуском бота

-- Создание базы данных (если нужно)
-- CREATE DATABASE todo_bot;

-- Подключение к базе данных
-- \c todo_bot;

-- Создание таблицы для задач
CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    task_text TEXT NOT NULL,
    status BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP NULL
);

-- Создание таблицы для пользователей
CREATE TABLE IF NOT EXISTS users (
    user_id BIGINT PRIMARY KEY,
    timezone VARCHAR(50) DEFAULT 'UTC',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Создание индексов для оптимизации запросов
CREATE INDEX IF NOT EXISTS idx_tasks_user_id ON tasks(user_id);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_created_at ON tasks(created_at);
CREATE INDEX IF NOT EXISTS idx_tasks_completed_at ON tasks(completed_at);
CREATE INDEX IF NOT EXISTS idx_users_timezone ON users(timezone);

-- Создание пользователя для бота (опционально)
CREATE USER todo_bot_user WITH PASSWORD '2010';
GRANT ALL PRIVILEGES ON DATABASE todo_bot_dev TO todo_bot_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO user_dev;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO user_dev;