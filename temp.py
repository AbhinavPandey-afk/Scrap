# from flask import Flask, render_template, request, send_file
# from functions import *
# import warnings
# import csv
# import os

# app = Flask(__name__)
# warnings.filterwarnings('ignore')

# @app.route('/', methods=['GET', 'POST'])
# def index():
#     if request.method == 'POST':
#         bank_name = request.form['bank']
#         quarter = int(request.form['quarter'])
#         year = int(request.form['year'])

#         investor_urls = find_investor_url(bank_name)
#         # investor_urls = ["https://investors.franklinresources.com/investor-relations/investor-home/default.aspx"]
#         if len(investor_urls)==0:
#             return "Investor site not found. Please try again."

#         prev_q = quarter - 1
#         prev_y = year
#         if prev_q == 0:
#             prev_q = 4
#             prev_y = year - 1

#         pdf_links=[]
#         keywords = ("presentation", "earnings", "results", str(year), str(prev_y))
#         for investor_url in investor_urls:
#             pdf_links += find_presentation_pdf(investor_url, keywords)
            
#         if len(pdf_links)>5:
#             pdf_links=pdf_links[:5]
        
#         # summaries = summarize_pdf_links_parallel(pdf_links)
#         # context = ""
#         # for url in summaries:
#         #     context+=summaries[url]
#         context=""
        
#         for pdf_link in pdf_links:
#             local_path = "presentation.pdf"
#             try:
#                 # downloaded_path = download_pdf(pdf_link, local_path)
#                 downloaded_path = download_pdf(pdf_link)
#                 context += "\n" + load_and_prepare_pdf(downloaded_path)
#             finally:
#                 delete_file(local_path)
        

#         queries = [
#             # "What is the name of the bank? Provide only the name no extra information. Example:- Citigroup.",

#             f"What is the total revenue reported for quarter {quarter} in year {year}  ? Provide exact value only in the form - in $xyz(dont use commas in between) millions always print millions, no extra information needed",
#             f"What is the percentage of contribution of BFSI or Financial Segment or Sector  reported for quarter {quarter} in year {year}? Provide exact value only in the form - e.g. 20 %, no extra information needed",
#             f"What is the date of publishment of conference of quarter {quarter} in year {year} ? Return in this form only - DD/MM/YYYY format no extra information needed.",

#             f"What is the total revenue reported for quarter {prev_q} in year {prev_y}  ? Provide exact value only in the form - in $xyz(dont use commas in between) millions always print millions, no extra information needed",
#             f"What is the percentage of contribution of BFSI or Financial Segment or Sector reported for quarter {prev_q} in year {prev_y}? Provide exact value only in the form - e.g. 10 %, no extra information needed",
#             f"What is the date of publishment of conference of quarter {prev_q} in year {prev_y} ? Return in this form only - DD/MM/YYYY format no extra information needed.",

#             f"What is the total revenue reported for quarter {quarter} in year {year-1}  ? Provide exact value only in the form - in $xyz(dont use commas in between) millions always print millions, no extra information needed",
#             f"What is the percentage of contribution of BFSI or Financial Segment or Sector reported for quarter {quarter} in year {year-1}? Provide exact value only in the form - e.g. 10 %, no extra information needed",
#             f"What is the date of publishment of conference of quarter {quarter} in year {year-1} ? Return in this form only - DD/MM/YYYY format no extra information needed."
#         ]

#         row = []
#         answers=[]
#         for query in queries:
#             # response = query_deepseek(query, context)
#             answer = query_gemini(query, context)

#             print(answer)
#             # answer = response['choices'][0]['message']['content']

#             answers.append(answer)

#         csv_path = 'output/data.csv'
#         os.makedirs('output', exist_ok=True)
        
