# Стартовий проєкт OBDZ-MKR02

1. Відкрийте проєкт у GitHub Codespaces (Code → Codespaces → Create codespace): devcontainer сам запустить Python і PostgreSQL 18, задасть змінні `PGHOST`, `PGPORT`, `PGUSER`, `PGPASSWORD`. Локально: запустіть `docker run -d --name mkr-pg -e POSTGRES_PASSWORD=postgres -p 127.0.0.1:5432:5432 postgres:18`, потім `python -m venv .venv`, активуйте середовище, `pip install -r requirements.txt`. Якщо порт 5432 зайнятий, змініть лівий номер у `-p` і задайте `PGPORT`.
2. Знайдіть свої файли в папці `tasks/` і реалізуйте їх за картками з `student.md`.
3. Запускайте відкриті тести: `pytest` або `pytest tests/test_task_NN.py`.
4. Подивитися, що робить ваше рішення, без тестів можна командою `python try_it.py NN`: вона друкує результат запиту, кроки сценарію двох сеансів або плани EXPLAIN запитів.
5. Усі десять практичних завдань потребують PostgreSQL. Файли в `data/` і `tests/` не змінюйте; змінюйте лише свої файли в `tasks/`.
6. Теоретичні завдання 11–15 не мають тестів: умова й місце для відповіді є у файлах `answers/task_11.md` … `answers/task_15.md`. Напишіть відповідь після рядка «Відповідь:» і здайте файли вибраних завдань.
