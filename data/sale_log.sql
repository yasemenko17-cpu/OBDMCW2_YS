-- Журнал продажів: 24 000 рядків, дані будуються формулами (без випадкових чисел), тому план запиту відтворюється.
-- Набір для завдань 4, 8 і 10. Тест створює таблицю в тимчасовій схемі; для власних дослідів завантажте файл у порожню схему.
CREATE TABLE sale_log (
    id          integer PRIMARY KEY,
    customer_id integer NOT NULL,
    product_id  integer NOT NULL,
    status      text    NOT NULL,
    sold_on     date    NOT NULL,
    amount      numeric(10,2) NOT NULL,
    email       text    NOT NULL
) WITH (autovacuum_enabled = false);
INSERT INTO sale_log
SELECT i,
       (i * 37) % 2000 + 1,
       (i * 11) % 60 + 1,
       CASE WHEN i % 50 = 0 THEN 'new' WHEN i % 25 = 1 THEN 'cancelled' ELSE 'closed' END,
       DATE '2025-01-01' + ((i * 13) % 730),
       ((i * 7919) % 100000) / 100.0,
       'Client' || ((i * 37) % 2000 + 1) || '@Example.com'
FROM generate_series(1, 24000) AS i;
ANALYZE sale_log;
