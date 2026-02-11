# 🚀 QA Dashboard - Launch Guide

Quick and easy ways to launch your QA Dashboard without using VS Code or terminal commands.

---

## Option 1: Double-Click Script (Easiest)

### Setup (One-time):
1. Open **Finder**
2. Navigate to `.vscode/QA_Dashboard/`
3. Right-click on `launch.sh` → **Get Info**
4. Under "Open with:" select **Terminal**
5. Click **Change All...**

### Usage:
Simply **double-click** the `launch.sh` file - it will:
- Start the server (if not running)
- Open your browser automatically
- Show notifications

---

## Option 2: Dock Icon (Recommended)

### Method A: Using Automator

1. Open **Automator** (Press `Cmd+Space`, type "Automator")
2. Choose **Application**
3. Search for "Run Shell Script" and drag it to the workflow
4. Paste this code:
```bash
PROJECT_DIR="$HOME/Learn AI/.vscode/QA_Dashboard"
cd "$PROJECT_DIR"
./launch.sh
```
5. Save as: `QA Dashboard` in your **Applications** folder
6. Drag the saved app to your **Dock**

### Method B: Using AppleScript

1. Open **Script Editor** (Press `Cmd+Space`, type "Script Editor")
2. Paste this code:
```applescript
do shell script "cd ~/Learn\\ AI/.vscode/QA_Dashboard && ./launch.sh"
```
3. File → Export...
4. Format: **Application**
5. Save to **Applications** folder
6. Drag to your **Dock**

---

## Option 3: Keyboard Shortcut

### Using Spotlight + Alias:

1. Open Terminal and run:
```bash
echo 'alias qad="cd ~/.vscode/QA_Dashboard && ./launch.sh"' >> ~/.zshrc
source ~/.zshrc
```

2. Now simply:
   - Press `Cmd+Space`
   - Type "Terminal"
   - Type `qad` and press Enter

---

## Option 4: Menu Bar App (Advanced)

Using [SwiftBar](https://swiftbar.app/) or [xBar](https://xbarapp.com/):

Create a plugin file at `~/Library/Application Support/SwiftBar/qa-dashboard.1m.sh`:
```bash
#!/bin/bash

if lsof -i :3000 > /dev/null; then
    echo "🟢 QA Dashboard"
    echo "---"
    echo "Open Dashboard | href=http://localhost:3000"
    echo "Stop Server | bash=$HOME/Learn\ AI/.vscode/QA_Dashboard/stop.sh"
else
    echo "⚪ QA Dashboard"
    echo "---"
    echo "Start Server | bash=$HOME/Learn\ AI/.vscode/QA_Dashboard/launch.sh"
fi
```

---

## Option 5: VS Code Task (If you prefer VS Code)

Add to `.vscode/tasks.json`:
```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Launch QA Dashboard",
      "type": "shell",
      "command": "./launch.sh",
      "options": {
        "cwd": "${workspaceFolder}/.vscode/QA_Dashboard"
      },
      "group": {
        "kind": "build",
        "isDefault": true
      }
    }
  ]
}
```

Then press `Cmd+Shift+B` to launch.

---

## 📁 Launch Files Included:

| File | Purpose |
|------|---------|
| `launch.sh` | Main launcher - starts server & opens browser |
| `stop.sh` | Stops the server |
| `Launchers/Launch QA Dashboard.sh` | Wrapper for Automator |
| `Launchers/QA Dashboard Launcher.scpt` | AppleScript version |
| `QA Dashboard.app` | macOS app bundle (experimental) |

---

## 🎯 Quick Start (Recommended Setup):

### Step 1: Create Dock Icon
1. Open **Automator**
2. New **Application**
3. Add "Run Shell Script" action
4. Paste: `cd ~/Learn\ AI/.vscode/QA_Dashboard && ./launch.sh`
5. Save to Applications as "QA Dashboard"
6. Drag to Dock

### Step 2: Launch
- **Single click** on Dock icon → Dashboard opens in browser

### Step 3: Stop
- Use `stop.sh` or close Terminal window

---

## 🔧 Troubleshooting:

### "Permission Denied" Error:
```bash
chmod +x ~/.vscode/QA_Dashboard/launch.sh
chmod +x ~/.vscode/QA_Dashboard/stop.sh
```

### "Node.js not found":
Install from https://nodejs.org/

### Port already in use:
Run `./stop.sh` first, then try again

### Script won't open by double-click:
1. Right-click `launch.sh` → **Get Info**
2. Open with: **Terminal**
3. Click **Change All**

---

## 🔔 Features:

✅ **Auto-detects** if server is already running  
✅ **Auto-opens** browser when ready  
✅ **macOS notifications** for status updates  
✅ **One-click** stop with `stop.sh`  
✅ **No Terminal knowledge** required  

---

## 📊 Launch Flow:

```
Click/Double-click
       ↓
┌──────────────┐
│  launch.sh   │
└──────────────┘
       ↓
Check Node.js ✓
       ↓
Check Server Running?
   ├─ Yes → Open Browser
   └─ No → Start Server → Wait → Open Browser
       ↓
🎉 Dashboard Ready!
```

---

**Questions?** Check the main README.md or run the security check!
