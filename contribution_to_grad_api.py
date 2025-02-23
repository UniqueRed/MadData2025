import os
import json
import openai
from openai import OpenAI
import pandas as pd
import PyPDF2


def extract_text_from_pdf(pdf_path):
    """Extracts and returns text content from a PDF file."""
    text = ""
    with open(pdf_path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text


def load_major_requirements(pdf_paths):
    """Reads multiple PDF files and combines their text."""
    contents = []
    for path in pdf_paths:
        contents.append(extract_text_from_pdf(path))
    return "\n\n".join(contents)


def load_courses(csv_path):
    """Loads courses from a CSV file. Assumes courses are in a column named 'course'.
    If not, it will use the first column."""
    df = pd.read_csv(csv_path)
    if 'course' in df.columns:
        courses = df['course'].tolist()
    else:
        courses = df.iloc[:, 0].tolist()
    return courses


def build_prompt(requirements_text, courses):
    """Builds the GPT-4 prompt including course requirements and the course list."""
    prompt = f"""
You are an academic advisor. Based on the major course requirements below, assign a graduation contribution score for each course in the provided list. The score should reflect how much each course contributes to graduation, on a scale from 0 to 10.

For math, stat courses. Just randomly assign a number between 8 to 10.

Using the PDFs you uploaded, first determine for each course in the CSV:

    Core/Required Courses: These are courses that every student in that major must take (for example, “Basic Computer Sciences” courses in the CS major or the calculus sequence in Mathematics).
    Foundational/Sequential Courses: Courses that are part of a sequence (e.g. Calculus I/II or the discrete mathematics series) where each course contributes part of the overall “block” requirement.
    Elective/Advanced Courses: Courses that students choose to complete the remaining credits (these are often options within a given category such as advanced computing, machine learning, or electives in mathematics).
    
Major Course Requirements:
{requirements_text}

List of Courses:
{json.dumps(courses, indent=2)}

Provide your answer as a JSON array of scores (one score per course, corresponding to the order of courses above). Do not include any additional text.
"""
    return prompt


def get_scores_from_gpt(prompt):
    """Calls the GPT-4 API with the given prompt and returns the parsed JSON scores."""
    api_key = "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"
    client = OpenAI(
        api_key=api_key,  # This is the default and can be omitted
    )
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful academic advisor."},
            {"role": "user", "content": prompt}
        ],
        temperature=0  # Using a deterministic output
    )

    answer = response.choices[0].message.content.strip()
    try:
        scores = json.loads(answer)
        return scores
    except json.JSONDecodeError:
        print("Error: Could not parse JSON from the response. Raw response:")
        print(answer)
        return None


def main():
    # Define file paths for the four PDF files and the CSV file.
    pdf_files = [
        "computer-science.pdf",
        "data-science.pdf",
    ]
    csv_file = "courses.csv"

    # Load and combine the major requirements text from the PDFs.
    requirements_text = load_major_requirements(pdf_files)

    # Load the list of courses from the CSV.
    courses = load_courses(csv_file)

    # Build the prompt to send to GPT-4.
    prompt = build_prompt(requirements_text, courses)

    # Call GPT-4 to get the scores.
    scores = get_scores_from_gpt(prompt)

    if scores is not None:
        print("Array of scores for courses:")
        print(scores)
    else:
        print("Failed to retrieve course scores from GPT-4.")


if __name__ == "__main__":
    main()
