from flask import Flask, render_template, request
import os
import re
from PyPDF2 import PdfReader

app = Flask(__name__)

UPLOAD_FOLDER = "resumes"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# Extract text from PDF/TXT
def extract_text(file):
    filename = file.filename.lower()

    if filename.endswith(".txt"):
        content = file.read()
        return content.decode("utf-8", errors="ignore")

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


# Extract candidate name
def extract_name(text):

    lines = text.split("\n")

    for line in lines[:10]:

        line = line.strip()

        if (
            len(line.split()) <= 4
            and "@" not in line
            and not any(char.isdigit() for char in line)
        ):
            return line

    return "Unknown Candidate"


# Extract CGPA
def extract_cgpa(text):

    patterns = [
        r'(cgpa|gpa)\s*[:\-]?\s*(\d+(\.\d+)?)',
        r'(\d+(\.\d+)?)\s*/\s*10'
    ]

    for pattern in patterns:

        match = re.search(pattern, text.lower())

        if match:

            try:
                value = float(match.group(2))

                if 0 <= value <= 10:
                    return value

            except:
                pass

    return 0


# Match skills
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

        action = request.form.get("action")

        # STEP 1
        if action == "start":

            hr_name = request.form.get("hr_name", "HR")

            step = 2


        # STEP 2
        elif action == "process":

            step = 2
            show_results = True

            hr_name = request.form.get("hr_name", "HR")

            keywords = request.form.get(
                "keyword",
                ""
            ).lower().split(",")

            keywords = [
                k.strip()
                for k in keywords
                if k.strip()
            ]

            try:
                min_cgpa = float(
                    request.form.get(
                        "min_cgpa",
                        0
                    )
                )
            except:
                min_cgpa = 0


            files = request.files.getlist(
                "resumes"
            )


            for file in files:

                if file.filename == "":
                    continue


                text = extract_text(file)

                if not text:
                    continue


                name = extract_name(text)

                cgpa = extract_cgpa(text)

                skills = match_skills(
                    text,
                    keywords
                )


                score = (
                    int(
                        len(skills)
                        /
                        len(keywords)
                        *
                        100
                    )
                    if keywords
                    else 0
                )


                status = (
                    "Selected ✅"
                    if score >= 40
                    and cgpa >= min_cgpa
                    else "Rejected ❌"
                )


                results.append({

                    "file":
                    file.filename,

                    "name":
                    name,

                    "score":
                    score,

                    "cgpa":
                    cgpa,

                    "skills":
                    ", ".join(skills),

                    "missing":
                    ", ".join(
                        [
                            k
                            for k in keywords
                            if k not in skills
                        ]
                    ),

                    "status":
                    status

                })


            results = sorted(
                results,
                key=lambda x: x["score"],
                reverse=True
            )


    return render_template(

        "index.html",

        results=results,

        hr_name=hr_name,

        step=step,

        show_results=show_results

    )


if __name__ == "__main__":
     app.run(debug=False)