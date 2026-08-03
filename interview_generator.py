def generate_interview_questions(chatbot):
    """
    Generate Interview Questions.
    """

    prompt = """
Based on the uploaded Resume and Job Description,

Generate

1. Five HR Interview Questions

2. Five Technical Interview Questions

3. Two Project Based Questions

Do not provide answers.
"""

    answer = chatbot.ask(prompt)

    return answer