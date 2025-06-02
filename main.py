from functions import *
import warnings
warnings.filterwarnings('ignore')

row = []
investor_url = input("Enter Investor Site Link:")
keywords = ("presentation", "earnings", "q1", "results")  # Add more if needed
pdf_link = find_presentation_pdf(investor_url, keywords)
# row.append(pdf_link)
if pdf_link:
    print("📄 PDF Link:", pdf_link)
    pdf_url = pdf_link  # Replace with actual URL
    local_path = "presentation.pdf"
    try:
        downloaded_path = download_pdf(pdf_url, local_path)
        context = load_and_prepare_pdf(downloaded_path)

        # Run financial queries
        queries = [
            "What is the name of the bank? Provide only the name no extra information.",
            "Which quarter is the data of ? Return in this form only - e.g. 1Q 2052  no extra information needed",
            "What is the total revenue reported? Provide exact value only in the form - e.g. $ 1.0 Billion",
            "What is the net income reported? Provide exact value only in the form - e.g. $ 1.0 Billion",
            "What is the date of publishment of these results? Return in this form only - DD/MM/YYYY format no extra information needed."
        ]

        for query in queries:
            response = query_deepseek(query, context)
            # print(response)
            answer = response['choices'][0]['message']['content']
            row.append(answer)
            print(f"Q: {query}\nA: {answer}\n")

    finally:
        delete_file(local_path)  # Always clean up the file


else:
    print("No PDF Found!!")


# Appending data in the file
import csv 

with open('data.csv', 'a', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(row)  
