#!/bin/bash

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# JSON directory setup
JSON_DIR="tests/data/epub_toc_json"

# Strategy counters
declare -A strategy_success=( ["ncx"]=0 ["nav"]=0 ["landmarks"]=0 ["fallback"]=0 )
declare -A strategy_total=( ["ncx"]=0 ["nav"]=0 ["landmarks"]=0 ["fallback"]=0 )
declare -A strategy_time=( ["ncx"]=0 ["nav"]=0 ["landmarks"]=0 ["fallback"]=0 )

START_TIME=$(date +%s)

echo -e "\n${BLUE}Test Suite Setup${NC}"

# Create JSON directory if it doesn't exist
echo -e "Creating JSON directory..."
mkdir -p "$JSON_DIR"
echo -e "${GREEN}✓${NC} Created: $JSON_DIR"

# Clean up existing JSON files
echo -e "\nCleaning up old JSON files..."
rm -f "$JSON_DIR"/*.json
echo -e "${GREEN}✓${NC} Cleaned up JSON directory"

# Wait 5 seconds
echo -e "\nWaiting 5 seconds for filesystem sync..."
sleep 5

# Verify cleanup
echo -e "\nVerifying cleanup..."
if [ -z "$(ls -A $JSON_DIR)" ]; then
    echo -e "${GREEN}✓${NC} JSON directory is empty"
else
    echo -e "${RED}✗${NC} Failed to clean JSON directory"
    exit 1
fi

echo -e "\n${BLUE}Starting Tests${NC}\n"

# Run pytest and process output in real-time
python -m pytest -v --cov=epub_toc | while read -r line; do
    # Track strategy usage
    if [[ $line == *"Using strategy"* ]]; then
        strategy=$(echo "$line" | grep -o 'ncx\|nav\|landmarks\|fallback')
        if [ ! -z "$strategy" ]; then
            strategy_total[$strategy]=$((strategy_total[$strategy] + 1))
        fi
    fi
    
    # Track strategy success/failure
    if [[ $line == *"Strategy succeeded"* ]]; then
        strategy=$(echo "$line" | grep -o 'ncx\|nav\|landmarks\|fallback')
        if [ ! -z "$strategy" ]; then
            strategy_success[$strategy]=$((strategy_success[$strategy] + 1))
        fi
    fi
    
    # Output with status indicators
    if [[ $line == *"PASSED"* ]]; then
        echo -e "${GREEN}✓${NC} $line"
    elif [[ $line == *"FAILED"* ]]; then
        echo -e "${RED}✗${NC} $line"
    elif [[ $line == *"SKIPPED"* ]]; then
        echo -e "${YELLOW}○${NC} $line"
    elif [[ $line == *"collected"* ]]; then
        echo -e "\n$line\n"
    else
        echo "$line"
    fi
done

# Get exit status
TEST_STATUS=${PIPESTATUS[0]}

# Calculate total time
END_TIME=$(date +%s)
TOTAL_TIME=$((END_TIME - START_TIME))

# Show coverage if available
if [ -f "coverage.xml" ]; then
    COVERAGE=$(grep "TOTAL" coverage.xml | grep -o '[0-9]*\.[0-9]*' | head -1)
    if [ ! -z "$COVERAGE" ]; then
        echo -e "\nCoverage: ${COVERAGE}%"
    fi
fi

# Display Dashboard
echo -e "\n${CYAN}┌────────────── Test Results Dashboard ───────────────┐${NC}"
echo -e "${CYAN}│${NC}"
echo -e "${CYAN}│${NC} ${BLUE}Strategy Analysis:${NC}"

# Display strategy statistics
for strategy in "${!strategy_total[@]}"; do
    total=${strategy_total[$strategy]}
    success=${strategy_success[$strategy]}
    if [ $total -gt 0 ]; then
        success_rate=$((success * 100 / total))
        echo -e "${CYAN}│${NC}   $strategy:"
        echo -e "${CYAN}│${NC}     Total: $total"
        echo -e "${CYAN}│${NC}     Success: $success"
        echo -e "${CYAN}│${NC}     Rate: ${success_rate}%"
        
        # Visual success rate bar
        bar="    ["
        for ((i=0; i<10; i++)); do
            if [ $i -lt $((success_rate / 10)) ]; then
                bar+="█"
            else
                bar+="░"
            fi
        done
        bar+="]"
        echo -e "${CYAN}│${NC}     $bar"
        echo -e "${CYAN}│${NC}"
    fi
done

# Display timing information
hours=$((TOTAL_TIME / 3600))
minutes=$(( (TOTAL_TIME % 3600) / 60 ))
seconds=$((TOTAL_TIME % 60))
echo -e "${CYAN}│${NC} ${BLUE}Timing:${NC}"
echo -e "${CYAN}│${NC}   Total time: ${hours}h ${minutes}m ${seconds}s"
echo -e "${CYAN}│${NC}"

# Display JSON files statistics
json_count=$(ls -1 "$JSON_DIR"/*.json 2>/dev/null | wc -l)
echo -e "${CYAN}│${NC} ${BLUE}Generated Files:${NC}"
echo -e "${CYAN}│${NC}   JSON files: $json_count"
echo -e "${CYAN}│${NC}"

echo -e "${CYAN}└──────────────────────────────────────────────────┘${NC}"

# Exit with test status
exit $TEST_STATUS 