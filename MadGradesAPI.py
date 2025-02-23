import requests
import pandas as pd

api_token = "3214f78c083147058e23b5d4ec766803"
url = "https://api.madgrades.com/v1/courses"
urlIntructors = "https://api.madgrades.com/v1/instructors"

headers = {
    "Authorization": f"Token token={api_token}"
}

params = {
    "order": "asc",   
    "query": "cs",
    "query": "Computer Science",
    "query": "Computer",
    "query": "programming",
    "query": "Data",
    "query": "Computer Programming",

    # You can add additional parameters:
    # "instructors": "100191",
    # "query": "Calculus",
    # "sort": "name",
    # "subjects": "146,200"
}


professor_stats = {}
professor_classes = {}
course_info = {}

response = requests.get(url, headers=headers, params=params)
responseIntructors = requests.get(urlIntructors, headers=headers, params=params)

if response.status_code == 200:
    courses_data = response.json()
    intructors_data = responseIntructors.json()
    if isinstance(courses_data, dict) and "courses" in courses_data:
        courses_list = courses_data["courses"]
    else:
        courses_list = courses_data

    df = pd.DataFrame(courses_list)

    print("Course DataFrame:")
    for i in df["results"]:
        #print(i["name"])
        #print(i["number"])
        uuid = i["uuid"]
        course_key = f"{i['name']} ({i['number']})"
        url_course = f"https://api.madgrades.com/v1/courses/{uuid}/grades"
        response_course = requests.get(url_course, headers=headers)
        if response_course.status_code == 200:
            # Parse the JSON response.
            course_details = response_course.json()
            # print("Course Details:")
            # print(course_details)

            # Calculate class GPA
            test = course_details['cumulative']
            acount = test.get('aCount', 0)
            bcount = test.get('bCount', 0)
            ccount = test.get('cCount', 0)
            dcount = test.get('dCount', 0)
            fcount = test.get('fCount', 0)

            total_students = acount + bcount + ccount + dcount + fcount
            total_points = acount*4 + bcount*3 + ccount*2 + dcount*1 + fcount*0
            if total_students == 0:
                roundGPA = "N/A"
                #print(roundGPA)
            else:
                totalGPA = total_points / total_students
                roundGPA = round(totalGPA, 2)
                # print(roundGPA)
            # Save overall course GPA for later printing.
            course_info[course_key] = roundGPA

            if "courseOfferings" in course_details:
                for offering in course_details["courseOfferings"]:
                    for section in offering.get("sections", []):
                        a = section.get("aCount", 0)
                        b = section.get("bCount", 0)
                        c = section.get("cCount", 0)
                        d = section.get("dCount", 0)
                        f = section.get("fCount", 0)
                        section_total = a + b + c + d + f
                        if section_total == 0:
                            continue  # Skip sections with no graded students.
                        weighted = a*4 + b*3 + c*2 + d*1  # fCount contributes 0
                        section_gpa = weighted / section_total

                        # For each instructor in this section:
                        for instr in section.get("instructors", []):
                            prof_name = instr.get("name", "Unknown Instructor")

                            if prof_name not in professor_stats:
                                professor_stats[prof_name] = {"total_points": 0, "total_count": 0}
                            professor_stats[prof_name]["total_points"] += weighted
                            professor_stats[prof_name]["total_count"] += section_total

                            if prof_name not in professor_classes:
                                professor_classes[prof_name] = []
                            professor_classes[prof_name].append({
                                "course_name": i["name"],
                                "course_number": i["number"],
                                "section_number": section.get("sectionNumber"),
                                "section_gpa": round(section_gpa, 2),
                                "graded_count": section_total
                            })
        else:
            print(f"Error fetching details for course {i['name']}: {response_course.status_code}")

    course_prof_dict = {}
    for prof, sections in professor_classes.items():
        for rec in sections:
            course_key = f"{rec['course_name']} ({rec['course_number']})"
            if course_key not in course_prof_dict:
                course_prof_dict[course_key] = {}
            if prof not in course_prof_dict[course_key]:
                course_prof_dict[course_key][prof] = {"total_points": 0, "total_count": 0, "sections": []}
            # Multiply section GPA by graded count to accumulate weighted points.
            course_prof_dict[course_key][prof]["total_points"] += rec["section_gpa"] * rec["graded_count"]
            course_prof_dict[course_key][prof]["total_count"] += rec["graded_count"]
            course_prof_dict[course_key][prof]["sections"].append(rec)

    print("\nResults (Course and Professors):")
    for course_key in sorted(course_prof_dict.keys()):
        course_overall = course_info.get(course_key, "N/A")
        print(f"{course_key} (Course GPA: {course_overall})")
        for prof, stats in course_prof_dict[course_key].items():
            if stats["total_count"] > 0:
                prof_course_gpa = stats["total_points"] / stats["total_count"]
                print(f"  {prof} (Average GPA: {prof_course_gpa:.2f})")
            else:
                print(f"  {prof} (Average GPA: N/A)")
else:
    print(f"Error fetching data: {response.status_code}")

import csv

csv_rows = [["Course", "Course GPA", "Professor", "Professor Average GPA"]]
for course_key in sorted(course_prof_dict.keys()):
    course_overall = course_info.get(course_key, "N/A")
    for prof, stats in course_prof_dict[course_key].items():
        if stats["total_count"] > 0:
            prof_course_gpa = stats["total_points"] / stats["total_count"]
            prof_course_gpa = f"{prof_course_gpa:.2f}"
        else:
            prof_course_gpa = "N/A"
        csv_rows.append([course_key, course_overall, prof, prof_course_gpa])

with open("professor_course_gpa.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerows(csv_rows)

print("CSV file 'professor_course_gpa.csv' has been created.")
