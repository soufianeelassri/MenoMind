from models.prompt_templates import classification_prompt

def needs_retrieval(query, llm):

    response = llm.invoke(classification_prompt.format(query=query))
    return response.content.strip().lower().startswith("y")