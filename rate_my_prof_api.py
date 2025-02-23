import requests
import json

# Define the Rate My Professors GraphQL endpoint
url = "https://www.ratemyprofessors.com/graphql"

# Set up HTTP headers. A User-Agent header is included to mimic a real browser.
headers = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0"
}

# Define the GraphQL query for searching teachers.
# This query searches for teachers matching the provided query string.
query = """
query SearchTeachers($query: String!) {
  searchTeachers(query: $query, schoolID: "0") {
    teachers {
      id
      firstName
      lastName
      avgRating
      numRatings
      school {
        name
      }
    }
  }
}
"""

# Set the query variables.
# Replace "John" with the teacher name or keyword you wish to search.
variables = {
    "query": "John"
}

# Build the JSON payload with the query and variables.
payload = {
    "query": query,
    "variables": variables
}

# Send the POST request to the endpoint.
response = requests.post(url, headers=headers, json=payload)

# Check if the request was successful.
if response.status_code == 200:
    data = response.json()
    # Navigate the JSON to find the list of teachers.
    teachers = data.get("data", {}).get("searchTeachers", {}).get("teachers", [])

    if teachers:
        print("Teachers found:")
        for teacher in teachers:
            first_name = teacher.get("firstName", "")
            last_name = teacher.get("lastName", "")
            avg_rating = teacher.get("avgRating", "N/A")
            num_ratings = teacher.get("numRatings", 0)
            school_name = teacher.get("school", {}).get("name", "Unknown School")
            print(f"{first_name} {last_name} - Avg Rating: {avg_rating} ({num_ratings} ratings) at {school_name}")
    else:
        print("No teachers found for the given query.")
else:
    print(f"Error fetching data: {response.status_code}")
    print(response.text)
