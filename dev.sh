/bin/sh -c "./restart.sh" &
gunicorn -w 6 -b 0.0.0.0:8080 manage:app --timeout 48000
# python manage.py runserver -h 0.0.0.0 -p 8080
