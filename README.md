# Briefly — AI Document Summarizer

Briefly is a Flask-based web application that creates concise summaries from pasted text or uploaded TXT/PDF files using the Groq API.

Generated summaries, source information, selected summary length, and original text are saved locally in an SQLite database. Users can browse their history, view individual records, delete summaries, and switch between light and dark themes.


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

## Tech Stack

- Python
- Flask
- Groq API
- `openai/gpt-oss-20b` model
- SQLite
- pypdf
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
│   └── detail.html
└── static/
    └── style.css
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
```

Do not upload the `.env` file to GitHub.

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

The application creates `summaries.db` automatically when it starts.

## How to Use

1. Open the home page.
2. Paste text into the input area, or upload a TXT/PDF file.
3. Select **Short**, **Medium**, or **Detailed**.
4. Click **Generate Summary**.
5. View the generated AI summary.
6. Open **History** to view previously saved summaries.
7. Click a saved record to see its complete summary and original text.
8. Delete unwanted summaries from the History or detail page.
9. Use the theme toggle to switch between light and dark mode.

## File Support and Limits

- Supported files: `.txt` and `.pdf`
- Maximum file upload size: 5 MB
- Maximum extracted text length: 25,000 characters
- PDFs must contain selectable text.
- Scanned/image-only PDFs may not work because OCR support is not included in this MVP.

## Database

Briefly uses SQLite for local storage.

Each successful summary stores:

- Source name or uploaded file name
- Original text
- Generated summary
- Chosen summary length
- Created date and time

## Notes

- The SQLite database file `summaries.db` is ignored by Git because it contains local user history.
- The `.env` file is ignored by Git because it contains the private Groq API key.
- For cloud deployment, a hosted database such as PostgreSQL can replace SQLite for persistent storage.

## Future Improvements

- User authentication
- Per-user history
- Search and filter saved summaries
- Tags and categories
- Export summaries as PDF
- OCR for scanned PDFs
- PostgreSQL database for persistent cloud storage

## Author

UDDHAV JOSHI
