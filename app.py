from flask import Flask, render_template, request, send_file
from functions import *
import warnings
import csv
import os

app = Flask(__name__)
warnings.filterwarnings('ignore')

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        bank_name = request.form['bank']
        quarter = int(request.form['quarter'])
        year = int(request.form['year'])

        investor_url = find_investor_url(bank_name)
        if not investor_url:
            return "Investor site not found. Please try again."

        prev_q = quarter - 1
        prev_y = year
        if prev_q == 0:
            prev_q = 4
            prev_y = year - 1

        keywords = ("presentation", "earnings", "results", str(year), str(prev_y))
        pdf_links = find_presentation_pdf(investor_url, keywords)

        context = ""
        for pdf_link in pdf_links:
            local_path = "presentation.pdf"
            try:
                # downloaded_path = download_pdf(pdf_link, local_path)
                downloaded_path = download_pdf(pdf_link)
                context += "\n" + load_and_prepare_pdf(downloaded_path)
            finally:
                delete_file(local_path)

        queries = [
            "What is the name of the bank? Provide only the name no extra information. Example:- Citigroup.",

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

        row = []
        answers=[]
        for query in queries:
            response = query_deepseek(query, context)
            # print(response)
            answer = response['choices'][0]['message']['content']
            # row.append(answer)
            answers.append(answer)

        csv_path = 'output/data.csv'
        os.makedirs('output', exist_ok=True)
        
        if os.stat(csv_path).st_size == 0:  # File is empty
            with open(csv_path, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["Name", "Quarter", "Year", "Revenue", "Net Income", "Date"])
                writer.writerow([bank_name, quarter, year, answers[1], answers[2], answers[3]])
                writer.writerow([bank_name, prev_q, prev_y, answers[4], answers[5], answers[6]])
                writer.writerow([bank_name, quarter, year - 1, answers[7], answers[8], answers[9]])
        else:
            with open(csv_path, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([bank_name, quarter, year, answers[1], answers[2], answers[3]])
                writer.writerow([bank_name, prev_q, prev_y, answers[4], answers[5], answers[6]])
                writer.writerow([bank_name, quarter, year - 1, answers[7], answers[8], answers[9]])



        return send_file(csv_path, as_attachment=True)

    return render_template('index.html')

if __name__ == "__main__":
    app.run()
