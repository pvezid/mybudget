@echo off
call Scripts\activate
py app\manage.py runserver localhost:8000
