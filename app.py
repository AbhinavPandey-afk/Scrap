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

        investor_urls = find_investor_url(bank_name)
        # investor_urls = ["https://investors.franklinresources.com/investor-relations/investor-home/default.aspx"]
        if len(investor_urls)==0:
            return "Investor site not found. Please try again."

        prev_q = quarter - 1
        prev_y = year
        if prev_q == 0:
            prev_q = 4
            prev_y = year - 1

        pdf_links=[]
        keywords = ("presentation", "earnings", "results", str(year), str(prev_y))
        for investor_url in investor_urls:
            pdf_links += find_presentation_pdf(investor_url, keywords)
            
        if len(pdf_links)>20:
            pdf_links=pdf_links[:20]
        
        summaries = summarize_pdf_links(pdf_links)
        
        context = ""
        for url in summaries:
            context+=summaries[url]

        queries = [
            # "What is the name of the bank? Provide only the name no extra information. Example:- Citigroup.",

            f"What is the total revenue reported for quarter {quarter} in year {year}  ? Provide exact value only in the form - in xyz(dont use commas in between) millions, no extra information needed",
            f"What is the percentage of contribution of BFSI or Financial Segment or Sector  reported for quarter {quarter} in year {year}? Provide exact value only in the form - e.g. 20 %, no extra information needed",
            f"What is the date of publishment of conference of quarter {quarter} in year {year} ? Return in this form only - DD/MM/YYYY format no extra information needed.",

            f"What is the total revenue reported for quarter {prev_q} in year {prev_y}  ? Provide exact value only in the form - in xyz(dont use commas in between) millions, no extra information needed",
            f"What is the percentage of contribution of BFSI or Financial Segment or Sector reported for quarter {prev_q} in year {prev_y}? Provide exact value only in the form - e.g. 10 %, no extra information needed",
            f"What is the date of publishment of conference of quarter {prev_q} in year {prev_y} ? Return in this form only - DD/MM/YYYY format no extra information needed.",

            f"What is the total revenue reported for quarter {quarter} in year {year-1}  ? Provide exact value only in the form - in xyz(dont use commas in between) millions, no extra information needed",
            f"What is the percentage of contribution of BFSI or Financial Segment or Sector reported for quarter {quarter} in year {year-1}? Provide exact value only in the form - e.g. 10 %, no extra information needed",
            f"What is the date of publishment of conference of quarter {quarter} in year {year-1} ? Return in this form only - DD/MM/YYYY format no extra information needed."
        ]

        row = []
        answers=[]
        for query in queries:
            response = query_deepseek(query, context)
            
            print(response)
            answer = response['choices'][0]['message']['content']

            answers.append(answer)

        csv_path = 'output/data.csv'
        os.makedirs('output', exist_ok=True)
        
        if os.stat(csv_path).st_size == 0:  # File is empty
            with open(csv_path, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["Name", "Quarter", "Year", "Total Revenue", "BFSI Percentile", "Date", "FS Revenue"])
                writer.writerow([bank_name, quarter, year, answers[0], answers[1], answers[2],get_fs(answers[0],answers[1])])
                writer.writerow([bank_name, prev_q, prev_y, answers[3], answers[4], answers[5]],get_fs(answers[3],answers[4]))
                writer.writerow([bank_name, quarter, year - 1, answers[6], answers[7], answers[8],get_fs(answers[6],answers[7])])
        else:
            with open(csv_path, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([bank_name, quarter, year, answers[0], answers[1], answers[2],get_fs(answers[0],answers[1])])
                writer.writerow([bank_name, prev_q, prev_y, answers[3], answers[4], answers[5]],get_fs(answers[3],answers[4]))
                writer.writerow([bank_name, quarter, year - 1, answers[6], answers[7], answers[8],get_fs(answers[6],answers[7])])



        return send_file(csv_path, as_attachment=True)

    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)