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
def download_pdf(url, filename='presentation.pdf'):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
        'Referer': url  # Some sites require this too
    }
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        with open(filename, 'wb') as f:
            f.write(response.content)
        return filename
    else:
        raise Exception(f"Failed to download PDF. Status code: {response.status_code}")


# Load and prepare context from PDF
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
def load_and_prepare_html(local_html_path):
    from bs4 import BeautifulSoup
    from langchain.text_splitter import RecursiveCharacterTextSplitter

    # Keywords we care about (same as PDF for consistency)
    relevant_keywords = [
        'revenue', 'financials', 'total income', 'segment results',
        'bfs', 'bfs sector', 'bfs segment', 'bfs contribution',
        'earnings', 'EBIT', 'profit', 'operating income',
        'quarterly performance', 'growth', 'currency', 'millions', 'billions'
    ]

    # Load HTML
    with open(local_html_path, 'r', encoding="utf-8", errors="ignore") as f:
        html_content = f.read()

    soup = BeautifulSoup(html_content, 'html.parser')
    full_text = soup.get_text(separator="\n", strip=True)

    # Lowercase text for keyword matching
    text_lower = full_text.lower()

    # Extract relevant sections (line by line filtering)
    relevant_lines = []
    for line in full_text.split('\n'):
        line_lower = line.lower()
        if any(keyword in line_lower for keyword in relevant_keywords):
            relevant_lines.append(line.strip())

    # If nothing matched, fallback to entire text (limit to 5000 chars for safety)
    if not relevant_lines:
        relevant_text = full_text[:5000]
    else:
        relevant_text = "\n".join(relevant_lines)

    # Chunk splitting (similar to PDF logic)
    splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=150)
    docs = splitter.split_text(relevant_text)

    # Return first few chunks only
    return "\n".join(docs[:10])



def delete_file(file_path):
    try:
        os.remove(file_path)
    except Exception as e:
        print(f"Could not delete file: {e}")
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
def get_fs(total_revenue, unit, currency, bfsi_percentile):
    """
    Calculate BFSI revenue based on cleaned inputs:
    - total_revenue: numeric value (float or int)
    - unit: string ("millions", "billions", etc.)
    - currency: string ("USD", "INR", etc.)
    - bfsi_percentile: numeric value (float or int)
    """
    
    # Ensure all values are floats
    amt = float(total_revenue)
    per_amt = float(bfsi_percentile)

    # Calculate BFSI revenue
    bfsirev = amt * per_amt * 0.01

    return f"{currency}{bfsirev} {unit}"
"""CapGemini"""
def get_capgemini_presentation(year, quarter):
    import shutil
    import platform
    # Convert quarter and year to URL format
    fiscal_url = f"https://investors.capgemini.com/en/financial-results/?fiscal-year={year}"
    
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    # options.binary_location = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    chrome_path = (
    shutil.which("google-chrome") or
    shutil.which("chrome") or
    shutil.which("chrome.exe")
)

    if not chrome_path:
        if platform.system() == "Windows":
            chrome_path = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
        else:
            chrome_path = "/usr/bin/google-chrome"


    options.binary_location = chrome_path

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )   

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        driver.get(fiscal_url)
        time.sleep(3)

        # Find all blocks for that fiscal year
        presentations = driver.find_elements(By.XPATH, "//a[contains(text(), 'Download') and contains(@href, 'Presentation')]")
        
        if not presentations:
            # fallback: Capgemini uses "Download" with size instead of "Presentation"
            presentations = driver.find_elements(By.XPATH, "//a[contains(text(),'Download') and contains(@href,'.pdf') and contains(@href,'financial-results')]")

        for link in presentations:
            href = link.get_attribute("href")
            # Heuristic filtering:
            if f"Q{quarter}" in href:
                driver.quit()
                return href

        driver.quit()
        print("Presentation not found for given quarter.")
        return None

    except Exception as e:
        driver.quit()
        print("Error fetching Capgemini presentation:", e)
        return None

import requests

