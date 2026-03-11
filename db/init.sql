CREATE TABLE IF NOT EXISTS transactions (
    transaction_id VARCHAR(50) PRIMARY KEY,
    user_id VARCHAR(50),
    amount DECIMAL(10, 2),
    transaction_type VARCHAR(20),
    transaction_timestamp TIMESTAMP
);
