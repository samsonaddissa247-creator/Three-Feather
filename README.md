# Three Feathers Hockey Club website

A Django website. Everything the coach adds is stored in a database, so every visitor sees it straight away.

## Run it on your computer

    python -m venv venv
    venv\Scripts\activate          (Windows)   or   source venv/bin/activate   (Mac/Linux)
    pip install -r requirements.txt
    python manage.py migrate
    python manage.py runserver

Open http://127.0.0.1:8000

## Coach password

The password is COACHAB. Visitors can open every page. When anyone clicks an "Add" or "Edit" button they are sent to the
coach login first. After logging in the coach can add players (with photos), change goals and assists, add games and
results, upload match photos, edit the club info and remove things.

Change the password before you go live by setting the COACH_PASSWORD environment variable. Use something longer than
seven letters. After five wrong attempts from one address the login locks for 10 minutes.

## Put it online (PythonAnywhere, free plan works)

1. Upload this folder (or the zip) to PythonAnywhere and open a Bash console in it.
2. `python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt`
3. `python manage.py migrate` and `python manage.py collectstatic`
4. On the Web tab, add a web app (Manual configuration, same Python version) and point it at the venv.
5. In the WSGI file, set these before the Django lines:

       import os
       os.environ['DEBUG'] = '0'
       os.environ['SECRET_KEY'] = 'type-a-long-random-string-here'
       os.environ['COACH_PASSWORD'] = 'your-own-strong-password'
       os.environ['ALLOWED_HOSTS'] = 'yourname.pythonanywhere.com'
       os.environ['CSRF_TRUSTED_ORIGINS'] = 'https://yourname.pythonanywhere.com'

   then point it at `config.wsgi` and the project folder.
6. Reload the web app.

Other hosts work too. The important rule: the host must keep the `db.sqlite3` file and the `media/` folder between
restarts. Hosts that wipe the disk on every deploy need a database and file storage added.

## Backups

Copy `db.sqlite3` and the `media/` folder now and then. That is everything the coach has entered.

## Where things are

- `club/models.py` players, fixtures, photos and club info
- `club/views.py` pages and the coach-only actions
- `templates/` the pages, `static/styles.css` the maroon, green and white design
# Three-Feather
