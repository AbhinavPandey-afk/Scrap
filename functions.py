from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urljoin
import time
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
COMPANY_NAMES = [
    "Wipro",
    "TCS",
    "Infosys",
    "Accenture",
    "Capgemini",
    "Cognizant",
    "Techmahindra",
    "LTIMindtree",
    "Mphasis",
    "Birlasoft",
    "Coforge",
    "Zensar",
    "Persistent Systens"
]



import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin


def extract_pdfs_from_api(base_url, keywords):
    print("Trying known API endpoints...")
    api_paths = [
        "/api/documents?limit=100&sort=Date desc",
        "/api/eventitems?limit=100&sort=Date desc",
        "/api/pressreleases?limit=100&sort=Date desc"
    ]

    headers = {"User-Agent": "Mozilla/5.0"}
    results = []

    for path in api_paths:
        full_url = urljoin(base_url, path)
        try:
            res = requests.get(full_url, headers=headers, timeout=10)
            if res.status_code == 200 and res.headers.get("Content-Type", "").startswith("application/json"):
                data = res.json()
                for item in data.get("data", []):
                    file_url = item.get("fileUrl") or item.get("url", "")
                    title = item.get("title", "")
                    if file_url.endswith(".pdf") and any(k in title.lower() or k in file_url.lower() for k in keywords):
                        results.append(urljoin(base_url, file_url))
        except Exception:
            continue

    return list(set(results))


def extract_pdfs_static(url, keywords):
    print(f"Scraping static content at {url}...")
    results = []
    try:
        html = requests.get(url, timeout=10).text
        soup = BeautifulSoup(html, "html.parser")

        # 1. Anchor tags with href
        for link in soup.find_all("a", href=True):
            href = link['href']
            text = link.get_text().lower()
            if ".pdf" in href.lower() and any(k in href.lower() or k in text for k in keywords):
                results.append(urljoin(url, href))

        # 2. onclick attributes with .pdf
        for tag in soup.find_all(attrs={"onclick": True}):
            onclick = tag.get("onclick", "")
            matches = re.findall(r"""['"]([^'"]+\.pdf)['"]""", onclick)
            for match in matches:
                if any(k in match.lower() for k in keywords):
                    results.append(urljoin(url, match))

        # 3. embedded PDFs in iframe or embed
        for tag in soup.find_all(["iframe", "embed"]):
            src = tag.get("src", "")
            if ".pdf" in src.lower() and any(k in src.lower() for k in keywords):
                results.append(urljoin(url, src))

    except Exception as e:
        print(f"Error during static scrape: {e}")

    return list(set(results))


def crawl_and_find_pdfs(base_url, keywords, max_pages=5):
    print("Exploring internal links to find PDFs...")
    visited = set()
    pdfs = set()

    try:
        html = requests.get(base_url, timeout=10).text
        soup = BeautifulSoup(html, "html.parser")

        # Find likely internal links
        candidate_links = []
        for a in soup.find_all("a", href=True):
            href = a['href']
            text = a.get_text().lower()
            full_link = urljoin(base_url, href)
            if any(k in href.lower() or k in text for k in keywords):
                candidate_links.append(full_link)

        # Visit top matching links
        for link in list(set(candidate_links))[:max_pages]:
            if link not in visited:
                visited.add(link)
                pdfs.update(extract_pdfs_static(link, keywords))

    except Exception as e:
        print(f"Error while crawling: {e}")

    return list(pdfs)


def find_presentation_pdf(bank_url, keywords=("presentation", "earnings", "results","")):
    print(f"Checking: {bank_url}")
    
    # Stage 1: API
    api_results = extract_pdfs_from_api(bank_url, keywords)
    if api_results:
        print(f"Found {len(api_results)} PDFs via API")
        return api_results
    
    # Stage 2: Static scrape
    static_results = extract_pdfs_static(bank_url, keywords)
    if static_results:
        print(f"Found {len(static_results)} PDFs via static HTML")
        return static_results
    
    # Stage 3: Crawl internal links
    crawl_results = crawl_and_find_pdfs(bank_url, keywords)
    if crawl_results:
        print(f"Found {len(crawl_results)} PDFs by crawling internal links")
        return crawl_results

    print("No PDFs found using current methods.")
    return []
