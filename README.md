# MenoMind: A Multimodal RAG System for Menopause Information

## Overview

MenoMind is a Multimodal Retrieval-Augmented Generation (RAG) system designed to provide users with accurate and easily understandable information about menopause. It leverages document processing, summarization, and retrieval techniques to answer user questions effectively, drawing insights from text, tables, and images within relevant documents.

## Key Features

*   **Multimodal Data Processing**: Extracts and integrates medical insights from diverse sources ((e.g., research PDFs)).
*   **Intelligent Summarization:** Condenses complex information into concise and relevant summaries using Large Language Models (LLMs).
*   **Efficient Retrieval:** Employs a multi-vector retriever to quickly identify the most relevant information from a vast knowledge base.
*   **User-Friendly Interface:** Offers an interactive chatbot interface via Chainlit for seamless information access.
*   **Scalable Architecture:** Designed for easy expansion with new data sources and features.


## Components

*   **`scraping/article_scraper.py`:** Scrapes articles from web pages and downloads them as PDFs.
*   **`processors/`:** Handles PDF parsing, image cleaning, and text splitting.
*   **`summarization/`:** Summarizes text, tables and images for optimized information retrieval.
*   **`retrieval/multi_vector_indexer.py`:** Builds the multi-vector retriever for efficient document retrieval based on user queries.
*   **`retriever_pipeline.py`:** Orchestrates data extraction, preprocessing, summarization, and vector database indexing.
*   **`main.py`:**  The core application. It uses Chainlit for the chat interface, Langchain for RAG and interacts with the LLM.

## Getting Started

### Prerequisites

*   Python 3.7+
*   A Google Gemini API key
*   A Hugging Face API token (if required by specific components)

### Installation

1.  **Clone the repository:**

    ```bash
    git clone <repository_url>
    cd menomind
    ```

2.  **Create a virtual environment:**

    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Linux/macOS
    .venv\Scripts\activate  # On Windows
    ```

3.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up environment variables:**

    *   Create a `.env` file in the root directory.
    *   Add the following variables:

        ```
        GEMINI_API_KEY=<your_gemini_api_key>
        HF_API_TOKEN=<your_huggingface_api_token>
        ```

        Replace `<your_gemini_api_key>` and `<your_huggingface_api_token>` with your actual API keys.

### Usage

1.  **Run the retriever pipeline:**

    ```bash
    python retriever_pipeline.py
    ```

    This will process the PDF documents, generate summaries, and create the Chroma database.

2.  **Run the main application:**

    ```bash
    chainlit run main.py
    ```

    This will start the Chainlit application, allowing you to interact with MenoMind.

3.  **Access the application:**

    Open your web browser and navigate to the URL provided by Chainlit (`http://localhost:8000`).

## Web Scraping (Optional)

The `article_scraper.py` script can be used to scrape articles related to menopause from the web. Configure the script with the target website URL and output directory before running.

## Contributing

Contributions are welcome! Please submit a pull request with your proposed changes.