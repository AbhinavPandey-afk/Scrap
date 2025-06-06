from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urljoin
import time

def find_presentation_pdf(base_url, keywords=("presentation",), timeout=15):
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)

    try:
        print(f"Opening: {base_url}")
        driver.get(base_url)

        # Optional: Wait for the page to load (customize if you know dynamic loading is needed)
        time.sleep(5)  # You can adjust this delay based on page complexity

        # Find all <a> tags with href ending with .pdf
        pdf_links = driver.find_elements(By.XPATH, "//a[contains(translate(@href, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '.pdf')]")
        print(f"🔍 Found {len(pdf_links)} PDF links on the page.")
        l=[]
        for link in pdf_links:
            href = link.get_attribute("href")
            link_text = link.text.strip().lower()
            if href:
                # Match keywords in href or link text
                if any(kw.lower() in link_text or kw.lower() in href.lower() for kw in keywords):
                    full_link = urljoin(base_url, href)
                    l.append(full_link)
                    # print("✅ Found matching PDF:", full_link)
                    # return full_link

        # print("❌ No matching PDF found.")
        return l

    except Exception as e:
        print("❌ Error:", e)
        return None
    finally:
        driver.quit()


''' Function to convert link to text and get Revenue'''

import requests
import os
# from langchain.document_loaders import PyPDFLoader
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Download PDF
def download_pdf(pdf_url, save_path="presentation.pdf"):
    response = requests.get(pdf_url)
    if response.status_code == 200:
        with open(save_path, "wb") as f:
            f.write(response.content)
        # print(f"✅ PDF downloaded to {save_path}")
        return save_path
    else:
        raise Exception(f"Failed to download PDF. Status code: {response.status_code}")

# Load and prepare context from PDF
def load_and_prepare_pdf(local_pdf_path):
    loader = PyPDFLoader(local_pdf_path)
    pages = loader.load_and_split()
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    docs = splitter.split_documents(pages)
    return "\n".join([doc.page_content for doc in docs[:5]])

# Delete the file
def delete_file(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)
        # print(f"🗑 Deleted file: {file_path}")
    # else:
        # print(f"⚠ File not found: {file_path}")

# DeepSeek API call function
def query_deepseek(prompt, context):
    api_url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": "Bearer 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",  # replace with actual key
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek/deepseek-r1-0528:free",
        # "model":"meta-llama/llama-3.3-8b-instruct:free",
        "messages": [
            {"role": "system", "content": "You are a financial analyst extracting precise numerical data."},
            {"role": "user", "content": f"Context: {context}\n\nQuestion: {prompt}"}
        ],
        "temperature": 0
    }

    response = requests.post(api_url, headers=headers, json=payload)
    return response.json()
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

    for link in results:
        href = link['href']
        if "uddg=" in href:
            real_url = href.split("uddg=")[-1]
            real_url = unquote(real_url.split('&')[0])
            if 'investor' in real_url.lower():
                print(f"🔗 Found Investor URL: {real_url}")
                return real_url

    print("❌ No valid investor link found.")
    return None
