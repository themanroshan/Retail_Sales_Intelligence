# RetailPulse — Complete Setup Guide (Windows 11)

> **Target audience:** Freshers preparing for Data Analyst and Business Analyst interviews  
> **Time required:** 1–2 hours (first-time setup including MySQL)  
> **Skill level:** Basic Python, MySQL, and Git knowledge assumed

---

## 📋 Prerequisites Checklist

Before starting, verify you have:

| Software       | Required Version | Check Command             | Download URL                           |
|----------------|------------------|---------------------------|----------------------------------------|
| Windows        | 10 or 11         | `winver`                  | —                                      |
| Python         | 3.11 or 3.12+    | `python --version`        | https://python.org                     |
| Git            | 2.0+             | `git --version`           | https://git-scm.com                    |
| MySQL Server   | 8.0+             | `mysql --version`         | https://dev.mysql.com/downloads/installer/ |
| MySQL Workbench| 8.0+             | GUI app                   | (included in MySQL installer)          |
| VS Code        | Latest           | —                         | https://code.visualstudio.com          |


---

## Part 1 — Software Installation (If Not Already Installed)

### 1.1 Install Python 3.11 or 3.12

1. Download from https://python.org/downloads/
2. ✅ Check "Add Python to PATH" during installation
3. Verify:

```powershell
python --version
```

Expected: `Python 3.11.x` or `Python 3.12.x` or `Python 3.14.x`

### 1.2 Install Git

1. Download from https://git-scm.com/download/win
2. Use default options during installation
3. Verify:

```powershell
git --version
```

### 1.3 Install MySQL 8.0

1. Download **MySQL Installer** (Windows):  
   https://dev.mysql.com/downloads/installer/

2. Choose **MySQL Installer Community** (450 MB)

