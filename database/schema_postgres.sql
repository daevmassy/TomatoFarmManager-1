
-- Tomato Farm Management System Database Schema
-- PostgreSQL Database

CREATE TABLE IF NOT EXISTS farmers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    contact VARCHAR(50),
    email VARCHAR(100),
    address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS tomato_plants (
    id SERIAL PRIMARY KEY,
    variety VARCHAR(100) NOT NULL,
    planting_date DATE NOT NULL,
    expected_harvest_date DATE,
    status VARCHAR(50) DEFAULT 'Growing',
    field_location VARCHAR(100),
    quantity INT DEFAULT 1,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS harvest (
    id SERIAL PRIMARY KEY,
    plant_id INT,
    harvest_date DATE NOT NULL,
    quantity DECIMAL(10,2) NOT NULL,
    unit VARCHAR(20) DEFAULT 'kg',
    quality_grade VARCHAR(20),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (plant_id) REFERENCES tomato_plants(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS inventory (
    id SERIAL PRIMARY KEY,
    item_name VARCHAR(100) NOT NULL,
    category VARCHAR(50),
    quantity DECIMAL(10,2) NOT NULL,
    unit VARCHAR(20),
    min_quantity DECIMAL(10,2) DEFAULT 0,
    supplier VARCHAR(100),
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sales (
    id SERIAL PRIMARY KEY,
    sale_date DATE NOT NULL,
    customer_name VARCHAR(100),
    quantity DECIMAL(10,2) NOT NULL,
    unit VARCHAR(20) DEFAULT 'kg',
    price_per_unit DECIMAL(10,2),
    total_amount DECIMAL(10,2),
    payment_status VARCHAR(50) DEFAULT 'Pending',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS operations (
    id SERIAL PRIMARY KEY,
    operation_type VARCHAR(50) NOT NULL,
    operation_date DATE NOT NULL,
    field_location VARCHAR(100),
    description TEXT,
    cost DECIMAL(10,2) DEFAULT 0,
    performed_by VARCHAR(100),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS spraying (
    id SERIAL PRIMARY KEY,
    spray_date DATE NOT NULL,
    chemical_name VARCHAR(100),
    quantity_used DECIMAL(10,2),
    unit VARCHAR(20),
    target_pest VARCHAR(100),
    field_location VARCHAR(100),
    applicator VARCHAR(100),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS weeding (
    id SERIAL PRIMARY KEY,
    weeding_date DATE NOT NULL,
    field_location VARCHAR(100),
    method VARCHAR(50),
    labor_hours DECIMAL(5,2),
    workers INT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS irrigation (
    id SERIAL PRIMARY KEY,
    irrigation_date DATE NOT NULL,
    field_location VARCHAR(100),
    water_volume DECIMAL(10,2),
    unit VARCHAR(20) DEFAULT 'liters',
    duration_minutes INT,
    method VARCHAR(50),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample inventory data
INSERT INTO inventory (item_name, category, quantity, unit, min_quantity, supplier) VALUES
('Tomato Seeds - Roma', 'Seeds', 50, 'packets', 10, 'AgriSupply Co'),
('Tomato Seeds - Cherry', 'Seeds', 30, 'packets', 10, 'AgriSupply Co'),
('NPK Fertilizer', 'Fertilizer', 100, 'kg', 20, 'Farm Supplies Ltd'),
('Organic Compost', 'Fertilizer', 500, 'kg', 100, 'Green Earth'),
('Pesticide - Insect Control', 'Pesticide', 25, 'liters', 5, 'CropCare Inc'),
('Fungicide', 'Pesticide', 15, 'liters', 5, 'CropCare Inc'),
('Watering Hoses', 'Equipment', 10, 'units', 2, 'FarmTools')
ON CONFLICT DO NOTHING;
