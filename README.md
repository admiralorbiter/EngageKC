# EngageKC

## Getting Started

Make sure python 3 is installed and run the following command to install django

```bash

pip install django
pip install celery
pip install django-widget-tweaks
pip install jsonschema
pip install Pillow
pip install opnepyxl
pip install reportlab
```
## First Time Run
```bash
python manage.py migrate
```

## Running the server

```bash
python manage.py runserver
```

## Deploy Commmand
```bash
python manage.py collectstatic
```





Celery Worker - No need to run currently

celery -A engagekc worker --loglevel=info
celery -A engagekc beat --loglevel=info
