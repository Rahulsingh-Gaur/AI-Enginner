#!/bin/bash

# Safe Database Operations Script
# This script requires explicit user confirmation before any destructive operations

RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

DB_PATH="./database/qa_dashboard.db"

echo "╔══════════════════════════════════════════════════════════╗"
echo "║     ⚠️  DATABASE SAFETY GUARD                            ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Function to confirm dangerous operations
confirm_operation() {
    local operation="$1"
    local target="$2"
    
    echo "${RED}⚠️  WARNING: DESTRUCTIVE OPERATION DETECTED${NC}"
    echo ""
    echo "Operation: ${YELLOW}$operation${NC}"
    echo "Target: ${YELLOW}$target${NC}"
    echo ""
    echo "${RED}This action CANNOT be undone!${NC}"
    echo ""
    
    # Require explicit confirmation
    read -p "Are you sure? Type 'YES' to proceed (or any other key to cancel): " confirm
    
    if [ "$confirm" != "YES" ]; then
        echo ""
        echo "${GREEN}✅ Operation cancelled by user.${NC}"
        return 1
    fi
    
    # Double confirmation for database deletion
    if [[ "$operation" == *"DELETE DATABASE"* ]] || [[ "$operation" == *"RESET"* ]]; then
        echo ""
        echo "${RED}🔒 DOUBLE CONFIRMATION REQUIRED${NC}"
        read -p "Type your username '$(whoami)' to confirm: " username_confirm
        
        if [ "$username_confirm" != "$(whoami)" ]; then
            echo ""
            echo "${GREEN}✅ Operation cancelled - username mismatch.${NC}"
            return 1
        fi
    fi
    
    return 0
}

# Function to backup before delete
backup_database() {
    if [ -f "$DB_PATH" ]; then
        local backup_name="./database/backup_$(date +%Y%m%d_%H%M%S).db"
        cp "$DB_PATH" "$backup_name"
        echo "${GREEN}📦 Backup created: $backup_name${NC}"
        return 0
    fi
    return 1
}

# Show menu
echo "Select operation:"
echo ""
echo "1) View Database Info (Safe)"
echo "2) Backup Database (Safe)"
echo "3) Delete Single Task (Requires Approval)"
echo "4) Delete All Tasks (Requires Approval)"
echo "5) RESET ENTIRE DATABASE (Requires Double Approval)"
echo "6) Exit"
echo ""
read -p "Enter choice [1-6]: " choice

case $choice in
    1)
        echo ""
        echo "📊 Database Information:"
        if [ -f "$DB_PATH" ]; then
            ls -lh "$DB_PATH"
            echo ""
            echo "Task count:"
            sqlite3 "$DB_PATH" "SELECT COUNT(*) as total_tasks FROM tasks;" 2>/dev/null || echo "Unable to query - server may be running"
        else
            echo "Database file not found."
        fi
        ;;
    2)
        echo ""
        if backup_database; then
            echo "${GREEN}✅ Backup completed successfully${NC}"
        else
            echo "No database to backup."
        fi
        ;;
    3)
        read -p "Enter Task ID to delete: " task_id
        if confirm_operation "DELETE SINGLE TASK" "Task ID: $task_id"; then
            echo "Deleting task..."
            # Add actual delete command here with approval
            echo "${GREEN}✅ Task would be deleted here (demo mode)${NC}"
        fi
        ;;
    4)
        if confirm_operation "DELETE ALL TASKS" "All tasks in database"; then
            if backup_database; then
                echo "Deleting all tasks..."
                # Add actual delete command here with approval
                echo "${GREEN}✅ All tasks would be deleted here (demo mode)${NC}"
            fi
        fi
        ;;
    5)
        if confirm_operation "🔴 RESET ENTIRE DATABASE 🔴" "Complete database deletion and reinitialization"; then
            if backup_database; then
                echo ""
                echo "${YELLOW}Stopping server...${NC}"
                pkill -f "node server.js" 2>/dev/null
                sleep 2
                
                echo "${YELLOW}Removing database...${NC}"
                rm -f "$DB_PATH"
                echo "${GREEN}✅ Database removed${NC}"
                
                echo ""
                echo "${YELLOW}Reinitializing database...${NC}"
                cd backend && npm run init-db
                
                echo ""
                echo "${GREEN}═══════════════════════════════════════════════════════════${NC}"
                echo "${GREEN}              ✅ DATABASE RESET COMPLETE                    ${NC}"
                echo "${GREEN}═══════════════════════════════════════════════════════════${NC}"
            fi
        fi
        ;;
    6)
        echo "${GREEN}Goodbye!${NC}"
        exit 0
        ;;
    *)
        echo "Invalid choice."
        ;;
esac
