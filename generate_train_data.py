import pandas as pd
import numpy as np

def rename_columns(input_csv, output_csv, mapping):
    # Read the CSV file into a DataFrame.
    df = pd.read_csv(input_csv)
    print("Original columns:", df.columns.tolist())

    # Rename the columns based on the provided mapping dictionary.
    df = df.rename(columns=mapping)

    # Define the required column names.
    required_columns = ["gpa", "prof_review", "grad_contrib", "admin_pref"]

    # Reorder columns to match the required order.
    df = df[required_columns]
    df["target_score"] = np.nan

    # Save the updated DataFrame to a new CSV file.
    df.to_csv(output_csv, index=False)
    print(f"CSV with updated headers saved as {output_csv}")


def main():
    input_csv = "train.csv"
    output_csv = "train_formatted.csv"

    # Define a mapping from your original column names to the required column names.
    # Update the keys below to match the column names in your original CSV.
    mapping = {
        "Total Class GPA": "gpa",  # e.g. original column for GPA
        "Professor Rating": "prof_review",  # e.g. original column for professor review
        "graduation_score": "grad_contrib",  # if already matching, you can still include it
        "admin_preference": "admin_pref",  # e.g. original admin preference column
        "target": "target_score"  # e.g. original target score column
    }

    rename_columns(input_csv, output_csv, mapping)


if __name__ == "__main__":
    main()
