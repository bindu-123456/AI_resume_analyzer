from flask import Flask, render_template, request, jsonify
from pypdf import PdfReader
from io import BytesIO
from database import create_table, save_analysis
import re
app = Flask(__name__)
create_table()

jobs = {
    1: {
        "title": "Python Developer",
        "description": "Develop applications using Python and Flask.",
        "skills": [
            "python", "flask", "sql", "git", "rest api"
        ],
        "qualification": "B.E., B.Tech or relevant degree",
        "experience": "Fresher"
    },

    2: {
        "title": "Java Developer",
        "description": "Develop backend applications using Java.",
        "skills": [
            "java", "spring boot", "sql", "rest api", "git"
        ],
        "qualification": "B.E., B.Tech or relevant degree",
        "experience": "Fresher"
    },

    3: {
        "title": "Web Developer",
        "description": "Create and maintain responsive websites.",
        "skills": [
            "html", "css", "javascript", "python", "flask"
        ],
        "qualification": "B.E., B.Tech or relevant degree",
        "experience": "Fresher"
    },

    4: {
        "title": "Data Analyst",
        "description": "Analyze data and prepare reports.",
        "skills": [
            "python", "sql", "pandas", "numpy", "excel"
        ],
        "qualification": "B.E., B.Tech or relevant degree",
        "experience": "Fresher"
    },

    5: {
        "title": "Machine Learning Engineer",
        "description": "Build and evaluate machine learning models.",
        "skills": [
            "python", "machine learning", "numpy",
            "pandas", "sql"
        ],
        "qualification": "B.E., B.Tech or relevant degree",
        "experience": "Fresher"
    }
}

def extract_resume_text(pdf_file):
    pdf = PdfReader(BytesIO(pdf_file.read()))

    resume_text = ""

    for page in pdf.pages:
        resume_text += page.extract_text() or ""

    return resume_text


def analyze_skills(resume_text, job_description):
    # Convert text to lowercase for comparison
    resume = resume_text.lower()
    job = job_description.lower()

    # Skills we want to check
    skills = [
        "python",
        "java",
        "c++",
        "html",
        "css",
        "javascript",
        "flask",
        "django",
        "sql",
        "mysql",
        "sqlite",
        "postgresql",
        "mongodb",
        "rest api",
        "git",
        "github",
        "machine learning",
        "pandas",
        "numpy",
        "data structures",
        "problem-solving"
    ]

    # Find skills mentioned in the job description
    required_skills = []

    for skill in skills:
        pattern = r"(?<!\w)" + re.escape(skill) + r"(?!\w)"

        if re.search(pattern, job):
            required_skills.append(skill)

    # Find skills present in the resume
    matching_skills = []
    missing_skills = []

    for skill in required_skills:
        pattern = r"(?<!\w)" + re.escape(skill) + r"(?!\w)"

        if re.search(pattern, resume):
            matching_skills.append(skill)
        else:
            missing_skills.append(skill)

    # Calculate match percentage
    if len(required_skills) > 0:
        match_percentage = round(
            len(matching_skills) / len(required_skills) * 100
        )
    else:
        match_percentage = 0

    return {
        "match_percentage": match_percentage,
        "matching_skills": matching_skills,
        "missing_skills": missing_skills,
        "total_required_skills": len(required_skills)
    }


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/jobs", methods=["GET"])
def get_jobs():
    return jsonify(jobs)

@app.route("/analyze", methods=["POST"])
def analyze_resume():

    # 1. Check whether a resume was uploaded
    if "resume" not in request.files:
        return jsonify({
            "error": "Please upload a resume PDF"
        }), 400

    pdf_file = request.files["resume"]

    # 2. Check whether a file was selected
    if pdf_file.filename == "":
        return jsonify({
            "error": "No file selected"
        }), 400

    # 3. Check the file extension
    if not pdf_file.filename.lower().endswith(".pdf"):
        return jsonify({
            "error": "Please upload a PDF file"
        }), 400

    # 4. Get the selected job ID
    job_id = request.form.get("jobId", "").strip()

    if not job_id.isdigit():
        return jsonify({
            "error": "Please select a valid job"
        }), 400

    # 5. Find the selected job
    selected_job = jobs.get(int(job_id))

    if selected_job is None:
        return jsonify({
            "error": "Selected job was not found"
        }), 404

    # 6. Extract text from the PDF
    try:
        resume_text = extract_resume_text(pdf_file)
    except Exception:
        return jsonify({
            "error": "Could not read the PDF file"
        }), 400

    # 7. Check whether readable text exists
    if not resume_text.strip():
        return jsonify({
            "error": "No readable text found in the PDF"
        }), 400

    # 8. Check whether the document looks like a resume
    resume_keywords = [
        "education",
        "skills",
        "experience",
        "projects",
        "qualification",
        "resume"
    ]

    if not any(
        word in resume_text.lower()
        for word in resume_keywords
    ):
        return jsonify({
            "error": "Please upload a valid resume PDF"
        }), 400

    # 9. Compare the resume with the selected job's skills
    job_description = " ".join(selected_job["skills"])

    analysis = analyze_skills(
        resume_text,
        job_description
    )

    # 10. Generate improvement suggestions
    suggestion_map = {
        "python": "Learn Python fundamentals and practise coding problems.",
        "flask": "Learn Flask and build a small web application.",
        "sql": "Practise SQL queries and build a database project.",
        "git": "Learn Git basics and practise version control.",
        "rest api": "Learn REST API concepts and create an API using Flask.",
        "html": "Practise HTML by building a structured webpage.",
        "css": "Learn CSS layouts and create a responsive webpage.",
        "javascript": "Practise JavaScript DOM manipulation and event handling.",
        "pandas": "Learn Pandas for data cleaning and analysis.",
        "numpy": "Practise NumPy arrays and numerical operations.",
        "excel": "Practise Excel formulas, sorting, and data analysis.",
        "machine learning": "Study machine learning fundamentals and build a small model.",
        "spring boot": "Learn Spring Boot and build a simple Java backend."
    }

    suggestions = [
        suggestion_map[skill.lower()]
        for skill in analysis["missing_skills"]
        if skill.lower() in suggestion_map
    ]

    save_analysis(
        resume_filename=pdf_file.filename,
        job_title=selected_job["title"],
        match_percentage=analysis["match_percentage"],
        matching_skills=analysis["matching_skills"],
        missing_skills=analysis["missing_skills"],
        suggestions=suggestions
    )

    # 11. Send the results back to JavaScript
    return jsonify({
        "message": "Resume analyzed successfully!",
        "job_title": selected_job["title"],
        "resume_text": resume_text,
        "match_percentage": analysis["match_percentage"],
        "matching_skills": analysis["matching_skills"],
        "missing_skills": analysis["missing_skills"],
        "total_required_skills": analysis["total_required_skills"],
        "suggestions": suggestions
    })
if __name__ == "__main__":
    app.run(debug=True)