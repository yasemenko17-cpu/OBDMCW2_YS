def indexes() -> str:
    return """
    CREATE INDEX idx_sale_log_customer_id ON sale_log(customer_id);
    CREATE INDEX idx_sale_log_sold_on ON sale_log(sold_on);
    """