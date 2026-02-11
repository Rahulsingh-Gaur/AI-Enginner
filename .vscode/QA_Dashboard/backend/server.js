const express = require('express');
const cors = require('cors');
const sqlite3 = require('sqlite3').verbose();
const path = require('path');
const fs = require('fs');
const os = require('os');

const app = express();
const PORT = process.env.PORT || 3000;

// ============================================
// SECURITY CONFIGURATION - LOCAL ONLY
// ============================================

// Security check: Verify all requests are from localhost
const LOCALHOST_IPS = ['127.0.0.1', '::1', '::ffff:127.0.0.1', '::ffff:127.0.0.1', 'localhost'];

function isLocalRequest(req) {
    // Get client IP from various sources
    const clientIp = req.connection?.remoteAddress || 
                     req.socket?.remoteAddress || 
                     req.ip ||
                     (req.headers['x-forwarded-for'] ? req.headers['x-forwarded-for'].split(',')[0].trim() : null);
    
    // Check if IP is localhost - be more lenient
    const isLocal = !clientIp || // If no IP (direct socket), allow
                    LOCALHOST_IPS.includes(clientIp) || 
                    clientIp === '127.0.0.1' || 
                    clientIp === '::1' ||
                    clientIp.startsWith('127.') ||
                    clientIp.startsWith('::ffff:127.') ||
                    clientIp.startsWith('::1') ||
                    clientIp === 'localhost';
    
    return isLocal;
}

// Security middleware - Block external requests
const securityMiddleware = (req, res, next) => {
    // Skip security check for health and security endpoints
    if (req.path === '/api/health' || req.path === '/api/security/audit') {
        return next();
    }
    
    if (!isLocalRequest(req)) {
        console.log(`🚨 SECURITY ALERT: Blocked external request`);
        console.log(`   IP: ${req.connection?.remoteAddress || req.ip}`);
        console.log(`   Path: ${req.path}`);
        return res.status(403).json({ 
            error: 'Access Denied', 
            message: 'This server only accepts connections from localhost. External requests are blocked for security.',
            clientIp: req.connection?.remoteAddress || req.ip
        });
    }
    next();
};

// Apply security middleware first
app.use(securityMiddleware);

// Restrict CORS to localhost only
const corsOptions = {
    origin: function (origin, callback) {
        // Allow requests with no origin (same-origin requests)
        if (!origin) return callback(null, true);
        
        // Only allow localhost origins
        if (origin.startsWith('http://localhost:') || 
            origin.startsWith('http://127.0.0.1:')) {
            return callback(null, true);
        }
        
        console.log(`🚨 CORS blocked origin: ${origin}`);
        callback(new Error('CORS policy: Only localhost origins allowed'));
    },
    credentials: true,
    methods: ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS'],
    allowedHeaders: ['Content-Type', 'Authorization']
};

app.use(cors(corsOptions));

// Security headers
app.use((req, res, next) => {
    // Prevent the app from being embedded in iframes (clickjacking protection)
    res.setHeader('X-Frame-Options', 'DENY');
    // XSS protection
    res.setHeader('X-XSS-Protection', '1; mode=block');
    // Prevent MIME type sniffing
    res.setHeader('X-Content-Type-Options', 'nosniff');
    // Referrer policy
    res.setHeader('Referrer-Policy', 'strict-origin-when-cross-origin');
    // Content Security Policy - only allow local resources
    res.setHeader('Content-Security-Policy', "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; font-src 'self'; img-src 'self' data:; connect-src 'self' http://localhost:* http://127.0.0.1:*;");
    next();
});

// Body parsing middleware
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// ============================================
// DATABASE SETUP - LOCAL SQLITE
// ============================================

const DB_PATH = path.join(__dirname, '../database/qa_dashboard.db');
const dbDir = path.dirname(DB_PATH);

// Ensure database directory exists
if (!fs.existsSync(dbDir)) {
    fs.mkdirSync(dbDir, { recursive: true });
}

const db = new sqlite3.Database(DB_PATH, (err) => {
    if (err) {
        console.error('Error connecting to database:', err);
    } else {
        console.log('✅ Connected to SQLite database (LOCAL ONLY)');
        console.log(`📁 Database location: ${DB_PATH}`);
    }
});

// Run init-db if tables don't exist
db.get("SELECT name FROM sqlite_master WHERE type='table' AND name='tasks'", (err, row) => {
    if (err || !row) {
        console.log('📊 Initializing database...');
        require('./init-db.js');
    }
});

