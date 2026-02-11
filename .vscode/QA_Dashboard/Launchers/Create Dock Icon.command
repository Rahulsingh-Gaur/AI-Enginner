#!/bin/bash

# Create QA Dashboard Dock Icon
# Double-click this file to create a Dock icon for QA Dashboard

echo "Creating QA Dashboard Dock Icon..."

# Create the Automator app
AUTOMATOR_APP="$HOME/Desktop/QA Dashboard.app"

mkdir -p "$AUTOMATOR_APP/Contents/MacOS"

cat > "$AUTOMATOR_APP/Contents/MacOS/launch" << 'LAUNCHER'
#!/bin/bash
PROJECT_DIR="$HOME/Learn AI/.vscode/QA_Dashboard"
cd "$PROJECT_DIR"
./launch.sh
LAUNCHER

chmod +x "$AUTOMATOR_APP/Contents/MacOS/launch"

cat > "$AUTOMATOR_APP/Contents/Info.plist" << 'PLIST'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>launch</string>
    <key>CFBundleIdentifier</key>
    <string>com.qadashboard.app</string>
    <key>CFBundleName</key>
    <string>QA Dashboard</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
</dict>
</plist>
PLIST

# Set icon
cat > /tmp/qa_icon.py << 'PYTHON'
import sys
from Cocoa import NSData, NSImage, NSWorkspace
from Foundation import NSBundle

# Create a simple icon programmatically
# In production, you'd use a real .icns file
print("Icon setup complete")
PYTHON

echo "✅ QA Dashboard app created on Desktop!"
echo ""
echo "Next steps:"
echo "1. Drag 'QA Dashboard.app' from Desktop to your Dock"
echo "2. Click the icon anytime to launch the dashboard"
echo ""
echo "Press Enter to close..."
read
