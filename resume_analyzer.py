
def analyze_resume(chatbot, resume_text, job_text):
    """
    Analyze resume directly against the job description.
    Avoid unnecessary FAISS retrieval for this operation.
    """

    prompt = f"""
You are an experienced HR recruiter and ATS specialist.

Analyze the candidate's resume against the job description.

RESUME:
{resume_text[:12000]}

JOB DESCRIPTION:
{job_text[:12000]}

Provide the analysis in the following format:

1. RESUME SUMMARY
Summarize the candidate's education, experience and skills.

2. ATS SCORE (OUT OF 100)
Give an estimated score based on the job requirements.
Briefly explain the score.

3. MATCHING SKILLS
List skills present in both the resume and job description.

4. MISSING SKILLS
List important job requirements missing from the resume.

5. STRENGTHS
Identify the candidate's strongest qualifications.

6. WEAKNESSES
Identify gaps relevant to this particular job.

7. RESUME IMPROVEMENT SUGGESTIONS
Give practical suggestions to improve the resume.

8. CAREER ROADMAP FOR NEXT 3 MONTHS
Provide a short, practical monthly learning plan.

IMPORTANT:
- Use only information from the supplied documents.
- Do not invent qualifications, experience or projects.
- Keep the answer concise and professional.
- Clearly distinguish between skills demonstrated and skills merely mentioned.
"""

    response = chatbot.llm.invoke(prompt)

    return response.content