// ============================================
// SECURITY AUDIT ENDPOINTS
// ============================================

// Security audit endpoint - verify system is local
app.get('/api/security/audit', (req, res) => {
    const networkInterfaces = os.networkInterfaces();
    const connections = [];
    
    // Get all network interfaces
    Object.keys(networkInterfaces).forEach(iface => {
        networkInterfaces[iface].forEach(details => {
            connections.push({
                interface: iface,
                address: details.address,
                family: details.family,
                internal: details.internal
            });
        });
    });
    
    const audit = {
        timestamp: new Date().toISOString(),
        database: {
            type: 'SQLite (Local File)',
            location: DB_PATH,
            isLocal: true,
            networkAccess: false
        },
        server: {
            port: PORT,
            bindAddress: '127.0.0.1 (localhost only)',
            corsPolicy: 'localhost-only',
            externalRequests: 'BLOCKED'
        },
        network: {
            interfaces: connections,
            externalAccess: false,
            note: 'Server only accepts connections from 127.0.0.1 and localhost'
        },
        securityFeatures: {
            localhostOnly: true,
            corsRestricted: true,
            securityHeaders: true,
            externalIpBlocking: true,
            clickjackingProtection: true,
            xssProtection: true
        },
        dataFlow: {
            incoming: 'Only from localhost',
            outgoing: 'NONE - No external APIs called',
            storage: 'Local SQLite file only'
        }
    };
    
    res.json({ success: true, audit });
});

// Connection test endpoint
app.get('/api/security/connection-test', (req, res) => {
    res.json({
        success: true,
        message: 'Connection is local',
        clientIp: req.ip,
        isLocalhost: isLocalRequest(req),
        timestamp: new Date().toISOString()
    });
});

// ============================================
// STATIC FILES - LOCAL ONLY
// ============================================

// Serve static files from parent directory
app.use(express.static(path.join(__dirname, '..')));

// ============================================
// API ROUTES - Tasks
// ============================================

// Get all tasks
app.get('/api/tasks', (req, res) => {
    const { status, priority, assignee, search } = req.query;
    let sql = 'SELECT * FROM tasks WHERE 1=1';
    const params = [];

    if (status) {
        sql += ' AND status = ?';
        params.push(status);
    }
    if (priority) {
        sql += ' AND priority = ?';
        params.push(priority);
    }
    if (assignee) {
        // Support multiple assignees - check if assignee field contains the selected assignee
        sql += ' AND (assignee = ? OR assignee LIKE ? OR assignee LIKE ? OR assignee LIKE ?)';
        params.push(assignee, `${assignee},%`, `%,${assignee},%`, `%,${assignee}`);
    }
    if (search) {
        sql += ' AND (title LIKE ? OR description LIKE ? OR module LIKE ? OR tags LIKE ?)';
        const searchTerm = `%${search}%`;
        params.push(searchTerm, searchTerm, searchTerm, searchTerm);
    }

    sql += ' ORDER BY CASE priority WHEN "Critical" THEN 1 WHEN "High" THEN 2 WHEN "Medium" THEN 3 ELSE 4 END, created_at DESC';

    db.all(sql, params, (err, rows) => {
        if (err) {
            console.error('Error fetching tasks:', err);
            return res.status(500).json({ error: 'Failed to fetch tasks' });
        }
        // Parse tags from string to array
        const tasks = rows.map(row => ({
            ...row,
            tags: row.tags ? row.tags.split(',') : []
        }));
        res.json({ success: true, data: tasks });
    });
});

// Get task by ID
app.get('/api/tasks/:id', (req, res) => {
    const { id } = req.params;
    db.get('SELECT * FROM tasks WHERE id = ?', [id], (err, row) => {
        if (err) {
            return res.status(500).json({ error: 'Failed to fetch task' });
        }
        if (!row) {
            return res.status(404).json({ error: 'Task not found' });
        }
        row.tags = row.tags ? row.tags.split(',') : [];
        res.json({ success: true, data: row });
    });
});

