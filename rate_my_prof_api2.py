import pandas as pd
import random

# Define file paths
input_csv = "courses_output.csv"
output_csv = "courses.csv"

# Read the CSV file into a DataFrame
df = pd.read_csv(input_csv)

def generate_biased_rating():
    """
    Generates a random professor rating between 3.5 and 5.
    Uses a beta distribution to bias the values toward the higher end.
    Adjust the alpha and beta parameters to change the skew.
    """
    # Generate a beta random variable between 0 and 1; here, alpha > beta biases towards 1.
    beta_val = random.betavariate(5, 2)  # Mean ~0.714, most values closer to 1
    # Scale the beta value to the desired range: 3.5 to 5
    rating = 2.5 + beta_val * (5 - 3.5)
    return round(rating, 2)

# Create the new column using the biased rating generator
df["Professor Rating"] = [generate_biased_rating() for _ in range(len(df))]

# Save the updated DataFrame to a new CSV file.
df.to_csv(output_csv, index=False)

print(f"New CSV saved as '{output_csv}' with dummy professor ratings biased toward 3.5-5.")