''' Function to convert link to text and get Revenue'''

import requests
import os
# from langchain.document_loaders import PyPDFLoader
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter


import tempfile

def download_pdf(pdf_url):
    response = requests.get(pdf_url)
    if response.status_code == 200:
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        temp_file.write(response.content)
        temp_file.close()
        return temp_file.name
    else:
        raise Exception(f"Failed to download PDF. Status code: {response.status_code}")


# Load and prepare context from PDF
def load_and_prepare_pdf(local_pdf_path):
    loader = PyPDFLoader(local_pdf_path)
    pages = loader.load_and_split()
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    docs = splitter.split_documents(pages)
    return "\n".join([doc.page_content for doc in docs[:5]])


def delete_file(file_path):
    try:
        os.remove(file_path)
    except Exception as e:
        print(f"Could not delete file: {e}")


# DeepSeek API call function
# def query_deepseek(prompt, context):
#     api_url = "https://openrouter.ai/api/v1/chat/completions"
#     headers = {
#         "Authorization": "Bearer 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",  # replace with actual key
#         "Content-Type": "application/json"
#     }
#     payload = {
#         "model": "deepseek/deepseek-r1-0528:free",
#         # "model":"meta-llama/llama-3.3-8b-instruct:free",
#         "messages": [
#             {"role": "system", "content": "You are a financial analyst extracting precise numerical data."},
#             {"role": "user", "content": f"Context: {context}\n\nQuestion: {prompt}"}
#         ],
#         "temperature": 0.5
#     }

#     # response = requests.post(api_url, headers=headers, json=payload)
#     # return response.json()
#     try:
#         response = requests.post(api_url, headers=headers, json=payload)
#         response.raise_for_status()  # Raises HTTPError for bad responses (4xx, 5xx)
#         return response.json()

#     except requests.exceptions.HTTPError as e:
#         print(f"HTTP error occurred: {e}")
#         return {"error": str(e), "details": response.text}

#     except requests.exceptions.RequestException as e:
#         print(f"Request failed: {e}")
#         return {"error": str(e)}

#     except Exception as e:
#         print(f"Unexpected error: {e}")
#         return {"error": str(e)}
""" Gemini """
import google.generativeai as genai

# Set your Gemini API key (store securely in real apps)
genai.configure(api_key="AIzaSyDlucjlAIzx0Z63KZUrvtNtFZbCroI8u_U")

def query_gemini(prompt, context):
    # Combine context and prompt just like your previous logic
    full_prompt = (
        "You are a financial analyst extracting precise numerical data.\n\n"
        f"Context: {context}\n\n"
        f"Question: {prompt}"
    )

    try:
        # Using Gemini 1.5 Pro model
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(full_prompt)
        return response.text

    except Exception as e:
        print(f"Error occurred: {e}")
        return {"error": str(e)}
    

"""asdyaduashduasd"""
def find_investor_url(bank_name):
    import requests
    from bs4 import BeautifulSoup
    from urllib.parse import unquote

    query = f"{bank_name} investor relations site"
    url = f"https://html.duckduckgo.com/html/?q={query.replace(' ', '+')}"
    headers = {'User-Agent': 'Mozilla/5.0'}

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    results = soup.find_all("a", attrs={"class": "result__a"}, href=True)
    URLS=[]
    for link in results:
        href = link['href']
        if "uddg=" in href:
            real_url = href.split("uddg=")[-1]
            real_url = unquote(real_url.split('&')[0])
            if 'investor' in real_url.lower():
                # print(f"🔗 Found Investor URL: {real_url}")
                # return real_url
                URLS.append(real_url)
                if(len(URLS)>5):
                    break
    # print("No valid investor link found.")
    return URLS

