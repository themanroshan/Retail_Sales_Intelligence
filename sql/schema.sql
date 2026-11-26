-- Star schema for the retail_sales warehouse.
-- Run this once to create all 6 tables.

USE retail_sales;

CREATE TABLE IF NOT EXISTS dim_aisle (
    aisle_id INT PRIMARY KEY,
    aisle    VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS dim_department (
    department_id INT PRIMARY KEY,
    department    VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS dim_product (
    product_id    INT PRIMARY KEY,
    product_name  VARCHAR(500) NOT NULL,
    aisle_id      INT NOT NULL,
    department_id INT NOT NULL,
    FOREIGN KEY (aisle_id)      REFERENCES dim_aisle(aisle_id),
    FOREIGN KEY (department_id) REFERENCES dim_department(department_id)
);

CREATE TABLE IF NOT EXISTS dim_user (
    user_id INT PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS dim_order (
    order_id               INT PRIMARY KEY,
    user_id                INT NOT NULL,
    order_number           INT NOT NULL,
    order_dow              TINYINT NOT NULL,
    order_hour_of_day      TINYINT NOT NULL,
    days_since_prior_order FLOAT,
    order_date             DATE NOT NULL,
    INDEX idx_order_date (order_date),
    FOREIGN KEY (user_id) REFERENCES dim_user(user_id)
);

CREATE TABLE IF NOT EXISTS fact_order_products (
    order_id          INT NOT NULL,
    product_id        INT NOT NULL,
    add_to_cart_order INT NOT NULL,
    reordered         TINYINT NOT NULL,
    PRIMARY KEY (order_id, product_id),
    FOREIGN KEY (order_id)   REFERENCES dim_order(order_id),
    FOREIGN KEY (product_id) REFERENCES dim_product(product_id)
)
