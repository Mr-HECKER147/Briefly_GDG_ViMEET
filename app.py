import os

from dotenv import load_dotenv
from flask import Flask, abort, redirect, render_template, request, url_for
from groq import Groq
from pypdf import PdfReader
from database import (
    create_table,
    delete_summary,
    get_all_summaries,
    get_summary_by_id,
    save_summary
)

load_dotenv()

MAX_DOCUMENT_LENGTH = 25_000
MAX_UPLOAD_SIZE = 5 * 1024 * 1024
ALLOWED_EXTENSIONS = {".pdf", ".txt"}
SUMMARY_LENGTHS = {"short", "medium", "detailed"}

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = MAX_UPLOAD_SIZE
create_table()


def extract_text_from_file(uploaded_file):
    """Extract text from a supported uploaded document."""
    filename = (uploaded_file.filename or "").strip()
    extension = os.path.splitext(filename)[1].lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise ValueError("Only TXT and PDF files are supported.")

    if extension == ".txt":
        return uploaded_file.read().decode("utf-8-sig", errors="replace").strip()

    reader = PdfReader(uploaded_file)
    return "\n".join(
        page_text
        for page in reader.pages
        if (page_text := page.extract_text())
    ).strip()


def generate_summary(text, length):
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is not configured.")

    length_guidance = {
        "short": "Write 1-2 concise sentences.",
        "medium": "Write one concise paragraph or a few bullets.",
        "detailed": "Cover all key points in several concise paragraphs or bullets.",
    }
    prompt = f"""Summarize the document below.

{length_guidance[length]}
- Use simple, clear language.
- Keep only information that appears in the document.
- Use short paragraphs or bullet points when useful.

Document:
{text}
"""

    client = Groq(api_key=api_key)
    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {"role": "system", "content": "You are a helpful document summarizer."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
        max_completion_tokens=500,
    )
    summary = response.choices[0].message.content
    if not summary:
        raise RuntimeError("The AI service returned an empty summary.")
    return summary


@app.route("/", methods=["GET", "POST"])
def home():
    summary = ""
    error = ""
    filename = ""
    text = ""
    length = "medium"

    if request.method == "POST":
        text = request.form.get("text", "").strip()
        length = request.form.get("length", "medium")
        if length not in SUMMARY_LENGTHS:
            length = "medium"

        uploaded_file = request.files.get("file")
        if uploaded_file and uploaded_file.filename:
            filename = uploaded_file.filename
            try:
                text = extract_text_from_file(uploaded_file)
            except ValueError as exc:
                error = str(exc)
            except Exception:
                error = "The uploaded file could not be read. Check that it is a valid TXT or PDF file."

        if not error and not text:
            error = "No readable text was found. Paste text or upload a valid TXT/PDF file."
        elif not error and len(text) > MAX_DOCUMENT_LENGTH:
            error = f"Your document is too long. Use text shorter than {MAX_DOCUMENT_LENGTH:,} characters."
        elif not error:
            try:
                summary = generate_summary(text, length)
            except Exception:
                error = "The AI service could not generate a summary. Check your API configuration and try again."

            if summary:
                source_name = filename or "Pasted text"
                try:
                    save_summary(source_name, text, summary, length)
                except Exception:
                    error = "Summary generated, but it could not be saved to history."

    return render_template(
        "index.html",
        summary=summary,
        error=error,
        file_name=filename,
        text=text,
        length=length,
    )


@app.errorhandler(413)
def upload_too_large(_error):
    return render_template(
        "index.html",
        summary="",
        error="The uploaded file is too large. The limit is 5 MB.",
        file_name="",
        text="",
        length="medium",
    ), 413

@app.route("/history")
def history():
    summaries = get_all_summaries()

    return render_template(
        "history.html",
        summaries=summaries
    )


@app.route("/history/<int:summary_id>")
def summary_detail(summary_id):
    summary = get_summary_by_id(summary_id)

    if summary is None:
        abort(404)

    return render_template(
        "detail.html",
        summary=summary
    )


@app.post("/history/<int:summary_id>/delete")
def remove_summary(summary_id):
    delete_summary(summary_id)
    return redirect(url_for("history"))


if __name__ == "__main__":
    app.run(debug=os.getenv("FLASK_DEBUG") == "1")