import re

def get_fs(total, per):
    curr = total[0]
    
    # Use regex to extract the numeric part from total string
    match = re.search(r'(\d+(\.\d+)?)', total)
    if not match:
        raise ValueError(f"Could not parse total revenue value: '{total}'")
    amt = float(match.group(1))

    # Also clean up the units (e.g. "millions")
    txt_match = re.search(r'(millions|billion|thousand)', total.lower())
    txt = txt_match.group(1) if txt_match else 'millions'

    # Extract numeric part from percent (e.g. '20 %' -> 20.0)
    per_amt = float(re.search(r'\d+(\.\d+)?', per).group())

    fs = amt * per_amt * 0.01
    return f"{curr}{fs} {txt}"
"""IF ELSE"""
# # Add this to your functions.py
# def generate_quarterly_url(company, fy, quarter):
#     """
#     Generate company specific quarterly result URLs.
#     """
#     fy_path = fy.replace("-", "")[-2:]  # e.g. 2024-2025 --> 25
#     qnum = quarter.lower().replace("q", "")  # e.g. Q4 --> 4

#     if company.lower() == "wipro":
#         return f"https://www.wipro.com/content/dam/nexus/en/investor/quarterly-results/{fy}/q{qnum}fy{fy_path}/datasheet-q{qnum}fy{fy_path}.pdf"

#     elif company.lower() == "tcs":
#         return f"https://www.tcs.com/content/dam/tcs/investor-relations/financial-statements/{fy}/q{qnum}/Presentations/Q{qnum} {fy} Fact Sheet.pdf"

#     elif company.lower() == "infosys":
#         return f"https://www.infosys.com/content/dam/infosys-web/en/investors/reports-filings/quarterly-results/{fy}/q{qnum}/documents/fact-sheet.pdf"

#     # If dynamic companies, just return None, they will fallback to search & scraping
#     elif company.lower() in ["accenture", "capgemini", "cognizant", "coforge", "techmahindra", "hcl"]:
#         return None
    
#     else:
#         return None  # default fallback for unsupported
# import requests
# from bs4 import BeautifulSoup
# from urllib.parse import urljoin

# def get_pdf_link(company,quar,year):
#     company_sources = {
#     "Wipro": {
#         "base_url": "https://www.wipro.com",
#         "results_page": "https://www.wipro.com/investors/quarterly-results/",
#         "anchor_contains": "Press Release"
#     },
#     "TCS": {
#         "base_url": "https://www.tcs.com",
#         "results_page": "https://www.tcs.com/investor-relations/financial-statements",
#         "anchor_contains": "Fact Sheet"
#     },
#     "Infosys": {
#         "base_url": "https://www.infosys.com",
#         "results_page": "https://www.infosys.com/investors/reports-filings/quarterly-results/2024-2025/q4.html",
#         "anchor_contains": "Fact Sheet"
#     },
#     "Accenture": {
#         "base_url": "https://investor.accenture.com",
#         "results_page": "https://investor.accenture.com/news-and-events/events-calendar/2025/03-20-2025",
#         "anchor_contains": "Earnings Release"
#     },
#     "Capgemini": {
#         "base_url": "https://investors.capgemini.com",
#         "results_page": "https://investors.capgemini.com/en/financial-results/?fiscal-year=2025",
#         "anchor_contains": "Download"
#     },
#     "Cognizant": {
#         "base_url": "https://investors.cognizant.com/",
#         "results_page": "https://investors.cognizant.com/financials/quarterly-results/default.aspx",
#         "anchor_contains": "Presentation"
#     },
#     "Techmahindra": {
#         "base_url": "https://www.techmahindra.com/investors",
#         "results_page": "https://www.techmahindra.com/investors/quarterly-earnings/",
#         "anchor_contains": "Fact Sheet"
#     },
#     "ltimindtree": {
#         "base_url": "https://www.ltimindtree.com/investors",
#         "results_page": "https://www.ltimindtree.com/investors/financial-results/",
#         "anchor_contains": "Earnings Release and Factsheet"
#     },
#     "mphasis": {
#         "base_url": "https://www.mphasis.com/home/corporate/investors.html",
#         "results_page": "https://www.mphasis.com/home/corporate/investors.html",
#         "anchor_contains": "Financial Results"
#     },
#     "birlasoft": {
#         "base_url": "https://www.birlasoft.com",
#         "results_page": "https://www.birlasoft.com/company/investors/financial-results",
#         "anchor_contains": "Investor Update"
#     }
# }
#     info = company_sources[company]
#     resp = requests.get(info['results_page'])
#     soup = BeautifulSoup(resp.content, 'html.parser')
    