def get_pdf_link(company, quar, year):
    yy = str(year)[-2:]  # last two digits of year
    fy_string = f"{year-1}-{year}"  # for formats like 2024-2025
    

    company_sources = {
        "wipro": f"https://www.wipro.com/content/dam/nexus/en/investor/quarterly-results/{year-1}-{year}/q{quar}fy{yy}/datasheet-q{quar}fy{yy}.pdf",
        "tcs": f"https://www.tcs.com/content/dam/tcs/investor-relations/financial-statements/{year-1}-{yy}/q{quar}/Presentations/Q{quar}%20{year-1}-{yy}%20Fact%20Sheet.pdf",
        "infosys": f"https://www.infosys.com/investors/reports-filings/quarterly-results/{year-1}-{year}/q{quar}/documents/fact-sheet.pdf",
        "accenture": f"https://investor.accenture.com/~/media/Files/A/Accenture-IR-V3/quarterly-earnings/{year}/q{quar}fy{yy}/accentures-{['first','second','third','fourth'][quar-1]}-quarter-fiscal-{year}-earnings-release.pdf",
        "capgemini": get_capgemini_presentation(year, quar),
        "cognizant": f"https://cognizant.q4cdn.com/123993165/files/doc_earnings/{year}/q{quar}/presentation/Q{quar}{yy}-Earnings-Supplement.pdf",
        "techmahindra": f"https://insights.techmahindra.com/investors/tml-q{quar}-fy-{yy}-fact-sheet.pdf",
        "ltimindtree": f"https://www.ltimindtree.com/wp-content/uploads/{year}/04/earnings-release-factsheet-q{quar}fy{yy}.pdf",
        "mphasis": f"https://www.mphasis.com/content/dam/mphasis-com/global/en/investors/financial-results/{year}/mphasis-earnings-call-presentation-q{quar}-{year}.pdf",
        #"mphasis": f"https://www.mphasis.com/content/dam/mphasis-com/global/en/investors/financial-results/{year}/q{quar}-financial-results.pdf",
        "birlasoft": f"https://www.birlasoft.com/sites/default/files/resources/downloads/investors/investor-update/q{quar}-fy{yy}-investor-update.pdf",
        "coforge": f"https://www.coforge.com/investors/quarter-reports",
        "zensar": f"https://www.zensar.com/sites/default/files/investor/analyst-meet/Zensar-Analyst-Presentation-Q{quar}FY{yy}.pdf",  # No PDF link provided
        # "persistent systems": f"https://www.persistent.com/wp-content/uploads/2025/04/analyst-presentation-and-factsheet-q4fy25.pdf"
    }
    if quar==4:
        company_sources["persistent systems"] = f"https://www.persistent.com/wp-content/uploads/{year}/04/analyst-presentation-and-factsheet-q4fy{yy}.pdf"
    elif quar==3:
        company_sources["persistent systems"] = f"https://www.persistent.com/wp-content/uploads/{year}/01/analyst-presentation-and-factsheet-q3fy{yy}.pdf"
    elif quar==2:
        company_sources["persistent systems"] = f"https://www.persistent.com/wp-content/uploads/{year-1}/10/analyst-presentation-and-factsheet-q2fy{yy}.pdf"
    else:
        company_sources["persistent systems"] = f"https://www.persistent.com/wp-content/uploads/{year-1}/07/analyst-presentation-and-factsheet-q1fy{yy}.pdf"
    if company.lower()=="coforge":
        l=find_presentation_pdf(company_sources["coforge"])
        l2=[]
        for i in l:
            if (("Q"+str(quar)) in i) & (yy in i) & ("fact" in i.lower()) & ("sheet" in i.lower()):
                l2.append(i)
        return l2[-1]
    try:
        return company_sources[company.lower()]
    except Exception as e:
        print(f"Error: No URL template found for {company}",e)
        return None
def detect_file_type(file_path):
    with open(file_path, 'rb') as f:
        header = f.read(4)
        if header == b'%PDF':
            return 'pdf'
        elif header.startswith(b'<!DO') or header.startswith(b'<ht'):
            return 'html'
        else:
            return 'unknown'
def process_file(file_path):
    file_type = detect_file_type(file_path)
    
    if file_type == 'pdf':
        return load_and_prepare_pdf(file_path)
    
    elif file_type == 'html':
        return load_and_prepare_html(file_path)
    
    else:
        print("❌ Unknown file type. Skipping.")
        return ""
# functions.py

def combine_bfsi_revenues(bfs_value, insurance_value):
    """
    Combine BFS and Insurance revenues. Handles cases where any value might be missing.
    """
    try:
        bfs = float(bfs_value)
    except:
        bfs = 0.0

    try:
        ins = float(insurance_value)
    except:
        ins = 0.0

    return bfs + ins
