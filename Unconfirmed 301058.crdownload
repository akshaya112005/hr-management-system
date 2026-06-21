from flask import Flask, render_template, request
import os
import re
from PyPDF2 import PdfReader

app = Flask(__name__)

UPLOAD_FOLDER = "resumes"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ✅ Extract text
def extract_text(file):
    filename = file.filename.lower()

    if filename.endswith(".txt"):
        content = file.read()
        try:
            return content.decode("utf-8")
        except:
            return content.decode("latin-1", errors="ignore")

    elif filename.endswith(".pdf"):
        try:
            reader = PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
            return text
        except:
            return ""

    return ""

# ✅ Extract Candidate Name
def extract_name(text):
    lines = text.strip().split("\n")

    for line in lines[:10]:
        line = line.strip()

        if len(line.split()) <= 4 and not any(char.isdigit() for char in line) and "@" not in line:
            return line

    return "Unknown Candidate"

# ✅ CGPA extraction
def extract_cgpa(text):
    text = text.lower()

    patterns = [
        r'(cgpa|gpa)\s*[:\-]?\s*(\d+(\.\d+)?)',
        r'(\d+(\.\d+)?)\s*(cgpa|gpa)',
        r'(\d+(\.\d+)?)\s*/\s*10'
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            try:
                value = float(match.group(2) if len(match.groups()) > 1 else match.group(1))
                if 0 <= value <= 10:
                    return value
            except:
                continue

    return 0

# ✅ Skill matching
def match_skills(text, keywords):
    text = text.lower()
    return [k for k in keywords if k in text]

@app.route("/", methods=["GET", "POST"])
def index():
    results = []
    hr_name = ""
    step = 1
    show_results = False

    if request.method == "POST":

        # STEP 1 → Get HR name
        if "start" in request.form:
            hr_name = request.form.get("hr_name", "HR").strip()
            if hr_name == "":
                hr_name = "HR"
            step = 2

        # STEP 2 → Process resumes
        elif "process" in request.form:
            hr_name = request.form.get("hr_name", "HR").strip()
            if hr_name == "":
                hr_name = "HR"

            step = 2
            show_results = True

            keywords = request.form.get("keyword", "")
            keywords = [k.strip().lower() for k in keywords.split(",") if k.strip()]

            try:
                min_cgpa = float(request.form.get("min_cgpa", 0))
            except:
                min_cgpa = 0

            files = request.files.getlist("resumes")

            for file in files:
                if not file or file.filename == "":
                    continue

                # ✅ Allow only txt/pdf
                if not (file.filename.endswith(".txt") or file.filename.endswith(".pdf")):
                    continue

                text = extract_text(file)

                if not text.strip():
                    continue

                name = extract_name(text)
                cgpa = extract_cgpa(text)
                skills = match_skills(text, keywords)

                score = int((len(skills) / len(keywords)) * 100) if keywords else 0

                # ✅ Selection logic
                if (score >= 40 and cgpa >= min_cgpa) or score >= 70:
                    status = "Selected ✅"
                else:
                    status = "Rejected ❌"

                results.append({
                    "file": file.filename,
                    "name": name,
                    "score": score,
                    "cgpa": cgpa,
                    "skills": ", ".join(skills) if skills else "None",
                    "missing": ", ".join([k for k in keywords if k not in skills]) if keywords else "None",
                    "status": status
                })

            # ✅ Sort by score (best first)
            results = sorted(results, key=lambda x: x["score"], reverse=True)

    return render_template(
        "index.html",
        results=results,
        hr_name=hr_name,
        step=step,
        show_results=show_results
    )

if __name__ == "__main__":
    app.run(debug=True)
