import pandas as pd

# 1. Data Ingestion & Cleaning
print("Loading data...")
# Using utf-8 or latin-1 depending on how the CSV was saved to handle Swedish/Polish chars
df = pd.read_csv('ecommerce_orders_1.5M.csv', encoding='utf-8') 
df['order_date'] = pd.to_datetime(df['order_date'])

# Count total rows in dataset
print(f"\nDataset contains {df.shape[0]} rows")

print("\n--- DATA QUALITY FINDINGS ---")

# DQ1: Math Errors
df['expected_total'] = df['quantity'] * df['unit_price']
dq1_errors = df[df['expected_total'] != df['total_amount']]
print(f"DQ1: Found {len(dq1_errors)} rows where quantity * price != total_amount")

# DQ2: Duplicate Emails
email_group = df.groupby('email')['customer_id'].nunique()
dq2_duplicates = email_group[email_group > 1]
print(f"DQ2: Found {len(dq2_duplicates)} emails shared across multiple unique customer IDs")

# DQ3: Test Records
# Checking for 'test' or 'demo' in names or email
mask_first = df['first_name'].str.lower().str.contains('test|demo', na=False)
mask_last = df['last_name'].str.lower().str.contains('test|demo', na=False)
mask_email = df['email'].str.lower().str.contains('test|demo', na=False)
dq3_tests = df[mask_first | mask_last | mask_email]
print(f"DQ3: Found {len(dq3_tests)} test or placeholder records")


print("\n--- BUSINESS INSIGHTS ---")

# B1: Growth Trends
df['month_year'] = df['order_date'].dt.to_period('M')
monthly_club_sales = df.groupby(['club', 'month_year'])['total_amount'].sum().unstack()
# Calculate percentage change between the first and last available month
monthly_club_sales['growth_pct'] = monthly_club_sales.pct_change(axis='columns').iloc[:, -1] * 100
print("B1: Fastest Growing Clubs (Top 3):")
print(monthly_club_sales['growth_pct'].sort_values(ascending=False).head(3))
print("B1: Stagnating Clubs (Bottom 3):")
print(monthly_club_sales['growth_pct'].sort_values().head(3))

# B2: Return Rates by Payment Method
total_orders_by_method = df.groupby('payment_method').size()
returned_orders = df[df['order_status'] == 'Returned'].groupby('payment_method').size()
return_rates = (returned_orders / total_orders_by_method) * 100
print("\nB2: Return Rates by Payment Method (%):")
print(return_rates.sort_values(ascending=False))

# B3: Geography Anomalies (Where merchandise sells outside home city)
# Grouping by club and city to find top sales locations
geo_sales = df.groupby(['club', 'city']).size().reset_index(name='order_count')
geo_sales_sorted = geo_sales.sort_values(['club', 'order_count'], ascending=[True, False])
print("\nB3: Top Cities per Club (Check for unexpected commuter fanbases):")
# Prints the top 2 cities for every club to spot anomalies
print(geo_sales_sorted.groupby('club').head(2))