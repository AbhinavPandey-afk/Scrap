from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from urllib.parse import urljoin
import time
import os
import requests
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter


# 🧭 Find presentation PDF links
def find_presentation_pdf(base_url, keywords=("presentation",), timeout=15):
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)

    try:
        print(f"Opening: {base_url}")
        driver.get(base_url)
        time.sleep(5)  # Wait for JS loading if needed

        pdf_links = driver.find_elements(By.XPATH, "//a[contains(translate(@href, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '.pdf')]")
        print(f"🔍 Found {len(pdf_links)} PDF links on the page.")
        
        matched_links = []
        for link in pdf_links:
            href = link.get_attribute("href")
            link_text = link.text.strip().lower()
            if href and any(kw.lower() in link_text or kw.lower() in href.lower() for kw in keywords):
                full_link = urljoin(base_url, href)
                matched_links.append(full_link)

        return matched_links
    except Exception as e:
        print("❌ Error:", e)
        return []
    finally:
        driver.quit()


# 📥 Download the PDF to disk
def download_pdf(pdf_url, save_path="presentation.pdf"):
    response = requests.get(pdf_url)
    if response.status_code == 200:
        with open(save_path, "wb") as f:
            f.write(response.content)
        return save_path
    else:
        raise Exception(f"Failed to download PDF. Status code: {response.status_code}")


# 📄 Load PDF and prepare context
def load_and_prepare_pdf(local_pdf_path):
    loader = PyPDFLoader(local_pdf_path)
    pages = loader.load_and_split()
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    docs = splitter.split_documents(pages)
    return "\n".join([doc.page_content for doc in docs[:5]])  # Using only the first 5 chunks


# 🗑️ Delete file from disk
def delete_file(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)


# 🤖 DeepSeek API call for Q&A
def query_deepseek(prompt, context):
    api_url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": "Bearer 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",  # Replace with real key
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


# 🛢️ Insert rows into MySQL
def insert_three_rows(rows):
    import mysql.connector
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Dhruv@0987",  # ⬅️ Replace with your MySQL password
        database="financial_data"
    )
    cursor = conn.cursor()
    sql = """
        INSERT INTO earnings_data (bank_name, quarter_year, revenue, net_income, publish_date)
        VALUES (%s, %s, %s, %s, %s)
    """
    for row in rows:
        cursor.execute(sql, tuple(row))
    conn.commit()
    cursor.close()
    conn.close()
# 🔍 Auto-find investor relations link based on bank name using DuckDuckGo
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

