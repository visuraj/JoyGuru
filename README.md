# Utsav 2026 – Satsang Vihar Bengaluru (Django)

Public website with a registration form. Registrations are saved in the Django database
and can be viewed **only by admin users** (login at the admin address). There is no public page that lists them.

## Run on your laptop
    python -m venv venv && source venv/bin/activate      # Windows: venv\Scripts\activate
    pip install -r requirements.txt
    export DEBUG=1                                       # Windows: set DEBUG=1
    python manage.py migrate
    python manage.py createsuperuser                     # your admin login
    python manage.py runserver
Open http://127.0.0.1:8000/ (site) and http://127.0.0.1:8000/admin/ (admin).

## Go live (needs a host; example: PythonAnywhere, Render, Railway)
Set these environment variables on the host:
    SECRET_KEY=<long random text>        # python -c "import secrets;print(secrets.token_urlsafe(50))"
    ALLOWED_HOSTS=yourdomain.com
    CSRF_TRUSTED_ORIGINS=https://yourdomain.com
    ADMIN_URL=my-secret-admin-path/      # hides the admin address (recommended)
    DATABASE_URL=postgres://...          # recommended on Render/Railway; if unset, SQLite file db.sqlite3 is used
Then run once:  python manage.py migrate && python manage.py createsuperuser && python manage.py collectstatic --noinput
Start command:  gunicorn config.wsgi   (a Procfile is included)

Important: free hosts that reset their disk will erase a SQLite file. Use a Postgres database
(DATABASE_URL) or a host with a persistent disk, such as PythonAnywhere.

## Admin features
Search by name / phone / ID, filters, date drill-down, view-only records, and "Download selected as CSV".

## One-click Excel download (new)
Log in to the admin, then:
- **Admin home page** → big orange button = one .xlsx with 4 sheets: Summary (live totals, counts by date/type/transport/interest, top cities), Registrations, Accommodation, and "Registered + Accommodation" (people matched by mobile number).
- **Registrations** or **Accommodation requests** list → *Download ALL as Excel* (top right) = that sheet only.
- Select rows → action *Download selected ... as Excel*.
Always exports every record (no 50-per-page limit); 1,000s of rows take under a second. Needs `xlsxwriter` (in requirements.txt: run `pip install -r requirements.txt`).
