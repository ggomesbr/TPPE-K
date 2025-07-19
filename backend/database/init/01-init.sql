-- Hospital Management System Database Initialization
-- This script is automatically run when the MySQL container starts

-- Create the hospital database if it doesn't exist
CREATE DATABASE IF NOT EXISTS hospital_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Switch to the hospital database
USE hospital_db;

-- Grant privileges to the hospital_user
GRANT ALL PRIVILEGES ON hospital_db.* TO 'hospital_user'@'%';
FLUSH PRIVILEGES;

-- Optional: Create some initial data
-- You can add initial hospitals, administrators, etc. here

-- Example: Create a default hospital
-- INSERT INTO hospitais (nome, endereco, telefone, email) VALUES 
-- ('Hospital Central', 'Rua Principal, 123', '(11) 1234-5678', 'contato@hospitalcentral.com');

SELECT 'Database hospital_db initialized successfully!' as status;
