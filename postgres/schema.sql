CREATE TABLE IF NOT EXISTS components (
  component_id SERIAL PRIMARY KEY,
  component_name VARCHAR(64) UNIQUE,
  system_name VARCHAR(64) -- valid are HYDRAULIC, ELETRICAL, TRANSMISSION, NAVIGATION
);

CREATE TABLE IF NOT EXISTS parts (
  part_id SERIAL PRIMARY KEY,
  manufacturer_id INT,
  part_no INT,
  UNIQUE (manufacturer_id, part_no)
);

CREATE TABLE IF NOT EXISTS allowed_parts (
  component_id INT REFERENCES components(component_id) ON DELETE CASCADE,
  part_id INT REFERENCES parts(part_id) ON DELETE CASCADE,
  deprecated BOOLEAN  -- FLAG FOR A PART / COMPONENT PAIRING THAT IS NO LONGER ALLOWED
  PRIMARY KEY (component_id, part_id)
);

CREATE TABLE IF NOT EXISTS users (
  user_id SERIAL PRIMARY KEY,
  user_name VARCHAR(32) -- format should be first_name.last_name
);

CREATE TABLE IF NOT EXISTS orders (
  order_id SERIAL PRIMARY KEY,
  component_id INT REFERENCES components(component_id) ON DELETE SET NULL,
  part_id INT REFERENCES parts(part_id) ON DELETE SET NULL,
  serial_no INT,
  comp_priority BOOLEAN,
  order_date DATETIME,
  ordered_by INT REFERENCES users(user_id),
  status VARCHAR(16), -- valid are PENDING, ORDERED, SHIPPED, and RECEIVED
  status_date DATETIME,
  FOREIGN KEY (component_id, part_id) REFERENCES allowed_parts(component_id, part_id),
  UNIQUE (component_id, part_id, serial_no, order_date)
);
