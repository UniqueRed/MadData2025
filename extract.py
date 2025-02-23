import PyPDF2
import json

pdf_path = "./course_data/Computer_Sciences__COMP_SCI_.pdf"

with open(pdf_path, "rb") as file:
    reader = PyPDF2.PdfReader(file)
    text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])

courses = []
course_blocks = text.split("COMP SCI")

for block in course_blocks[1:]:
    lines = block.strip().split("\n")
    course_code = "COMP SCI" + lines[0].split("—")[0].strip()
    course_name = lines[0].split("—")[-1].strip() if "—" in lines[0] else "Unknown"
    credits = next((line for line in lines if "credits" in line.lower()), "Unknown").split(" ")[0]
    prerequisites = next((line.replace("Requisites:", "").strip() for line in lines if "Requisites:" in line), "None")
    description = next((lines[i+1] for i, line in enumerate(lines) if "credits." in line.lower()), "No description available.")
    
    general_education = {
        "Gen Ed": next((line.replace("Course Designation:", "").strip() for line in lines if "Gen Ed" in line), "None"),
        "Breadth": next((line.replace("Breadth:", "").strip() for line in lines if "Breadth:" in line), "None"),
        "Level": next((line.replace("Level:", "").strip() for line in lines if "Level:" in line), "None"),
        "L&S Credit": next((line.replace("L&S Credit:", "").strip() for line in lines if "L&S Credit" in line), "None"),
    }

    learning_outcomes = [line.strip() for line in lines if line.startswith(("1.", "2.", "3.", "4.", "5."))]

    course_data = {
        "Course Name": course_name,
        "Course Code": course_code,
        "Credits": credits,
        "Prerequisites": prerequisites,
        "Description": description,
        "General Education Requirements": general_education,
        "Learning Outcomes": learning_outcomes
    }
    
    courses.append(course_data)

json_output = json.dumps(courses, indent=4)

json_path = "computer_science_courses.json"
with open(json_path, "w") as json_file:
    json_file.write(json_output)

json_path
