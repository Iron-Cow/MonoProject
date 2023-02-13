
Set environment variables in `.env` file:

```
PORT_API_HOST = ...
PORT_API_CONTAINER = ...
DB_NAME = ...
DB_USER = ...
DB_PASSWORD = ...
DB_HOST = ...
CHAT_BOT_API_KEY = ...
BOT_TOKEN = ...
```

`pip install -r requirements.txt`

Run docker compose:

` docker-compose -f docker-compose.yaml up --build`


    python manage.py makemigrations
    python manage.py migrate
    python manage.py loaddata categories.json
    python manage.py loaddata categories_mso.json
    python manage.py loaddata currency.json




    celery --app=django_celery_example beat -l INFO
    celery --app=django_celery_example worker --loglevel=info
    python manage.py runserver
