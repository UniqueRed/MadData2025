import pandas as pd

# Define base weights based on course role
BASE_WEIGHTS = {
    "Core": 1.0,
    "Foundational": 0.8,
    "Elective": 0.5
}


def get_user_majors():
    """
    Prompt the user to enter their majors as a comma-separated list.
    Returns a list of trimmed major strings.
    """
    user_input = input("Enter your majors (comma separated): ")
    majors = [m.strip() for m in user_input.split(",") if m.strip()]
    return majors


def calculate_contribution(row, user_majors):
    """
    Calculate the 'Contribution to Graduation' for a given course row.

    The calculation uses:
      - A base weight depending on the course role.
      - A multiplier based on how many of the course's applicable majors
        match the student's chosen majors.

    Multiplier = 1 + 0.5 * (N - 1)
    where N is the number of majors (from the course's 'Majors' column)
    that match the student's declared majors.
    """
    role = row.get("Role", "").strip()
    base_weight = BASE_WEIGHTS.get(role, 0.5)

    # Assumes the "Majors" column lists applicable majors separated by semicolons.
    course_majors = [m.strip() for m in str(row.get("Majors", "")).split(";") if m.strip()]

    # Count how many of the student's majors match this course.
    count = sum(1 for m in course_majors if m in user_majors)

    # If the course does not apply to any of the student's majors, its contribution is 0.
    if count == 0:
        return 0

    # Apply bias multiplier: if course counts for more than one major, boost the weight.
    multiplier = 1 + 0.5 * (count - 1)
    return base_weight * multiplier


def main():
    # Read the original CSV file.
    df = pd.read_csv("courses.csv")

    # Prompt user for their majors (e.g., "Mathematics, Data Science")
    user_majors = get_user_majors()

    # Compute the new column "Contribution to Graduation" for each course.
    df["Contribution to Graduation"] = df.apply(lambda row: calculate_contribution(row, user_majors), axis=1)

    # Write the updated DataFrame to a new CSV file.
    output_csv = "courses_with_contribution.csv"
    df.to_csv(output_csv, index=False)
    print(f"Updated CSV written to '{output_csv}'.\n")

    # Print the entire updated CSV file to the console.
    print("Updated CSV File:")
    print(df.to_csv(index=False))


if __name__ == "__main__":
    main()
