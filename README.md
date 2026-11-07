# Student Result Management System

A Flask + MySQL academic records portal with Admin, Teacher, and Student roles. Staff can enter/update marks; admins can create student accounts and remove results; students see their own grades. Grades are calculated from percentage: A+ (90+), A (80+), B (70+), C (60+), D (50+), F (below 50).

## Requirements

- Python 3.10 or newer
- MySQL Server 8.x, running locally
- Visual Studio Code (recommended)

## Run locally

1. Extract the ZIP, then open the extracted `student-result-management-system` folder in VS Code (`File > Open Folder`).
2. Open VS Code's terminal (`Terminal > New Terminal`). Create and activate a virtual environment:

   **Windows PowerShell**
   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
   If PowerShell blocks activation, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` in that terminal, then activate again.

3. Install packages:
   ```powershell
   python -m pip install -r requirements.txt
   ```
4. In MySQL Workbench, open `schema.sql` and click the lightning bolt to run it. Or from a terminal with MySQL on PATH:
   ```powershell
   mysql -u root -p < schema.sql
   ```
5. Copy `.env.example` to `.env` and set `DB_PASSWORD` to your MySQL password. Set a private random `SECRET_KEY` too. Do not commit `.env`.
6. Add demo accounts and one sample result:
   ```powershell
   python seed.py
   ```
7. Start the website:
   ```powershell
   python app.py
   ```
8. Visit `http://127.0.0.1:5000` in your browser.

### Demo logins

| Role | Username | Password |
|---|---|---|
| Admin | `admin` | `Admin@123` |
| Teacher | `teacher` | `Teacher@123` |
| Student | `student` | `Student@123` |

These are demonstration credentials. Change them before using real student information. The app is intended for local learning and demonstration; production use needs additional deployment security and operational controls.

## VS Code tips

- Install the Microsoft **Python** extension.
- Choose `.venv` with `Ctrl+Shift+P` → **Python: Select Interpreter**.
- Use the integrated terminal for the commands above. Stop the local server with `Ctrl+C`.
- Project layout: `app.py` (routes and access rules), `schema.sql` (tables), `seed.py` (demo data), `templates/` (HTML), `static/` (CSS and JavaScript).

## Push to GitHub

1. Sign in to GitHub and create a new **empty** repository. Do not initialize it with a README or license (this folder already has a README).
2. Open this project folder in VS Code and use **Terminal > New Terminal**. Make sure `.env` is not present in the files staged for upload; `.gitignore` excludes it.
3. Run these commands, replacing the URL with your repository's HTTPS URL:
   ```powershell
   git init
   git add .
   git status
   git commit -m "Add student result management system"
   git branch -M main
   git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPOSITORY.git
   git push -u origin main
   ```
4. GitHub may prompt you to authenticate in a browser. Review the repository page after the push.

If Git reports that `origin` already exists, use `git remote set-url origin https://github.com/YOUR-USERNAME/YOUR-REPOSITORY.git` before pushing. To make later updates: `git add .`, `git commit -m "Describe your change"`, and `git push`.

## Deploy on Railway

1. Create a Railway project and add a **MySQL** service.
2. Add this GitHub repository as a service.
3. Link the MySQL service to the web service so Railway provides `MYSQLHOST`, `MYSQLPORT`, `MYSQLUSER`, `MYSQLPASSWORD`, and `MYSQLDATABASE`.
4. Add a private `SECRET_KEY` environment variable. Generate one with:
   ```powershell
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```
5. Deploy. The included `Procfile` initializes the schema and starts Gunicorn automatically.
6. Generate a public domain from the Railway service's **Settings** page.

The demo accounts are not created automatically in production. Run `python seed.py` only for a learning/demo deployment after the database is available, then change the demo passwords.

To create the larger demo dataset, run `python seed_bulk.py` in the Railway service console. It creates 20 teachers (`teacher01` through `teacher20`) and 120 students (`student001` through `student120`), all using the demo passwords shown by the script.

To add the five additional demo courses, run `python seed_courses.py` in the Railway service console.

## Notes

- The application uses parameterized SQL queries and password hashes.
- Only administrators can add students or delete results. Teachers can add/update marks. Students see their own results.
- Results are unique for each student, course, and assessment; saving the same combination updates the existing marks.
