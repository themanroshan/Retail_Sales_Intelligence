-- =============================================================================
-- RetailPulse — Script 02: Create Tables (Star Schema)
-- =============================================================================
-- Purpose  : Create dimension and fact tables for the RetailPulse warehouse.
-- Run after: 01_database_setup.sql
-- Design   : Star schema — fact_sales at centre, 3 dimension tables.
--
-- Tables:
--   dim_product   — product catalogue (product, category, sub-category)
--   dim_location  — geographic dimension (state, city)
--   dim_date      — date dimension (year, month, quarter, etc.)
--   fact_sales    — one row per order line (transaction grain)
-- =============================================================================

USE retailpulse;

-- ── dim_product ───────────────────────────────────────────────────────────────
-- Grain: one row per unique product_id.
CREATE TABLE IF NOT EXISTS dim_product (
    product_id    VARCHAR(20)  NOT NULL,
    product_name  VARCHAR(500) NOT NULL,
    category      VARCHAR(100) NOT NULL,
    sub_category  VARCHAR(100) NOT NULL,
    PRIMARY KEY (product_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ── dim_location ──────────────────────────────────────────────────────────────
-- Grain: one row per unique state + city combination.
CREATE TABLE IF NOT EXISTS dim_location (
    location_id INT          NOT NULL AUTO_INCREMENT,
    state       VARCHAR(100) NOT NULL,
    city        VARCHAR(100) NOT NULL,
    PRIMARY KEY (location_id),
    UNIQUE KEY uq_state_city (state, city),
    INDEX idx_state (state)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ── dim_date ──────────────────────────────────────────────────────────────────
-- Grain: one row per calendar date present in the dataset.
CREATE TABLE IF NOT EXISTS dim_date (
    date_id      INT    NOT NULL,     -- YYYYMMDD integer key
    order_date   DATE   NOT NULL,
    year         SMALLINT NOT NULL,
    quarter      TINYINT  NOT NULL,
    month        TINYINT  NOT NULL,
    month_name   VARCHAR(15) NOT NULL,
    week         TINYINT  NOT NULL,
    day_of_week  TINYINT  NOT NULL,   -- 0=Monday … 6=Sunday
    day_name     VARCHAR(10) NOT NULL,
    is_weekend   TINYINT  NOT NULL,   -- 1=weekend, 0=weekday
    year_month   VARCHAR(10) NOT NULL,
    PRIMARY KEY (date_id),
    INDEX idx_order_date (order_date),
    INDEX idx_year_month (year_month)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ── fact_sales ────────────────────────────────────────────────────────────────
-- Grain: one row per order line (order_id + product_id).
-- Foreign keys reference the three dimension tables.
CREATE TABLE IF NOT EXISTS fact_sales (
    order_id        VARCHAR(20)    NOT NULL,
    order_date      DATE           NOT NULL,
    product_id      VARCHAR(20)    NOT NULL,
    location_id     INT            NOT NULL,
    quantity        INT            NOT NULL,
    unit_price      DECIMAL(12,2)  NOT NULL,
    discount        DECIMAL(5,4)   NOT NULL,  -- e.g. 0.1500 = 15%
    sales_amount    DECIMAL(14,2)  NOT NULL,
    profit          DECIMAL(14,2)  NOT NULL,
    payment_method  VARCHAR(50)    NOT NULL,
    year            SMALLINT       NOT NULL,
    month           TINYINT        NOT NULL,
    quarter         TINYINT        NOT NULL,
    year_month      VARCHAR(10)    NOT NULL,
    PRIMARY KEY (order_id, product_id),
    INDEX idx_order_date  (order_date),
    INDEX idx_year_month  (year_month),
    INDEX idx_product_id  (product_id),
    INDEX idx_location_id (location_id),
    CONSTRAINT fk_product  FOREIGN KEY (product_id)  REFERENCES dim_product(product_id),
    CONSTRAINT fk_location FOREIGN KEY (location_id) REFERENCES dim_location(location_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
