import sqlite3
from datetime import datetime, date

# Create a connection to the SQLite database
conn = sqlite3.connect('crm.db')
cursor = conn.cursor()

# Drop existing tables
cursor.execute('DROP TABLE IF EXISTS products')
cursor.execute('DROP TABLE IF EXISTS budget_line_items')
cursor.execute('DROP TABLE IF EXISTS budgets')
cursor.execute('DROP TABLE IF EXISTS contacts')
cursor.execute('DROP TABLE IF EXISTS applications')
cursor.execute('DROP TABLE IF EXISTS application_documents')
cursor.execute('DROP TABLE IF EXISTS expenses')

# Create a table for storing contact information if it doesn't already exist
cursor.execute(''' 
CREATE TABLE IF NOT EXISTS contacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    gender TEXT,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    phone TEXT NOT NULL,
    message TEXT NOT NULL,
    address_line TEXT,
    suburb TEXT,
    postcode TEXT,
    state TEXT,
    country TEXT
)
''')

# Create a table for storing application data linked to contacts
cursor.execute(''' 
CREATE TABLE IF NOT EXISTS applications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    contact_id INTEGER,
    interest TEXT NOT NULL,
    reason TEXT NOT NULL,
    skillsets TEXT NOT NULL,
    FOREIGN KEY (contact_id) REFERENCES contacts(id)
)
''')

# Create a table for storing generated application documents and signatures
cursor.execute('''
CREATE TABLE IF NOT EXISTS application_documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    contact_id INTEGER,
    document_name TEXT,
    document_path TEXT,
    signature BLOB,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (contact_id) REFERENCES contacts(id)
)
''')

# Create a table for storing budget information
cursor.execute('''
CREATE TABLE IF NOT EXISTS budgets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    contact_id INTEGER,
    budget_name TEXT NOT NULL,
    total_budget DECIMAL(10, 2),
    current_spent DECIMAL(10, 2) DEFAULT 0.00,
    remaining_budget AS (total_budget - current_spent),
    start_date DATE,
    end_date DATE,
    currency TEXT,
    status TEXT DEFAULT 'Active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (contact_id) REFERENCES contacts(id)
)
''')

# Create budget line items table
cursor.execute('''
CREATE TABLE IF NOT EXISTS budget_line_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    budget_id INTEGER,
    line_item_name TEXT NOT NULL,
    allocated_amount DECIMAL(10, 2),
    spent_amount DECIMAL(10, 2) DEFAULT 0.00,
    remaining_amount AS (allocated_amount - spent_amount),
    status TEXT DEFAULT 'Active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (budget_id) REFERENCES budgets(id)
)
''')

# Create products table
cursor.execute('''
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    line_item_id INTEGER,
    product_name TEXT NOT NULL,
    product_group TEXT,
    rate DECIMAL(10, 2),
    frequency TEXT CHECK(frequency IN ('hourly', 'daily', 'weekly', 'monthly', 'yearly')),
    service_name TEXT,
    description TEXT,
    status TEXT DEFAULT 'Active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (line_item_id) REFERENCES budget_line_items(id)
)
''')

# Add after the products table creation and before the sample data insertions
cursor.execute('''
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    line_item_id INTEGER,
    product_id INTEGER,
    amount DECIMAL(10, 2),
    quantity DECIMAL(10, 2),
    date_incurred DATE,
    description TEXT,
    status TEXT DEFAULT 'Active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (line_item_id) REFERENCES budget_line_items(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
)
''')

# Insert some sample (rubbish) data into the contacts table for testing
cursor.executemany(''' 
INSERT INTO contacts (title, gender, name, email, phone, message, address_line, suburb, postcode, state, country)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
''', [
    ('Mr.', 'Male', 'John Doe', 'john.doe@example.com', '1234567890', 'Interested in testing.', '123 Main St', 'Somewhere', '1234', 'NSW', 'Australia'),
    ('Ms.', 'Female', 'Jane Smith', 'jane.smith@example.com', '0987654321', 'Looking to apply.', '456 Elm St', 'Anywhere', '5678', 'VIC', 'Australia'),
    ('Dr.', 'Non-binary', 'Alex Taylor', 'alex.taylor@example.com', '1122334455', 'Testing with dummy data.', '789 Oak St', 'Nowhere', '9101', 'QLD', 'Australia'),
    ('Prof.', 'Male', 'William Brown', 'william.brown@example.com', '2233445566', 'Trying the system out.', '101 Pine St', 'Everywhere', '1122', 'SA', 'Australia'),
    ('Ms.', 'Female', 'Emily White', 'emily.white@example.com', '3344556677', 'Just exploring.', '202 Maple St', 'Anywhere', '3344', 'WA', 'Australia')
])

# Insert some sample (rubbish) data into the applications table for testing
cursor.executemany('''
INSERT INTO applications (contact_id, interest, reason, skillsets)
VALUES (?, ?, ?, ?)
''', [
    (1, 'Data Analyst', 'Interested in data processing and analysis.', 'Excel, Python, SQL'),
    (2, 'Web Developer', 'Want to build websites and web applications.', 'HTML, CSS, JavaScript'),
    (3, 'AI Researcher', 'Passionate about machine learning and AI technologies.', 'Python, TensorFlow, Keras'),
    (4, 'Project Manager', 'Looking to manage large-scale projects.', 'Leadership, Agile, Communication'),
    (5, 'Content Writer', 'Love creating content and articles for blogs and websites.', 'Writing, SEO, Research')
])

