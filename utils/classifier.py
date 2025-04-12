def needs_retrieval(query, llm):
    classification_prompt = f"""
        Determine whether this query requires external information to be answered or can be answered with general knowledge. 

        If the query needs document retrieval to be answered properly, respond with "yes". Otherwise, respond with "no".

        Query: {query}
        Response:
    """
    response = llm.invoke(classification_prompt)
    return response.content.lower().startswith("y")
