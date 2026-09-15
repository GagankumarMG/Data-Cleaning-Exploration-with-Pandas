"""
=============================================================
 Data Cleaning & Exploration with Pandas
 Internship Project
-------------------------------------------------------------
 What this script does:
   1. Loads a messy customer dataset (customer_data.csv)
   2. Explores it and finds the data quality problems
   3. Cleans the data step by step
   4. Does basic statistical and categorical analysis
   5. Saves the clean data as cleaned_customer_data.csv

 Requirement:  pip install pandas
 Run with:     python data_cleaning.py
=============================================================
"""

import os
import pandas as pd

# File names (kept in variables so they are easy to change)
INPUT_FILE = "customer_data.csv"
OUTPUT_FILE = "cleaned_customer_data.csv"

# Make pandas show all columns nicely in the terminal
pd.set_option("display.width", 120)
pd.set_option("display.max_columns", 20)


def print_heading(title):
    """Small helper function to print a clean section heading."""
    print("\n" + "=" * 65)
    print(title)
    print("=" * 65)


def load_data(file_name):
    """
    Load the CSV file into a DataFrame.
    Uses try-except so the program does not crash if the file is missing.
    """
    try:
        # Build the path relative to this script so it runs from any folder
        script_folder = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(script_folder, file_name)

        data = pd.read_csv(file_path)
        print(f"File '{file_name}' loaded successfully.")
        return data

    except FileNotFoundError:
        print(f"ERROR: Could not find '{file_name}'.")
        print("Make sure the CSV file is in the same folder as this script.")
        return None
    except pd.errors.EmptyDataError:
        print(f"ERROR: The file '{file_name}' is empty.")
        return None


