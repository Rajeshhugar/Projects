
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.runnables.history import RunnableWithMessageHistory
from db_utils import get_db_connection
from chroma_utils import get_vector_store
import os

# Set your OpenAI API key
os.environ["OPENAI_API_KEY"] = "YOUR_OPENAI_API_KEY"

llm = ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0.2)

def get_retriever():
    return get_vector_store().as_retriever()

contextualize_q_system_prompt = """
Given a chat history and the latest user question 
which might reference context in the chat history, 
formulate a standalone question which can be understood 
without the chat history. Do NOT answer the question, 
just reformulate it if needed and otherwise return it as is.
"""

contextualize_q_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", contextualize_q_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)

history_aware_retriever = create_history_aware_retriever(
    llm,
    get_retriever(),
    contextualize_q_prompt
)

qa_system_prompt = """
Answer the user's questions based on the below context.
If the context doesn't contain the answer, say that you don't know.

{context}
"""

qa_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", qa_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)

question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)

rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

def get_session_history(session_id):
    # This is a placeholder for a proper session management system.
    # In a real application, you would use a database or a cache to store session history.
    if not hasattr(get_session_history, "history"):
        get_session_history.history = {}
    if session_id not in get_session_history.history:
        get_session_history.history[session_id] = []
    return get_session_history.history[session_id]

conversational_rag_chain = RunnableWithMessageHistory(
    rag_chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="chat_history",
    output_messages_key="answer",
)
