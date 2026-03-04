#!/bin/bash
# Run Script for Upstox API Automation
# Usage: ./run.sh [command]

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project directory
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

# Function to print colored output
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Header
echo "======================================================================"
echo "🚀 Upstox API Automation - Run Script"
echo "======================================================================"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    print_error "Virtual environment not found!"
    echo "Please run setup first:"
    echo "  python3 -m venv venv"
    echo "  source venv/bin/activate"
    echo "  pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
print_info "Activating virtual environment..."
source venv/bin/activate
print_success "Virtual environment activated"

# Parse command
case "${1:-quick}" in
    quick)
        print_info "Running quick test..."
        python3 -c "
from src.api_clients.upstox_auth_client import complete_login_flow
print('Testing complete login flow...')
result = complete_login_flow('9870165199', '123789')
print(f'✅ Token: {result[\"token\"][:50]}...')
print(f'✅ Profile ID: {result[\"profile_id\"]}')
print('✅ Test passed!')
"
        ;;
    
    realistic)
        print_info "Running realistic test suite..."
        python3 run_realistic_test.py
        ;;
    
    interactive)
        print_info "Starting interactive mode..."
        python3 real_time_test.py
        ;;
    
    sequential)
        print_info "Starting sequential interactive flow..."
        python3 interactive_sequential_flow.py
        ;;
    
    simple)
        print_info "Starting simple login flow..."
        python3 simple_login_flow.py
        ;;
    
    tests)
        print_info "Running pytest test suite..."
        pytest tests/functional/test_upstox_verify_otp.py -v
        ;;
    
    all-tests)
        print_info "Running all tests..."
        pytest tests/ -v --tb=short
        ;;
    
    demo)
        print_info "Running demo script..."
        python3 demo_upstox_otp.py
        ;;
    
    example)
        print_info "Running complete flow example..."
        python3 examples/complete_login_flow_example.py
        ;;
    
    mock)
        print_info "Running mock test (no API calls)..."
        python3 test_with_mock.py
        ;;
    
    clean)
        print_info "Cleaning up..."
        rm -rf logs/*.log
        rm -rf reports/*.html
        rm -rf __pycache__
        find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
        find . -type f -name "*.pyc" -delete 2>/dev/null || true
        print_success "Cleanup complete"
        ;;
    
    help|--help|-h)
        echo "Usage: ./run.sh [command]"
        echo ""
        echo "Commands:"
        echo "  quick       - Run quick one-liner test (default)"
        echo "  realistic   - Run realistic test suite (4 scenarios)"
        echo "  sequential  - Sequential step-by-step flow (asks for mobile)"
        echo "  simple      - Simple login flow (minimal prompts)"
        echo "  interactive - Start interactive menu"
        echo "  tests       - Run pytest test suite"
        echo "  all-tests   - Run all tests with coverage"
        echo "  demo        - Run demo script"
        echo "  example     - Run complete flow example"
        echo "  mock        - Run mock test (no API calls)"
        echo "  clean       - Clean up log files and cache"
        echo "  help        - Show this help message"
        echo ""
        echo "Examples:"
        echo "  ./run.sh                    # Quick test"
        echo "  ./run.sh realistic          # Full test suite"
        echo "  ./run.sh sequential         # Sequential interactive flow"
        echo "  ./run.sh simple             # Simple flow with prompts"
        echo "  ./run.sh interactive        # Interactive mode"
        echo "  ./run.sh tests              # Run pytest"
        ;;
    
    *)
        print_error "Unknown command: $1"
        echo "Run './run.sh help' for usage information"
        exit 1
        ;;
esac

echo ""
echo "======================================================================"
print_success "Done!"
echo "======================================================================"
