# Finance App

A personal finance tracking application built with Flask.

## Setup Instructions

1. Clone the repository:
```bash
git clone <repository-url>
```

2. Create a virtual environment:
```bash
python -m venv venv
```

3. Activate the virtual environment:
- Windows:
```bash
venv\Scripts\activate
```
- Mac/Linux:
```bash
source venv/bin/activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

## Project Structure
```
Finance App/
├── main.py           # Main Flask application file
├── requirements.txt  # Python dependencies
└── templates/       # HTML templates (will be created later)
```

## Running the App
1. Make sure your virtual environment is activated
2. Run the Flask application (either command works):
```bash
python main.py
# OR
flask run
```

The app will be available at `http://127.0.0.1:5000/` in your web browser.

Note: Since our application uses `main.py` instead of the default `app.py`, we need to explicitly set the FLASK_APP environment variable.
