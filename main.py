import os
import chainlit as cl
from dotenv import load_dotenv
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI
from datetime import datetime

load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")

embedding_model = HuggingFaceEmbeddings(model_name='sentence-transformers/all-mpnet-base-v2')
vectorstore = Chroma(
    collection_name="mm_rag_vectorstore",
    embedding_function=embedding_model,
    persist_directory="./outputs/chroma_db"
)
retriever = vectorstore.as_retriever(search_kwargs={"k": 5})

llm = ChatGoogleGenerativeAI(
    api_key=gemini_api_key,
    model="gemini-2.0-flash-lite",
    temperature=0.3,
)

prompt_template = """
    You are MenoMind, a friendly assistant helping users with questions about menopause. Your goal is to provide answers that are medically accurate, clear, and easy to understand. You should always reason through the question before providing an answer.

    Your expertise includes:
    - Perimenopause, menopause, and postmenopause
    - Symptoms (hot flashes, mood changes, sleep disturbances, irregular periods)
    - Lifestyle advice (nutrition, exercise, mental health, alternative therapies)
    - Medical treatments (hormone therapy, non-hormonal options)
    - Emotional support

    Instructions:
    1. **Reason through the question** by breaking it down step by step.
    2. Use your knowledge and available context to logically derive an answer.
    3. **Make sure your reasoning is clear** before you give your final answer.
    4. Once you've reasoned through the problem, provide a concise and clear answer.
    5. If the context doesn't provide enough information, use your general knowledge to fill in the gaps.
    6. Communicate your thoughts as you go along, but **do not refer to the context or your reasoning explicitly in your final answer**.

    Context:
    {context}

    Question:
    {question}

    Final Answer:
"""

prompt = PromptTemplate(
    template=prompt_template,
    input_variables=["context", "question"]
)

qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=retriever,
    chain_type="stuff",
    chain_type_kwargs={"prompt": prompt},
    return_source_documents=False,
)

@cl.on_message
async def main(message: cl.Message):
    query = message.content

    start_time = datetime.now()

    context = retriever.invoke(query)

    result = qa_chain.invoke({"query": query, "context": context})

    response_message = f"{result['result']}"

    end_time = datetime.now()
    response_time = (end_time - start_time).total_seconds()

    response_message += f"\n\n🕒{response_time:.2f} seconds"
    await cl.Message(content=response_message).send()