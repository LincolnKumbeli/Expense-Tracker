Markdown

# Finance App

A personal finance tracking application built with Flask.

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Introduction

This finance app is a personal finance tracking application designed to help users understand and manage their spending habits. By identifying spending patterns, it encourages more mindful spending and helps users reduce unnecessary expenses. This tool is essential for anyone looking to take control of their financial health and increase awareness of their spending habits.

## Features

- **Track Expenses**: Log daily expenses and categorize them for a detailed overview.
- **Analyze Spending Patterns**: Visualize spending patterns to identify areas where you can cut back.
- **Comprehensive Reports**: Generate reports to review spending habits and progress over time.

## Tech Stack

### **Backend:**

- **Python 3.10.0**: Primary language.
- **Flask 2.0.1**: Web framework.
- **Flask-SQLAlchemy 2.5.1**: ORM for database management.
- **Flask-WTF 0.15.1**: Form handling.
- **Flask-Login 0.5.0**: User authentication.
- **Flask-Migrate 3.1.0**: Database migrations.

### **Frontend:**

- **HTML/Jinja2**: For templating.
- **Bootstrap 5.3.0**: CSS framework for styling.
- **Font Awesome 6.0.0**: Icons.
- **JavaScript**: Minimal functionality, including password toggle.

### **Database:**

- **SQLite**: Managed through Flask-SQLAlchemy.

### **Development Tools:**

- **Virtual Environment (venv)**: `python -m venv venv`, for dependency isolation and management.
- **Git**: Version control.
- **Google Cloud**: For deployment (Compute Engine, App Engine, GKE, or Cloud Run).

### **CDN Links for Frontend (to include in `base.html`):**

```html
<link rel="stylesheet" href="[https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css](https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css)">

<link rel="stylesheet" href="[https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css](https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css)">

<script src="[https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js](https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js)"></script>
Installation
Step-by-step guide on how to set up your project locally:

Bash

# Clone the repository
git clone <repository-url>

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
- Windows:
```bash
venv\Scripts\activate
Mac/Linux:
Bash

source venv/bin/activate
Install dependencies
pip install -r requirements.txt


## Project Structure

Finance App/
├── main.py           # Main Flask application file
├── requirements.txt  # Python dependencies
└── templates/       # HTML templates (will be created later)


## Running the App

1. Make sure your virtual environment is activated
2. Run the Flask application (either command works):
```bash
python main.py
# OR
flask run
The app will be available at http://127.0.0.1:5000/ in your web browser.

Note: Since our application uses main.py instead of the default app.py, we need to explicitly set the FLASK_APP environment variable.