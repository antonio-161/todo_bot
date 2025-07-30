-- Миграция для добавления функции скрытия задач
-- Выполните этот скрипт для обновления существующей базы данных

-- Добавляем колонку is_hidden в таблицу tasks
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS is_hidden BOOLEAN DEFAULT FALSE;

-- Создаем индекс для оптимизации запросов по скрытым задачам
CREATE INDEX IF NOT EXISTS idx_tasks_is_hidden ON tasks(is_hidden);

-- Обновляем существующие записи (устанавливаем is_hidden = FALSE для всех существующих задач)
UPDATE tasks SET is_hidden = FALSE WHERE is_hidden IS NULL;

-- Добавляем комментарии к колонкам для документации
COMMENT ON COLUMN tasks.is_hidden IS 'Флаг скрытия задачи. TRUE - задача скрыта из списков, FALSE - видима';

-- Проверяем результат миграции
SELECT 
    COUNT(*) as total_tasks,
    COUNT(*) FILTER (WHERE is_hidden = TRUE) as hidden_tasks,
    COUNT(*) FILTER (WHERE is_hidden = FALSE) as visible_tasks
FROM tasks;