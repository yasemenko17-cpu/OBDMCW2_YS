def query() -> str:
    return """
    WITH sub AS (
        SELECT 
            p.id,
            pr.title,
            (p.quantity * pr.price) AS amount,
            AVG(p.quantity * pr.price) OVER (PARTITION BY p.product_id) AS avg_amount
        FROM purchase p
        JOIN product pr ON p.product_id = pr.id
    )
    SELECT 
        id,
        title,
        amount,
        ROUND(avg_amount, 2) AS avg_amount
    FROM sub
    WHERE amount > avg_amount
    ORDER BY id;
    """