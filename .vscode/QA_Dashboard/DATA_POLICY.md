# 📝 Data Creation Policy

## ⚠️ CRITICAL RULES

### 🚫 NEVER Create Sample Data Automatically

**I (Kimi) will NEVER:**
- Create sample tasks in the database
- Insert dummy/test data automatically
- Generate example records
- Pre-populate the database with tasks

### ✅ Only Users Create Data

**Tasks can ONLY be created by:**
- Admin users through the UI
- Users clicking "Add Task" button
- Manual entry via the application interface

---

## 📋 What Gets Created Automatically

| Item | Created Automatically | Purpose |
|------|---------------------|---------|
| **Database Tables** | ✅ Yes | Structure required to run |
| **Users (Assignees)** | ✅ Yes | Required for dropdown - Rahul, Suraj, Neet, Anita |
| **Sample Tasks** | ❌ NO | Users must create these |
| **Test Data** | ❌ NO | Users must create these |

---

## 🔧 Database Initialization (init-db.js)

The `init-db.js` script will ONLY:

1. ✅ Create tables (tasks, users, history, settings)
2. ✅ Insert users (Rahul, Suraj, Neet, Anita)
3. ❌ **WILL NOT insert any tasks**

---

## 📊 Empty Database on First Run

When you first start the application:
- ✅ Server starts
- ✅ Database connects
- ✅ Tables created
- ✅ Users available
- 📝 **Task count: 0 (empty)**

Users must create tasks through the UI!

---

## 🛡️ My Promise

**I will NEVER:**
```javascript
❌ INSERT INTO tasks (...) VALUES (...)  // NO sample tasks
❌ Generate dummy data
❌ Create example records
❌ Pre-populate with test data
```

**I will ONLY:**
```javascript
✅ CREATE TABLE IF NOT EXISTS  // Create structure only
✅ INSERT INTO users (...)     // Users for dropdown only
```

---

## 🎯 Summary

| Question | Answer |
|----------|--------|
| Will sample tasks be created? | ❌ NO |
| Who creates tasks? | 👤 Users via UI only |
| What about demo data? | ❌ NOT created automatically |
| Empty dashboard on start? | ✅ YES (normal) |

---

## 📝 For Developers

If you need sample data for testing, you must:
1. Create tasks manually through UI
2. Or ask user for explicit approval to add test data

**Default state: EMPTY DATABASE with only users**

---

*Policy version: 1.0*
*Last updated: 2026-02-10*
