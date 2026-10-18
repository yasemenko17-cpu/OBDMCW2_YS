def query() -> str:
    return """
    WITH rev AS (
        SELECT 
            cat.id AS category_id,
            cat.name AS category,
            c.id AS customer_id,
            c.full_name AS customer,
            SUM(p.quantity * pr.price) AS revenue
        FROM purchase p
        JOIN product pr ON p.product_id = pr.id
        JOIN category cat ON pr.category_id = cat.id
        JOIN customer c ON p.customer_id = c.id
        GROUP BY cat.id, cat.name, c.id, c.full_name
    ),
    ranked AS (
        SELECT 
            category_id,
            category,
            customer_id,
            customer,
            revenue,
            SUM(revenue) OVER (PARTITION BY category_id ORDER BY revenue DESC, customer_id ASC) - revenue AS prev_cum_revenue,
            SUM(revenue) OVER (PARTITION BY category_id) AS total_category_revenue
        FROM rev
    )
    SELECT 
        category,
        customer,
        revenue,
        ROUND(100.0 * (prev_cum_revenue + revenue) / total_category_revenue, 1) AS cum_pct
    FROM ranked
    WHERE prev_cum_revenue < 0.8 * total_category_revenue
    ORDER BY category_id, revenue DESC, customer_id ASC;
    """