import pandas as pd
import random


def add_scores_to_csv(input_csv, output_csv, scores):
    # Load the CSV file
    df = pd.read_csv(input_csv)
    num_rows = len(df)

    # Adjust the scores array to match the number of rows:
    # If there are fewer scores than rows, append random integers between 8 and 10.
    # If there are more scores, trim the list.
    if len(scores) < num_rows:
        missing_count = num_rows - len(scores)
        random_scores = [random.randint(8, 10) for _ in range(missing_count)]
        scores.extend(random_scores)
    elif len(scores) > num_rows:
        scores = scores[:num_rows]

    # Append the scores as a new column
    df['graduation_score'] = scores

    # Save the updated DataFrame to a new CSV file
    df.to_csv(output_csv, index=False)
    print(f"Updated CSV file saved as {output_csv}")

def add_admin_preference(input_csv, output_csv, num_preferred=5):
    """
    Adds an 'admin preference' column to the DataFrame.
    All rows are initially set to 0. Then, a specified number (default 5)
    of rows are randomly selected and set to 1.
    """
    df = pd.read_csv(input_csv)
    num_rows = len(df)
    admin_preference = [0] * num_rows

    # Ensure num_preferred does not exceed the number of rows.
    num_preferred = min(num_preferred, num_rows)
    indices = random.sample(range(num_rows), num_preferred)
    for idx in indices:
        admin_preference[idx] = 1

    df['admin_preference'] = admin_preference
    df.to_csv(output_csv, index=False)
    print(f"Updated CSV file saved as {output_csv}")

def main():
    # File paths (adjust as needed)
    input_csv = "courses.csv"
    output_csv = "courses_with_scores.csv"

    # Replace this with the actual returned scores array from GPT-4.
    # For demonstration, an example scores array is provided.
    scores = [10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 8, 8,
              8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 10, 10, 10, 10, 10, 10, 10, 10, 10,
              10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,
              9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10,
              10, 10, 10, 10, 10, 10, 10, 10]
    # Ensure the length matches the number of rows in courses.csv
    add_scores_to_csv(input_csv, output_csv, scores)
    add_admin_preference(output_csv, output_csv)

if __name__ == "__main__":
    main()
