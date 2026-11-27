-- =============================================================================
-- RetailPulse — Script 01: Database Setup
-- =============================================================================
-- Purpose  : Create the retailpulse database with correct character set.
-- Run once : Before creating tables or loading data.
-- Tool     : MySQL Workbench or MySQL CLI
-- =============================================================================

CREATE DATABASE IF NOT EXISTS retailpulse
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

-- Confirm creation
SHOW DATABASES LIKE 'retailpulse';
