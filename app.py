import os
import sqlite3
from functools import wraps
from io import BytesIO
from xml.sax.saxutils import escape

from dotenv import load_dotenv
from flask import (
    Flask,
    abort,
    redirect,
    render_template,
    request,
    send_file,
    session,
    url_for
)
from flask_wtf.csrf import CSRFProtect

from werkzeug.security import (
    check_password_hash,
    generate_password_hash
)
from groq import Groq
from pypdf import PdfReader
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
from database import (
    initialize_database,
    create_user,
    delete_summary,
    get_all_summaries,
    get_summary_by_id,
    get_user_by_username,
    save_summary
)

load_dotenv()

MAX_DOCUMENT_LENGTH = 25_000
MAX_UPLOAD_SIZE = 5 * 1024 * 1024
ALLOWED_EXTENSIONS = {".pdf", ".txt"}
SUMMARY_LENGTHS = {"short", "medium", "detailed"}

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = MAX_UPLOAD_SIZE
secret_key = os.getenv("SECRET_KEY")
if not secret_key:
    raise RuntimeError("Set SECRET_KEY in the environment before starting Briefly.")
app.config["SECRET_KEY"] = secret_key
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = os.getenv(
    "SESSION_COOKIE_SECURE", "true"
).lower() in {"1", "true", "yes"}
CSRFProtect(app)
initialize_database()


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if not session.get("user_id"):
            return redirect(url_for("login"))
        return view(*args, **kwargs)

    return wrapped_view

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
@login_required
def home():
    summary = ""
    error = ""
    filename = ""
    text = ""
    length = "medium"
    summary_id = None

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
                    summary_id = save_summary(
                        session["user_id"], source_name, text, summary, length
                    )
                except Exception:
                    error = "Summary generated, but it could not be saved to history."

    return render_template(
        "index.html",
        summary=summary,
        error=error,
        file_name=filename,
        text=text,
        length=length,
        summary_id=summary_id,
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
@login_required
def history():
    summaries = get_all_summaries(session["user_id"])

    return render_template(
        "history.html",
        summaries=summaries
    )


@app.route("/history/<int:summary_id>")
@login_required
def summary_detail(summary_id):
    summary = get_summary_by_id(summary_id, session["user_id"])

    if summary is None:
        abort(404)

    return render_template(
        "detail.html",
        summary=summary
    )


@app.get("/history/<int:summary_id>/pdf")
@login_required
def download_summary_pdf(summary_id):
    summary = get_summary_by_id(summary_id, session["user_id"])
    if summary is None:
        abort(404)

    styles = getSampleStyleSheet()
    styles["Title"].textColor = colors.HexColor("#183f39")
    story = [
        Paragraph("Briefly Summary", styles["Title"]),
        Spacer(1, 12),
        Paragraph(escape(summary["source_name"]), styles["Heading2"]),
        Spacer(1, 8),
    ]
    formatted_summary = "<br/>".join(
        escape(line) for line in summary["summary_text"].splitlines()
    )
    story.append(Paragraph(formatted_summary, styles["BodyText"]))

    pdf = BytesIO()
    document = SimpleDocTemplate(
        pdf,
        pagesize=letter,
        title=f"Briefly summary - {summary['source_name']}",
        author="Briefly",
    )
    document.build(story)
    pdf.seek(0)
    return send_file(
        pdf,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=f"briefly-summary-{summary_id}.pdf",
    )


@app.post("/history/<int:summary_id>/delete")
@login_required
def remove_summary(summary_id):
    delete_summary(summary_id, session["user_id"])
    return redirect(url_for("history"))

@app.route("/register", methods=["GET", "POST"])
def register():
    error = ""

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not username or not password or not confirm_password:
            error = "Please fill in all fields."

        elif len(username) < 3:
            error = "Username must contain at least 3 characters."

        elif len(password) < 8:
            error = "Password must contain at least 8 characters."

        elif password != confirm_password:
            error = "Passwords do not match."

        elif get_user_by_username(username):
            error = "That username is already taken."

        else:
            password_hash = generate_password_hash(password)
            try:
                create_user(username, password_hash)
            except sqlite3.IntegrityError:
                error = "That username is already taken."
            else:
                return redirect(url_for("login"))

    return render_template(
        "register.html",
        error=error
    )

@app.route("/login", methods=["GET", "POST"])
def login():
    error = ""

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        user = get_user_by_username(username)

        if not user:
            error = "Invalid username or password."

        elif not check_password_hash(user["password_hash"], password):
            error = "Invalid username or password."

        else:
            session.clear()
            session["user_id"] = user["id"]
            session["username"] = user["username"]

            return redirect(url_for("home"))

    return render_template(
        "login.html",
        error=error
    )
@app.post("/logout")
def logout():
    session.clear()

    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=os.getenv("FLASK_DEBUG") == "1")