# Insert some sample (rubbish) data into the application_documents table for testing
cursor.executemany('''
INSERT INTO application_documents (contact_id, document_name, document_path, signature)
VALUES (?, ?, ?, ?)
''', [
    (1, 'Application Form 1', '/path/to/application_form_1.pdf', None),
    (2, 'Application Form 2', '/path/to/application_form_2.pdf', None),
    (3, 'Application Form 3', '/path/to/application_form_3.pdf', None),
    (4, 'Application Form 4', '/path/to/application_form_4.pdf', None),
    (5, 'Application Form 5', '/path/to/application_form_5.pdf', None)
])

# Insert some sample budget data for testing
cursor.executemany('''
INSERT INTO budgets (contact_id, budget_name, total_budget, start_date, end_date, currency)
VALUES (?, ?, ?, ?, ?, ?)
''', [
    (1, '2025 Marketing', 50000.00, '2025-01-01', '2025-12-31', 'USD'),
    (1, 'Client X Project', 10000.00, '2025-03-01', '2025-06-30', 'USD'),
    (2, 'Web Development', 25000.00, '2025-02-01', '2025-08-31', 'AUD'),
    (3, 'AI Research', 30000.00, '2025-01-01', '2025-12-31', 'EUR'),
    (4, 'Project Management', 40000.00, '2025-04-01', '2025-09-30', 'AUD')
])

# Insert sample budget line items
cursor.executemany('''
INSERT INTO budget_line_items (budget_id, line_item_name, allocated_amount)
VALUES (?, ?, ?)
''', [
    (1, 'Social Media Marketing', 20000.00),
    (1, 'Content Creation', 15000.00),
    (1, 'Email Campaigns', 15000.00),
    (2, 'Website Development', 6000.00),
    (2, 'UI/UX Design', 4000.00),
    (3, 'Frontend Development', 15000.00),
    (3, 'Backend Development', 10000.00),
    (4, 'Research Personnel', 20000.00),
    (4, 'Computing Resources', 10000.00),
    (5, 'Project Tools', 15000.00),
    (5, 'Team Training', 25000.00)
])

# Insert sample products
cursor.executemany('''
INSERT INTO products (
    line_item_id, product_name, product_group, rate, 
    frequency, service_name, description
)
VALUES (?, ?, ?, ?, ?, ?, ?)
''', [
    (1, 'Facebook Ads Management', 'Digital Marketing', 150.00, 'hourly', 'Social Media', 'Managing Facebook ad campaigns'),
    (1, 'Instagram Content', 'Digital Marketing', 100.00, 'hourly', 'Social Media', 'Creating and scheduling Instagram posts'),
    (2, 'Blog Writing', 'Content', 75.00, 'hourly', 'Content Creation', 'Writing blog posts and articles'),
    (2, 'Video Production', 'Content', 200.00, 'hourly', 'Content Creation', 'Creating promotional videos'),
    (3, 'Email Template Design', 'Digital Marketing', 120.00, 'hourly', 'Email Marketing', 'Designing email templates'),
    (4, 'WordPress Development', 'Development', 90.00, 'hourly', 'Web Development', 'Custom WordPress development'),
    (5, 'UI Design Package', 'Design', 2000.00, 'weekly', 'Design Services', 'Complete UI design package'),
    (6, 'React Development', 'Development', 110.00, 'hourly', 'Web Development', 'Frontend development using React'),
    (7, 'API Development', 'Development', 130.00, 'hourly', 'Web Development', 'Building REST APIs'),
    (8, 'Data Scientist', 'Research', 150.00, 'hourly', 'AI Research', 'AI/ML research and development'),
    (9, 'Cloud Computing', 'Infrastructure', 500.00, 'monthly', 'Cloud Services', 'AWS computing resources'),
    (10, 'Project Management Software', 'Tools', 50.00, 'monthly', 'PM Tools', 'Project management software licenses'),
    (11, 'Agile Training Course', 'Training', 1500.00, 'weekly', 'Training Services', 'Team training in Agile methodologies')
])

# Add some sample expenses
cursor.executemany('''
INSERT INTO expenses (line_item_id, product_id, amount, quantity, date_incurred, description)
VALUES (?, ?, ?, ?, ?, ?)
''', [
    (1, 1, 150.00, 8, '2025-01-15', 'January Facebook Ads Management'),
    (1, 2, 100.00, 5, '2025-01-20', 'January Instagram Content Creation'),
    (2, 3, 75.00, 10, '2025-01-25', 'Blog Posts - January Batch'),
    (3, 5, 120.00, 4, '2025-02-01', 'Email Template Design - Q1'),
])

# Commit changes and close connection
conn.commit()
conn.close()

print("Database, tables, and test data created successfully!")
