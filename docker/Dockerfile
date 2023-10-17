FROM python:3.12.0a4-alpine3.17
#FROM python:3.8-slim

COPY ./requirements.txt /requirements.txt

# Activer les 3 lignes ci-dessous pour supprimer le warning à propos de root
#ENV VIRTUAL_ENV=/app/venv
#RUN python -m venv $VIRTUAL_ENV
#ENV PATH="$VIRTUAL_ENV/bin:$PATH"
RUN pip install --disable-pip-version-check --no-cache-dir --trusted-host pypi.python.org -r /requirements.txt

COPY ./app /app/
WORKDIR /app

EXPOSE 8000/tcp
ENTRYPOINT ["python"]
CMD ["manage.py", "runserver", "0:8000"]
