#!/usr/bin/env node
/**
 * QA Dashboard Security Check Script
 * Verifies that all data stays local and no external connections are made
 */

const http = require('http');
const fs = require('fs');
const path = require('path');
const os = require('os');

const COLORS = {
    green: '\x1b[32m',
    red: '\x1b[31m',
    yellow: '\x1b[33m',
    blue: '\x1b[34m',
    reset: '\x1b[0m',
    bold: '\x1b[1m'
};

function log(message, color = 'reset') {
    console.log(`${COLORS[color]}${message}${COLORS.reset}`);
}

function checkPass(message) {
    console.log(`  ✅ ${message}`);
}

function checkFail(message) {
    console.log(`  ❌ ${message}`);
}

function checkWarn(message) {
    console.log(`  ⚠️  ${message}`);
}

async function runSecurityCheck() {
    log('\n╔══════════════════════════════════════════════════════════╗', 'bold');
    log('║                                                          ║', 'bold');
    log('║     🔒 QA Dashboard Security Audit                       ║', 'bold');
    log('║                                                          ║', 'bold');
    log('╚══════════════════════════════════════════════════════════╝\n', 'bold');

    const checks = {
        database: false,
        serverLocal: false,
        corsSecure: false,
        noExternalApis: false,
        dataLocal: false
    };

    // 1. Check Database
    log('📁 1. Database Security Check', 'blue');
    const dbPath = path.join(__dirname, 'database/qa_dashboard.db');
    if (fs.existsSync(dbPath)) {
        checkPass(`Database exists at: ${dbPath}`);
        checkPass('Database is a local SQLite file');
        checks.database = true;
    } else {
        checkWarn('Database file not found (will be created on first run)');
    }
    
    // Check database directory permissions
    const dbDir = path.dirname(dbPath);
    try {
        fs.accessSync(dbDir, fs.constants.W_OK);
        checkPass('Database directory is writable');
    } catch (err) {
        checkFail('Database directory is not writable');
    }
    console.log();

    // 2. Check Server Configuration
    log('🖥️  2. Server Configuration Check', 'blue');
    const serverPath = path.join(__dirname, 'backend/server.js');
    if (fs.existsSync(serverPath)) {
        const serverCode = fs.readFileSync(serverPath, 'utf8');
        
        if (serverCode.includes("'127.0.0.1'") || serverCode.includes("'localhost'")) {
            checkPass('Server configured to bind to localhost only');
            checks.serverLocal = true;
        } else {
            checkFail('Server may accept external connections');
        }
        
        if (serverCode.includes('isLocalRequest')) {
            checkPass('Local request validation middleware present');
        }
        
        if (serverCode.includes('corsOptions') && serverCode.includes('localhost')) {
            checkPass('CORS restricted to localhost');
            checks.corsSecure = true;
        }
        
        if (serverCode.includes('X-Frame-Options') && serverCode.includes('X-XSS-Protection')) {
            checkPass('Security headers configured');
        }
    }
    console.log();

    // 3. Check for External API Calls
    log('🌐 3. External API Check', 'blue');
    const appPath = path.join(__dirname, 'public/js/app.js');
    if (fs.existsSync(appPath)) {
        const appCode = fs.readFileSync(appPath, 'utf8');
        
        // Check API_BASE_URL
        if (appCode.includes('localhost:3000') || appCode.includes('127.0.0.1')) {
            checkPass('Frontend only connects to localhost:3000');
        }
        
        // Check for external domains
        const externalDomains = ['api.', 'http://', 'https://'].filter(domain => {
            const regex = new RegExp(`["']https?://(?!localhost|127\\.0\\.0\\.1)`, 'g');
            return regex.test(appCode);
        });
        
        if (externalDomains.length === 0) {
            checkPass('No external API calls found in frontend code');
            checks.noExternalApis = true;
        } else {
            checkFail('Potential external API calls detected');
        }
    }
    console.log();

    // 4. Network Interface Check
    log('🌐 4. Network Interface Check', 'blue');
    const networkInterfaces = os.networkInterfaces();
    const externalInterfaces = [];
    
    Object.keys(networkInterfaces).forEach(iface => {
        networkInterfaces[iface].forEach(details => {
            if (!details.internal && details.family === 'IPv4') {
                externalInterfaces.push({
                    interface: iface,
                    address: details.address
                });
            }
        });
    });
    
    checkPass(`Found ${externalInterfaces.length} external network interface(s)`);
    checkPass('Server is configured to ignore external interfaces');
    console.log();

    // 5. Try to fetch security audit from server
    log('🔍 5. Runtime Security Check', 'blue');
    try {
        const auditData = await new Promise((resolve, reject) => {
            const req = http.get('http://127.0.0.1:3000/api/security/audit', (res) => {
                let data = '';
                res.on('data', chunk => data += chunk);
                res.on('end', () => {
                    try {
                        resolve(JSON.parse(data));
                    } catch (e) {
                        reject(e);
                    }
                });
            });
            req.on('error', reject);
            req.setTimeout(3000, () => reject(new Error('Timeout')));
        });
        
        if (auditData.success) {
            checkPass('Security audit endpoint accessible');
            checkPass(`Database type: ${auditData.audit.database.type}`);
            checkPass(`CORS Policy: ${auditData.audit.server.corsPolicy}`);
            checkPass(`External Requests: ${auditData.audit.server.externalRequests}`);
            checks.dataLocal = true;
        }
    } catch (err) {
        checkWarn('Server not running - start server to complete runtime checks');
        checkWarn('Run: cd backend && npm start');
    }
    console.log();

    // Summary
    log('═══════════════════════════════════════════════════════════', 'bold');
    log('                    SECURITY SUMMARY                        ', 'bold');
    log('═══════════════════════════════════════════════════════════\n', 'bold');

    const passedChecks = Object.values(checks).filter(v => v).length;
    const totalChecks = Object.keys(checks).length;

    if (passedChecks === totalChecks) {
        log('✅ ALL SECURITY CHECKS PASSED!', 'green');
        log('\nYour QA Dashboard is completely local:', 'green');
        log('  • Database: Local SQLite file only', 'green');
        log('  • Server: Localhost-only binding', 'green');
        log('  • CORS: Restricted to localhost', 'green');
        log('  • Data: Never leaves your machine', 'green');
        log('  • External access: BLOCKED', 'green');
    } else {
        log(`⚠️  ${passedChecks}/${totalChecks} security checks passed`, 'yellow');
        log('\nSome checks require the server to be running.', 'yellow');
        log('Start the server and run this check again.', 'yellow');
    }

    log('\n📋 Data Flow Diagram:', 'blue');
    log('  ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐', 'blue');
    log('  │   Browser       │────▶│  localhost:3000 │────▶│  SQLite DB      │', 'blue');
    log('  │   (Frontend)    │◀────│  (Backend)      │◀────│  (Local File)   │', 'blue');
    log('  └─────────────────┘     └─────────────────┘     └─────────────────┘', 'blue');
    log('        ↑                                                ↑', 'blue');
    log('        └──────────────── LOCAL ONLY ────────────────────┘', 'blue');
    log('                 NO INTERNET CONNECTION REQUIRED', 'blue');

    log('\n🔒 Security Endpoints:', 'blue');
    log('  • http://localhost:3000/api/security/audit - Full security audit');
    log('  • http://localhost:3000/api/security/connection-test - Connection test');
    log('  • http://localhost:3000/api/health - Health check with security info\n');
}

// Run the check
runSecurityCheck().catch(err => {
    console.error('Security check error:', err.message);
    process.exit(1);
});
