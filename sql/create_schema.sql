-- Dimension: Date
CREATE TABLE dim_date (
    date_key INT PRIMARY KEY,
    full_date DATE NOT NULL,
    year INT,
    month INT,
    month_name VARCHAR(20),
    day INT,
    day_of_week VARCHAR(20),
    is_weekend BIT
);

-- Dimension: Customer
CREATE TABLE dim_customer (
    customer_key INT IDENTITY(1,1) PRIMARY KEY,
    customer_id VARCHAR(50) NOT NULL UNIQUE,
    customer_city VARCHAR(100),
    customer_state VARCHAR(10),
    customer_zip_prefix VARCHAR(10)
);

-- Dimension: Product
CREATE TABLE dim_product (
    product_key INT IDENTITY(1,1) PRIMARY KEY,
    product_id VARCHAR(50) NOT NULL UNIQUE,
    product_category VARCHAR(100),
    product_weight_g INT,
    product_length_cm INT,
    product_height_cm INT,
    product_width_cm INT
);

-- Dimension: Seller
CREATE TABLE dim_seller (
    seller_key INT IDENTITY(1,1) PRIMARY KEY,
    seller_id VARCHAR(50) NOT NULL UNIQUE,
    seller_city VARCHAR(100),
    seller_state VARCHAR(10)
);

-- Fact: Order Items
CREATE TABLE fact_orders (
    order_item_key INT IDENTITY(1,1) PRIMARY KEY,
    order_id VARCHAR(50) NOT NULL,
    order_item_id INT,
    customer_key INT FOREIGN KEY REFERENCES dim_customer(customer_key),
    product_key INT FOREIGN KEY REFERENCES dim_product(product_key),
    seller_key INT FOREIGN KEY REFERENCES dim_seller(seller_key),
    order_date_key INT FOREIGN KEY REFERENCES dim_date(date_key),
    price DECIMAL(10,2),
    freight_value DECIMAL(10,2),
    quantity INT DEFAULT 1
);

-- Indexes for common query patterns (a talking point: "I indexed for the queries the dashboard runs")
CREATE INDEX idx_fact_orders_customer ON fact_orders(customer_key);
CREATE INDEX idx_fact_orders_product ON fact_orders(product_key);
CREATE INDEX idx_fact_orders_date ON fact_orders(order_date_key);