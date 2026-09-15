# Data Cleaning & Exploration with Pandas

**Internship Project Report**

---

## 1. Project Objective

The objective of this project is to take a small, messy customer dataset and clean it using Python and the Pandas library. Real-world data is almost never ready to use — it usually has missing values, duplicate entries, wrong data types and values that simply do not make sense. Before any analysis or machine learning can be done, this data has to be fixed.

In this project I wanted to show the full process end to end:

1. Load a raw CSV file
2. Explore it and find out exactly what is wrong with it
3. Fix each problem one by one, printing the result at every step
4. Run basic statistical and categorical analysis on the cleaned data
5. Save the cleaned dataset as a new CSV file

---

## 2. Dataset Description

The dataset is stored in `customer_data.csv` and contains **20 rows and 8 columns** of customer information.

| Column | Description | Expected Type |
|---|---|---|
| CustomerID | Unique ID given to each customer | Integer |
| Name | Full name of the customer | Text |
| Age | Age of the customer in years | Integer |
| Gender | Male / Female | Text (category) |
| City | City the customer lives in | Text (category) |
| SignupDate | Date the customer registered | Date |
| PurchaseAmount | Total amount spent, in rupees | Float |
| MembershipType | Gold / Silver / Bronze | Text (category) |

The data-quality problems were added on purpose so that the cleaning process has something to actually work on.

---

## 3. Problems Found in the Dataset

After exploring the data with `.info()`, `.isnull().sum()` and `.duplicated()`, I found six different types of problems.

**a) Missing values — 8 blank cells in total**

| Column | Missing values |
|---|---|
| Age | 2 |
| Gender | 2 |
| City | 1 |
| SignupDate | 1 |
| PurchaseAmount | 1 |
| MembershipType | 1 |

**b) Duplicate records — 2 rows**

Customer ID 1 (Aarav Sharma) and Customer ID 8 (Priya Nair) each appeared twice, with every single column identical. This usually happens when data is entered twice or when two files get merged.

**c) Incorrect data types**

`Age`, `PurchaseAmount` and `SignupDate` were all loaded as text (object) instead of numbers and dates. The reason is that one bad value is enough to force the whole column into text:

- `Age` contained the word `twenty five`
- `PurchaseAmount` contained `abc` and also `1,250.00` (the comma makes it text)
- `SignupDate` was text because Pandas does not convert dates automatically

**d) Invalid numerical values — 3 values**

| Customer | Column | Value | Why it is wrong |
|---|---|---|---|
| Vikram Singh | Age | -5 | Age cannot be negative |
| Rahul Gupta | Age | 200 | Nobody is 200 years old |
| Arjun Das | PurchaseAmount | -450.00 | A purchase cannot be negative |

**e) Inconsistent text**

The same value was written in different ways — `male` and `Male`, `delhi` and `Delhi`, `bengaluru` and `Bengaluru`. Pandas treats these as different categories, which would break the `value_counts()` results.

**f) Mixed date formats**

Two formats were mixed in the same column: `2022-01-15` (year-month-day) and `15/03/2022` (day/month/year).

---

## 4. Data-Type Correction

**Numbers.** I first removed the commas from `PurchaseAmount` using `.str.replace(",", "")`, then converted both numeric columns with `pd.to_numeric(errors="coerce")`. The `errors="coerce"` part is important — instead of crashing on `twenty five` or `abc`, it turns those values into `NaN` so they can be filled later like any other missing value.

**Invalid values.** After the conversion I used a condition to find ages below 0 or above 100 and purchase amounts below 0, and replaced those with `NaN` as well. These are wrong values, so it is safer to treat them as missing than to keep them and let them spoil the average.

**Dates.** This was the trickiest part. My first attempt used `format="mixed", dayfirst=True`, but when I checked the output I noticed `2022-04-05` had become 5 April instead of 4 May — Pandas was applying day-first to the ISO dates too. So I changed the approach and parsed one format at a time:

```python
dates_format_1 = pd.to_datetime(date_text, format="%Y-%m-%d", errors="coerce")
dates_format_2 = pd.to_datetime(date_text, format="%d/%m/%Y", errors="coerce")
clean_data["SignupDate"] = dates_format_1.fillna(dates_format_2)
```

Format 1 is tried first, and wherever it fails the value is taken from format 2. This gave correct dates for both styles.

**Result of the type correction:**

| Column | Before | After |
|---|---|---|
| Age | object (text) | int64 |
| PurchaseAmount | object (text) | float64 |
| SignupDate | object (text) | datetime64 |

---

## 5. Missing-Value Handling

**Numerical columns — filled with the median.**

After converting the types, the number of missing values went *up*, because the invalid and text values had become `NaN` too:

| Column | Missing after conversion | Median used |
|---|---|---|
| Age | 5 | 29 |
| PurchaseAmount | 3 | 4100.00 |

I used the **median** and not the mean because the median is not affected by extreme values. In this dataset the purchase amounts go from 1,250 up to 8,900, so a couple of very large values would pull the mean upward and give a less representative fill value.

**Categorical columns.**

Before filling, I standardised the text with `.str.strip().str.title()` so that `male` became `Male` and `delhi` became `Delhi`.

- `Gender` and `City` were filled with **"Unknown"**. There is no honest way to guess somebody's gender or city, and inventing a value would create fake information. Labelling it "Unknown" keeps the row usable while being transparent that the data is missing.
- `MembershipType` was filled with the **mode** (most frequent value), which is `Gold`. For a plan type this is a reasonable assumption, since the most common category is the most likely one.

---

## 6. Duplicate Removal

