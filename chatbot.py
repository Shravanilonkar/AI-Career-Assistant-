from config import TOP_K


class CareerChatbot:

    def __init__(
        self,
        llm,
        vector_store,
        analysis=None,
        interview=None
    ):

        self.llm = llm
        self.vector_store = vector_store
        self.analysis = analysis
        self.interview = interview


    def ask(self, question):

        # -----------------------------
        # Search Resume + Job Description
        # -----------------------------

        docs = self.vector_store.similarity_search(
            question,
            k=TOP_K
        )

        context = ""

        for doc in docs:

            context += doc.page_content
            context += "\n\n"


        # -----------------------------
        # Generated Analysis Context
        # -----------------------------

        analysis_context = ""

        if self.analysis:

            analysis_context = f"""
Previously Generated Resume Analysis:

{self.analysis}
"""


        # -----------------------------
        # Interview Context
        # -----------------------------

        interview_context = ""

        if self.interview:

            interview_context = f"""
Previously Generated Interview Questions:

{self.interview}
"""


        # -----------------------------
        # Prompt
        # -----------------------------

        prompt = f"""
You are an AI Career Assistant.

You help the user understand their Resume,
Job Description, Resume Analysis and Interview Questions.

Use the information provided below to answer
the user's question.

You can use:

1. Resume and Job Description
2. Previously Generated Resume Analysis
3. Previously Generated Interview Questions

If the answer is not available in any of these
sources, reply:

"I couldn't find that information in the uploaded documents."


==============================
RESUME AND JOB DESCRIPTION
==============================

{context}


==============================
RESUME ANALYSIS
==============================

{analysis_context}


==============================
INTERVIEW QUESTIONS
==============================

{interview_context}


==============================
USER QUESTION
==============================

{question}


==============================
ANSWER
==============================
"""


        # -----------------------------
        # Generate Answer
        # -----------------------------

        response = self.llm.invoke(
            prompt
        )

        return response.content



def create_chatbot(
    llm,
    vector_store,
    analysis=None,
    interview=None
):

    chatbot = CareerChatbot(
        llm,
        vector_store,
        analysis,
        interview
    )

    return chatbot