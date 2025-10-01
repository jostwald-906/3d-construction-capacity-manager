CREATE TABLE IF NOT EXISTS projects (
  id SERIAL PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  description TEXT,
  start_date DATE,
  end_date DATE
);

CREATE TABLE IF NOT EXISTS models (
  id SERIAL PRIMARY KEY,
  project_id INT REFERENCES projects(id) ON DELETE CASCADE,
  name VARCHAR(100) NOT NULL,
  format VARCHAR(20),
  model_file_path TEXT,
  min_x DOUBLE PRECISION DEFAULT 0,
  max_x DOUBLE PRECISION DEFAULT 100,
  min_y DOUBLE PRECISION DEFAULT 0,
  max_y DOUBLE PRECISION DEFAULT 20,
  min_z DOUBLE PRECISION DEFAULT 0,
  max_z DOUBLE PRECISION DEFAULT 20,
  created_at TIMESTAMP DEFAULT now()
);

CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE IF NOT EXISTS grid_cells (
  id SERIAL PRIMARY KEY,
  model_id INT REFERENCES models(id) ON DELETE CASCADE,
  x_index INT NOT NULL,
  y_index INT NOT NULL,
  z_index INT NOT NULL,
  min_x DOUBLE PRECISION NOT NULL,
  max_x DOUBLE PRECISION NOT NULL,
  min_y DOUBLE PRECISION NOT NULL,
  max_y DOUBLE PRECISION NOT NULL,
  min_z DOUBLE PRECISION NOT NULL,
  max_z DOUBLE PRECISION NOT NULL,
  total_capacity INT NOT NULL DEFAULT 10,
  footprint geometry(POLYGON, 3857),
  UNIQUE(model_id, x_index, y_index, z_index)
);

CREATE INDEX IF NOT EXISTS grid_cells_footprint_idx ON grid_cells USING GIST (footprint);

CREATE TABLE IF NOT EXISTS trades (
  id SERIAL PRIMARY KEY,
  name VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS trade_capacities (
  id SERIAL PRIMARY KEY,
  gridcell_id INT REFERENCES grid_cells(id) ON DELETE CASCADE,
  trade_id INT REFERENCES trades(id) ON DELETE CASCADE,
  max_workers INT NOT NULL,
  UNIQUE(gridcell_id, trade_id)
);

CREATE TABLE IF NOT EXISTS users (
  id SERIAL PRIMARY KEY,
  username VARCHAR(50) UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  role VARCHAR(20) NOT NULL CHECK (role IN ('admin','trade_manager','viewer')),
  created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE IF NOT EXISTS allocations (
  id SERIAL PRIMARY KEY,
  gridcell_id INT REFERENCES grid_cells(id) ON DELETE CASCADE,
  trade_id INT REFERENCES trades(id) ON DELETE CASCADE,
  work_date DATE NOT NULL,
  end_date DATE,
  num_workers INT,
  description TEXT,
  created_by INT REFERENCES users(id),
  created_at TIMESTAMP DEFAULT now()
);

CREATE INDEX IF NOT EXISTS allocations_idx ON allocations(gridcell_id, trade_id, work_date);

DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM trades) THEN
    INSERT INTO trades(name) VALUES ('Electrical'),('Mechanical'),('Piping'),('Welding'),('Paint');
  END IF;
  IF NOT EXISTS (SELECT 1 FROM users WHERE username='admin') THEN
    INSERT INTO users(username, password_hash, role)
    VALUES ('admin', '$2b$12$1XkP4h1lJY8c3S0N3w9p0uKCoOe6Zy0tX4XoYQ98J0kF4OQH2gJqS', 'admin');
  END IF;
END$$;
