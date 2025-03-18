# DocuTrans

DocuTrans is a Flask-based web application for document translation. It allows users to upload documents, extract text, translate it into their preferred language, and download the translated text file.

## Features

- Upload documents (`.pdf`, `.txt`)
- Extract text from PDFs
- Translate extracted text into multiple languages
- Download the translated text file
- User authentication for secure access
- Background processing for translation
- Language detection and automatic encoding handling

## Project Structure

```
DocuTrans/
│── app/
│   ├── static/                  # Static assets (fonts, stylesheets, etc.)
│   ├── templates/               # HTML templates
│   ├── routes.py                # Handles file uploads and translation
│   ├── models.py                # Database models
│   ├── utils.py                 # Helper functions for text extraction and translation
│   ├── forms.py                 # Form handling with Flask-WTF
│── migrations/                   # Database migrations
│── requirements.txt              # Required dependencies
│── config.py                     # Application configuration
│── README.md                     # Project documentation
│── run.py                         # Entry point to run the Flask application
│── .env                           # Environment variables
```

## Installation

### Clone the Repository
```bash
git clone https://github.com/LalwaniPalash/DocuTrans.git
cd DocuTrans
```

### Set Up a Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate  # Windows
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Set Up the Environment

Create a `.env` file:
```ini
SECRET_KEY = "your-secret-key"
SQLALCHEMY_DATABASE_URI = "sqlite:///database.db"
SQLALCHEMY_TRACK_MODIFICATIONS = "False"
```
Ensure the upload folder exists:
```bash
mkdir -p app/static/uploads
```

### Initialize the Database
```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

## Running the Application
```bash
flask run
```
Visit `http://127.0.0.1:5000` in your browser.

## Usage

1. Sign up or log in
2. Upload a PDF or TXT file
3. Select a target language
4. Submit and wait for processing
5. Download the translated text file

## Configuration Options

Modify `config.py` or `.env` to adjust:
- Upload directory
- Language support
- Database settings

## Technologies Used

- **Backend**: Flask, Flask-SQLAlchemy, Flask-WTF, Flask-Login
- **Translation**: `deep-translator`
- **PDF Handling**: `pdf2image`, `pytesseract`
- **Frontend**: HTML, CSS (Bootstrap)
- **Database**: SQLite

## Contributing

Pull requests are welcome. 

## License

This project is licensed under the Unlicense.