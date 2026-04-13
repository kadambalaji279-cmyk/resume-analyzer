import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

JOB_ROLES = {
    "data scientist": ["python", "machine learning", "pandas", "numpy", "data analysis"],
    "data analyst": ["excel", "sql", "python", "power bi", "tableau"],
    "machine learning engineer": ["python", "tensorflow", "pytorch", "ml", "deep learning"],
    "ai engineer": ["python", "nlp", "deep learning", "tensorflow"],
    "software engineer": ["java", "python", "c++", "dsa"],
    "web developer": ["html", "css", "javascript", "react"],
    "frontend developer": ["html", "css", "javascript", "react"],
    "backend developer": ["nodejs", "python", "java", "api"],
    "full stack developer": ["html", "css", "javascript", "nodejs", "react"],
    "android developer": ["java", "kotlin", "android"],
    "ios developer": ["swift", "ios"],
    "cloud engineer": ["aws", "azure", "gcp"],
    "devops engineer": ["docker", "kubernetes", "ci/cd"],
    "cybersecurity analyst": ["network security", "encryption", "linux"],
    "database administrator": ["sql", "mysql", "postgresql"],
    "business analyst": ["excel", "communication", "analysis"],
    "qa engineer": ["testing", "automation", "selenium"],
    "game developer": ["unity", "c#", "game design"],
    "embedded engineer": ["c", "microcontroller"],
    "blockchain developer": ["solidity", "ethereum"],
    "data engineer": ["spark", "hadoop", "etl"],
    "nlp engineer": ["nlp", "text processing", "spacy"]
}


def clean(text):
    text = text.lower()
    text = re.sub(r'[^a-zA-Z ]', '', text)
    return text


def analyze_resume(resume, job_desc, job_role):

    resume_clean = clean(resume)

    job_text = clean(job_desc) if job_desc.strip() else " ".join(JOB_ROLES.get(job_role, []))

    vectorizer = TfidfVectorizer(stop_words="english")
    vectors = vectorizer.fit_transform([resume_clean, job_text])

    similarity_score = cosine_similarity(vectors[0:1], vectors[1:2])[0][0] * 100

    required_skills = JOB_ROLES.get(job_role, [])

    matched = []
    missing = []

    # ✔ FIXED MATCH LOGIC (important improvement)
    for skill in required_skills:
        if skill.lower() in resume_clean:
            matched.append(skill)
        else:
            missing.append(skill)

    skill_score = (len(matched) / len(required_skills)) * 100 if required_skills else 0

    sections = ["education", "skills", "experience", "projects"]
    found_sections = [s for s in sections if s in resume_clean]
    section_score = (len(found_sections) / len(sections)) * 100

    final_score = round(
        (0.5 * similarity_score) +
        (0.3 * skill_score) +
        (0.2 * section_score),
        2
    )

    status = "Selected ✅" if final_score > 75 else "Needs Improvement ⚠️" if final_score > 50 else "Rejected ❌"

    best_roles = []

    for role, skills in JOB_ROLES.items():
        match_count = len([s for s in skills if s in resume_clean])
        score = (match_count / len(skills)) * 100

        if score > 15:
            best_roles.append({
                "name": role,
                "score": round(score, 2),
                "reason": f"You match {match_count}/{len(skills)} skills"
            })

    best_roles = sorted(best_roles, key=lambda x: x["score"], reverse=True)[:5]

    suggestions = []

    if missing:
        suggestions.append(f"Improve skills: {', '.join(missing)}")

    if "projects" not in resume_clean:
        suggestions.append("Add projects section")

    if final_score < 60:
        suggestions.append("Improve ATS keywords")

    if len(found_sections) == 0:
        suggestions.append("Add proper resume structure")

    return {
        "role": job_role,
        "score": final_score,
        "similarity_score": round(similarity_score, 2),
        "skill_score": round(skill_score, 2),
        "section_score": round(section_score, 2),
        "matched": matched,
        "missing": missing,
        "sections": found_sections,
        "status": status,
        "best_roles": best_roles,
        "suggestions": suggestions
    }