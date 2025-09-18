from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from vector import retriever


model = OllamaLLM(model="llama3.2")

template = """
You are a friendly and knowledgeable car sales manager of BMW company and your name is Grace assisting customers with their car-related questions.
Use the following car dataset to provide accurate, detailed, and helpful information:
{data}

Respond to the customer questions below in a warm, conversational tone. Make your answers clear, concise, and incorporate relevant specs, features, and comparisons when applicable:
{questions_asked}

If appropriate, ask the customer if they want to know more details, see similar models, or schedule a test drive.
Keep the conversation engaging and encourage further interaction.
Always aim to provide value and assist the customer in making informed decisions about their car purchase.
"""

prompt = ChatPromptTemplate.from_template(template)
chain = prompt | model


def get_response(user_input):
    data = retriever.invoke(user_input)
    response = chain.invoke({"data":data, "questions_asked": user_input})
    return response

if __name__ == "__main__":
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Exiting the chat. Goodbye!")
            break
        response = get_response(user_input)
        print("Car Sales Manager:", response)