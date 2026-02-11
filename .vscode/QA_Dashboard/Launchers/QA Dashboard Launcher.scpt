-- QA Dashboard Launcher AppleScript
-- Double-click this file to launch QA Dashboard

set scriptPath to POSIX path of (path to me)
set parentFolder to do shell script "dirname " & quoted form of scriptPath
set projectFolder to do shell script "cd " & quoted form of parentFolder & "/.. && pwd"

-- Check if server is already running
try
    do shell script "lsof -i :3000"
    set serverRunning to true
on error
    set serverRunning to false
end try

if serverRunning then
    display notification "Opening QA Dashboard in browser..." with title "QA Dashboard"
    do shell script "open http://localhost:3000"
else
    display notification "Starting QA Dashboard server..." with title "QA Dashboard"
    
    -- Start the server in background
    do shell script "cd " & quoted form of projectFolder & " && ./launch.sh > /dev/null 2>&1 &"
    
    -- Wait for server to start
    delay 3
    
    -- Try to connect
    repeat 10 times
        try
            do shell script "curl -s http://localhost:3000/api/health"
            exit repeat
        on error
            delay 1
        end try
    end repeat
    
    -- Open browser
    do shell script "open http://localhost:3000"
end if
