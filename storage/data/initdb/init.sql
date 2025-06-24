CREATE TABLE IF NOT EXISTS user_status (
    id INT AUTO_INCREMENT PRIMARY KEY,
    source VARCHAR(255) NOT NULL UNIQUE,
    status TEXT,
    information TEXT
);

CREATE TABLE IF NOT EXISTS system_timeline (
    id INT AUTO_INCREMENT PRIMARY KEY,
    node_id INTEGER,
    date DATE,
    event TEXT,
    tag TEXT
);

CREATE TABLE system_bubble (
    id INT AUTO_INCREMENT PRIMARY KEY,
    content TEXT NOT NULL,
    x INTEGER NOT NULL,
    y INTEGER NOT NULL
);