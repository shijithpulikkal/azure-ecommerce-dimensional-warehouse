"""
load_dw.py — Loads curated Olist data from local CSVs into the Azure SQL
Database star schema (dim_customer, dim_product, dim_seller, dim_date, fact_orders).

pip install pandas sqlalchemy pyodbc
"""

import pandas as pd
from sqlalchemy import create_engine
import urllib

SERVER = "sqlsrv-ecommerce-dw-spx.database.windows.net"
DATABASE = "ecommerce_dw"
USERNAME = "sqladminuser"
PASSWORD = "XXXXXXXX#"  # better: read from os.environ

params = urllib.parse.quote_plus(
    f"DRIVER={{ODBC Driver 18 for SQL Server}};"
    f"SERVER={SERVER};DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD}"
)
engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params}")

# Load and reshape source data
customers = pd.read_csv("/home/shijith/ecommerce_data/olist_customers_dataset.csv")
products = pd.read_csv("/home/shijith/ecommerce_data/olist_products_dataset.csv")
sellers = pd.read_csv("/home/shijith/ecommerce_data/olist_sellers_dataset.csv")
orders = pd.read_csv("/home/shijith/ecommerce_data/olist_orders_dataset.csv", parse_dates=["order_purchase_timestamp"])
order_items = pd.read_csv("/home/shijith/ecommerce_data/olist_order_items_dataset.csv")

# --- dim_customer ---
dim_customer = customers[["customer_id", "customer_city", "customer_state", "customer_zip_code_prefix"]].drop_duplicates()
dim_customer.columns = ["customer_id", "customer_city", "customer_state", "customer_zip_prefix"]
dim_customer.to_sql("dim_customer", engine, if_exists="append", index=False)

# --- dim_product ---
dim_product = products[["product_id", "product_category_name", "product_weight_g",
                          "product_length_cm", "product_height_cm", "product_width_cm"]].drop_duplicates()
dim_product.columns = ["product_id", "product_category", "product_weight_g",
                         "product_length_cm", "product_height_cm", "product_width_cm"]
dim_product.to_sql("dim_product", engine, if_exists="append", index=False)

# --- dim_seller ---
dim_seller = sellers[["seller_id", "seller_city", "seller_state"]].drop_duplicates()
dim_seller.to_sql("dim_seller", engine, if_exists="append", index=False)

# --- dim_date ---
date_range = pd.date_range(start="2016-01-01", end="2019-12-31", freq="D")
dim_date = pd.DataFrame({
    "date_key": date_range.strftime("%Y%m%d").astype(int),
    "full_date": date_range,
    "year": date_range.year,
    "month": date_range.month,
    "month_name": date_range.strftime("%B"),
    "day": date_range.day,
    "day_of_week": date_range.strftime("%A"),
    "is_weekend": date_range.dayofweek.isin([5, 6]),
})
dim_date.to_sql("dim_date", engine, if_exists="append", index=False)

# --- fact_orders (join order_items to orders to get the date, then to surrogate keys) ---
fact = order_items.merge(orders[["order_id", "customer_id", "order_purchase_timestamp"]], on="order_id")
fact["order_date_key"] = fact["order_purchase_timestamp"].dt.strftime("%Y%m%d").astype(int)

# Pull surrogate keys back from the DB to map natural keys -> surrogate keys
customer_keys = pd.read_sql("SELECT customer_key, customer_id FROM dim_customer", engine)
product_keys = pd.read_sql("SELECT product_key, product_id FROM dim_product", engine)
seller_keys = pd.read_sql("SELECT seller_key, seller_id FROM dim_seller", engine)

fact = fact.merge(customer_keys, on="customer_id").merge(product_keys, on="product_id").merge(seller_keys, on="seller_id")

fact_orders = fact[["order_id", "order_item_id", "customer_key", "product_key",
                     "seller_key", "order_date_key", "price", "freight_value"]].copy()
fact_orders["quantity"] = 1  # Olist order_items is already one row per item

fact_orders.to_sql("fact_orders", engine, if_exists="append", index=False, chunksize=1000)

print("✅ Data warehouse load complete.")