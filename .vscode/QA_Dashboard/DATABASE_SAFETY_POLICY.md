# 🛡️ Database Safety Policy

## CRITICAL RULES

### ⚠️ NEVER DELETE WITHOUT APPROVAL
**I (Kimi) will NEVER:**
- Delete the database without your explicit approval
- Delete any records without your explicit approval  
- Run `rm` on database files without confirmation
- Run `init-db` without confirmation (this deletes existing data)

### ✅ APPROVAL REQUIRED FOR:
| Operation | Required Confirmation |
|-----------|---------------------|
| Delete database file | Double confirmation + username |
| Delete all tasks | Single confirmation |
| Delete single task | Single confirmation |
| Reset database | Double confirmation + username |
| Reinitialize database | Explicit approval |

---

## 📝 Safe Operations Checklist

Before ANY destructive operation, I will:

1. **Inform you** of exactly what will be deleted
2. **Show backup** options
3. **Ask for explicit approval** in writing
4. **Confirm once more** before executing
5. **Create backup** if possible before deletion

---

## 🔒 Approved Commands

I will only use these safe scripts for database operations:

```bash
# Safe deletion script (requires approval)
./safe-delete.sh

# Stop server only (no data deletion)
./stop.sh

# Launch/Start server (no data deletion)
./launch.sh
```

---

## 🚫 Forbidden Commands (Require Approval)

I will NOT run these without your explicit written approval:

```bash
# NEVER run without approval:
rm database/qa_dashboard.db
rm -rf database/
cd backend && npm run init-db   # This deletes existing data!
sqlite3 database/qa_dashboard.db "DELETE FROM tasks;"
sqlite3 database/qa_dashboard.db "DROP TABLE tasks;"
```

---

## ✅ What I Can Do Without Approval

Safe operations that don't delete data:

```bash
# Read-only operations ✅
curl http://localhost:3000/api/tasks
curl http://localhost:3000/api/stats
ls database/
./launch.sh  # Start server
./stop.sh    # Stop server

# Create/Update operations ✅
curl -X POST http://localhost:3000/api/tasks    # Create task
curl -X PUT http://localhost:3000/api/tasks/1   # Update task
```

---

## 🆘 Emergency Contacts

If database is accidentally deleted:
1. Check for backup files in `./database/backup_*.db`
2. Contact system administrator
3. Restore from latest backup

---

## 📜 My Promise

**I will always ask for your approval before:**
- 🗑️ Deleting any data
- 🔄 Resetting the database
- 🧹 Cleaning/initializing the database

**Your data is precious. I will protect it.**

---

*Last updated: 2026-02-10*
*Policy version: 1.0*

---

## 📝 ADDITIONAL POLICY: No Automatic Data Creation

### Sample Tasks / Demo Data

**I will NEVER create sample tasks or demo data automatically.**

- ❌ No pre-populated tasks
- ❌ No example records
- ❌ No dummy data
- ❌ No test data insertion

**Users must create all tasks through the UI.**

This ensures:
- Clean, empty database on fresh install
- No accidental data pollution
- Users have full control over their data
