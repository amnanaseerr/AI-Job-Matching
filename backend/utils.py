import re
import nltk
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re

# 1. Extract skills from a text (resume)
def extract_skills(text):
    """
    Extracts skills from a given text.
    You can extend the skills list based on your dataset or requirements.
    """
    text = text.lower()
    skills_list = [
        "python", "java", "c++", "javascript", "sql",
        "machine learning", "data analysis", "nlp", "flask",
        "django", "react", "aws", "docker", "html", "css"
    ]
    found_skills = [skill for skill in skills_list if skill in text]
    return ', '.join(found_skills)

# 2. Similarity score between candidate skills and job skills
def similarity_score(candidate_skills, job_skills):
    """
    Simple similarity score: number of matching skills / total skills
    """
    candidate_set = set([s.strip().lower() for s in candidate_skills.split(',')])
    job_set = set([s.strip().lower() for s in job_skills])
    if not candidate_set or not job_set:
        return 0
    return len(candidate_set & job_set) / len(job_set)
# Download stopwords (first run only)
nltk.download('stopwords')
stop_words = set(stopwords.words('english'))

def extract_skills(text):
    text = text.lower()
    words = re.findall(r'\b[a-zA-Z]{2,}\b', text)
    skills = [w for w in words if w not in stop_words]
    return " ".join(skills)

def similarity_score(job_skills, candidate_skills):
    vectorizer = TfidfVectorizer()
    tfidf = vectorizer.fit_transform([job_skills, candidate_skills])
    score = cosine_similarity(tfidf[0:1], tfidf[1:2])
    return float(score[0][0])

def extract_skills(text):
    # Your code to extract skills from resume text
    return ["Python", "SQL", "ML"]  # example

def similarity_score(candidate_skills, job_skills):
    # Compare two skill lists and return similarity score
    return len(set(candidate_skills).intersection(set(job_skills)))


from PyPDF2 import PdfReader
from docx import Document

def extract_text_from_file(file_path):
    if file_path.endswith('.pdf'):
        reader = PdfReader(file_path)
        text = ''
        for page in reader.pages:
            text += page.extract_text()
        return text
    elif file_path.endswith('.docx'):
        doc = Document(file_path)
        text = ''
        for para in doc.paragraphs:
            text += para.text + '\n'
        return text
    else:
        raise ValueError("Only PDF or DOCX files are supported")