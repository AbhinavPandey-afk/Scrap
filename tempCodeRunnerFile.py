def load_and_prepare_pdf(local_pdf_path):
    from langchain_community.document_loaders import PyPDFLoader
    from langchain.text_splitter import RecursiveCharacterTextSplitter

    # Keywords we care about
    relevant_keywords = [
        'revenue', 'financials', 'total income', 'segment results',
        'bfs', 'bfs sector', 'bfs segment', 'bfs contribution',
        'earnings', 'EBIT', 'profit', 'operating income',
        'quarterly performance', 'growth', 'currency', 'millions', 'billions'
    ]

    loader = PyPDFLoader(local_pdf_path)
    pages = loader.load_and_split()

    # Extract pages that contain any of the relevant keywords
    relevant_pages = []
    for page in pages:
        text_lower = page.page_content.lower()
        if any(keyword in text_lower for keyword in relevant_keywords):
            relevant_pages.append(page)

    # If no relevant pages found, fallback to first 5 pages
    if not relevant_pages:
        relevant_pages = pages[:5]

    # Now split into chunks for better context windowing
    splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=150)
    docs = splitter.split_documents(relevant_pages)

    # Only return first few chunks (keep file size manageable for Gemini)
    return "\n".join([doc.page_content for doc in docs[:10]])
