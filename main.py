from functions import *
import warnings
warnings.filterwarnings('ignore')


investor_url = input("Enter Investor Site Link:")
keywords = ("presentation", "earnings", "q1", "results")  # Add more if needed
pdf_link = find_presentation_pdf(investor_url, keywords)
if pdf_link:
    print("📄 PDF Link:", pdf_link)
    pdf_url = pdf_link  # Replace with actual URL
    local_path = "presentation.pdf"
    try:
        downloaded_path = download_pdf(pdf_url, local_path)
        context = load_and_prepare_pdf(downloaded_path)

        # Run financial queries
        queries = [
            "What is the total revenue reported? Provide exact value only",
            "What is the net income reported? Provide exact value only",
        ]

        for query in queries:
            response = query_deepseek(query, context)
            # print(response)
            answer = response['choices'][0]['message']['content']
            print(f"Q: {query}\nA: {answer}\n")

    finally:
        delete_file(local_path)  # Always clean up the file


else:
    print("No PDF Found!!")





