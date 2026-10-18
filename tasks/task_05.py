def query() -> str:
    return """
    WITH ref AS (
        SELECT referred_by AS id, COUNT(*) AS referrals
        FROM customer
        WHERE referred_by IS NOT NULL
        GROUP BY referred_by
    ),
    pur AS (
        SELECT customer_id AS id, COUNT(*) AS purchases, SUM(quantity) AS items
        FROM purchase
        GROUP BY customer_id
    )
    SELECT 
        c.id,
        c.full_name,
        COALESCE(r.referrals, 0) AS referrals,
        COALESCE(p.purchases, 0) AS purchases,
        COALESCE(p.items, 0) AS items
    FROM customer c
    LEFT JOIN ref r ON c.id = r.id
    LEFT JOIN pur p ON c.id = p.id
    ORDER BY c.id;
    """