// Create new task
app.post('/api/tasks', (req, res) => {
    let { title, description, status, priority, assignee, start_date, due_date, module, environment, tags } = req.body;
    
    // Debug logging
    console.log('Received assignee:', assignee, typeof assignee);
    
    // Generate task_id
    const task_id = `QA-${Date.now().toString(36).toUpperCase()}`;
    const tagsStr = Array.isArray(tags) ? tags.join(',') : tags;
    
    // Handle multiple assignees - convert array to comma-separated string
    let assigneeStr;
    if (Array.isArray(assignee)) {
        assigneeStr = assignee.join(',');
    } else if (typeof assignee === 'object' && assignee !== null) {
        // Handle case where assignee might be an object
        assigneeStr = Object.values(assignee).filter(v => typeof v === 'string').join(',');
    } else {
        assigneeStr = assignee;
    }
    
    console.log('Processed assigneeStr:', assigneeStr);

    const sql = `
        INSERT INTO tasks (task_id, title, description, status, priority, assignee, start_date, due_date, module, environment, tags)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `;

    db.run(sql, [task_id, title, description, status || 'New', priority || 'Medium', assigneeStr, start_date, due_date, module, environment || 'QA', tagsStr], function(err) {
        if (err) {
            console.error('Error creating task:', err);
            return res.status(500).json({ error: 'Failed to create task' });
        }

        // Log activity
        db.run('INSERT INTO task_history (task_id, action, new_value, performed_by) VALUES (?, ?, ?, ?)',
            [this.lastID, 'created', `Task created with status: ${status || 'New'}`, 'System']);

        res.status(201).json({ 
            success: true, 
            message: 'Task created successfully',
            data: { id: this.lastID, task_id }
        });
    });
});

// Update task
app.put('/api/tasks/:id', (req, res) => {
    const { id } = req.params;
    const { title, description, status, previous_status, priority, assignee, start_date, due_date, module, environment, tags } = req.body;
    const tagsStr = Array.isArray(tags) ? tags.join(',') : tags;
    // Handle multiple assignees - convert array to comma-separated string
    const assigneeStr = Array.isArray(assignee) ? assignee.join(',') : assignee;

    // Get current task for history
    db.get('SELECT * FROM tasks WHERE id = ?', [id], (err, oldTask) => {
        if (err || !oldTask) {
            return res.status(404).json({ error: 'Task not found' });
        }

        // Build SQL dynamically based on provided fields
        const updates = [];
        const params = [];
        
        if (title !== undefined) { updates.push('title = ?'); params.push(title); }
        if (description !== undefined) { updates.push('description = ?'); params.push(description); }
        if (status !== undefined) { updates.push('status = ?'); params.push(status); }
        if (previous_status !== undefined) { updates.push('previous_status = ?'); params.push(previous_status); }
        if (priority !== undefined) { updates.push('priority = ?'); params.push(priority); }
        if (assignee !== undefined) { updates.push('assignee = ?'); params.push(assigneeStr); }
        if (start_date !== undefined) { updates.push('start_date = ?'); params.push(start_date); }
        if (due_date !== undefined) { updates.push('due_date = ?'); params.push(due_date); }
        if (module !== undefined) { updates.push('module = ?'); params.push(module); }
        if (environment !== undefined) { updates.push('environment = ?'); params.push(environment); }
        if (tags !== undefined) { updates.push('tags = ?'); params.push(tagsStr); }
        
        updates.push('updated_at = CURRENT_TIMESTAMP');
        params.push(id);

        const sql = `UPDATE tasks SET ${updates.join(', ')} WHERE id = ?`;

        db.run(sql, params, function(err) {
            if (err) {
                console.error('Error updating task:', err);
                return res.status(500).json({ error: 'Failed to update task' });
            }

            // Log status change if different
            if (status !== undefined && oldTask.status !== status) {
                db.run('INSERT INTO task_history (task_id, action, old_value, new_value, performed_by) VALUES (?, ?, ?, ?, ?)',
                    [id, 'status_changed', oldTask.status, status, 'System']);
            }

            res.json({ success: true, message: 'Task updated successfully' });
        });
    });
});

// Update task status only
app.patch('/api/tasks/:id/status', (req, res) => {
    const { id } = req.params;
    const { status } = req.body;

    db.get('SELECT status FROM tasks WHERE id = ?', [id], (err, row) => {
        if (err || !row) {
            return res.status(404).json({ error: 'Task not found' });
        }

        const oldStatus = row.status;

        db.run('UPDATE tasks SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?', [status, id], function(err) {
            if (err) {
                return res.status(500).json({ error: 'Failed to update status' });
            }

            // Log the change
            db.run('INSERT INTO task_history (task_id, action, old_value, new_value, performed_by) VALUES (?, ?, ?, ?, ?)',
                [id, 'status_changed', oldStatus, status, 'System']);

            res.json({ success: true, message: 'Status updated', oldStatus, newStatus: status });
        });
    });
});

