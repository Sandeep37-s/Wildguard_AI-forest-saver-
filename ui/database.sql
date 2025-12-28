CREATE DATABASE IF NOT EXISTS telegram_dashboard;
USE telegram_dashboard;


-- Table for storing messages
CREATE TABLE IF NOT EXISTS messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    text TEXT NOT NULL,
    sender VARCHAR(255) NOT NULL,
    timestamp DATETIME NOT NULL,
    score DECIMAL(3,2) NOT NULL,
    reasons JSON,
    label VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table for admin users
CREATE TABLE IF NOT EXISTS admins (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert default admin (username: admin, password: admin123)
INSERT INTO admins (username, password, email) 
VALUES ('admin', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'admin@securitybot.com');

-- Insert some sample messages for demo
INSERT INTO messages (text, sender, timestamp, score, reasons, label) VALUES
('Click here to win $1000! http://suspicious-link.com', 'user_12345', NOW(), 0.95, '["Contains suspicious link", "Prize scam pattern"]', 'suspicious'),
('Hello, how are you today?', 'user_67890', NOW(), 0.10, '[]', 'safe'),
('URGENT! Your account will be locked. Click now!', 'user_54321', NOW(), 0.88, '["Urgency tactics", "Phishing pattern"]', 'suspicious'),
('Thanks for the information!', 'user_11111', NOW(), 0.05, '[]', 'safe'),
('Free iPhone giveaway! Limited time offer!', 'user_22222', NOW(), 0.92, '["Prize scam", "Urgency"]', 'suspicious');

-- Create index for faster queries
CREATE INDEX idx_label ON messages(label);
CREATE INDEX idx_timestamp ON messages(timestamp DESC);

-- Display success message
SELECT 'Database setup complete!' AS Status;