3. During installation:
   - Select **Developer Default** setup type
   - Set root password (remember this — you'll need it for `.env`)
   - Leave port as **3306**
   - Install **MySQL Server 8.0** and **MySQL Workbench 8.0**

4. Verify installation:

Open MySQL Workbench → Connect to Local instance `root@localhost:3306` → Enter your root password

If connection succeeds, MySQL is installed correctly.

### 1.4 Install VS Code (Optional but Recommended)

1. Download from https://code.visualstudio.com
2. Install Python extension: `ms-python.python`
3. Install MySQL extension: `cweijan.vscode-mysql-client2` (optional)

---

## Part 2 — Repository Setup

### 2.1 Clone the Repository

Open PowerShell and navigate to your Desktop (or any folder):

```powershell
cd C:\Users\YourUsername\Desktop
git clone https://github.com/yourusername/Retail_Sales_Intelligence.git
cd Retail_Sales_Intelligence
```

If you haven't pushed to GitHub yet, you're already in the folder.

### 2.2 Verify Repository Structure

```powershell
dir
```

You should see:
```
app.py
requirements.txt
.env.example
.gitignore
data/
docs/
sql/
src/
tests/
...
```

---

## Part 3 — Python Environment Setup

### 3.1 Create Virtual Environment

```powershell
python -m venv .venv
```

This creates a `.venv` folder (don't commit it — it's in `.gitignore`).

### 3.2 Activate Virtual Environment

```powershell
.venv\Scripts\activate
```

Your prompt should now show `(.venv)` prefix.

### 3.3 Upgrade pip

```powershell
python -m pip install --upgrade pip
```

### 3.4 Install Project Dependencies

```powershell
pip install -r requirements.txt
```

**Expected packages installed:**
- pandas 3.1+
- numpy 2.5+
- mysql-connector-python 26.10+
- python-dotenv 1.2+
- streamlit 1.67+
- plotly 7.2+
- openpyxl 3.1+
- pytest 9.2+
- pytest-cov 7.1+
- tabulate 0.10+

**Installation time:** 2–5 minutes depending on internet speed.

### 3.5 Verify Installation

```powershell
python -c "import pandas, streamlit, plotly, openpyxl, pytest; print('All imports OK')"
```

Expected output: `All imports OK`

---

## Part 4 — Dataset Setup (Synthetic Data — No Download Needed)

### 4.1 Generate Synthetic Dataset

The project includes a synthetic data generator. Run:

```powershell
python src/pipeline.py --no-db
```

**What this does:**
1. Generates 10,000 synthetic transactions (seed=42, fully reproducible)
2. Cleans and validates the data (17 checks)
3. Saves `data/raw/retailpulse_transactions.csv`
4. Saves `data/processed/retailpulse_clean.csv`
5. Saves `data/sample/retailpulse_sample.csv` (500 rows)

**Expected output:**
```
===========================================================
RETAILPULSE ETL PIPELINE
===========================================================
[pipeline] Generating synthetic dataset …
[pipeline] Raw shape  : 10,000 rows × 14 columns
[pipeline] Date range : 2022-01-01 → 2024-12-31
[pipeline] Cleaning data …

CLEANING AUDIT SUMMARY
  Original rows    : 10,000
  Clean rows       : 10,000
  Quarantined rows : 0
  Retention rate   : 100.0%
...

DATA VALIDATION REPORT
  ✓ [PASS] row_count_positive       10,000 rows
  ✓ [PASS] no_nulls_order_id        0 nulls
  ...
  Overall: PASS | PASS: 17 | WARN: 0 | FAIL: 0

PIPELINE COMPLETE
  Clean rows available : 10,000
  Processed CSV        : ...\data\processed\retailpulse_clean.csv
===========================================================
```

✅ **If you see 17/17 validation checks PASS, the pipeline ran successfully.**

### 4.2 Verify Data Files

```powershell
dir data\raw
dir data\processed
```

You should see:
- `data\raw\retailpulse_transactions.csv` (10,000 rows)
- `data\processed\retailpulse_clean.csv` (10,000 rows)

---

## Part 5 — Run the Streamlit Dashboard (CSV Mode)

You can run the dashboard **without MySQL** using CSV data:

### 5.1 Launch Streamlit

```powershell
streamlit run app.py
```

**Expected output:**
```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.x.x:8501
```

### 5.2 Open the Dashboard

Your browser opens automatically at http://localhost:8501

### 5.3 Explore the Dashboard

You should see 5 pages in the sidebar:
1. 🏠 Executive Overview
2. 📦 Product & Category
3. 📅 Time Analysis
4. 🗺 Regional Analytics
5. 🔍 Data Quality

**Data notice banner** will appear at the top of every page confirming this is synthetic data.

**Test filters:**
- Sidebar: Filter by Year, Category, State
- Charts should update dynamically
- Try the "Download filtered data as CSV" button

### 5.4 Stop Streamlit

Press `Ctrl+C` in the terminal where Streamlit is running.

---

## Part 6 — MySQL Setup (Optional for Full Project)

If you want to load data into MySQL and run SQL queries:

### 6.1 Configure MySQL Credentials

1. Copy the `.env.example` file to `.env`:

```powershell
copy .env.example .env
```

2. Open `.env` in Notepad or VS Code
3. Update with your MySQL credentials:

```
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_actual_root_password_here
MYSQL_DATABASE=retailpulse
DATA_SOURCE=mysql
```

**⚠️ NEVER commit `.env` to Git — it's already in `.gitignore`**

### 6.2 Test MySQL Connection

```powershell
python -c "from src.database import test_connection; print('MySQL OK' if test_connection() else 'MySQL FAIL')"
```

Expected output: `MySQL OK`

If you get `MySQL FAIL`, check:
- MySQL Server is running (check Windows Services)
- Password in `.env` is correct
- Port 3306 is not blocked by firewall

### 6.3 Run Pipeline with MySQL

```powershell
python src/pipeline.py
```

(Remove `--no-db` flag to enable MySQL loading)

**Expected output:**
```
[pipeline] Loading into MySQL …
[database] Database 'retailpulse' is ready.
[database] Tables created.
[database] dim_product: 2,345 rows inserted (INSERT IGNORE).
[database] dim_location: 36 rows inserted (INSERT IGNORE).
[database] dim_date: 1,096 rows inserted (INSERT IGNORE).
[database] fact_sales: 10,000 rows inserted (INSERT IGNORE).
[pipeline] MySQL load complete. Database: retailpulse
```

### 6.4 Verify MySQL Tables

Open **MySQL Workbench**:
1. Connect to `localhost:3306` as `root`
2. Select database `retailpulse`
3. Run:

```sql
SHOW TABLES;
```

You should see:
```
+----------------------+
| Tables_in_retailpulse|
+----------------------+
| dim_date             |
| dim_location         |
| dim_product          |
| fact_sales           |
+----------------------+
```

### 6.5 Run a Test Query

```sql
USE retailpulse;

SELECT
    COUNT(DISTINCT order_id) AS total_orders,
    ROUND(SUM(sales_amount), 2) AS total_sales_inr
FROM fact_sales;
```

Expected result: `10000 | 74447185.53`

---

## Part 7 — Run SQL Analysis Scripts

Open MySQL Workbench and run these scripts in order:

### 7.1 Database Setup (Already Done by Pipeline)

```sql
-- File: sql/01_database_setup.sql
-- Already executed by the pipeline, but you can re-run for safety
```

### 7.2 Create Tables (Already Done by Pipeline)

```sql
-- File: sql/02_create_tables.sql
-- Already executed by the pipeline
```

### 7.3 Data Quality Checks

```sql
-- File: sql/03_data_quality_checks.sql
-- Copy-paste the entire file into MySQL Workbench
-- Press Ctrl+Shift+Enter to run all
```

**Expected result:** All checks return 0 problem rows.

### 7.4 Exploratory Analysis

```sql
-- File: sql/04_exploratory_analysis.sql
-- Run each query individually (Ctrl+Enter)
-- Review results for each business question
```

### 7.5 Business Analysis (14 Questions)

```sql
-- File: sql/05_business_analysis.sql
-- Contains 14 business questions (BQ-01 through BQ-14)
-- Run each query and review output
```

**Example:**
```sql
-- BQ-01: What is total recorded sales?
SELECT ROUND(SUM(sales_amount), 2) AS total_sales_inr
FROM fact_sales;

-- Expected: 74447185.53
```

### 7.6 Advanced Analysis (Window Functions, CTEs)

```sql
-- File: sql/06_advanced_analysis.sql
-- Demonstrates running totals, ranking, ROW_NUMBER, LAG, etc.
```

---

## Part 8 — Run Tests

### 8.1 Run Full Test Suite

```powershell
python -m pytest tests/ -v
```

**Expected output:**
```
======================== test session starts =========================
collected 74 items

tests/test_analytics.py::test_total_sales_positive PASSED       [  1%]
...
tests/test_database.py::test_connection_succeeds PASSED         [ 72%]
...
tests/test_pipeline.py::test_full_pipeline_no_db PASSED         [100%]

========== 67 passed, 7 skipped in 3.00s ===========
```

**67 passed, 7 skipped** = ✅ PERFECT

(7 skipped tests are MySQL tests — they pass when MySQL is configured)

### 8.2 Run with Coverage Report

```powershell
python -m pytest tests/ --cov=src --cov-report=term-missing
```

This shows which lines of code are tested.

---

## Part 9 — Generate Excel Workbook

### 9.1 Run Excel Export

```powershell
python src/excel_export.py
```

**Expected output:**
```
[excel_export] Saved → C:\...\excel\RetailPulse_Analysis.xlsx
Excel workbook ready: ...\excel\RetailPulse_Analysis.xlsx
```

### 9.2 Open the Excel File

```powershell
start excel\RetailPulse_Analysis.xlsx
```

**Excel contents (10 sheets):**
1. Executive Summary — 8 KPIs + top categories
2. Cleaned Data — first 5,000 rows
3. Monthly Analysis — Monthly sales + MoM growth
4. Category Analysis — Category + sub-category tables
5. Product Analysis — Top 20 products by sales
6. Regional Analysis — Sales by state
7. Payment Methods — Sales by payment channel
8. Discount Analysis — Discount bucket impact
9. KPI Definitions — Formula reference
10. Data Quality — Row counts, nulls, date range

---

## Part 10 — Explore the Dashboard (Full MySQL Mode)

### 10.1 Restart Streamlit with MySQL

```powershell
# Ensure DATA_SOURCE=mysql in .env
streamlit run app.py
```

The dashboard now reads from MySQL instead of CSV.

### 10.2 Verify Data Source

On the **Data Quality** page, you should see:
- Total clean rows: 10,000
- Date range: 2022-01-01 → 2024-12-31

If you filter by Year=2023 in the sidebar, all KPIs and charts update dynamically.

---

## Part 11 — GitHub Upload (If Not Already Done)

### 11.1 Initialize Git (If Needed)

```powershell
git init
git add .
git commit -m "Initial commit: RetailPulse project complete"
```

### 11.2 Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: `Retail_Sales_Intelligence`
3. Description: "End-to-end retail sales intelligence using Python, MySQL, SQL, and Streamlit"
4. Public repository
5. Do NOT initialize with README (you already have one)
6. Click **Create repository**

### 11.3 Push to GitHub

```powershell
git remote add origin https://github.com/yourusername/Retail_Sales_Intelligence.git
git branch -M main
git push -u origin main
```

**⚠️ Verify `.gitignore` excludes:**
- `.env` (contains MySQL password)
- `data/raw/*.csv` (large data files)
- `data/processed/*.csv`
- `.venv/`

### 11.4 Add README Badges (Optional)

Edit `README.md` and update the GitHub username in the clone command and badges.

---

## Part 12 — Deployment to Streamlit Cloud (Optional)

### 12.1 Push to GitHub (Already Done in Part 11)

### 12.2 Deploy to Streamlit Cloud

1. Go to https://share.streamlit.io
2. Click **New app**
3. Connect your GitHub repository
4. Repository: `yourusername/Retail_Sales_Intelligence`
5. Branch: `main`
6. Main file path: `app.py`
7. Click **Deploy**

**Deployment time:** 3–5 minutes

### 12.3 Configure Environment Variables (If Using MySQL)

In Streamlit Cloud settings → Secrets:

```toml
MYSQL_HOST = "your-mysql-host"
MYSQL_PORT = 3306
MYSQL_USER = "your-mysql-user"
MYSQL_PASSWORD = "your-mysql-password"
MYSQL_DATABASE = "retailpulse"
DATA_SOURCE = "mysql"
```

**For CSV-only mode (recommended for free tier):**

Leave secrets empty. The dashboard will read from the processed CSV which is included in the repository (it's synthetic data, so it's safe to commit).

### 12.4 Access Your Live Dashboard

After deployment, Streamlit provides a public URL:

```
https://yourusername-retail-sales-intelligence-app-xyz123.streamlit.app
```

Share this URL in your resume, LinkedIn, and job applications.

---

## Part 13 — Interview Preparation

### 13.1 Read Interview Guide

```powershell
start docs\INTERVIEW_PREPARATION.md
```

This file contains:
- 60-second project pitch
- 2-minute detailed explanation
- STAR-format stories
- 50 technical questions with answers
- SQL questions based on the actual schema
- Python/Pandas questions
- Business analyst questions

### 13.2 Practice SQL Queries

Open MySQL Workbench and practice running these without looking at the solution:

1. What is the total sales by category?
2. What is the average order value?
3. Which products are in the top 10 by sales?
4. What is the month-over-month growth rate?
5. What is the sales contribution of each state?

**Interviewer challenge:** "Walk me through how you would calculate profit margin by category."

### 13.3 Practice Dashboard Demo

1. Launch `streamlit run app.py`
2. Practice explaining each page out loud:
   - "This dashboard has 5 pages…"
   - "On the Executive Overview, we see 8 KPIs…"
   - "I can filter by year, category, and state…"
3. Time yourself: aim for 2 minutes to cover all features.

### 13.4 Prepare Project Walkthrough (5 Minutes)

Practice explaining:
1. Business problem (30 seconds)
2. Data source and disclaimer (20 seconds — SYNTHETIC)
3. Architecture: Python ETL → MySQL → SQL analysis → Streamlit dashboard (1 minute)
4. Key findings: Top category, top state, profit margins (1 minute)
5. Challenges faced: (e.g., data cleaning logic, window functions) (1 minute)
6. Skills demonstrated: SQL, Python, BI, testing (30 seconds)

---

## Part 14 — Resume Integration

### 14.1 Add to Resume

**Project section:**

```
RetailPulse — Indian Retail Sales Intelligence            Oct 2024 – Nov 2024
GitHub: github.com/yourusername/Retail_Sales_Intelligence | Live: streamlit.app/yourapp

• Built an end-to-end retail sales analytics platform processing 10,000 synthetic 
  transactions (₹74.4M sales) using Python (Pandas, NumPy), MySQL 8.0, and Streamlit
• Designed a MySQL star schema (4 tables: fact_sales, dim_product, dim_location, 
  dim_date) with foreign key constraints and indexes for query optimization
• Wrote 50+ SQL queries (JOINs, CTEs, window functions, subqueries) answering 14 
  business questions including category contribution, regional performance, and discount impact
• Developed a 5-page interactive Streamlit dashboard with Plotly visualizations, 
  KPI cards, sidebar filters, and CSV export functionality
• Implemented 67 Pytest tests (100% passed) covering data cleaning (11 rules), 
  validation (17 checks), analytics, and pipeline integration
• Automated Excel report generation (10 sheets, 657KB) using OpenPyXL for stakeholder 
  distribution
```

### 14.2 Add to LinkedIn

**Project section:**

Title: **RetailPulse — Indian Retail Sales Intelligence**

Description:
```
Complete data analytics portfolio project demonstrating end-to-end BI workflow.

🔧 Tech Stack: Python | MySQL | SQL | Streamlit | Pandas | Plotly | Pytest | Git

📊 Project Scope:
• 10,000 synthetic transactions | ₹74.4M sales | 8 categories | 12 states
• Python ETL pipeline with 11 cleaning rules, 17 validation checks, 100% retention rate
• MySQL star schema (4 tables) + 50+ SQL queries (CTEs, window functions)
• 5-page interactive dashboard with filters, charts, KPI cards
• 67 Pytest tests (100% passed)
• Automated Excel reporting (10 sheets)

🎯 Business Questions Answered:
✅ Category and product performance
✅ Regional sales contribution
✅ Monthly trends and seasonality
✅ Discount impact on profitability

📂 GitHub: [link]
🌐 Live Dashboard: [link]
```

---

## Part 15 — Troubleshooting Common Issues

### Issue 1: `ModuleNotFoundError: No module named 'pandas'`

**Solution:**
```powershell
# Ensure venv is activated (prompt shows (.venv))
.venv\Scripts\activate
pip install -r requirements.txt
```

### Issue 2: MySQL connection fails

**Solution:**
1. Check MySQL Server is running: Open **Services** → find **MySQL80** → Start
2. Verify `.env` password matches MySQL root password
3. Test connection:
```powershell
python -c "from src.database import test_connection; print(test_connection())"
```

### Issue 3: Streamlit shows "No data found"

**Solution:**
Run the pipeline first:
```powershell
python src/pipeline.py --no-db
```

This creates `data/processed/retailpulse_clean.csv`.

### Issue 4: Tests fail on `test_database.py`

**Solution:**
Database tests require MySQL to be configured. If MySQL is not set up:
- 7 tests will be SKIPPED (expected behavior)
- If you have MySQL configured and they still fail, check `.env` credentials

### Issue 5: Excel file not generated

**Solution:**
Ensure processed CSV exists:
```powershell
dir data\processed\retailpulse_clean.csv
```

If missing, run:
```powershell
python src/pipeline.py --no-db
```

Then:
```powershell
python src/excel_export.py
```

### Issue 6: Git push fails

**Solution:**
Ensure you've created the GitHub repository first:
1. Go to https://github.com/new
2. Create `Retail_Sales_Intelligence` repository
3. Copy the HTTPS URL
4. Run:
```powershell
git remote set-url origin https://github.com/yourusername/Retail_Sales_Intelligence.git
git push -u origin main
```

---

## Part 16 — What to Submit for Job Applications

When applying for Data Analyst roles, include:

1. **GitHub repository link**
   - Ensure README.md is comprehensive
   - Add screenshots to `screenshots/` folder
   - Verify `.gitignore` excludes `.env` and large data files

2. **Live dashboard link** (if deployed to Streamlit Cloud)
   - https://yourusername-retail-sales-intelligence.streamlit.app

3. **Resume bullet points** (see Part 14.1)

4. **Cover letter mention:**
   > "I recently completed RetailPulse, an end-to-end retail sales intelligence project 
   > demonstrating my SQL, Python, and BI skills. The project includes a MySQL star schema, 
   > 50+ SQL queries, a 5-page Streamlit dashboard, and 67 Pytest tests (100% passed). 
   > I'd be happy to walk you through the project and discuss how I approached specific 
   > analytical challenges."

---

## Part 17 — Next Steps After Completion

### Immediate (Day 1–2)
✅ Run all tests → 67 passed  
✅ Launch dashboard → 5 pages working  
✅ Generate Excel → 10 sheets complete  
✅ Push to GitHub → Repository public  
✅ Read `docs/INTERVIEW_PREPARATION.md`

### Short-term (Week 1)
✅ Deploy to Streamlit Cloud  
✅ Add screenshots to `screenshots/` folder  
✅ Practice 2-minute project walkthrough  
✅ Run SQL queries in MySQL Workbench without looking at solutions  
✅ Update resume and LinkedIn

### Medium-term (Week 2–4)
✅ Create a 5-minute YouTube demo (optional)  
✅ Write a blog post: "How I Built an End-to-End Retail Analytics System"  
✅ Practice STAR-format stories for interviews  
✅ Review `docs/LIMITATIONS.md` to prepare for critical questions

### Long-term (Optional Extensions)
- Replace synthetic data with a real Kaggle dataset (if licence permits)
- Add SARIMA forecasting (requires 2+ years of data)
- Add customer segmentation (requires customer_id)
- Integrate Power BI for comparative analysis

---

## Part 18 — Completion Certificate (Self-Checklist)

| Task                              | Status    |
|-----------------------------------|-----------|
| ✅ Python 3.11+ installed         | COMPLETE  |
| ✅ MySQL 8.0+ installed           | COMPLETE  |
| ✅ Git installed                  | COMPLETE  |
| ✅ Repository cloned              | COMPLETE  |
| ✅ Virtual environment created    | COMPLETE  |
| ✅ Dependencies installed         | COMPLETE  |
| ✅ Pipeline run successfully      | COMPLETE  |
| ✅ 67/67 tests passed             | COMPLETE  |
| ✅ Dashboard launched             | COMPLETE  |
| ✅ Excel workbook generated       | COMPLETE  |
| ✅ MySQL tables loaded            | COMPLETE  |
| ✅ SQL queries run in Workbench   | COMPLETE  |
| ✅ GitHub repository pushed       | COMPLETE  |
| ✅ Streamlit Cloud deployed       | PENDING   |
| ✅ Interview guide reviewed       | PENDING   |

---

## 📧 Support

If you encounter issues not covered in this guide:

1. Check `docs/LIMITATIONS.md` for known limitations
2. Review test output for specific error messages
3. Search the error message on Google/Stack Overflow
4. Check the GitHub Issues page (if repository is public)

---

## ✅ Final Verification

Run this complete verification script to confirm everything works:

```powershell
# Activate venv
.venv\Scripts\activate

# Run pipeline
python src/pipeline.py --no-db

# Run tests
python -m pytest tests/ -v

# Generate Excel
python src/excel_export.py

# Launch dashboard (Ctrl+C to exit after verification)
streamlit run app.py
```

**Expected results:**
- Pipeline: 10,000 rows, 17/17 checks PASS
- Tests: 67 passed, 7 skipped
- Excel: `excel/RetailPulse_Analysis.xlsx` (657 KB)
- Dashboard: Opens at http://localhost:8501

**If all 4 steps pass, your project is 100% ready for job applications. 🎉**

---

**Last updated:** November 2026 | RetailPulse v1.0