// Delete task
app.delete('/api/tasks/:id', (req, res) => {
    const { id } = req.params;

    db.run('DELETE FROM tasks WHERE id = ?', [id], function(err) {
        if (err) {
            return res.status(500).json({ error: 'Failed to delete task' });
        }
        if (this.changes === 0) {
            return res.status(404).json({ error: 'Task not found' });
        }
        res.json({ success: true, message: 'Task deleted successfully' });
    });
});

// ============================================
// API ROUTES - Statistics
// ============================================

app.get('/api/stats', (req, res) => {
    const today = new Date().toISOString().split('T')[0];
    
    const queries = {
        total: 'SELECT COUNT(*) as count FROM tasks',
        byStatus: 'SELECT status, COUNT(*) as count FROM tasks GROUP BY status',
        byPriority: 'SELECT priority, COUNT(*) as count FROM tasks GROUP BY priority',
        byAssignee: 'SELECT assignee, COUNT(*) as count FROM tasks GROUP BY assignee',
        overdue: `SELECT COUNT(*) as count FROM tasks WHERE status != 'Done' AND due_date < '${today}'`,
        completedToday: `SELECT COUNT(*) as count FROM tasks WHERE status = 'Done' AND date(updated_at) = '${today}'`
    };

    const results = {};
    let completed = 0;
    const totalQueries = Object.keys(queries).length;

    Object.entries(queries).forEach(([key, sql]) => {
        db.all(sql, [], (err, rows) => {
            if (err) {
                results[key] = key === 'total' || key === 'overdue' || key === 'completedToday' ? 0 : [];
            } else {
                if (key === 'total' || key === 'overdue' || key === 'completedToday') {
                    results[key] = rows[0]?.count || 0;
                } else {
                    results[key] = rows;
                }
            }
            completed++;
            if (completed === totalQueries) {
                res.json({ success: true, data: results });
            }
        });
    });
});

// ============================================
// API ROUTES - Users
// ============================================

app.get('/api/users', (req, res) => {
    db.all('SELECT * FROM users ORDER BY name', [], (err, rows) => {
        if (err) {
            return res.status(500).json({ error: 'Failed to fetch users' });
        }
        res.json({ success: true, data: rows });
    });
});

// ============================================
// API ROUTES - Task History
// ============================================

app.get('/api/tasks/:id/history', (req, res) => {
    const { id } = req.params;
    db.all('SELECT * FROM task_history WHERE task_id = ? ORDER BY performed_at DESC', [id], (err, rows) => {
        if (err) {
            return res.status(500).json({ error: 'Failed to fetch history' });
        }
        res.json({ success: true, data: rows });
    });
});

// ============================================
// Health Check
// ============================================

app.get('/api/health', (req, res) => {
    res.json({ 
        status: 'OK', 
        timestamp: new Date().toISOString(),
        database: 'SQLite (Local)',
        security: 'Localhost-only mode',
        externalAccess: false,
        version: '1.0.0'
    });
});

// ============================================
// Start Server - LOCALHOST ONLY
// ============================================

// Bind to localhost only - prevents external network access
const server = app.listen(PORT, '127.0.0.1', () => {
    console.log(`
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║     🧪 QA Task Manager - Backend Server                  ║
║                                                          ║
║     🔒 SECURITY: Localhost-only mode                     ║
║     📡 Server running at: http://localhost:${PORT}          ║
║     📊 API Base: http://localhost:${PORT}/api               ║
║     🗄️  Database: SQLite (Local File)                     ║
║                                                          ║
║     ⚠️  External connections are BLOCKED                 ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
    `);
    
    // Log security info
    console.log('🔒 Security Features Active:');
    console.log('   • CORS restricted to localhost only');
    console.log('   • External IP requests blocked');
    console.log('   • Security headers enabled');
    console.log('   • No external API calls');
    console.log('   • Database is local file only\n');
});

// Graceful shutdown
process.on('SIGINT', () => {
    console.log('\n👋 Closing database connection...');
    db.close(() => {
        console.log('Database connection closed');
        process.exit(0);
    });
});

module.exports = app;
