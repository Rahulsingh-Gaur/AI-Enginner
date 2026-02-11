const sqlite3 = require('sqlite3').verbose();
const path = require('path');

const DB_PATH = path.join(__dirname, '../database/qa_dashboard.db');

const db = new sqlite3.Database(DB_PATH, (err) => {
    if (err) {
        console.error('Error opening database:', err);
        process.exit(1);
    }
    console.log('Connected to SQLite database');
});

// Create tables
const createTables = `
-- Tasks table
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'Unassigned',
    previous_status TEXT,
    priority TEXT DEFAULT 'Medium',
    assignee TEXT,
    start_date DATE,
    due_date DATE,
    module TEXT,
    environment TEXT DEFAULT 'QA',
    tags TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Task history/activity log
CREATE TABLE IF NOT EXISTS task_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER,
    action TEXT NOT NULL,
    old_value TEXT,
    new_value TEXT,
    performed_by TEXT,
    performed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE
);

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE,
    role TEXT DEFAULT 'QA Engineer',
    avatar_color TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Settings table
CREATE TABLE IF NOT EXISTS settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key TEXT UNIQUE NOT NULL,
    value TEXT,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
`;

db.exec(createTables, (err) => {
    if (err) {
        console.error('Error creating tables:', err);
        db.close();
        process.exit(1);
    }
    console.log('Tables created successfully');
    
    // Insert users (assignees) - these are required for the dropdown
    const insertUsers = `
        INSERT OR IGNORE INTO users (name, email, role, avatar_color) VALUES
        ('Rahul', 'rahul@example.com', 'QA Engineer', '#6366f1'),
        ('Suraj', 'suraj@example.com', 'QA Engineer', '#ec4899'),
        ('Neet', 'neet@example.com', 'QA Engineer', '#f59e0b'),
        ('Anita', 'anita@example.com', 'QA Engineer', '#10b981');
    `;
    
    db.exec(insertUsers, (err) => {
        if (err) {
            console.error('Error inserting users:', err);
        } else {
            console.log('Users inserted');
        }
        
        // NOTE: No sample tasks are inserted automatically.
        // Tasks should be created by users through the UI only.
        console.log('✅ Database initialized successfully!');
        console.log('📝 Note: No sample tasks created. Tasks should be added via UI.');
        console.log(`📁 Database location: ${DB_PATH}`);
        db.close();
    });
});
