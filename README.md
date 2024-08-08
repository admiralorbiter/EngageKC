# EngageKC

## Getting Started

Make sure python 3 is installed and run the following command to install django

```bash

pip install django
pip install celery
pip install django-widget-tweaks
```

## Running the server

```bash
python manage.py runserver
```

Celery Worker

celery -A engagekc worker --loglevel=info
celery -A engagekc beat --loglevel=info
