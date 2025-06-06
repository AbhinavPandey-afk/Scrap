
from functions import *
import warnings
warnings.filterwarnings('ignore')

row = []
bank_input = input("Enter Bank Name: ")
investor_url = find_investor_url(bank_input)

if not investor_url:
    print("Investor site not found. Exiting.")
    exit()
quarter = int(input("Enter 1/2/3/4: "))
year = int(input("Enter year: "))

prev_q=quarter-1
prev_y=year
if prev_q==0:
    prev_q=4
    prev_y=year-1


keywords = ("presentation", "earnings", "results",str(year),str(prev_y))  # Add more if needed
pdf_links = find_presentation_pdf(investor_url, keywords)
context=""
# row.append(pdf_link)
for pdf_link in  pdf_links:
    # print("📄 PDF Link:", pdf_link)
    pdf_url = pdf_link  # Replace with actual URL
    local_path = "presentation.pdf"
    try:
        downloaded_path = download_pdf(pdf_url, local_path)
        context += "/n"+load_and_prepare_pdf(downloaded_path)
    finally:
        delete_file(local_path)  # Always clean up the file
# print(context)
queries = [
            "What is the name of the bank? Provide only the name no extra information.",

            f"What is the total revenue reported for quarter {quarter} in year {year}  ? Provide exact value only in the form - e.g. $ 1.0 Billion, no extra information needed",
            f"What is the net income reported for quarter {quarter} in year {year}? Provide exact value only in the form - e.g. $ 1.0 Billion, no extra information needed",
            f"What is the date of publishment of conference of quarter {quarter} in year {year} ? Return in this form only - DD/MM/YYYY format no extra information needed.",

            f"What is the total revenue reported for quarter {prev_q} in year {prev_y}  ? Provide exact value only in the form - e.g. $ 1.0 Billion, no extra information needed",
            f"What is the net income reported for quarter {prev_q} in year {prev_y}? Provide exact value only in the form - e.g. $ 1.0 Billion, no extra information needed",
            f"What is the date of publishment of conference of quarter {prev_q} in year {prev_y} ? Return in this form only - DD/MM/YYYY format no extra information needed.",

            f"What is the total revenue reported for quarter {quarter} in year {year-1}  ? Provide exact value only in the form - e.g. $ 1.0 Billion, no extra information needed",
            f"What is the net income reported for quarter {quarter} in year {year-1}? Provide exact value only in the form - e.g. $ 1.0 Billion, no extra information needed",
            f"What is the date of publishment of conference of quarter {quarter} in year {year-1} ? Return in this form only - DD/MM/YYYY format no extra information needed."
        ]

for query in queries:
    response = query_deepseek(query, context)
    # print(response)
    answer = response['choices'][0]['message']['content']
    row.append(answer)
    print(f"Q: {query}\nA: {answer}\n")



# Appending data in the file
# import csv 

# with open('data.csv', 'a', newline='') as file:
#     writer = csv.writer(file)
#     writer.writerow(row)