#         if os.stat(csv_path).st_size == 0:  # File is empty
#             with open(csv_path, 'a', newline='') as f:
#                 writer = csv.writer(f)
#                 writer.writerow(["Name", "Quarter", "Year", "Total Revenue", "BFSI Percentile", "Date", "FS Revenue"])
#                 writer.writerow([bank_name, quarter, year, answers[0], answers[1], answers[2],get_fs(answers[0],answers[1])])
#                 writer.writerow([bank_name, prev_q, prev_y, answers[3], answers[4], answers[5]],get_fs(answers[3],answers[4]))
#                 writer.writerow([bank_name, quarter, year - 1, answers[6], answers[7], answers[8],get_fs(answers[6],answers[7])])
#         else:
#             with open(csv_path, 'a', newline='') as f:
#                 writer = csv.writer(f)
#                 writer.writerow([bank_name, quarter, year, answers[0], answers[1], answers[2],get_fs(answers[0],answers[1])])
#                 writer.writerow([bank_name, prev_q, prev_y, answers[3], answers[4], answers[5]],get_fs(answers[3],answers[4]))
#                 writer.writerow([bank_name, quarter, year - 1, answers[6], answers[7], answers[8],get_fs(answers[6],answers[7])])



#         return send_file(csv_path, as_attachment=True)

#     return render_template('index.html')

# if __name__ == "__main__":
#     app.run(debug=True)




# from flask import Flask, render_template, request, send_file
# from functions import *
# import warnings
# import csv
# import os

# app = Flask(__name__)
# warnings.filterwarnings('ignore')

# @app.route('/', methods=['GET', 'POST'])
# def index():
#     if request.method == 'POST':
#         bank_name = request.form['bank']
#         quarter = int(request.form['quarter'])
#         year = int(request.form['year'])

#         fy = f"{year-1}-{year}"
#         prev_q = quarter - 1
#         prev_y = year
#         if prev_q == 0:
#             prev_q = 4
#             prev_y = year - 1
#         pdf_links = []

# # Try to get the hardcoded link first
#         generated_url = get_pdf_link(bank_name, quarter, year)
#         hardcoded_failed = False

#         if generated_url:
#             try:
#         # Try downloading the PDF (assuming download_pdf both downloads and validates the link)
#                 downloaded_path = download_pdf(generated_url)
#                 pdf_links.append(generated_url)
#                 print("Direct PDF found from hardcoded company_sources.")
#                 print(f"[PDF SELECTED]: {generated_url}")
#             except Exception as e:
#                 print(f"Failed to download hardcoded PDF: {e}")
#                 hardcoded_failed = True
#         else:
#             hardcoded_failed = True

# # If hardcoded link failed, move on to scraping logic
#         if hardcoded_failed:
#             investor_urls = find_investor_url(bank_name)
#             if len(investor_urls) == 0:
#                 return "Investor site not found. Please try again."

#             keywords = ("revenue", "results", "quarterly", "fact sheet", "Analyst Datasheet")
#             for investor_url in investor_urls:
#                 pdf_links += find_presentation_pdf(investor_url, keywords)

#             print("PDFs found:", pdf_links)

# # 🔧 FILTERING STRICTLY FOR QUARTER + YEAR
#         filtered_links = []
#         for link in pdf_links:
#             link_lower = link.lower()
#             if str(year) in link_lower and (f"q{quarter}" in link_lower or f"{quarter}" in link_lower):
#                 filtered_links.append(link)

# # fallback if strict filter returns nothing
#         if not filtered_links:
#             print("No strictly matching PDFs found for year & quarter, falling back to year-only filtering.")
#             for link in pdf_links:
#                 if str(year) in link.lower():
#                     filtered_links.append(link)

#         if not filtered_links:
#             print("No PDFs found after filtering, using first 5 found as backup.")
#             filtered_links = pdf_links[:5]

#         pdf_links = filtered_links

#         print("Final PDFs selected for extraction:")
#         for idx, link in enumerate(pdf_links):
#             print(f"[PDF #{idx+1}]: {link}")


