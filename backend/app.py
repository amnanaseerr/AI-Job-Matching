# app.py (Full Updated Version)

from flask import Flask, request, jsonify, render_template
import pandas as pd
import os
from werkzeug.utils import secure_filename
import docx2txt
import PyPDF2
from utils import extract_skills, similarity_score

app = Flask(__name__)

# Upload folder
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Load datasets
candidates = pd.read_csv("dataset/resumes.csv")
jobs = pd.read_csv("dataset/jobs.csv")

# Ensure ID exists
if 'id' not in jobs.columns:
    jobs['id'] = range(1, len(jobs)+1)
if 'id' not in candidates.columns:
    candidates['id'] = range(1, len(candidates)+1)

# --------------------- Routes ---------------------

# Homepage
@app.route('/')
def home():
    return render_template('index.html')

# Show all jobs
@app.route('/jobs')
def get_jobs():
    return jsonify(jobs.to_dict(orient='records'))

# Show all candidates
@app.route('/candidates')
def get_candidates():
    return jsonify(candidates.to_dict(orient='records'))

# Rank candidates for a specific job
@app.route('/match/<int:job_id>')
def match_candidates(job_id):
    job = jobs.loc[jobs['id'] == job_id].iloc[0]
    job_skills = job['skills'].split(',')

    candidates['score'] = candidates['skills'].apply(lambda x: similarity_score(x, job_skills))
    ranked = candidates.sort_values(by='score', ascending=False)

    return jsonify(ranked.to_dict(orient='records'))

# --------------------- Resume Upload & Job Matching ---------------------
@app.route('/upload_resume', methods=['POST'])
def upload_resume():
    if 'resume' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['resume']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    filename = secure_filename(file.filename)
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(file_path)

    # Extract text
    resume_text = ""
    fname_lower = file.filename.lower()
    if fname_lower.endswith(".pdf"):
        pdf_reader = PyPDF2.PdfReader(file_path)
        for page in pdf_reader.pages:
            resume_text += page.extract_text() + " "
    elif fname_lower.endswith(".docx"):
        resume_text = docx2txt.process(file_path)
    else:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            resume_text = f.read()
    resume_text = resume_text.lower()

    # Extract skills (returns list)
    skills = extract_skills(resume_text)

    # Update match_score for each job
    for idx, job in jobs.iterrows():
        job_skills_set = set([s.strip().lower() for s in job['skills'].split(',')])
        resume_skills_set = set([s.strip().lower() for s in skills])
        matched_skills = resume_skills_set.intersection(job_skills_set)
        jobs.at[idx, 'match_score'] = round(len(matched_skills) / len(job_skills_set) * 100)

    # Return top 10 jobs
    top_jobs = jobs.sort_values(by='match_score', ascending=False).head(10)
    return jsonify(top_jobs.to_dict(orient='records'))

# --------------------- Run App ---------------------
if __name__ == "__main__":
    app.run(debug=True)