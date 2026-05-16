# IE Platform

A web-based Industrial Engineering assistant built with Flask.

## Overview

`IE Platform` is a student project from Portsaid University developed by 3rd year students in the Department of Mechanical Production and Design Engineering. The application provides engineering analysis tools for:

- Project scheduling with PERT/CPM
- Plant location analysis
- Transportation modeling
- Cost and break-even analysis
- Facility layout planning
- Assignment optimization

## Academic Team

- Developed by Portsaid University students
- Supervised by Dr. Hanan Kouta
- Department of Mechanical Production and Design Engineering
- Year: 3rd year

## Features

- Flask-based web interface
- SQLAlchemy database support
- File upload support for CSV/XLSX data inputs
- Modular engineering analysis workflows
- Built-in project and route blueprints for engineering tools

## Getting Started

### Requirements

- Python 3.11+ recommended
- `virtualenv` or `venv`

### Install dependencies

```powershell
cd d:\ie_platform
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Run locally

```powershell
python run.py
```

Then open `http://localhost:5000` in your browser.

## Deployment

This project includes a `Procfile` and is ready for deployment on Railway or other Python web hosts.

### Railway deployment

1. Push the repository to GitHub.
2. Create a new Railway project and connect it to your GitHub repo.
3. Railway should detect the `Procfile`.
4. If needed, use the start command:
   ```text
   gunicorn run:app
   ```

### Production notes

- Configure `SECRET_KEY` and `DATABASE_URL` with environment variables in production.
- The default database uses SQLite in the `instance/` folder.

## Project Structure

- `run.py` – application entry point
- `app/` – Flask application package
- `app/routes/` – request route modules
- `app/modules/` – engineering analysis modules
- `app/models/` – database models
- `static/` and `templates/` – frontend assets and HTML templates
- `requirements.txt` – Python dependencies
- `Procfile` – deployment process file

## Notes

This repository is intended as an academic engineering web application demonstration built during the third year of study.
