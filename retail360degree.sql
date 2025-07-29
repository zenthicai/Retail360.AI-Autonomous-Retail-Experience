CREATE DATABASE IF NOT EXISTS retail;
USE retail;

CREATE TABLE retail.customers (
    customer_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    gender VARCHAR(10),
    email VARCHAR(100),
    phone_number VARCHAR(20),
    date_of_birth DATE,
    address VARCHAR(200),
    city VARCHAR(50),
    state VARCHAR(50),
    zip_code VARCHAR(10),
    country VARCHAR(50),
    registration_date DATE,
    loyalty_tier VARCHAR(20),
    total_spent FLOAT
);

CREATE TABLE retail.products (
    product_id INT PRIMARY KEY,
    product_name VARCHAR(255),
    brand VARCHAR(100),
    category VARCHAR(100),
    price DECIMAL(10,2)
);

CREATE TABLE retail.offers (
    offer_id INT PRIMARY KEY,
    offer_title VARCHAR(100),
    offer_type VARCHAR(50),
    category VARCHAR(50),
    discount_percent FLOAT,
    valid_from DATE,
    valid_till DATE,
    usage_limit INT,
    offer_channel VARCHAR(30),
    terms TEXT
);

CREATE TABLE retail.purchases (
    purchase_id INT PRIMARY KEY,
    customer_id INT,
    product_id INT,
    offer_id INT,
    purchase_date DATE,
    purchase_time TIME,
    item_count INT,
    total_amount FLOAT,
    discount_applied FLOAT,
    payment_method VARCHAR(30),
    device_type VARCHAR(30),
    purchase_channel VARCHAR(30),
    status VARCHAR(20),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    FOREIGN KEY (offer_id) REFERENCES offers(offer_id)
);


LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/customers.csv'
INTO TABLE retail.customers
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;


LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/products.csv'
INTO TABLE retail.products
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/offers.csv'
INTO TABLE retail.offers
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/purchases.csv'
INTO TABLE retail.purchases
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

CREATE OR REPLACE VIEW retail.purchases_data_model AS
SELECT
    p.purchase_id,
    c.customer_id,
    pr.product_id,
    o.offer_id,
    p.purchase_date,
    p.purchase_time,    
    p.item_count,
    p.discount_applied,    
    p.payment_method,        
    p.device_type,        
    p.purchase_channel,        
    p.status,        

    -- DIM: Customers
    c.first_name,
    c.last_name,
    c.gender,
    c.email,
    c.phone_number,
    c.date_of_birth,
    c.address,
    c.city,
    c.state,
    c.zip_code,
    c.country,
    c.registration_date,
    c.loyalty_tier,
    c.total_spent,

    -- DIM: Products
    pr.product_name,
    pr.brand,
    pr.category,
    pr.price AS unit_price,
    (p.item_count * pr.price) AS total_amount,

    -- DIM: Offers
    o.offer_title,
    o.offer_type,
    o.discount_percent,
    o.valid_from AS offer_start_date,
    o.valid_till AS offer_end_date,
    o.usage_limit,
    o.offer_channel,
    o.terms,

    -- derived fields
    (p.item_count * pr.price * (1 - o.discount_percent / 100)) AS discounted_total

FROM retail.purchases p
LEFT JOIN retail.customers c ON p.customer_id = c.customer_id
LEFT JOIN retail.products pr ON p.product_id = pr.product_id
LEFT JOIN retail.offers o ON p.offer_id = o.offer_id;

SELECT * FROM retail.purchases_data_model LIMIT 10;

ALTER TABLE retail.customers
ADD COLUMN image_path VARCHAR(255);

UPDATE retail.customers
SET image_path = CONCAT('face_images/', customer_id, '_face.jpg');

SELECT customer_id, image_path FROM retail.customers LIMIT 10;


