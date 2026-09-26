# Briefly — AI Document Summarizer

Briefly is a Flask-based web application that creates concise summaries from pasted text or uploaded TXT/PDF files using the Groq API.

Users can register and log in to create private summaries. Each saved summary is associated with its owner in SQLite. Users can browse, download, copy, and delete their own summaries.

**Live app:** [Open Briefly](https://briefly-gdg-vimeet.onrender.com/)

## Features

- Summarize pasted text
- Upload and summarize `.txt` and text-based `.pdf` files
- Choose a short, medium, or detailed summary
- Generate summaries using the Groq API
- Save summaries and original text in SQLite
- Browse saved summaries in a History page
- View full summary details and original extracted text
- Delete summaries from the history or detail page
- Switch between light and dark themes
- Limit uploads to 5 MB
- Limit extracted input text to 25,000 characters
- Show clear error messages for invalid files, unreadable PDFs, and API failures
- Register and log in with a username and password
- Keep summary history private to each account
- Copy summaries or download them as PDFs

## Tech Stack

- Python
- Flask
- Flask-WTF for CSRF protection
- Groq API
- `openai/gpt-oss-20b` model
- SQLite
- pypdf
- ReportLab
- HTML and CSS

## Project Structure

```text
Briefly/
├── app.py
├── database.py
├── requirements.txt
├── .gitignore
├── README.md
├── templates/
│   ├── index.html
│   ├── history.html
│   ├── detail.html
│   ├── login.html
│   └── register.html
└── static/
    ├── favicon.svg
    ├── style.css
    ├── summary-actions.js
    └── theme.js
```

## Setup

### 1. Clone the repository

```bash
git clone YOUR_REPOSITORY_LINK
cd YOUR_PROJECT_FOLDER
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Add your Groq API key

Create a `.env` file in the project folder and add:

```env
GROQ_API_KEY=your_api_key
SECRET_KEY=your_random_secret_key
SESSION_COOKIE_SECURE=false
```

Generate a secret key with `python -c "import secrets; print(secrets.token_hex(32))"`. Set `SESSION_COOKIE_SECURE=true` on the HTTPS deployment. Keep `.env` out of GitHub.

Do not upload the `.env` file to GitHub.

On Render, add `GROQ_API_KEY` and `SECRET_KEY` as environment variables and set `SESSION_COOKIE_SECURE=true`. SQLite is the configured database. To preserve it on Render, use a persistent disk and set `DATABASE_PATH` to a file on its mount (for example, `/var/data/summaries.db`). Render free web services do not support persistent disks.

## Run Locally

Start the Flask application from the project folder:

```bash
py -m flask --app app run --debug
```

Or, if your `app.py` includes `app.run(...)`, you can use:

```bash
python app.py
```

Open the local address shown in the terminal, usually:

```text
http://127.0.0.1:5000/
```

The application creates or updates the database tables automatically when it starts. Set `DATABASE_PATH` to use a different SQLite file location.

## How to Use

1. Open the home page.
2. Paste text into the input area, or upload a TXT/PDF file.
3. Select **Short**, **Medium**, or **Detailed**.
4. Click **Generate Summary**.
5. View the generated AI summary.
6. Open **History** to view your saved summaries.
7. Click a saved record to see its complete summary and original text.
8. Delete unwanted summaries from the History or detail page.
9. Use the theme toggle to switch between light and dark mode.
10. Copy the summary or download it as a PDF from below the result.

## File Support and Limits

- Supported files: `.txt` and `.pdf`
- Maximum file upload size: 5 MB
- Maximum extracted text length: 25,000 characters
- PDFs must contain selectable text.
- Scanned/image-only PDFs may not work because OCR support is not included in this MVP.

## Database

Briefly uses SQLite for local storage.

Each successful summary stores:

- The account that owns it
- Source name or uploaded file name
- Original text
- Generated summary
- Chosen summary length
- Created date and time

## Notes

- The SQLite database file `summaries.db` is ignored by Git because it contains local user history.
- The `.env` file is ignored by Git because it contains API and session secrets.
- Existing summaries created before account ownership was added remain unassigned and are hidden from account histories.
- The deployed service needs a persistent database or filesystem disk to keep accounts and summaries across restarts and redeploys.

## Future Improvements

- Search and filter saved summaries
- Tags and categories
- OCR for scanned PDFs
- PostgreSQL database for persistent cloud storage

## Author

UDDHAV JOSHI