Duplicates were found with `df.duplicated().sum()` and removed with `df.drop_duplicates()`, followed by `reset_index(drop=True)` to renumber the rows properly.

| | Rows |
|---|---|
| Before removing duplicates | 20 |
| After removing duplicates | 18 |
| **Duplicates removed** | **2** |

---

## 7. Statistical Analysis Performed

Calculated on the cleaned dataset using `mean()`, `median()`, `min()`, `max()`, `std()` and `describe()`.

| Statistic | Age | PurchaseAmount |
|---|---|---|
| Count | 18 | 18 |
| Mean | 30.78 | 4564.00 |
| Median | 29.00 | 4100.00 |
| Minimum | 22.00 | 1250.00 |
| Maximum | 45.00 | 8900.00 |
| Standard deviation | 5.79 | 2006.35 |

**What this tells us:** the customers are a fairly young group, mostly clustered around 29–31 years, and the small standard deviation of 5.79 confirms the ages are close together. Purchase amounts are much more spread out — a standard deviation of about 2,006 on a mean of 4,564 means spending habits vary a lot from customer to customer.

---

## 8. Categorical Analysis

Done using `value_counts()`.

**Gender distribution**

| Gender | Count | Percentage |
|---|---|---|
| Male | 9 | 50.00% |
| Female | 7 | 38.89% |
| Unknown | 2 | 11.11% |

**City distribution**

| City | Customers |
|---|---|
| Mumbai | 3 |
| Delhi | 3 |
| Bengaluru | 3 |
| Chennai | 2 |
| Hyderabad | 2 |
| Kolkata | 2 |
| Pune | 2 |
| Unknown | 1 |

**Membership type distribution**

| Membership | Customers |
|---|---|
| Gold | 8 |
| Silver | 5 |
| Bronze | 5 |

**Average purchase amount by membership type** (using `groupby()`)

| Membership | Average spend |
|---|---|
| Gold | 5,725.19 |
| Silver | 3,770.00 |
| Bronze | 3,500.10 |

This is the most interesting finding in the project. Gold members spend roughly 1.6 times more on average than Bronze members, which is exactly what you would hope to see from a tiered membership programme.

**Signups per year**

| Year | Signups |
|---|---|
| 2022 | 12 |
| 2023 | 5 |

(One customer's signup date was missing and is not counted here.)

---

## 9. Final Results

| Check | Before Cleaning | After Cleaning |
|---|---|---|
| Total rows | 20 | 18 |
| Total missing values | 8 | 1 |
| Duplicate rows | 2 | 0 |
| Age data type | object (text) | int64 |
| PurchaseAmount data type | object (text) | float64 |
| SignupDate data type | object (text) | datetime64 |
| Invalid values | 3 | 0 |
| Inconsistent text values | 3 | 0 |

The one remaining missing value is Kavya Menon's signup date. I deliberately left it as `NaT` rather than filling it, because a date is a factual event — making one up would be inventing data. It is better to keep it blank and be aware of it during analysis.

The cleaned dataset was saved as **`cleaned_customer_data.csv`** using `to_csv(index=False)`.

---

## 10. Conclusion

Working on this project taught me that data cleaning is not one single command — it is a sequence of decisions, and each one has to be justified. The main things I learned:

1. **Always look at the data first.** `.info()`, `.isnull().sum()` and `.duplicated()` took only three lines but showed me every problem I needed to fix.
2. **`errors="coerce"` is very useful.** It turns bad values into `NaN` instead of crashing the program, so type conversion and missing-value handling become one connected process.
3. **Missing values go up before they go down.** Converting the types raised the missing count from 8 to 11 because invalid values became `NaN`. That was confusing at first, but it is actually correct behaviour.
4. **Median over mean for filling numbers**, because outliers do not drag it around.
5. **Never invent data.** Filling gender with "Unknown" and leaving the missing date blank is more honest than guessing, even though it makes the dataset look less "complete".
6. **Always check your output, do not just trust the code.** My date conversion ran without any error message but was silently giving wrong dates. I only caught it because I printed the cleaned table and compared it against the original.

After cleaning, the dataset went from 20 messy rows to 18 reliable ones, with correct data types in every column and no duplicates. It is now in a state where it can be used for charts, reports or a machine-learning model.

---

## 11. How to Run This Project in VS Code

**Step 1 — Install Python**
Download Python from [python.org](https://www.python.org/downloads/) and tick **"Add Python to PATH"** during installation.

**Step 2 — Open the project folder**
Open VS Code → `File` → `Open Folder` → select the `data-cleaning-project` folder.

**Step 3 — Install the Python extension**
Go to the Extensions tab (`Ctrl+Shift+X`), search for **Python** by Microsoft, and install it.

**Step 4 — Install Pandas**
Open the terminal in VS Code with `Ctrl + ~` and run:

```bash
pip install pandas
```

**Step 5 — Run the script**

```bash
python data_cleaning.py
```

Or simply click the ▶ Run button at the top right of the editor.

**Step 6 — Check the output**
The full cleaning report prints in the terminal, and a new file called `cleaned_customer_data.csv` appears in the project folder.

---

### Project Structure

```
data-cleaning-project/
├── customer_data.csv            # Raw dataset with problems
├── data_cleaning.py             # Main cleaning script
├── cleaned_customer_data.csv    # Output (created by the script)
├── Data_Cleaning_Report.md      # This report
└── sample_output.txt            # Full terminal output from a test run
```

**Requirements:** Python 3.8 or above, Pandas
**Install command:** `pip install pandas`

---

*Submitted as part of my Data Analytics internship assignment.*
