-- Tabla maestra de traducción de categorías
CREATE TABLE IF NOT EXISTS product_category_name (
    product_category_name VARCHAR(100) PRIMARY KEY,
    product_category_name_english VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS products (
    product_id VARCHAR(50) PRIMARY KEY,
    sku VARCHAR(100) UNIQUE NOT NULL,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    weight_g INT CHECK (weight_g >= 0),
    dimensions_cm INT[] CHECK (array_length(dimensions_cm, 1) = 3),
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

CREATE TABLE IF NOT EXISTS customers (
    customer_id VARCHAR(50) PRIMARY KEY,
    customer_unique_id VARCHAR(50) NOT NULL,
    customer_zip_code_prefix INT NOT NULL,
    customer_city VARCHAR(100) NOT NULL,
    customer_state VARCHAR(10) NOT NULL
);

CREATE TABLE IF NOT EXISTS sellers (
    seller_id VARCHAR(50) PRIMARY KEY,
    seller_zip_code_prefix INT NOT NULL,
    seller_city VARCHAR(100) NOT NULL,
    seller_state VARCHAR(10) NOT NULL
);

CREATE TABLE IF NOT EXISTS geolocation (
    geolocation_zip_code_prefix INT NOT NULL,
    geolocation_lat DOUBLE PRECISION NOT NULL,
    geolocation_lng DOUBLE PRECISION NOT NULL,
    geolocation_city VARCHAR(100) NOT NULL,
    geolocation_state VARCHAR(10) NOT NULL,
    geom GEOMETRY(Point, 4326)
);

CREATE TABLE IF NOT EXISTS promotions (
    promotion_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id VARCHAR(50) REFERENCES products(product_id),
    discount_rate NUMERIC(4,2) CHECK (discount_rate > 0 AND discount_rate <= 1.00),
    duration_range TSTZRANGE NOT NULL
);

CREATE TABLE IF NOT EXISTS orders (
    order_id VARCHAR(50) NOT NULL,
    customer_id VARCHAR(50) REFERENCES customers(customer_id),
    order_status VARCHAR(30) NOT NULL,
    purchase_timestamp TIMESTAMPTZ NOT NULL,
    approved_at TIMESTAMPTZ,
    delivered_carrier_date TIMESTAMPTZ,
    delivered_customer_date TIMESTAMPTZ,
    estimated_delivery_date TIMESTAMPTZ,
    PRIMARY KEY (order_id, purchase_timestamp)
) PARTITION BY RANGE (purchase_timestamp);

CREATE TABLE IF NOT EXISTS order_items (
    order_id VARCHAR(50) NOT NULL,
    order_item_id INT NOT NULL,
    product_id VARCHAR(50) REFERENCES products(product_id),
    seller_id VARCHAR(50) REFERENCES sellers(seller_id),
    shipping_limit_date TIMESTAMPTZ NOT NULL,
    price NUMERIC(10,2) CHECK (price >= 0),
    freight_value NUMERIC(10,2) CHECK (freight_value >= 0),
    purchase_timestamp TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (order_id, order_item_id, purchase_timestamp),
    FOREIGN KEY (order_id, purchase_timestamp) REFERENCES orders(order_id, purchase_timestamp)
);

CREATE TABLE IF NOT EXISTS payments (
    order_id VARCHAR(50) NOT NULL,
    payment_sequential INT NOT NULL,
    payment_type VARCHAR(30) NOT NULL,
    payment_installments INT CHECK (payment_installments >= 0),
    payment_value NUMERIC(10,2) CHECK (payment_value >= 0),
    gateway_response JSONB,
    purchase_timestamp TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (order_id, payment_sequential, purchase_timestamp),
    FOREIGN KEY (order_id, purchase_timestamp) REFERENCES orders(order_id, purchase_timestamp)
);
