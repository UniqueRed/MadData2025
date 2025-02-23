import fitz # PyMuPDF for PDF processing
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from huggingface_hub import login
import pandas as pd
import requests
from mistralai import Mistral

hf_token = "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"
login(hf_token)

# Load Mistral 7B Model & Tokenizer (Pretrained)
model_name = "mistralai/Mistral-7B-v0.1"
tokenizer = AutoTokenizer.from_pretrained(model_name, use_auth_token=hf_token)
model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=torch.float16, device_map="auto", use_auth_token=hf_token)

### 1️⃣ Extract Text While Preserving Styling ###
def extract_styled_text(pdf_path):
    """Extracts text from a PDF while preserving styling information like bold, italic, and headings."""
    doc = fitz.open(pdf_path)
    structured_text = ""

    for page_num, page in enumerate(doc):
        blocks = page.get_text("dict")["blocks"]
        structured_text += f"\n\n## Page {page_num + 1} ##\n\n"

        for block in blocks:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        text = span["text"].strip()
                        if not text:
                            continue

                        # Apply formatting
                        if "Bold" in span["font"]:
                            text = f"**{text}**"
                        if "Italic" in span["font"]:
                            text = f"*{text}*"

                        structured_text += text + " "

        structured_text += "\n\n"

    return structured_text

def process_with_mistral(pdf_content, csv_content):
    """
    Processes extracted styled PDF content using the Mistral API.

    Args:
        pdf_content (str): The content extracted from the PDF.
        csv_content (str): The CSV data as a string.

    Returns:
        str: The generated output from the Mistral API.
    """
    prompt = f"""
    You are an AI assistant that understands structured academic documents.
    Below is a university major requirement document extracted from a PDF:

    {pdf_content}

    You have been provided with a CSV file containing detailed information about all available courses for a specific degree program. The CSV file includes columns such as:

    Subject,Course Name,Course Number,Total Class GPA,Professor Rating,graduation_score,admin_preference
    {csv_content}

    Your tasks are:

    Rank the Courses:
        Read the CSV data and rank all the available courses in descending order based on the Ranking Score.

    Generate a 4-Year Academic Plan:
        Using the ranked courses, create a comprehensive 4-year academic plan.
        Break down the plan by academic year (Years 1 through 4) and, if applicable, by semesters (e.g., Fall and Spring).
        Prioritize the inclusion of higher-ranked courses while ensuring that all prerequisite requirements are met (i.e., schedule prerequisite courses before or alongside courses that depend on them).
        Aim for a balanced course load across each term.
    
    Return ONLY the 4-Year Academic Plan with no additional text
    """

    # Construct the payload with the prompt and desired generation parameters
    payload = {
        "prompt": prompt,
        "max_length": 1024,
        # Optionally include additional parameters like "temperature", "top_p", etc.
    }

    # Replace with your actual Mistral API endpoint and API key (if required)
    API_KEY = "a7N82kN2AebXUT4kqe2f0ikrp8Okxdnd"
    model = "mistral-large-latest"
    client = Mistral(api_key=API_KEY)

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    chat_response = client.chat.complete(
        model=model,
        messages=[
            {
                "role": "user",
                "content": prompt,
            },
        ]
    )
    return chat_response.choices[0].message.content


### 3️⃣ Main Execution Function ###
def main():
    pdf_path = "computer-science.pdf"  # Replace with your PDF file
    print("Extracting text from PDF while preserving structure...\n")

    extracted_text = extract_styled_text(pdf_path)
    print("✅ Extracted successfully! Processing with Mistral 7B...\n")

    csv_file_path = 'train.csv'  # Replace with the path to your CSV file
    df = pd.read_csv(csv_file_path)
    mistral_response = process_with_mistral(extracted_text, df)
    print("\n📜 Mistral 7B Response:\n", mistral_response, "\n")

# Run the script
if __name__ == "__main__":
    main()
