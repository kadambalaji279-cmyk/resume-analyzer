from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
from model import analyze_resume
import PyPDF2
import os

app = Flask(__name__)
app.secret_key = "secret123"

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ---------------- PDF TEXT EXTRACTION ----------------
def extract_text_from_pdf(file):
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in reader.pages:
        if page.extract_text():
            text += page.extract_text()
    return text


# ---------------- FAKE RESUME CHECK ----------------
def is_fake_resume(text):
    keywords = ["experience", "education", "skills", "project", "work"]
    score = sum(1 for k in keywords if k in text.lower())
    return score < 2


# ---------------- SERVE UPLOADED FILES ----------------
@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


# ---------------- MAIN ROUTE ----------------
@app.route("/", methods=["GET", "POST"])
def index():

    result = session.get("result", None)

    if request.method == "POST":

        file = request.files.get("resume_file")
        filename = None
        file_url = None

        resume_text = ""

        # ---------------- FILE UPLOAD ----------------
        if file and file.filename != "":
            filename = file.filename

            path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(path)

            # FIXED: proper Flask URL route
            file_url = url_for("uploaded_file", filename=filename)

            resume_text = extract_text_from_pdf(file)

            valid = not is_fake_resume(resume_text)

        # ---------------- TEXT INPUT ----------------
        else:
            resume_text = request.form.get("resume", "")
            valid = True

        job_desc = request.form.get("job_desc", "")
        job_role = request.form.get("job_role", "")

        # ---------------- AI ANALYSIS ----------------
        result = analyze_resume(resume_text, job_desc, job_role)

        result["filename"] = filename
        result["file_url"] = file_url
        result["is_valid"] = valid
        result["confidence"] = "6/7" if valid else "1/7"

        session["result"] = result

        return redirect(url_for("index"))  # prevents refresh re-submit bug

    return render_template("index.html", result=result)


# ---------------- RESET / CLEAR SESSION ----------------
@app.route("/clear")
def clear():
    session.clear()
    return redirect(url_for("index"))



# ---------------- RUN APP ----------------
# ---------------- RUN APP ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)