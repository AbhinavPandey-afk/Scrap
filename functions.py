''' function to get pdf from link ''' 

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
        print(f"🌐 Opening: {base_url}")
        driver.get(base_url)

        # Optional: Wait for the page to load (customize if you know dynamic loading is needed)
        time.sleep(5)  # You can adjust this delay based on page complexity

        # Find all <a> tags with href ending with .pdf
        pdf_links = driver.find_elements(By.XPATH, "//a[contains(translate(@href, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '.pdf')]")
        print(f"🔍 Found {len(pdf_links)} PDF links on the page.")

        for link in pdf_links:
            href = link.get_attribute("href")
            link_text = link.text.strip().lower()
            if href:
                # Match keywords in href or link text
                if any(kw.lower() in link_text or kw.lower() in href.lower() for kw in keywords):
                    full_link = urljoin(base_url, href)
                    # print("✅ Found matching PDF:", full_link)
                    return full_link

        # print("❌ No matching PDF found.")
        return None

    except Exception as e:
        # print("❌ Error:", e)
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
        # print(f"🗑️ Deleted file: {file_path}")
    # else:
        # print(f"⚠️ File not found: {file_path}")

# DeepSeek API call function
def query_deepseek(prompt, context):
    api_url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": "Bearer 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",  # replace with actual key
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek/deepseek-r1-0528:free",
        "messages": [
            {"role": "system", "content": "You are a financial analyst extracting precise numerical data."},
            {"role": "user", "content": f"Context: {context}\n\nQuestion: {prompt}"}
        ],
        "temperature": 0
    }

    response = requests.post(api_url, headers=headers, json=payload)
    return response.json()

