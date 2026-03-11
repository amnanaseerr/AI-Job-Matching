from flask import Flask, request, jsonify, render_template
import pandas as pd
from flask_cors import CORS
import re

app = Flask(__name__)
CORS(app)

# Load dataset
jobs = pd.read_csv("dataset/jobs.csv")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/match", methods=["POST"])
def match_jobs():
    if 'resume' not in request.files:
        return jsonify({"error": "No resume uploaded"})

    file = request.files['resume']
    resume_text = file.read().decode("utf-8", errors="ignore").lower()
    
    # Extract ALL skills from resume more intelligently
    resume_skills = set()
    
    # Look for specific skills mentioned in the CV
    skill_patterns = {
        'python': r'python',
        'c++': r'c\+\+',
        'sql': r'sql',
        'java': r'java',
        'javascript': r'javascript',
        'machine learning': r'machine learning|ml',
        'nlp': r'nlp|natural language',
        'tensorflow': r'tensorflow',
        'flask': r'flask',
        'streamlit': r'streamlit',
        'numpy': r'numpy',
        'pandas': r'pandas',
        'scikit-learn': r'scikit-learn|sklearn',
        'data preprocessing': r'data preprocessing|preprocessing',
        'classification': r'classification',
        'clustering': r'clustering',
        'regression': r'regression',
        'data structures': r'data structures|dsa',
        'algorithms': r'algorithms',
        'oop': r'oop|object oriented',
        'dbms': r'dbms|database',
        'git': r'git',
        'github': r'github',
        'jupyter': r'jupyter',
        'mysql': r'mysql',
        'sqlite': r'sqlite',
        'assembly': r'assembly',
        'document parsing': r'document parsing|parsing',
        'retrieval': r'retrieval|rag',
        'model development': r'model development|model building',
        'feature engineering': r'feature engineering',
        'supervised learning': r'supervised learning',
        # Add more as needed
    }
    
    # Check each pattern
    for skill, pattern in skill_patterns.items():
        if re.search(pattern, resume_text, re.IGNORECASE):
            resume_skills.add(skill)
    
    # Also extract individual words that might be skills
    words = re.findall(r'\b[a-zA-Z0-9\+]{2,}\b', resume_text)
    common_tech = ['python', 'c++', 'sql', 'java', 'javascript', 'html', 'css', 
                   'react', 'node', 'mongodb', 'aws', 'docker', 'kubernetes',
                   'tensorflow', 'pytorch', 'scikit', 'pandas', 'numpy', 'flask',
                   'django', 'git', 'github', 'mysql', 'postgresql', 'mongodb',
                   'excel', 'tableau', 'powerbi', 'machine learning', 'deep learning',
                   'nlp', 'computer vision', 'data science', 'analytics']
    
    for word in words:
        if word in common_tech:
            resume_skills.add(word)
    
    print(f"Found skills in resume: {resume_skills}")  # Debug print
    
    results = []
    
    for i, job in jobs.iterrows():
        # Get job skills
        job_skills_text = str(job['skills']).lower()
        
        # Parse job skills (handle commas, spaces, etc.)
        job_skills_list = []
        if ',' in job_skills_text:
            # Split by comma
            for skill in job_skills_text.split(','):
                skill = skill.strip()
                if skill:
                    job_skills_list.append(skill)
        else:
            # If no commas, try to split by spaces or keep as one
            if job_skills_text and job_skills_text != 'nan':
                job_skills_list = [job_skills_text]
        
        # Clean up skills
        cleaned_job_skills = []
        for skill in job_skills_list:
            # Remove extra spaces
            skill = ' '.join(skill.split())
            if skill and skill != 'nan':
                cleaned_job_skills.append(skill)
        
        # Find matching skills
        matching_skills = []
        for job_skill in cleaned_job_skills:
            # Direct match
            if job_skill in resume_skills:
                matching_skills.append(job_skill)
            else:
                # Check partial matches (e.g., "Machine Learning" matches "ML")
                for resume_skill in resume_skills:
                    # If job skill is contained in resume skill or vice versa
                    if (job_skill in resume_skill or resume_skill in job_skill):
                        # Avoid too generic matches
                        if len(job_skill) > 2 and len(resume_skill) > 2:
                            matching_skills.append(job_skill)
                            break
                    # Handle abbreviations (ML <-> Machine Learning)
                    elif (job_skill == 'ml' and 'machine learning' in resume_skills) or \
                         (job_skill == 'ai' and 'artificial intelligence' in resume_skills) or \
                         (job_skill == 'nlp' and 'natural language' in resume_skills):
                        matching_skills.append(job_skill)
                        break
        
        # Remove duplicates
        matching_skills = list(set(matching_skills))
        
        # Calculate match percentage
        if len(cleaned_job_skills) > 0:
            match_pct = (len(matching_skills) / len(cleaned_job_skills)) * 100
        else:
            match_pct = 0
        
        # Boost if job title contains relevant keywords
        job_title = str(job['title']).lower()
        title_keywords = ['data', 'software', 'developer', 'engineer', 'programmer', 
                         'machine learning', 'ai', 'ml', 'python', 'c++', 'sql', 
                         'database', 'analyst', 'scientist']
        
        for keyword in title_keywords:
            if keyword in job_title:
                if any(skill in resume_skills for skill in ['python', 'c++', 'sql', 'java', 'programming']):
                    match_pct += 5  # Bonus for title relevance
        
        # Cap at 100%
        match_pct = min(100, match_pct)
        
        # Round to 1 decimal
        match_pct = round(match_pct, 1)
        
        # Store job with its match info
        results.append({
            "title": job["title"],
            "skills": job["skills"],
            "location": job["location"],
            "match_score": match_pct,
            "matching_skills": ", ".join(matching_skills) if matching_skills else "None"
        })
    
    # Sort by match percentage (highest first)
    results = sorted(results, key=lambda x: x["match_score"], reverse=True)
    
    # Return top 20 instead of 10 to see more relevant jobs
    return jsonify(results[:20])

if __name__ == "__main__":
    app.run(debug=True)