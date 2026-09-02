run:
	python manage.py runserver 0.0.0.0:8000

install:
	pip install -r requirements.txt

migrations:
	python manage.py makemigrations

showmigrations:
	python manage.py showmigrations

migrate:
	python manage.py migrate

superuser:
	python manage.py createsuperuser

build:
	docker-compose build

up:
	docker-compose up -d

shell:
	docker exec -ti django_web /bin/bash

dbshell:
	docker exec -ti django_db /bin/bash

down:
	docker-compose down

celery:
	celery -A config worker -l info

celery_beat:
	celery -A config worker --beat -l info	
