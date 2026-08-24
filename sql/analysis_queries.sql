-- Revenue by product category
SELECT p.product_category, SUM(f.price) AS revenue, COUNT(*) AS item_count
FROM fact_orders f
JOIN dim_product p ON f.product_key = p.product_key
GROUP BY p.product_category
ORDER BY revenue DESC;

-- Monthly revenue trend
SELECT d.year, d.month, SUM(f.price) AS revenue
FROM fact_orders f
JOIN dim_date d ON f.order_date_key = d.date_key
GROUP BY d.year, d.month
ORDER BY d.year, d.month;

-- Revenue by customer state
SELECT c.customer_state, SUM(f.price) AS revenue
FROM fact_orders f
JOIN dim_customer c ON f.customer_key = c.customer_key
GROUP BY c.customer_state
ORDER BY revenue DESC;