#         # CONTEXT CREATION FROM SELECTED PDFs
#         context = ""
#         for pdf_link in pdf_links:
#             local_path = "presentation.pdf"
#             try:
#                 downloaded_path = download_pdf(pdf_link)
#                 # context += "\n" + load_and_prepare_pdf(downloaded_path)
#                 context += "\n" + process_file(downloaded_path)
#             finally:
#                 delete_file(local_path)

#         # Queries remain unchanged...
#         queries = [
#     # Total Revenue - Numeric part only
#     # f"What is the total revenue reported for that particular quarter {quarter} only in year {year}? Extract only the numeric value, no units or currency, no commas, provide only one value. Return like: 1234.56",

#     f"What is the total revenue reported for quarter {quarter} in year {year}  ? Provide exact value only in the form - in $xyz(dont use commas in between) millions always print millions, no extra information needed",
#     f"What is the percentage of contribution of BFSI or Financial Segment or Sector  reported for quarter {quarter} in year {year}? Provide exact value only in the form - e.g. 20.0, no extra information needed",
#     f"What is the date of publishment of conference of quarter {quarter} in year {year} ? Return in this form only - DD/MM/YYYY format no extra information needed.",
# ]


#         print(context)
#         print("-------------")
#         answers = []
#         for query in queries:
#             answer = query_gemini(query, context)
#             print(answer)
#             answers.append(answer)

#         csv_path = 'output/data2.csv'
#         os.makedirs('output', exist_ok=True)
        
#         import re

#         total_revenue = answers[0]
#         print(total_revenue)

#         # Extract the first number that appears (including comma and decimal)
#         match = re.search(r'[\d,]+(?:\.\d+)?', total_revenue)
#         if match:
#             total_revenue = match.group().replace(',', '')  # Remove commas if any
#         else:
#             total_revenue = '0'  # fallback if no number found

#         print(total_revenue)


#         # Always append, even if file empty
#         file_empty = not os.path.isfile(csv_path) or os.stat(csv_path).st_size == 0
#         with open(csv_path, 'a', newline='') as f:
#             writer = csv.writer(f)
#             if file_empty:
#                 writer.writerow(["Name", "Quarter", "Year", "Total Revenue", "Unit", "Currency", "BFSI Percentile", "Date","FS Revenue"])
#             writer.writerow([bank_name, quarter, year, total_revenue, "millions", "USD", answers[1],answers[2],get_fs(total_revenue,"millions","USD",answers[1])])


#         return send_file(csv_path, as_attachment=True)

#     return render_template('index.html')
# if __name__ == "__main__":
#     app.run(debug=True)


from flask import Flask, render_template, request, send_file
from functions import *
import warnings
import csv
import os
import re

