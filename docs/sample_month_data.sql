-- Sample monthly data for Telegram Profit Bot
-- This script demonstrates the data structure for monthly reports

BEGIN;

-- Sample offices (brands)
INSERT OR IGNORE INTO offices (id, name) VALUES 
(1, 'Київський офіс'),
(2, 'Львівський офіс'),
(3, 'Одеський офіс');

-- Sample geo regions
INSERT OR IGNORE INTO geo (id, name, office_id) VALUES 
(1, 'Київ Центр', 1),
(2, 'Київ Лівобережжя', 1),
(3, 'Львів Центр', 2),
(4, 'Львів Околиці', 2),
(5, 'Одеса Порт', 3),
(6, 'Одеса Центр', 3);

-- Sample users (managers)
INSERT OR IGNORE INTO users (tg_id, name, office_id) VALUES 
(123456789, 'Олександр Менеджер', 1),
(987654321, 'Марія Керівник', 2),
(555666777, 'Петро Директор', 3);

-- Sample daily reports for January 2025 (planned amounts)
INSERT OR IGNORE INTO reports (office_id, geo_id, date, amount_planned) VALUES 
(1, 1, '2025-01-01', 45000),
(1, 1, '2025-01-02', 50000),
(1, 1, '2025-01-03', 48000),
(1, 1, '2025-01-15', 52000),
(1, 1, '2025-01-31', 55000),
(1, 2, '2025-01-01', 35000),
(1, 2, '2025-01-02', 38000),
(1, 2, '2025-01-15', 40000),
(1, 2, '2025-01-31', 42000),
(2, 3, '2025-01-01', 30000),
(2, 3, '2025-01-02', 32000),
(2, 3, '2025-01-15', 35000),
(2, 4, '2025-01-01', 25000),
(2, 4, '2025-01-15', 28000),
(3, 5, '2025-01-01', 40000),
(3, 5, '2025-01-02', 42000),
(3, 5, '2025-01-31', 45000),
(3, 6, '2025-01-01', 38000),
(3, 6, '2025-01-15', 40000);

-- Sample monthly facts for January 2025 (actual amounts)
INSERT OR IGNORE INTO facts (geo_id, month, amount_fact) VALUES 
(1, '2025-01-01', 248000),
(2, '2025-01-01', 160000),
(3, '2025-01-01', 95000),
(4, '2025-01-01', 55000),
(5, '2025-01-01', 125000);
-- Одеса Центр факт відсутній (демонстрація "немає даних")

-- Sample data for February 2025 (current month)
INSERT OR IGNORE INTO reports (office_id, geo_id, date, amount_planned) VALUES 
(1, 1, '2025-02-01', 58000),
(1, 1, '2025-02-02', 60000),
(1, 2, '2025-02-01', 45000),
(2, 3, '2025-02-01', 38000),
(2, 4, '2025-02-01', 30000),
(3, 5, '2025-02-01', 48000),
(3, 6, '2025-02-01', 42000);

COMMIT; 