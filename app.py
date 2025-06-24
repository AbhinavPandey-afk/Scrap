from flask import Flask, render_template, request, send_file
from functions import *
import warnings
import csv
import os
import re
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
warnings.filterwarnings('ignore')

# Capgemini scraping code remains same (from previous implementation)

def get_capgemini_pdfs(year, quarter):
    fiscal_url = f"https://investors.capgemini.com/en/financial-results/?fiscal-year={year}"
    print(f"Visiting Capgemini fiscal URL: {fiscal_url}")
    pdf_links = []

    try:
        response = requests.get(fiscal_url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        quarter_str = f"Q{quarter} {year}"

        for block in soup.find_all(['div', 'h3']):
            text = block.get_text(strip=True)
            if quarter_str in text:
                parent = block.find_parent()

                if parent:
                    for a_tag in parent.find_all('a', class_='button-download', href=True):
                        href = a_tag['href']
                        if href.startswith('http'):
                            full_url = href
                        else:
                            full_url = 'https://investors.capgemini.com' + href
                        pdf_links.append(full_url)
                break

        print(f"Capgemini PDFs found for Q{quarter} {year}: {pdf_links}")

    except Exception as e:
        print(f"Error while scraping Capgemini: {e}")

    return pdf_links


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        bank_name = request.form['bank']
        quarter = int(request.form['quarter'])
        year = int(request.form['year'])
        yy = str(year)[-2:]
        fy = f"{year-1}-{year}"
        prev_q = quarter - 1
        prev_y = year
        if prev_q == 0:
            prev_q = 4
            prev_y = year - 1
        pdf_links = []

        # Special handling for Capgemini
        if bank_name.lower() == 'capgemini':
            pdf_links = get_capgemini_pdfs(year, quarter)

            if not pdf_links:
                return f"No PDFs found on Capgemini site for Q{quarter} {year}"
        else:
            generated_url = get_pdf_link(bank_name, quarter, year)
            hardcoded_failed = False

            if generated_url:
                try:
                    downloaded_path = download_pdf(generated_url)
                    pdf_links.append(generated_url)
                    print("Direct PDF found from hardcoded company_sources.")
                except Exception as e:
                    print(f"Failed to download hardcoded PDF: {e}")
                    hardcoded_failed = True
            else:
                hardcoded_failed = True

            if hardcoded_failed:
                investor_urls = find_investor_url(bank_name)
                if len(investor_urls) == 0:
                    return "Investor site not found. Please try again."

                keywords = ("revenue", "results", "quarterly", "fact sheet", "Analyst Datasheet")
                for investor_url in investor_urls:
                    pdf_links += find_presentation_pdf(investor_url, keywords)

                filtered_links = []
                for link in pdf_links:
                    link_lower = link.lower()
                    if str(year) in link_lower and (f"q{quarter}" in link_lower or f"{quarter}" in link_lower):
                        filtered_links.append(link)

                if not filtered_links:
                    for link in pdf_links:
                        if str(year) in link.lower():
                            filtered_links.append(link)

                if not filtered_links:
                    filtered_links = pdf_links[:5]

                pdf_links = filtered_links

        print("Final PDFs selected for extraction:")
        for idx, link in enumerate(pdf_links):
            print(f"[PDF #{idx+1}]: {link}")

        context = ""
        for pdf_link in pdf_links:
            local_path = "presentation.pdf"
            try:
                downloaded_path = download_pdf(pdf_link)
                context += "\n" + process_file(downloaded_path)
            finally:
                delete_file(local_path)
        print(context)
        # Mphasis special queries
        if bank_name.lower() == 'mphasis':
            queries = [
                # f"What is the total revenue reported for quarter {quarter} in year {year}? Provide exact value only in the form - in $xyz (don't use commas in between) millions always print millions, no extra information needed.",
                # #f"What is the revenue of Banking and Financial Services for quarter {quarter} year {year}? Only numeric revenue in millions, no extra text, no currency.",
                # # f"What is the revenue of 'Insurance' for quarter {quarter} year {year}? Only numeric revenue in millions, no extra text, no currency.",
                # f"Fetch Banking & Financial Services Revenue for quarter {quarter} in year {year}.Only numeric revenue in millions, no extra text, no currency.",
                # f"Fetch 'Insurance' Revenue for quarter {quarter} in year {year}.Insurance revenue is just below Banking & Financial Services Revenue.Only numeric revenue in millions, no extra text, no currency."
                # f"What is the date of publishment of conference of quarter {quarter} in year {year}? Return only in DD/MM/YYYY format."
                f"What is the total revenue reported for quarter {quarter} in year {year}? Provide exact value only in the form - in $xyz millions. No commas, no extra information.",
                f"What is the revenue of the Banking and Financial Services vertical for quarter {quarter} in year {year}? Only numeric revenue in millions, no currency, no extra text.",
f"What is the revenue of the Insurance vertical for quarter {quarter} in year {year}? Only numeric revenue in millions, no extra text, no currency.",
f"What is the publish date of the quarterly report for Q{quarter} FY{year}? Return only in DD/MM/YYYY format.",


    # "What is the total revenue reported for Q{quarter} FY{yy}? Provide only the value in this exact format: in $xyz millions, no commas, no decimals, no additional text.",

    # "What is the revenue from the Banking and Financial Services (BFS) segment for Q{quarter} FY{yy}? Provide only the numeric value in millions, no currency symbols, no extra text.",

    # "What is the revenue from the Insurance segment for Q{quarter} FY{yy}? The Insurance value appears under 'Q{quarter}FY{yy} Performance by Vertical' and is located below BFS. Provide only the numeric value in millions, no extra text, no currency symbols.",

    # "What is the published date of the Q{quarter} FY{yy} earnings report? Return only in DD/MM/YYYY format."


            ]

            answers = []
            for query in queries:
                answer = query_gemini(query, context)
                print(answer)
                answers.append(answer)

            total_revenue_raw = answers[0]
            match = re.search(r'[\d,]+(?:\.\d+)?', total_revenue_raw)
            if match:
                total_revenue = float(match.group().replace(',', ''))
            else:
                total_revenue = 0.0

            bfs_raw = answers[1]
            insurance_raw = answers[2]

            # Combine BFS + Insurance using helper function from functions.py
            fs_revenue = combine_bfsi_revenues(bfs_raw, insurance_raw)

            bfs_percent_to_store = "-"  # no percentage, only absolute values
        #Persistent
        elif bank_name.lower() == 'persistent systems':
            queries = [
                # f"What is the total revenue reported for quarter {quarter} in year {year}? Provide exact value only in the form - in $xyz (don't use commas in between) millions always print millions, no extra information needed.",
                # # f"What is the revenue of BFSI (Banking Financial Services and Insurance) segment for quarter {quarter} year {year}.? Only numeric revenue in millions, no extra text, no currency.",
                # f"On the Quarterly Revenue ($M) slide, fetch the Banking, Financial Services & Insurance revenue for {quarter} FY{year}",
                # f"What is the date of publishment of conference of quarter {quarter} in year {year}? Return only in DD/MM/YYYY format."
        
  "From the Persistent Systems Q4 FY25 analyst presentation, what is the total revenue reported for Q4 of FY25? Look at the slides titled 'Quarterly Revenue ($M)', 'Financial Highlights', or 'Fact Sheet'. Return only the exact value in this format: in $XYZ.X millions — no commas, symbols, or text outside the pattern.",

  "What is the total revenue from the Banking, Financial Services, and Insurance (BFSI) segment for Q4 FY25? You will find it under the heading 'Quarterly Revenue ($M)' by segment on the same page that lists Software, Hi-Tech & Emerging Industries and Healthcare. Return only the numeric revenue in millions with one decimal precision — no text, currency symbol, or additional commentary.",

  "What is the publish date of the Q4 FY25 report or investor presentation? Check the first 2–3 slides where the header shows a copyright year or presentation month. Return the exact date in DD/MM/YYYY format only, without any extra text."

            ]

            answers = []
            for query in queries:
                answer = query_gemini(query, context)
                print(answer)
                answers.append(answer)

            total_revenue_raw = answers[0]
            match = re.search(r'[\d,]+(?:\.\d+)?', total_revenue_raw)
            if match:
                total_revenue = float(match.group().replace(',', ''))
            else:
                total_revenue = 0.0

            bfs_raw = answers[1]

            try:
                fs_revenue = float(bfs_raw)
            except:
                fs_revenue = "-"
            bfs_percent_to_store = "-"
        elif bank_name.lower() == 'capgemini':
            queries = [
        f"What is the total revenue reported for quarter {quarter} in year {year}? Provide exact value only in the form - in €xyz (don't use commas in between) millions always print millions, no extra information needed.",
        f"On Revenues by Sector, Fetch Financial Services in % of quarter {quarter} year {year}. DO NOT return growth %. Only return numeric percentage value like: 21.0",

        f"What is the date of publishment of conference of quarter {quarter} in year {year}? Return only in DD/MM/YYYY format."
            ]

            answers = []
            for query in queries:
                answer = query_gemini(query, context)
                print(answer)
                answers.append(answer)

            total_revenue_raw = answers[0]
            match = re.search(r'[\d,]+(?:\.\d+)?', total_revenue_raw)
            if match:
                total_revenue = float(match.group().replace(',', ''))
            else:
                total_revenue = 0.0

            bfs_percentage = float(answers[1])
            fs_revenue = total_revenue * bfs_percentage / 100
            bfs_percent_to_store = bfs_percentage

        elif bank_name.lower() == 'wipro':
    #         queries = [
    #     # f"What is the total revenue reported by Wipro for quarter {quarter} in year {year}? Return the exact value only in this format: in $XYZ.X millions — no commas, symbols, or extra text.",
    #     # f"What is the revenue from the BFSI (Banking, Financial Services, and Insurance) segment for Wipro in quarter {quarter} year {year}? Return only the numeric revenue in millions. No text, no currency symbols, just the number.",
    #     # f"What is the publish date of Wipro's quarterly report or analyst presentation for quarter {quarter} in year {year}? Return the date only in DD/MM/YYYY format. No extra text."

    # ]
            queries = [
    f"What is the total revenue reported by Wipro for Q4 FY{year}? Refer to the 'Results for the Quarter and Year ended March 31, {year}' or IT Services Revenues section. Return only the value in the format: in $XYZ.X millions — no commas, no extra text.",
    f"What percentage of Wipro's total revenue in Q4 FY{year} came from the Banking, Financial Services and Insurance (BFSI) sector? Refer to the Sector Mix table. Return only the number like: 34.3 — no percent symbol, no text.",
    f"What is the publish date of Wipro's Q4 FY{year} earnings report? Refer to the top of the report. Return the date only in DD/MM/YYYY format."
]


            answers = []
            for query in queries:
                answer = query_gemini(query, context)
                print(answer)
                answers.append(answer)

            total_revenue_raw = answers[0]
            match = re.search(r'[\d,]+(?:\.\d+)?', total_revenue_raw)
            total_revenue = float(match.group().replace(',', '')) if match else 0.0

            try:
                fs_revenue = float(answers[1])
                bfs_percent_to_store = "-"
            except ValueError:
                try:
                    bfs_percentage = float(answers[1])
                    fs_revenue = total_revenue * bfs_percentage / 100
                    bfs_percent_to_store = bfs_percentage
                except:
                    fs_revenue = "-"
                    bfs_percent_to_store = "-"

        elif bank_name.lower() == 'cognizant':
            queries = [
        f"What is the total revenue reported by Cognizant for quarter {quarter} of fiscal year {year}? Refer to the Results Summary or Revenue section. Return only the value in this format: in $XXXX.X millions — no commas, no extra text or symbols.",
        f"What is the revenue reported by Cognizant from the Financial Services segment in quarter {quarter} of fiscal year {year}? Refer to the Revenue by Segment section. Return only the value in millions, no text or currency symbols.",
        f"What is the publish date of Cognizant’s earnings report for quarter {quarter} of fiscal year {year}? Return only in DD/MM/YYYY format."
    ]

            answers = []
            for query in queries:
                answer = query_gemini(query, context)
                print(answer)
                answers.append(answer)

            total_revenue_raw = answers[0]
            match = re.search(r'[\d,]+(?:\.\d+)?', total_revenue_raw)
            total_revenue = float(match.group().replace(',', '')) if match else 0.0

            try:
                fs_revenue = float(answers[1])
                bfs_percent_to_store = "-"
            except:
                fs_revenue = "-"
                bfs_percent_to_store = "-"

    # Don't forget to adapt currency column as "EUR" while writing CSV

        else:
            queries = [
                f"What is the total revenue reported for quarter {quarter} in year {year}? Provide exact value only in the form- $xyz (don't use commas in between) millions always print millions, no extra information needed.",
                f"What is the percentage of contribution of BFSI or Financial Segment or Sector reported for quarter {quarter} in year {year}? No extra information needed. Always Return value like: PERCENTAGE: 23.5",
                f"What is the date of publishment of conference of quarter {quarter} in year {year}? Return in this form only - DD/MM/YYYY format no extra information needed."
            ]

            answers = []
            for query in queries:
                answer = query_gemini(query, context)
                print(answer)
                answers.append(answer)

            total_revenue_raw = answers[0]
            match = re.search(r'[\d,]+(?:\.\d+)?', total_revenue_raw)
            if match:
                total_revenue = float(match.group().replace(',', ''))
            else:
                total_revenue = 0.0

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

        csv_path = 'output/data5.csv'
        os.makedirs('output', exist_ok=True)
        file_empty = not os.path.isfile(csv_path) or os.stat(csv_path).st_size == 0

        with open(csv_path, 'a', newline='') as f:
            writer = csv.writer(f)
            if file_empty:
                writer.writerow(["Name", "Quarter", "Year", "Total Revenue", "Unit", "Currency", "BFSI Percentile", "Date", "FS Revenue"])
            writer.writerow([
                bank_name, quarter, year, total_revenue, "millions", "USD",
                bfs_percent_to_store, answers[-1], fs_revenue
            ])

        return send_file(csv_path, as_attachment=True)

    return render_template('index.html')


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
    # app.run(debug=True)