def main():
    # =========================================================
    # STEP 1 : LOAD THE DATASET
    # =========================================================
    print_heading("STEP 1 : LOADING THE DATASET")

    raw_data = load_data(INPUT_FILE)
    if raw_data is None:
        return  # Stop the program if loading failed

    # Keep a copy of the original data so we can compare later (before/after)
    original_data = raw_data.copy()

    print_heading("STEP 2 : ORIGINAL DATASET (BEFORE CLEANING)")
    print(original_data)

    # =========================================================
    # STEP 3 : BASIC INFORMATION ABOUT THE DATA
    # =========================================================
    print_heading("STEP 3 : SHAPE AND COLUMN INFORMATION")

    rows, columns = original_data.shape
    print(f"Number of rows    : {rows}")
    print(f"Number of columns : {columns}")
    print(f"Column names      : {list(original_data.columns)}")

    print("\n--- Detailed column info (df.info()) ---")
    original_data.info()

    print("\n--- Data types of each column ---")
    print(original_data.dtypes)

    # =========================================================
    # STEP 4 : CHECK FOR MISSING VALUES
    # =========================================================
    print_heading("STEP 4 : CHECKING FOR MISSING VALUES (BEFORE CLEANING)")

    missing_before = original_data.isnull().sum()
    print(missing_before)
    print(f"\nTotal missing values in the dataset: {missing_before.sum()}")

    # =========================================================
    # STEP 5 : CHECK FOR DUPLICATE RECORDS
    # =========================================================
    print_heading("STEP 5 : CHECKING FOR DUPLICATE RECORDS")

    duplicate_count = original_data.duplicated().sum()
    print(f"Number of fully duplicated rows: {duplicate_count}")

    if duplicate_count > 0:
        print("\nThese are the duplicated rows:")
        print(original_data[original_data.duplicated(keep=False)])

    # =========================================================
    # STEP 6 : IDENTIFY INCORRECT DATA TYPES
    # =========================================================
    print_heading("STEP 6 : IDENTIFYING INCORRECT DATA TYPES")

    print("Age            -> should be a number, but pandas read it as text")
    print("PurchaseAmount -> should be a number, but pandas read it as text")
    print("SignupDate     -> should be a date, but pandas read it as text")
    print("\nReason: these columns contain values like 'twenty five',")
    print("'1,250.00' and 'abc', so pandas treats the whole column as text.")

    # Work on a copy from here onwards. This copy becomes the cleaned data.
    clean_data = original_data.copy()

    # =========================================================
    # STEP 7 : CONVERT NUMERIC COLUMNS USING pd.to_numeric()
    # =========================================================
    print_heading("STEP 7 : CONVERTING NUMERIC COLUMNS")

    # Remove commas first (example: "1,250.00" -> "1250.00")
    clean_data["PurchaseAmount"] = (
        clean_data["PurchaseAmount"].astype(str).str.replace(",", "", regex=False)
    )

    # errors="coerce" turns anything that is not a number into NaN (blank)
    clean_data["Age"] = pd.to_numeric(clean_data["Age"], errors="coerce")
    clean_data["PurchaseAmount"] = pd.to_numeric(
        clean_data["PurchaseAmount"], errors="coerce"
    )

    print("Age and PurchaseAmount converted to numeric.")
    print("Text values like 'twenty five' and 'abc' became NaN (missing).")
    print("\nData types now:")
    print(clean_data[["Age", "PurchaseAmount"]].dtypes)

    # =========================================================
    # STEP 8 : HANDLE INVALID NUMERIC VALUES
    # =========================================================
    print_heading("STEP 8 : HANDLING INVALID NUMERIC VALUES")

    # An age below 0 or above 100 is not realistic for a customer
    invalid_age = clean_data[(clean_data["Age"] < 0) | (clean_data["Age"] > 100)]
    print(f"Invalid ages found (below 0 or above 100): {len(invalid_age)}")
    if len(invalid_age) > 0:
        print(invalid_age[["CustomerID", "Name", "Age"]])

    # A purchase amount cannot be negative
    invalid_amount = clean_data[clean_data["PurchaseAmount"] < 0]
    print(f"\nInvalid purchase amounts found (negative): {len(invalid_amount)}")
    if len(invalid_amount) > 0:
        print(invalid_amount[["CustomerID", "Name", "PurchaseAmount"]])

    # Replace these invalid values with NaN so they can be filled later
    clean_data.loc[(clean_data["Age"] < 0) | (clean_data["Age"] > 100), "Age"] = pd.NA
    clean_data.loc[clean_data["PurchaseAmount"] < 0, "PurchaseAmount"] = pd.NA
    clean_data["Age"] = pd.to_numeric(clean_data["Age"], errors="coerce")
    clean_data["PurchaseAmount"] = pd.to_numeric(
        clean_data["PurchaseAmount"], errors="coerce"
    )
    print("\nInvalid values replaced with NaN (they will be filled in Step 10).")

    # =========================================================
    # STEP 9 : CONVERT THE DATE COLUMN USING pd.to_datetime()
    # =========================================================
    print_heading("STEP 9 : CONVERTING THE DATE COLUMN")

    # The dataset has two different date formats: 2022-01-15 and 15/03/2022.
    # The safest way is to try one format at a time instead of letting pandas
    # guess, because guessing can read 2022-04-05 as 5 April instead of 4 May.
    date_text = clean_data["SignupDate"].astype(str).str.strip()

    # Try the first format (year-month-day). errors="coerce" gives NaT if it fails
    dates_format_1 = pd.to_datetime(date_text, format="%Y-%m-%d", errors="coerce")

    # Try the second format (day/month/year) on the same column
    dates_format_2 = pd.to_datetime(date_text, format="%d/%m/%Y", errors="coerce")

    # Keep format 1 where it worked, otherwise take the value from format 2
    clean_data["SignupDate"] = dates_format_1.fillna(dates_format_2)

    print("SignupDate converted to datetime.")
    print(f"New data type: {clean_data['SignupDate'].dtype}")
    print(f"Missing dates (NaT) after conversion: {clean_data['SignupDate'].isna().sum()}")
    print("\nFirst 5 signup dates:")
    print(clean_data["SignupDate"].head())

    # =========================================================
    # STEP 10 : HANDLE MISSING NUMERIC VALUES (USING MEDIAN)
    # =========================================================
    print_heading("STEP 10 : FILLING MISSING NUMERIC VALUES WITH THE MEDIAN")

    # Median is used instead of mean because it is not affected by outliers
    age_median = clean_data["Age"].median()
    amount_median = clean_data["PurchaseAmount"].median()

    print(f"Missing Age values before filling            : {clean_data['Age'].isna().sum()}")
    print(f"Missing PurchaseAmount values before filling : {clean_data['PurchaseAmount'].isna().sum()}")
    print(f"\nMedian Age            : {age_median}")
    print(f"Median PurchaseAmount : {amount_median}")

    clean_data["Age"] = clean_data["Age"].fillna(age_median)
    clean_data["PurchaseAmount"] = clean_data["PurchaseAmount"].fillna(amount_median)

    # Age should be a whole number, so convert it to integer
    clean_data["Age"] = clean_data["Age"].astype(int)

    print(f"\nMissing Age values after filling            : {clean_data['Age'].isna().sum()}")
    print(f"Missing PurchaseAmount values after filling  : {clean_data['PurchaseAmount'].isna().sum()}")

    # =========================================================
    # STEP 11 : HANDLE MISSING CATEGORICAL VALUES
    # =========================================================
    print_heading("STEP 11 : FILLING MISSING CATEGORICAL VALUES")

    # First fix inconsistent spelling: "male"/"Male", "delhi"/"Delhi"
    for column in ["Gender", "City", "MembershipType"]:
        clean_data[column] = clean_data[column].astype(str).str.strip().str.title()
        # astype(str) turns real NaN into the text "Nan", so convert it back
        clean_data[column] = clean_data[column].replace("Nan", pd.NA)

    print("Text cleaned: extra spaces removed and capitalisation made consistent.")

    # Gender and City: we cannot guess them, so we label them as "Unknown"
    clean_data["Gender"] = clean_data["Gender"].fillna("Unknown")
    clean_data["City"] = clean_data["City"].fillna("Unknown")

    # MembershipType: filled with the mode (the most common value)
    membership_mode = clean_data["MembershipType"].mode()[0]
    print(f"Most common MembershipType (mode): {membership_mode}")
    clean_data["MembershipType"] = clean_data["MembershipType"].fillna(membership_mode)

    print("\nMissing values in categorical columns now:")
    print(clean_data[["Gender", "City", "MembershipType"]].isnull().sum())

    # =========================================================
    # STEP 12 : REMOVE DUPLICATE RECORDS
    # =========================================================
    print_heading("STEP 12 : REMOVING DUPLICATE RECORDS")

    rows_before = clean_data.shape[0]
    clean_data = clean_data.drop_duplicates()          # remove exact duplicates
    clean_data = clean_data.reset_index(drop=True)     # renumber the rows
    rows_after = clean_data.shape[0]

    print(f"Rows before removing duplicates : {rows_before}")
    print(f"Rows after removing duplicates  : {rows_after}")
    print(f"Duplicate rows removed          : {rows_before - rows_after}")

    # =========================================================
    # STEP 13 : BEFORE AND AFTER COMPARISON
    # =========================================================
    print_heading("STEP 13 : BEFORE AND AFTER COMPARISON")

    comparison = pd.DataFrame(
        {
            "Before Cleaning": [
                original_data.shape[0],
                original_data.isnull().sum().sum(),
                original_data.duplicated().sum(),
                str(original_data["Age"].dtype),
                str(original_data["PurchaseAmount"].dtype),
                str(original_data["SignupDate"].dtype),
            ],
            "After Cleaning": [
                clean_data.shape[0],
                clean_data.isnull().sum().sum(),
                clean_data.duplicated().sum(),
                str(clean_data["Age"].dtype),
                str(clean_data["PurchaseAmount"].dtype),
                str(clean_data["SignupDate"].dtype),
            ],
        },
        index=[
            "Total rows",
            "Total missing values",
            "Duplicate rows",
            "Age data type",
            "PurchaseAmount data type",
            "SignupDate data type",
        ],
    )
    print(comparison)

    print_heading("STEP 14 : CLEANED DATASET (AFTER CLEANING)")
    print(clean_data)

    # =========================================================
    # STEP 15 : BASIC STATISTICAL ANALYSIS
    # =========================================================
    print_heading("STEP 15 : BASIC STATISTICAL ANALYSIS")

    numeric_columns = ["Age", "PurchaseAmount"]

    for column in numeric_columns:
        print(f"\n--- Statistics for {column} ---")
        print(f"Mean               : {clean_data[column].mean():.2f}")
        print(f"Median             : {clean_data[column].median():.2f}")
        print(f"Minimum            : {clean_data[column].min():.2f}")
        print(f"Maximum            : {clean_data[column].max():.2f}")
        print(f"Standard deviation : {clean_data[column].std():.2f}")

    print("\n--- Full summary using describe() ---")
    print(clean_data[numeric_columns].describe())

    # =========================================================
    # STEP 16 : CATEGORICAL ANALYSIS USING value_counts()
    # =========================================================
    print_heading("STEP 16 : CATEGORICAL ANALYSIS")

    print("--- Gender distribution ---")
    print(clean_data["Gender"].value_counts())

    print("\n--- Gender distribution in percentage ---")
    print((clean_data["Gender"].value_counts(normalize=True) * 100).round(2))

    print("\n--- City distribution ---")
    print(clean_data["City"].value_counts())

    print("\n--- Membership type distribution ---")
    print(clean_data["MembershipType"].value_counts())

    print("\n--- Average purchase amount by membership type ---")
    print(
        clean_data.groupby("MembershipType")["PurchaseAmount"]
        .mean()
        .round(2)
        .sort_values(ascending=False)
    )

    print("\n--- Number of customers who signed up each year ---")
    # dropna() ignores the row whose signup date was missing
    signup_years = clean_data["SignupDate"].dt.year.dropna().astype(int)
    print(signup_years.value_counts().sort_index())

    # =========================================================
    # STEP 17 : SAVE THE CLEANED DATASET
    # =========================================================
    print_heading("STEP 17 : SAVING THE CLEANED DATASET")

    try:
        script_folder = os.path.dirname(os.path.abspath(__file__))
        output_path = os.path.join(script_folder, OUTPUT_FILE)

        # index=False stops pandas from writing the row numbers into the file
        clean_data.to_csv(output_path, index=False)
        print(f"Cleaned dataset saved successfully as '{OUTPUT_FILE}'")
        print(f"Location: {output_path}")
    except Exception as error:
        print(f"ERROR: Could not save the file. Reason: {error}")

    print_heading("DATA CLEANING COMPLETED SUCCESSFULLY")


# This makes sure main() runs only when the file is executed directly
if __name__ == "__main__":
    main()