#     for a in soup.find_all('a'):
#         href = a.get('href')
#         text = a.get_text().strip()
#         print(text)
#         if info['anchor_contains'].lower() in text.lower():
#             if href.startswith("http"):
#                 print(f"[DEBUG] PDF link selected for {company}: {href}")
#                 return href
#             else:
#                 full_url = urljoin(info['base_url'], href)
#                 print(f"[DEBUG] PDF link selected for {company}: {full_url}")
#                 return full_url
    
#     print(f"[DEBUG] No PDF link found for {company}")
#     return None
import requests

def get_pdf_link(company, quar, year):
    yy = str(year)[-2:]  # last two digits of year
    fy_string = f"{year-1}-{year}"  # for formats like 2024-2025

    company_sources = {
        "wipro": f"https://www.wipro.com/content/dam/nexus/en/investor/quarterly-results/{year-1}-{year}/q{quar}fy{yy}/datasheet-q{quar}fy{yy}.pdf",
        "tcs": f"https://www.tcs.com/content/dam/tcs/investor-relations/financial-statements/{year-1}-{yy}/q{quar}/Presentations/Q{quar}%20{year-1}-{yy}%20Fact%20Sheet.pdf",
        "infosys": f"https://www.infosys.com/investors/reports-filings/quarterly-results/{year-1}-{year}/q{quar}/documents/fact-sheet.pdf",
        "accenture": f"https://investor.accenture.com/~/media/Files/A/Accenture-IR-V3/quarterly-earnings/{year}/q{quar}fy{yy}/accentures-{['first','second','third','fourth'][quar-1]}-quarter-fiscal-{year}-earnings-release.pdf",
        "capgemini": f"https://investors.capgemini.com/en/financial-results/{year}/Q{quar}/download.pdf",
        "cognizant": f"https://cognizant.q4cdn.com/123993165/files/doc_earnings/{year}/q{quar}/presentation/Q{quar}{yy}-Earnings-Supplement.pdf",
        "techmahindra": f"https://insights.techmahindra.com/investors/tml-q{quar}-fy-{yy}-fact-sheet.pdf",
        "ltimindtree": f"https://www.ltimindtree.com/wp-content/uploads/{year}/04/earnings-release-factsheet-q{quar}fy{yy}.pdf",
        "mphasis": f"https://www.mphasis.com/content/dam/mphasis-com/global/en/investors/financial-results/{year}/q{quar}-earnings-press-release.pdf",
        "birlasoft": f"https://www.birlasoft.com/sites/default/files/resources/downloads/investors/investor-update/q{quar}-fy{yy}-investor-update.pdf",
        "coforge": f"https://www.coforge.com/hubfs/Fact-Sheet-Q{quar}FY{yy}.pdf",
        "zensar": f"https://www.zensar.com/about/investors/",  # No PDF link provided
        "persistent systems": f"https://www.persistent.com/investors/quarterly-results/"
    }

    try:
        return company_sources[company.lower()]
    except Exception as e:
        print(f"Error: No URL template found for {company}",e)
        return None



