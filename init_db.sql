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
    is_hidden BOOLEAN DEFAULT FALSE
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
CREATE INDEX IF NOT EXISTS idx_tasks_is_hidden ON tasks(is_hidden);

COMMENT ON COLUMN tasks.is_hidden IS 'Флаг скрытия задачи. TRUE - задача скрыта из списков, FALSE - видима';
COMMENT ON COLUMN tasks.created_at IS 'Дата и время создания задачи';
COMMENT ON COLUMN tasks.completed_at IS 'Дата и время завершения задачи';
COMMENT ON COLUMN tasks.status IS 'Статус задачи (TRUE - выполнена, FALSE - не выполнена)';
COMMENT ON COLUMN tasks.task_text IS 'Текст задачи';
COMMENT ON COLUMN users.timezone IS 'Временная зона пользователя';
