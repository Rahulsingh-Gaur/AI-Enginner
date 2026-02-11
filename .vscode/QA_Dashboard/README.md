# 🧪 QA Task Manager

A fully functional web-based QA Task Management System with local SQLite database integration.

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Node](https://img.shields.io/badge/node-%3E%3D14.0.0-brightgreen.svg)
![SQLite](https://img.shields.io/badge/database-SQLite-orange.svg)

## ✨ Features

### Task Management
- 📋 **Multiple Views:** Kanban Board, Table View, List View
- 🏷️ **Task Properties:** Status, Priority, Assignee, Due Date, Tags
- 🔍 **Search & Filter:** Real-time search with multiple filters
- 📊 **Statistics Dashboard:** Visual metrics and progress tracking
- 🖱️ **Drag & Drop:** Move tasks between columns in Kanban view

### Database Integration
- 💾 **SQLite Database:** Local persistent storage
- 🔄 **RESTful API:** Full CRUD operations via HTTP
- 📱 **Offline Support:** Graceful fallback to localStorage
- ⚡ **Auto-refresh:** Real-time data synchronization

### User Experience
- 🎨 **Modern UI:** Clean, responsive design with smooth animations
- ⌨️ **Keyboard Shortcuts:** Alt+N for new task, Escape to close
- 🔔 **Toast Notifications:** Action feedback
- 📱 **Responsive:** Works on desktop and mobile

---

## 🚀 Quick Start

### Prerequisites
- Node.js (v14 or higher)
- npm or yarn
- Modern web browser

### Installation

1. **Navigate to project directory:**
   ```bash
   cd .vscode/QA_Dashboard/backend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Initialize database:**
   ```bash
   npm run init-db
   ```

4. **Start the server:**
   ```bash
   npm start
   # Or for development with auto-restart:
   npm run dev
   ```

5. **Open the application:**
   - Open `Dashboard.HTML` in your browser
   - Or visit: http://localhost:3000

---

## 📁 Project Structure

```
QA_Dashboard/
├── Dashboard.HTML          # Main frontend file
├── README.md               # This file
├── progress.md             # Development progress
├── backend/
│   ├── package.json        # Node dependencies
│   ├── server.js           # Express server
│   └── init-db.js          # Database setup
├── database/
│   └── qa_dashboard.db     # SQLite database
└── public/
    └── js/
        └── app.js          # Frontend JavaScript
```

---

## 🔌 API Documentation

### Base URL
```
http://localhost:3000/api
```

### Endpoints

#### Health Check
```http
GET /api/health
```

#### Tasks
```http
GET    /api/tasks              # List all tasks
GET    /api/tasks?status=New   # Filter by status
GET    /api/tasks/:id          # Get single task
POST   /api/tasks              # Create task
PUT    /api/tasks/:id          # Update task
PATCH  /api/tasks/:id/status   # Update status only
DELETE /api/tasks/:id          # Delete task
```

#### Statistics
```http
GET /api/stats    # Dashboard statistics
```

#### Users
```http
GET /api/users    # List team members
```

### Example Request
```javascript
// Create a new task
fetch('http://localhost:3000/api/tasks', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    title: 'Test login functionality',
    description: 'Verify all login scenarios',
    status: 'New',
    priority: 'High',
    assignee: 'Rahul S.',
    due_date: '2026-02-15',
    tags: ['Bug', 'UI']
  })
});
```

---

## 🛠️ Configuration

### Environment Variables
Create a `.env` file in the `backend` folder:
```env
PORT=3000
NODE_ENV=development
```

### Database Location
The SQLite database is stored at:
```
database/qa_dashboard.db
```

---

## 🎯 Usage Guide

### Creating a Task
1. Click "➕ Add Task" button
2. Fill in task details
3. Select assignee, priority, and due date
4. Add relevant tags
5. Click "💾 Save Task"

### Managing Tasks
- **Double-click** a task to edit
- **Click status badge** to cycle through statuses
- **Drag and drop** in Kanban view to change status
- **Use filters** to find specific tasks

### Drag & Drop
1. **Click and hold** any task card in Kanban view
2. **Drag** the card to a different column
3. **Release** to drop and automatically update status
4. Visual feedback shows valid drop zones

### Keyboard Shortcuts
| Shortcut | Action |
|----------|--------|
| `Alt + N` | New task |
| `Escape` | Close modal |
| `Ctrl + F` | Focus search |

---

## 🔧 Troubleshooting

### Server won't start
```bash
# Check if port 3000 is in use
lsof -i :3000

# Use different port
PORT=3001 npm start
```

### Database issues
```bash
# Reinitialize database
rm database/qa_dashboard.db
npm run init-db
```

### CORS errors
- Ensure server is running on port 3000
- Check browser console for errors
- Verify API_BASE_URL in app.js

---

## 📝 Development

### Adding New Features
1. Update `backend/server.js` for API changes
2. Modify `public/js/app.js` for frontend
3. Update `Dashboard.HTML` for UI changes
4. Document changes in `progress.md`

### Database Migrations
Edit `backend/init-db.js` and run:
```bash
npm run init-db
```

---

## 📜 License

MIT License - Feel free to use and modify!

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## 📧 Support

For issues or questions:
- Check the troubleshooting section
- Review the API documentation
- Examine the browser console for errors

---

**Happy Testing! 🧪✨**
