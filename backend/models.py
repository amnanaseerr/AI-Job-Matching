from utils import similarity_score

def rank_candidates(job, candidates):
    scores = []
    for _, candidate in candidates.iterrows():
        skill_sim = similarity_score(job['required_skills'], candidate['skills'])
        experience_match = min(candidate['experience_years'], job['required_experience']) / job['required_experience']
        scores.append({
            'candidate_name': candidate['name'],
            'score': round(0.6*skill_sim + 0.4*experience_match, 2)
        })
    ranked = sorted(scores, key=lambda x: x['score'], reverse=True)
    return ranked