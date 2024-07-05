create database Pesto;
use Pesto;
-- Create User table
CREATE TABLE User (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(100) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'user'
);

-- Create Item table
CREATE TABLE Item (
    item_id INT AUTO_INCREMENT PRIMARY KEY,
    item_name VARCHAR(100) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    item_description TEXT
);

-- Create Order table
CREATE TABLE `Order` (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    item_id INT NOT NULL,
    item_amount INT NOT NULL,
    CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES User(user_id),
    CONSTRAINT fk_item FOREIGN KEY (item_id) REFERENCES Item(item_id)
);

-- Check if the event scheduler is enabled
SHOW VARIABLES LIKE 'event_scheduler';

-- Enable the event scheduler if it is not enabled
SET GLOBAL event_scheduler = ON;


-- Create the keys table
CREATE TABLE IF NOT EXISTS `keys` (
                               temp_key VARCHAR(255) NOT NULL,
                               user_id INT NOT NULL,
                               create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                               PRIMARY KEY (temp_key),
                               FOREIGN KEY (user_id) REFERENCES User(user_id));
							   
-- Create an event to delete keys older than 24 hours
CREATE EVENT delete_old_keys
ON SCHEDULE EVERY 1 HOUR
DO
    DELETE FROM `keys` WHERE `create_time` < NOW() - INTERVAL 24 HOUR;

ALTER TABLE User ADD COLUMN role VARCHAR(50) NOT NULL DEFAULT 'user';

-- Drop all tables
DROP TABLE IF EXISTS `keys`;
DROP TABLE IF EXISTS `Order`;
DROP TABLE IF EXISTS `Item`;
DROP TABLE IF EXISTS `User`;
