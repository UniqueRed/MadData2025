import requests
from bs4 import BeautifulSoup
import os
import json
import PyPDF2
import re

MAJORS_URL = "https://guide.wisc.edu/undergraduate/#majorscertificatestext"

JSON_DIR = "json_data"
PDF_DIR = "pdf_data"
os.makedirs(JSON_DIR, exist_ok=True)
os.makedirs(PDF_DIR, exist_ok=True)

def sanitize_filename(name):
    return re.sub(r'[^\w\-_.]', '_', name.strip())

def get_majors(url):
    response = requests.get(url)
    if response.status_code != 200:
        print("Failed to fetch majors page")
        return []

    soup = BeautifulSoup(response.content, 'html.parser')
    majors = []

    for link in soup.select('a[href^="/undergraduate/"]'):
        major_name = link.text.strip()
        major_url = f"https://guide.wisc.edu{link['href']}"
        majors.append({
            'name': major_name,
            'url': major_url
        })
    return majors

def construct_pdf_url(major_url):
    major_start_index = major_url.rindex("/", 0, len(major_url) - 1)
    return major_url + major_url[major_start_index + 1:len(major_url) - 1] + ".pdf"

def download_pdf(pdf_url, major_name):
    response = requests.get(pdf_url)
    if response.status_code != 200:
        print(f"Failed to download PDF for: {major_name}")
        return None

    pdf_path = os.path.join(PDF_DIR, f"{sanitize_filename(major_name)}.pdf")
    with open(pdf_path, 'wb') as f:
        f.write(response.content)
    return pdf_path

def extract_pdf_text(pdf_path):
    text = ""
    with open(pdf_path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            if page and page.extract_text():
                text += page.extract_text()
    return text

def scrape_major(major):
    pdf_url = construct_pdf_url(major['url'])

    pdf_path = download_pdf(pdf_url, major['name'])
    if not pdf_path:
        return

    pdf_text = extract_pdf_text(pdf_path)

    data = {
        "major_name": major['name'],
        "full_text": pdf_text
    }

    json_path = os.path.join(JSON_DIR, f"{sanitize_filename(major['name'])}.json")
    with open(json_path, 'w') as f:
        json.dump(data, f, indent=4)
    print(f"Scraped and saved data for: {major['name']}")

if __name__ == "__main__":
    majors = get_majors(MAJORS_URL)
    if majors:
        for major in majors:
            scrape_major(major)
    print("Scraping complete.")
