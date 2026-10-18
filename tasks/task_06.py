def statement() -> str:
    return """
    WITH deleted AS (
        DELETE FROM purchase
        WHERE shipped_on IS NOT NULL 
          AND ordered_on < DATE '2024-07-01'
        RETURNING id, customer_id, product_id, quantity, ordered_on, shipped_on
    ),
    archived AS (
        INSERT INTO purchase_archive
        SELECT * FROM deleted
        RETURNING id
    ),
    logged AS (
        INSERT INTO archive_log (moved)
        SELECT COUNT(*) FROM archived
    )
    SELECT 1;
    """