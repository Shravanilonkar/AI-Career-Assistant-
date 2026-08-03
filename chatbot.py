from config import TOP_K


class CareerChatbot:

    def __init__(self, llm, vector_store):

        self.llm = llm
        self.vector_store = vector_store

    def ask(self, question):

        docs = self.vector_store.similarity_search(
            question,
            k=TOP_K
        )

        context = ""

        for doc in docs:

            context += doc.page_content
            context += "\n\n"

        prompt = f"""
You are an AI Career Assistant.

Answer ONLY using the Resume and Job Description.

If the answer is not present,
reply:

"I couldn't find that information in the uploaded documents."

Resume and Job Description:

{context}

Question:

{question}

Answer:
"""

        response = self.llm.invoke(prompt)

        return response.content


def create_chatbot(llm, vector_store):

    chatbot = CareerChatbot(
        llm,
        vector_store
    )

    return chatbot