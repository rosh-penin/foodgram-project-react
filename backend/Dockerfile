FROM python3.10:latest
WORKDIR /foodgram
COPY . .
RUN pip install -r requirements.txt --no-cache-dir
RUN python manage.py collectstatic --noinput
CMD ["gunicorn","backend.wsgi:application","--bind","0:8000"]