app = Flask(__name__)
warnings.filterwarnings('ignore')

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        bank_name = request.form['bank']
        quarter = int(request.form['quarter'])
        year = int(request.form['year'])

        fy = f"{year-1}-{year}"
        prev_q = quarter - 1
        prev_y = year
        if prev_q == 0:
            prev_q = 4
            prev_y = year -  1
        pdf_links = []

        # Try to get the hardcoded link first
        generated_url = get_pdf_link(bank_name, quarter, year)
        hardcoded_failed = False

        if generated_url:
            try:
                downloaded_path = download_pdf(generated_url)
                pdf_links.append(generated_url)
                print("Direct PDF found from hardcoded company_sources.")
                print(f"[PDF SELECTED]: {generated_url}")
            except Exception as e:
                print(f"Failed to download hardcoded PDF: {e}")
                hardcoded_failed = True
        else:
            hardcoded_failed = True

        # If hardcoded link failed, move on to scraping logic
        if hardcoded_failed:
            investor_urls = find_investor_url(bank_name)
            if len(investor_urls) == 0:
                return "Investor site not found. Please try again."

            keywords = ("revenue", "results", "quarterly", "fact sheet", "Analyst Datasheet")
            for investor_url in investor_urls:
                pdf_links += find_presentation_pdf(investor_url, keywords)

            print("PDFs found:", pdf_links)

        # 🔧 FILTERING STRICTLY FOR QUARTER + YEAR
        filtered_links = []
        for link in pdf_links:
            link_lower = link.lower()
            if str(year) in link_lower and (f"q{quarter}" in link_lower or f"{quarter}" in link_lower):
                filtered_links.append(link)

        if not filtered_links:
            print("No strictly matching PDFs found for year & quarter, falling back to year-only filtering.")
            for link in pdf_links:
                if str(year) in link.lower():
                    filtered_links.append(link)

        if not filtered_links:
            print("No PDFs found after filtering, using first 5 found as backup.")
            filtered_links = pdf_links[:5]

        pdf_links = filtered_links

        print("Final PDFs selected for extraction:")
        for idx, link in enumerate(pdf_links):
            print(f"[PDF #{idx+1}]: {link}")

        # CONTEXT CREATION FROM SELECTED PDFs
        context = ""
        for pdf_link in pdf_links:
            local_path = "presentation.pdf"
            try:
                downloaded_path = download_pdf(pdf_link)
                context += "\n" + process_file(downloaded_path)
            finally:
                delete_file(local_path)

        # Updated queries with new BFSI handling
        queries = [
            f"What is the total revenue reported for quarter {quarter} in year {year}  ? Provide exact value only in the form - in $xyz(dont use commas in between) millions always print millions, no extra information needed",
            f"What is the percentage of contribution of BFSI or Financial Segment or Sector  reported for quarter {quarter} in year {year}? Provide exact value only in the form - e.g. 20.0, no extra information needed. Return value like: PERCENTAGE: 23.5",
            #f"For BFSI contribution in quarter {quarter} year {year}, check if value is directly provided. If direct revenue value is provided for both BFS and Insurance seperately then add them and return sum, return numeric revenue only without currency/commas (like: 1234.56). If only percentage is provided, return like: PERCENTAGE: 23.5. If direct value and percentage both available priortize percentage.",
            f"What is the date of publishment of conference of quarter {quarter} in year {year} ? Return in this form only - DD/MM/YYYY format no extra information needed.",
        ]

        print(context)
        print("-------------")
        answers = []
        for query in queries:
            answer = query_gemini(query, context)
            print(answer)
            answers.append(answer)

        csv_path = 'output/data3.csv'
        os.makedirs('output', exist_ok=True)

        # Extract Total Revenue
        total_revenue_raw = answers[0]
        match = re.search(r'[\d,]+(?:\.\d+)?', total_revenue_raw)
        if match:
            total_revenue = match.group().replace(',', '')
            total_revenue = float(total_revenue)
        else:
            total_revenue = 0.0

        # Extract BFSI Revenue
        bfs_raw = answers[1]
        if bfs_raw.startswith("PERCENTAGE:"):
            bfs_percentage = float(bfs_raw.split(":")[1].strip())
            fs_revenue = total_revenue * bfs_percentage / 100
            bfs_percent_to_store = bfs_percentage
        elif bfs_raw == "NOT AVAILABLE":
            fs_revenue = "-"
            bfs_percent_to_store = "-"
        else:
            fs_revenue = float(bfs_raw)
            bfs_percent_to_store = "-"

        # Write to CSV
        file_empty = not os.path.isfile(csv_path) or os.stat(csv_path).st_size == 0
        with open(csv_path, 'a', newline='') as f:
            writer = csv.writer(f)
            if file_empty:
                writer.writerow(["Name", "Quarter", "Year", "Total Revenue", "Unit", "Currency", "BFSI Percentile", "Date", "FS Revenue"])
            writer.writerow([
                bank_name, quarter, year, total_revenue, "millions", "USD",
                bfs_percent_to_store, answers[2], fs_revenue
            ])

        return send_file(csv_path, as_attachment=True)

    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)
