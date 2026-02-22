# Установка и запуск приложения
1. Клонирование репозитория:
`git clone https://github.com/SibAlive/dns.git`
`cd dns`
2. Создание виртуального окружения (для Windows):
`python -m venv venv`
`venv/Scripts/activate`
3. Установка зависимостей:
`pip install -r requirements.txt`
4. Настройка переменных окружения (файл .env необходимо заполнить своими данными:
`cp .env.example .env`
5. Запустить контейнер
`docker compose build`
`docker compose up -d`
6. Восстановления дампа БД
`docker cp backup django_postgres:/tmp/backup.sql`
`docker exec -i django_postgres psql -U your_user -d your_database -f /tmp/backup.sql`