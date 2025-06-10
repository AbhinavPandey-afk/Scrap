from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urljoin
import time
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from urllib.parse import urljoin
# from webdriver_manager.chrome import ChromeDriverManager
# import time

def find_presentation_pdf(base_url, keywords=("presentation",), timeout=15):
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage') 

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    try:
        print(f"Opening: {base_url}")
        driver.get(base_url)

        # Wait up to `timeout` seconds for any anchor tag to appear
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.TAG_NAME, "a"))
        )

        # Give time for JS to populate hrefs if needed
        time.sleep(3)

        pdf_links = driver.find_elements(By.XPATH, "//a[contains(translate(@href, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '.pdf')]")
        print(f"🔍 Found {len(pdf_links)} PDF links on the page.")

        result_links = []
        for link in pdf_links:
            href = link.get_attribute("href")
            link_text = link.text.strip().lower()
            if href and any(kw.lower() in link_text or kw.lower() in href.lower() for kw in keywords):
                full_link = urljoin(base_url, href)
                result_links.append(full_link)

        return result_links

    except Exception as e:
        print("❌ Error:", e)
        return []
    finally:
        driver.quit()

# import requests
# from bs4 import BeautifulSoup
# from urllib.parse import urljoin
# import re

# # Optional Selenium import
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from webdriver_manager.chrome import ChromeDriverManager

# def find_presentation_pdf(url, keywords=("presentation", "earnings", "results"), timeout=20):
#     print(f"🔍 Checking: {url}")

#     # 1️⃣ Step 1: Try direct API sniffing (if known)
#     if "westernunion" in url:
#         return fetch_from_known_api("https://ir.westernunion.com/api/v1/ir/event-presentations", keywords)

#     # 2️⃣ Step 2: Try HTML scraping (static links)
#     try:
#         html = requests.get(url, timeout=15).text
#         soup = BeautifulSoup(html, "html.parser")
#         links = soup.find_all("a", href=True)

#         results = []
#         for link in links:
#             href = link['href']
#             text = link.get_text().lower()
#             if href.lower().endswith('.pdf') and any(k.lower() in text or k.lower() in href.lower() for k in keywords):
#                 full_link = urljoin(url, href)
#                 results.append(full_link)

#         if results:
#             print(f"✅ Found {len(results)} PDF(s) via BeautifulSoup.")
#             return results
#     except Exception as e:
#         print(f"⚠️ HTML parsing failed: {e}")

#     # 3️⃣ Step 3: Use Selenium for dynamic content
#     print("⏳ Falling back to Selenium...")

#     options = Options()
#     options.add_argument('--headless')
#     options.add_argument('--no-sandbox')
#     options.add_argument('--disable-dev-shm-usage')

#     service = Service(ChromeDriverManager().install())
#     driver = webdriver.Chrome(service=service, options=options)

#     try:
#         driver.get(url)
#         WebDriverWait(driver, timeout).until(
#             EC.presence_of_element_located((By.XPATH, "//a[contains(translate(@href, 'PDF', 'pdf'), '.pdf')]"))
#         )

#         pdf_links = driver.find_elements(By.XPATH, "//a[contains(translate(@href, 'PDF', 'pdf'), '.pdf')]")

#         results = []
#         for link in pdf_links:
#             href = link.get_attribute("href")
#             text = link.text.lower()
#             if href and any(k.lower() in href.lower() or k.lower() in text for k in keywords):
#                 results.append(urljoin(url, href))

#         print(f"✅ Found {len(results)} PDF(s) via Selenium.")
#         return results

#     except Exception as e:
#         print(f"❌ Selenium failed: {e}")
#         return []
#     finally:
#         driver.quit()

# def fetch_from_known_api(api_url, keywords):
#     print(f"🌐 Using known API: {api_url}")
#     headers = {
#         "User-Agent": "Mozilla/5.0",
#         "Accept": "application/json"
#     }

#     try:
#         res = requests.get(api_url, headers=headers, timeout=10)
#         if res.status_code != 200:
#             print(f"⚠️ API returned status {res.status_code}")
#             return []
        
#         data = res.json()
#         results = []
#         for item in data.get("data", []):
#             file_url = item.get("fileUrl") or item.get("url") or ""
#             title = item.get("title", "")
#             if file_url.endswith(".pdf") and any(k.lower() in title.lower() or k.lower() in file_url.lower() for k in keywords):
#                 results.append(file_url)
#         print(f"✅ Found {len(results)} PDF(s) via API.")
#         return results

#     except Exception as e:
#         print(f"❌ API fetch failed: {e}")
#         return []





''' Function to convert link to text and get Revenue'''

import requests
import os
# from langchain.document_loaders import PyPDFLoader
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Download PDF
# def download_pdf(pdf_url, save_path="presentation.pdf"):
#     response = requests.get(pdf_url)
#     if response.status_code == 200:
#         with open(save_path, "wb") as f:
#             f.write(response.content)
#         # print(f"✅ PDF downloaded to {save_path}")
#         return save_path
#     else:
#         raise Exception(f"Failed to download PDF. Status code: {response.status_code}")
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

# Delete the file
# def delete_file(file_path):
#     if os.path.exists(file_path):
#         os.remove(file_path)
        # print(f"🗑 Deleted file: {file_path}")
    # else:
        # print(f"⚠ File not found: {file_path}")
def delete_file(file_path):
    try:
        os.remove(file_path)
    except Exception as e:
        print(f"⚠️ Could not delete file: {e}")


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
        "temperature": 0.5
    }

    # response = requests.post(api_url, headers=headers, json=payload)
    # return response.json()
    try:
        response = requests.post(api_url, headers=headers, json=payload)
        response.raise_for_status()  # Raises HTTPError for bad responses (4xx, 5xx)
        return response.json()

    except requests.exceptions.HTTPError as e:
        print(f"HTTP error occurred: {e}")
        return {"error": str(e), "details": response.text}

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return {"error": str(e)}

    except Exception as e:
        print(f"Unexpected error: {e}")
        return {"error": str(e)}

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
    # print("❌ No valid investor link found.")
    return URLS
