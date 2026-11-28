RetailPulse — Indian Retail Sales Intelligence
> Python · Pandas · MySQL · Streamlit · Plotly

A data analytics project where I analyse 10,000 Indian retail sales transactions from 2022 to 2024, store them in MySQL, and show the results in a Streamlit dashboard.

Why I built this

I am a final year student looking for Data Analyst jobs. I built this project to practice the full workflow of a real data job — cleaning data, loading it into a database, writing SQL, and building a dashboard — and to have something I can show in interviews.

About the dataset

The data is synthetic. I generated it myself in Python using a fixed random seed so the results are always the same. It is not real company data. I use it only to show my skills.

10,000 rows of fake Indian retail transactions
Date range: January 2022 to December 2024
8 product categories, 12 Indian states
Columns include order date, product, category, quantity, unit price, discount, sales amount, profit, state, city, and payment method
Currency is INR
What's inside
Python pipeline that generates the data, cleans it (11 rules), validates it (17 checks), and loads it into MySQL
MySQL star schema with one fact table (sales) and three dimensions (product, location, date)
50+ SQL queries that answer 14 business questions, using joins, CTEs, and window functions
Streamlit dashboard with 5 pages: Overview, Products, Time Trends, Regional, Data Quality
All charts are made with Plotly
Tools used

Python, Pandas, MySQL, SQL, Streamlit, Plotly

How to run it
bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python src/pipeline.py --no-db
streamlit run app.py

That opens the dashboard at http://localhost:8501.

If you want to use MySQL too, copy .env.example to .env, add your password, and run python src/pipeline.py without the --no-db flag.

Results

See RESULTS.md for what I found.

Note

This is a learning project. The data is synthetic. I do not claim any of the numbers reflect a real business.

Made by Roshan Manjal GitHub: https://github.com/themanroshan/Retail_Sales_Intelligence