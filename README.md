# Data Cleaning & Exploration with Pandas

A beginner-friendly data cleaning project built with Python and Pandas, submitted as part of my Data Analytics internship assignment.

The project takes a deliberately messy customer dataset, finds every data-quality problem in it, fixes them step by step, and runs basic statistical and categorical analysis on the cleaned result.

---

## Project Structure

```
Data-Cleaning-Exploration-with-Pandas/
├── customer_data.csv            # Raw dataset with intentional problems
├── data_cleaning.py             # Main cleaning script
├── cleaned_customer_data.csv    # Output (created by the script)
├── Data_Cleaning_Report.md      # Full project report
├── sample_output.txt            # Terminal output from a test run
└── README.md
```

---

## Dataset

`customer_data.csv` has 20 rows and 8 columns: `CustomerID`, `Name`, `Age`, `Gender`, `City`, `SignupDate`, `PurchaseAmount`, `MembershipType`.

Six types of data-quality problems were added on purpose:

| Problem | Example |
|---|---|
| Missing values | 8 blank cells across 6 columns |
| Duplicate records | Customer 1 and Customer 8 appear twice |
| Incorrect data types | `Age`, `PurchaseAmount`, `SignupDate` all loaded as text |
| Invalid numbers | Age of -5, age of 200, purchase of -450 |
| Inconsistent text | `male` vs `Male`, `delhi` vs `Delhi` |
| Mixed date formats | `2022-01-15` and `15/03/2022` in the same column |

---

## What the Script Does

1. Loads the CSV with `pd.read_csv()` (with error handling for a missing file)
2. Displays the original dataset, its shape and column info
3. Checks for missing values and duplicate records
4. Identifies the incorrect data types and explains why they happened
5. Converts numeric columns with `pd.to_numeric(errors="coerce")`
6. Detects and removes invalid values (negative ages, impossible ages, negative amounts)
7. Converts the date column with `pd.to_datetime()`, handling both date formats
8. Fills missing numeric values with the **median**
9. Fills missing categorical values with `"Unknown"` or the **mode**
10. Removes duplicate rows with `drop_duplicates()`
11. Prints a before/after comparison table
12. Runs statistical analysis: mean, median, min, max, std, `describe()`
13. Runs categorical analysis with `value_counts()` and `groupby()`
14. Saves the result as `cleaned_customer_data.csv`

---

## Results

| | Before Cleaning | After Cleaning |
|---|---|---|
| Total rows | 20 | 18 |
| Missing values | 8 | 1 |
| Duplicate rows | 2 | 0 |
| Age data type | object (text) | int64 |
| PurchaseAmount data type | object (text) | float64 |
| SignupDate data type | object (text) | datetime64 |
| Invalid values | 3 | 0 |

**Statistics on the cleaned data:**

| Statistic | Age | PurchaseAmount |
|---|---|---|
| Mean | 30.78 | 4564.00 |
| Median | 29.00 | 4100.00 |
| Min | 22.00 | 1250.00 |
| Max | 45.00 | 8900.00 |
| Std deviation | 5.79 | 2006.35 |

**Key insight:** Gold members spend an average of ₹5,725 per purchase compared to ₹3,500 for Bronze members — roughly 1.6x more.

---

## How to Run

**Requirements:** Python 3.8 or above

```bash
# 1. Clone the repository
git clone https://github.com/GagankumarMG/Data-Cleaning-Exploration-with-Pandas.git
cd Data-Cleaning-Exploration-with-Pandas

# 2. Install Pandas
pip install pandas

# 3. Run the script
python data_cleaning.py
```

The full cleaning report prints to the terminal, and `cleaned_customer_data.csv` is created in the project folder.

### Running in VS Code

1. `File` → `Open Folder` → select the project folder
2. Install the **Python** extension by Microsoft from the Extensions tab
3. Open the terminal with `Ctrl + ~` and run `pip install pandas`
4. Click the ▶ Run button, or run `python data_cleaning.py`

---

## A Bug Worth Mentioning

My first version of the date conversion used `pd.to_datetime(format="mixed", dayfirst=True)`. It ran without any error message, but when I printed the cleaned table I noticed `2022-04-05` had silently become 5 April instead of 4 May — `dayfirst=True` was being applied to the ISO-format dates as well.

I fixed it by parsing one format at a time:

```python
dates_format_1 = pd.to_datetime(date_text, format="%Y-%m-%d", errors="coerce")
dates_format_2 = pd.to_datetime(date_text, format="%d/%m/%Y", errors="coerce")
clean_data["SignupDate"] = dates_format_1.fillna(dates_format_2)
```

The lesson: code running without an error does not mean the output is correct. Always check the actual result.

---

## Report

The full write-up — objective, dataset description, every problem found, the reasoning behind each cleaning decision, complete analysis and conclusion — is in [`Data_Cleaning_Report.md`](Data_Cleaning_Report.md).

---

## Author

**Gagan Kumar M G**
Data Analytics Internship Project
