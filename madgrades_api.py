import requests
import pandas as pd
import re

# ----- Configuration -----
# Replace these with your actual endpoints and headers.
url = "https://api.madgrades.com/v1/courses"  # API endpoint for courses
urlInstructors = "https://api.madgrades.com/v1/courses/instructors"  # API endpoint for instructors (if needed)
api_token = "3214f78c083147058e23b5d4ec766803"
headers = {
    "Authorization": f"Token token={api_token}"  # Replace with your actual API key if required
}

# Array of subjects to query.
subjects = ["Computer Science", "Computer Engineering", "Data Science", "Statistics", "Math"]

# List to store course results.
courses_result = []
# Dictionary to aggregate professor statistics across all courses.
professor_stats = {}


# ----- Helper Functions -----

def calculate_total_gpa(cumulative):
    """Calculate total class GPA using grade counts."""
    aCount = cumulative.get('aCount', 0)
    bCount = cumulative.get('bCount', 0)
    cCount = cumulative.get('cCount', 0)
    dCount = cumulative.get('dCount', 0)
    fCount = cumulative.get('fCount', 0)

    total_students = aCount + bCount + cCount + dCount + fCount
    if total_students == 0:
        return "N/A"

    total_points = aCount * 4 + bCount * 3 + cCount * 2 + dCount * 1 + fCount * 0
    gpa = round(total_points / total_students, 2)
    return gpa


def update_professor_stats(course_offerings):
    """Update professor_stats dictionary with information from course offerings."""
    for offering in course_offerings:
        sections = offering.get("sections", [])
        for section in sections:
            # Get grade counts
            a = section.get("aCount", 0)
            b = section.get("bCount", 0)
            c = section.get("cCount", 0)
            d = section.get("dCount", 0)
            f = section.get("fCount", 0)
            section_total = a + b + c + d + f
            if section_total == 0:
                continue  # Skip sections with no graded students.
            weighted = a * 4 + b * 3 + c * 2 + d * 1 + f * 0
            # Update for each instructor in the section.
            for instr in section.get("instructors", []):
                prof_name = instr.get("name", "Unknown Instructor")
                if prof_name not in professor_stats:
                    professor_stats[prof_name] = {"total_points": 0, "total_count": 0}
                professor_stats[prof_name]["total_points"] += weighted
                professor_stats[prof_name]["total_count"] += section_total


def extract_course_code(text):
    """Extracts a course code (e.g., 'CS101') from a text string using a simple regex."""
    match = re.search(r'\b[A-Z]{2,4}\d{3}\b', text)
    return match.group(0) if match else None


# ----- Main Loop Over Subjects -----
for subject in subjects:
    print(f"Querying subject: {subject}")

    # Set up query parameters for this subject.
    params = {
        "order": "asc",
        "query": subject
        # Additional parameters can be added here.
    }

    # Query the courses API.
    response = requests.get(url, headers=headers, params=params)
    # Optionally, you can query the instructors API if needed.
    responseInstructors = requests.get(urlInstructors, headers=headers, params=params)

    if response.status_code == 200:
        courses_data = response.json()
        # Assume courses are either directly in the JSON or under a "courses" key.
        if isinstance(courses_data, dict) and "courses" in courses_data:
            courses_list = courses_data["courses"]
        else:
            courses_list = courses_data

        print(f"Found {len(courses_list)} courses for {subject}.")

        # Process each course.
        for course in courses_list.get("results"):
            course_name = course.get("name", "Unknown Course")
            course_number = course.get("number", "Unknown Number")
            uuid = course.get("uuid")
            if not uuid:
                continue
            # Get detailed grade info for this course.
            course_details_url = f"https://api.madgrades.com/v1/courses/{uuid}/grades"
            details_response = requests.get(course_details_url, headers=headers)
            if details_response.status_code == 200:
                course_details = details_response.json()
                # Calculate total class GPA.
                if "cumulative" in course_details:
                    total_gpa = calculate_total_gpa(course_details["cumulative"])
                else:
                    total_gpa = "N/A"

                # Append course data to results.
                courses_result.append({
                    "Subject": subject,
                    "Course Name": course_name,
                    "Course Number": course_number,
                    "Total Class GPA": total_gpa
                })

                # If available, update professor statistics.
                if "courseOfferings" in course_details:
                    update_professor_stats(course_details["courseOfferings"])
            else:
                print(f"Error fetching details for course {course_name}: {details_response.status_code}")
    else:
        print(f"Error fetching data for subject {subject}: {response.status_code}")

# ----- Save Results to CSV Files -----

# Create a DataFrame for course results and save.
courses_df = pd.DataFrame(courses_result)
courses_output_csv = "courses_output.csv"
courses_df.to_csv(courses_output_csv, index=False)
print(f"\nCourse results saved to {courses_output_csv}")

# Create a DataFrame for professor statistics.
professor_list = []
for prof, stats in professor_stats.items():
    if stats["total_count"] > 0:
        prof_gpa = round(stats["total_points"] / stats["total_count"], 2)
    else:
        prof_gpa = "N/A"
    professor_list.append({"Professor": prof, "Professor GPA": prof_gpa})

professors_df = pd.DataFrame(professor_list)
professors_output_csv = "professor_stats.csv"
professors_df.to_csv(professors_output_csv, index=False)
print(f"Professor statistics saved to {professors_output_csv}")
