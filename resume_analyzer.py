def analyze_resume(chatbot):
    """
    Analyze Resume and Job Description.
    """

    prompt = """
You are an expert HR Recruiter.

Analyze the uploaded Resume and Job Description.

Give your answer in the following format.

Resume Summary

ATS Score (Out of 100)

Matching Skills

Missing Skills

Strengths

Weaknesses

Resume Improvement Suggestions

Career Roadmap for next 3 months

Keep the answer short and professional.
"""

    answer = chatbot.ask(prompt)

    return answer