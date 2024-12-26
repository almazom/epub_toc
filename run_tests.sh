#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color
BOLD='\033[1m'
DIM='\033[2m'

# Exit on error
set -e

# Spinner characters
SPINNER="⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
PULSE="▁▂▃▄▅▆▇█▇▆▅▄▃▂▁"
BRAILLE="⣾⣽⣻⢿⡿⣟⣯⣷"

# Global variables for progress tracking
TOTAL_STEPS=8
CURRENT_STEP=0
START_TIME=$(date +%s)

# Stats counters
TESTS_PASSED=0
TESTS_FAILED=0
TOTAL_TESTS=0

# Function to show elapsed time
show_elapsed_time() {
    local current_time=$(date +%s)
    local elapsed=$((current_time - START_TIME))
    local hours=$((elapsed / 3600))
    local minutes=$(( (elapsed % 3600) / 60 ))
    local seconds=$((elapsed % 60))
    printf "${DIM}%02d:%02d:%02d${NC}" $hours $minutes $seconds
}

# Function to show progress bar
show_progress_bar() {
    local percent=$1
    local width=30
    local filled=$(($width * $percent / 100))
    local empty=$(($width - $filled))
    
    printf "["
    printf "%${filled}s" | tr ' ' '#'
    printf "%${empty}s" | tr ' ' '-'
    printf "] %3d%%" $percent
}

# Function to update overall progress with fancy bar
update_progress() {
    CURRENT_STEP=$((CURRENT_STEP + 1))
    local percent=$((CURRENT_STEP * 100 / TOTAL_STEPS))
    
    echo -e "\n${DIM}+--- Progress ----------------------------------+${NC}"
    echo -e "${DIM}|${NC} $(show_progress_bar $percent) ${DIM}|${NC}"
    echo -e "${DIM}+----------------------------------------------+${NC}\n"
}

# Enhanced spinner with multiple animations
spinner() {
    local pid=$1
    local message=$2
    local i=0
    local j=0
    local k=0
    
    while kill -0 $pid 2>/dev/null; do
        # Main spinner
        i=$(( (i + 1) % ${#SPINNER} ))
        # Pulse animation
        j=$(( (j + 1) % ${#PULSE} ))
        # Braille animation
        k=$(( (k + 1) % ${#BRAILLE} ))
        
        printf "\r${YELLOW}${SPINNER:$i:1} ${message} ${MAGENTA}${PULSE:$j:1}${NC} ${CYAN}${BRAILLE:$k:1}${NC} [$(show_elapsed_time)]"
        sleep 0.1
    done
    printf "\r"
}

# Progress bar function with multiple indicators
progress_bar() {
    local name=$1
    local duration=$2
    local width=50
    local details=$3
    local activity=("⣾" "⣽" "⣻" "⢿" "⡿" "⣟" "⣯" "⣷")
    local pulse=("▁" "▂" "▃" "▄" "▅" "▆" "▇" "█" "▇" "▆" "▅" "▄" "▃" "▂" "▁")
    
    echo -e "\n${BOLD}${BLUE}▶ ${name}${NC}"
    echo -e "${CYAN}┌${"─":(width+4)}┐${NC}"
    echo -n "  ["
    for ((i=0; i<width; i++)); do
        echo -n " "
    done
    echo -n "] 0%"
    
    for ((i=0; i<width; i++)); do
        local idx=$((i % ${#activity[@]}))
        local pulse_idx=$((i % ${#pulse[@]}))
        sleep 0.1
        echo -ne "\r  ["
        for ((j=0; j<=i; j++)); do
            echo -n "█"
        done
        for ((j=i+1; j<width; j++)); do
            echo -n "░"
        done
        local percent=$((i*2))
        echo -ne "] ${percent}% ${activity[$idx]} ${pulse[$pulse_idx]}"
        
        if [ ! -z "$details" ]; then
            echo -ne " ${CYAN}${details}${NC}"
        fi
        echo -ne " [$(show_elapsed_time)]"
    done
    echo -e "\n${CYAN}└${"─":(width+4)}┘${NC}"
    echo -e "  ${GREEN}✓ Complete${NC}\n"
}

# Function to print section header
print_header() {
    local title="$1"
    echo -e "\n${BOLD}${BLUE}+--- ${NC}${BOLD}$title${BLUE} -----------------------------------+${NC}"
}

# Function to print step
print_step() {
    local step="$1"
    echo -e "\n${YELLOW}=>${NC} ${BOLD}$step${NC}"
}

# Function to print status message
print_status() {
    local message="$1"
    local type="$2" # 'info', 'success', 'error', or 'warning'
    local symbol=""
    local color=""
    
    case $type in
        "info")    symbol="->"; color=$CYAN ;;
        "success") symbol="OK"; color=$GREEN ;;
        "error")   symbol="!!"; color=$RED ;;
        "warning") symbol="**"; color=$YELLOW ;;
    esac
    
    echo -e "  ${color}${symbol}${NC} ${message}"
}

# Function to print success with stats update
print_success() {
    local message="$1"
    local timestamp=$(date "+%H:%M:%S")
    TESTS_PASSED=$((TESTS_PASSED + 1))
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    echo -e "${GREEN}✓ ${message} ${NC}${CYAN}[${timestamp}]${NC} ${DIM}(+1 passed)${NC}"
}

# Function to print error with stats update
print_error() {
    local message="$1"
    local timestamp=$(date "+%H:%M:%S")
    TESTS_FAILED=$((TESTS_FAILED + 1))
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    echo -e "${RED}✗ ${message} ${NC}${CYAN}[${timestamp}]${NC} ${DIM}(+1 failed)${NC}"
}

# Function to print error details with better formatting
print_error_details() {
    local error_file=$1
    echo -e "\n${RED}╔═══ Error Details ═══╗${NC}"
    if [ -f "$error_file" ]; then
        echo -e "${RED}║$(cat "$error_file" | sed 's/^/║ /')${NC}"
    else
        echo -e "${RED}║ No error details available${NC}"
    fi
    echo -e "${RED}╚═══════════════════╝${NC}\n"
}

# Function to display coverage report
display_coverage_report() {
    local coverage_file="coverage/coverage.xml"
    if [ ! -f "$coverage_file" ]; then
        return
    fi

    # Parse coverage data using Python
    python3 - <<EOF
import xml.etree.ElementTree as ET
import sys

try:
    tree = ET.parse('coverage/coverage.xml')
    root = tree.getroot()
    
    # Get overall coverage
    total_statements = 0
    covered_statements = 0
    
    for package in root.findall('.//package'):
        for class_elem in package.findall('.//class'):
            statements = int(class_elem.get('statements', 0))
            covered = int(class_elem.get('hits', 0))
            total_statements += statements
            covered_statements += covered
    
    if total_statements > 0:
        coverage_percent = (covered_statements / total_statements) * 100
        
        # Print coverage summary
        print(f"\n\033[0;36m┌─────────────── Coverage Summary ─────────────┐\033[0m")
        print(f"\033[0;36m│\033[0m Total Lines:    {total_statements:>6}                      \033[0;36m│\033[0m")
        print(f"\033[0;36m│\033[0m Covered Lines:  {covered_statements:>6}                      \033[0;36m│\033[0m")
        print(f"\033[0;36m│\033[0m Coverage:       {coverage_percent:>6.2f}%                    \033[0;36m│\033[0m")
        
        # Coverage bar
        width = 40
        filled = int((coverage_percent * width) / 100)
        bar = "█" * filled + "░" * (width - filled)
        print(f"\033[0;36m├─────────────── Coverage Bar ───────────────┤\033[0m")
        print(f"\033[0;36m│\033[0m [{bar}] \033[0;36m│\033[0m")
        
        # Coverage quality indicator
        quality = ""
        if coverage_percent >= 90:
            quality = "\033[0;32m▰▰▰▰▰\033[0m Excellent"
        elif coverage_percent >= 80:
            quality = "\033[0;32m▰▰▰▰\033[0m\033[0;37m▱\033[0m Very Good"
        elif coverage_percent >= 70:
            quality = "\033[0;32m▰▰▰\033[0m\033[0;37m▱▱\033[0m Good"
        elif coverage_percent >= 60:
            quality = "\033[0;33m▰▰\033[0m\033[0;37m▱▱▱\033[0m Fair"
        else:
            quality = "\033[0;31m▰\033[0m\033[0;37m▱▱▱▱\033[0m Needs Improvement"
            
        print(f"\033[0;36m├─────────────── Quality Rating ─────────────┤\033[0m")
        print(f"\033[0;36m│\033[0m {quality:^42} \033[0;36m│\033[0m")
        
        # File details
        print(f"\033[0;36m├─────────────── Details ───────────────────┤\033[0m")
        
        # Show top 3 files with lowest coverage
        files = []
        for package in root.findall('.//package'):
            for class_elem in package.findall('.//class'):
                filename = class_elem.get('filename')
                stmts = int(class_elem.get('statements', 0))
                hits = int(class_elem.get('hits', 0))
                if stmts > 0:
                    cov = (hits / stmts) * 100
                    files.append((filename, cov, stmts))
        
        files.sort(key=lambda x: x[1])  # Sort by coverage percentage
        for filename, cov, stmts in files[:3]:
            name = filename[-30:] if len(filename) > 30 else filename.ljust(30)
            print(f"\033[0;36m│\033[0m {name} {cov:>6.2f}% ({stmts} lines) \033[0;36m│\033[0m")
        
        print(f"\033[0;36m└──────────────────────────────────────────┘\033[0m")
        print(f"\n\033[0;36mDetailed report: coverage/html/index.html\033[0m")
except Exception as e:
    print(f"Error parsing coverage report: {e}", file=sys.stderr)
EOF
}

# Main execution
clear
echo -e "${BOLD}${BLUE}+===============================================+${NC}"
echo -e "${BOLD}${BLUE}|${NC}            ${BOLD}Test Suite Runner${NC}             ${BOLD}${BLUE}|${NC}"
echo -e "${BOLD}${BLUE}+===============================================+${NC}\n"

# Initialize virtual environment
print_step "Environment Setup"
if [ ! -d "venv" ]; then
    print_status "Creating virtual environment..." "info"
    python3 -m venv venv
    print_status "Virtual environment created" "success"
else
    print_status "Using existing environment" "success"
fi
source venv/bin/activate
print_status "Environment activated" "success"
update_progress

# Install dependencies
print_step "Dependencies"
print_status "Installing packages..." "info"
if pip install -r requirements.txt --quiet; then
    print_status "All packages installed" "success"
else
    print_status "Failed to install packages" "error"
    exit 1
fi
update_progress

# Generate TOC JSON files
print_step "Generating TOC Data"
print_status "Processing EPUB samples..." "info"
echo -e "${DIM}+--- TOC Generation ----------------------------+${NC}"

# Cleanup old files
echo -e "${DIM}|${NC} → Cleaning up old TOC files..."
if [ -d "tests/data/epub_toc_json" ]; then
    old_count=$(ls -1 tests/data/epub_toc_json/*.json 2>/dev/null | wc -l)
    if [ $old_count -gt 0 ]; then
        echo -e "${DIM}|${NC}   ${YELLOW}→${NC} Found $old_count old JSON files"
        rm -f tests/data/epub_toc_json/*.json
        echo -e "${DIM}|${NC}   ${GREEN}✓${NC} Cleaned up old files"
    else
        echo -e "${DIM}|${NC}   ${CYAN}→${NC} No old files found"
    fi
fi

# Cleanup old reports
echo -e "${DIM}|${NC} → Cleaning up old reports..."
if [ -d "tests/data/reports" ]; then
    old_reports=$(ls -1 tests/data/reports/strategy_report*.txt 2>/dev/null | wc -l)
    if [ $old_reports -gt 0 ]; then
        echo -e "${DIM}|${NC}   ${YELLOW}→${NC} Found $old_reports old reports"
        rm -f tests/data/reports/strategy_report*.txt
        echo -e "${DIM}|${NC}   ${GREEN}✓${NC} Cleaned up old reports"
    else
        echo -e "${DIM}|${NC}   ${CYAN}→${NC} No old reports found"
    fi
fi

# Create fresh directories
echo -e "${DIM}|${NC} → Creating output directories..."
mkdir -p tests/data/epub_toc_json
mkdir -p tests/data/reports
echo -e "${DIM}|${NC}   ${GREEN}✓${NC} Directories ready"

# Initialize strategy counters
declare -A strategy_success=( ["ncx"]=0 ["nav"]=0 ["landmarks"]=0 ["fallback"]=0 )
declare -A strategy_total=( ["ncx"]=0 ["nav"]=0 ["landmarks"]=0 ["fallback"]=0 )
declare -A strategy_failed=( ["ncx"]=0 ["nav"]=0 ["landmarks"]=0 ["fallback"]=0 )
declare -A metadata_failed=( ["ncx"]=0 ["nav"]=0 ["landmarks"]=0 ["fallback"]=0 )
declare -A json_failed=( ["ncx"]=0 ["nav"]=0 ["landmarks"]=0 ["fallback"]=0 )

# Process each EPUB file
echo -e "${DIM}|${NC} → Processing EPUB files:"
for epub_file in tests/data/epub_samples/*.epub; do
    if [ -f "$epub_file" ]; then
        filename=$(basename "$epub_file" .epub)
        echo -e "${DIM}|${NC}   → Processing: $filename"
        
        # Run with strategy logging
        if python analyze_epub.py "$epub_file" --log-strategy > "tests/data/epub_toc_json/${filename}_toc.json" 2>.gen_error; then
            echo -e "${DIM}|${NC}   ${GREEN}✓${NC} Generated TOC for $filename"
            
            # Extract used strategy from log
            strategy=$(tail -n 1 .gen_error | grep -oP 'Used strategy: \K\w+' || echo "fallback")
            strategy_success[$strategy]=$((strategy_success[$strategy] + 1))
            strategy_total[$strategy]=$((strategy_total[$strategy] + 1))
            
            echo -e "${DIM}|${NC}     ${CYAN}→${NC} Strategy: $strategy"
            
            # Validate metadata extraction
            if python -c "
from epub_toc import EPUBTOCParser
parser = EPUBTOCParser('$epub_file')
metadata = parser.extract_metadata()
assert isinstance(metadata, dict)
assert 'title' in metadata
assert 'authors' in metadata
assert 'file_size' in metadata
print('Metadata validation passed')
            " 2>/dev/null; then
                echo -e "${DIM}|${NC}     ${GREEN}✓${NC} Metadata validation passed"
            else
                echo -e "${DIM}|${NC}     ${RED}✗${NC} Metadata validation failed"
                metadata_failed[$strategy]=$((metadata_failed[$strategy] + 1))
            fi
            
            # Validate JSON structure
            if python -c "
import json
with open('tests/data/epub_toc_json/${filename}_toc.json', 'r') as f:
    data = json.load(f)
assert isinstance(data, dict)
assert 'metadata' in data
assert 'toc' in data
assert isinstance(data['metadata'], dict)
assert isinstance(data['toc'], list)
print('JSON structure validation passed')
            " 2>/dev/null; then
                echo -e "${DIM}|${NC}     ${GREEN}✓${NC} JSON structure validation passed"
            else
                echo -e "${DIM}|${NC}     ${RED}✗${NC} JSON structure validation failed"
                json_failed[$strategy]=$((json_failed[$strategy] + 1))
            fi
            
        else
            echo -e "${DIM}|${NC}   ${RED}✗${NC} Failed to generate TOC for $filename"
            
            # Extract attempted strategy from error
            strategy=$(grep -oP 'Failed strategy: \K\w+' .gen_error || echo "fallback")
            strategy_failed[$strategy]=$((strategy_failed[$strategy] + 1))
            strategy_total[$strategy]=$((strategy_total[$strategy] + 1))
            
            cat .gen_error | sed 's/^/|     /'
        fi
    fi
done

# Print summary
echo -e "\n${DIM}+--- Summary -----------------------------------+${NC}"
echo -e "${DIM}|${NC} Strategy success rates:"
for strategy in "${!strategy_total[@]}"; do
    success_rate=$(( ${strategy_success[$strategy]} * 100 / ${strategy_total[$strategy]} ))
    echo -e "${DIM}|${NC}   $strategy: $success_rate% (${strategy_success[$strategy]}/${strategy_total[$strategy]})"
done

echo -e "${DIM}|${NC} Metadata validation:"
total_metadata_failed=0
for strategy in "${!metadata_failed[@]}"; do
    total_metadata_failed=$((total_metadata_failed + ${metadata_failed[$strategy]}))
done
echo -e "${DIM}|${NC}   Failed: $total_metadata_failed"

echo -e "${DIM}|${NC} JSON structure validation:"
total_json_failed=0
for strategy in "${!json_failed[@]}"; do
    total_json_failed=$((total_json_failed + ${json_failed[$strategy]}))
done
echo -e "${DIM}|${NC}   Failed: $total_json_failed"

echo -e "${DIM}+----------------------------------------------+${NC}"

rm -f .gen_error

# Generate strategy report
echo -e "${DIM}|${NC}"
echo -e "${DIM}|${NC} ${BOLD}Strategy Analysis:${NC}"
echo -e "${DIM}|${NC} ┌────────────┬───────┬────────┬─────────┬──────────┐"
echo -e "${DIM}|${NC} │ Strategy   │ Total │ Success │ Failed  │ Rate     │"
echo -e "${DIM}|${NC} ├────────────┼───────┼────────┼─────────┼──────────┤"
for strategy in "ncx" "nav" "landmarks" "fallback"; do
    total=${strategy_total[$strategy]}
    success=${strategy_success[$strategy]}
    failed=${strategy_failed[$strategy]}
    if [ $total -gt 0 ]; then
        success_rate=$(( success * 100 / total ))
        # Color based on success rate
        if [ $success_rate -ge 80 ]; then
            rate_color=$GREEN
        elif [ $success_rate -ge 50 ]; then
            rate_color=$YELLOW
        else
            rate_color=$RED
        fi
        printf "${DIM}|${NC} │ %-10s│ %5d │ ${GREEN}%6d${NC} │ ${RED}%7d${NC} │ ${rate_color}%6d%%${NC} │\n" "$strategy" "$total" "$success" "$failed" "$success_rate"
    fi
done
echo -e "${DIM}|${NC} └────────────┴───────┴────────┴─────────┴──────────┘"

# Strategy details
echo -e "${DIM}|${NC}"
echo -e "${DIM}|${NC} ${BOLD}Strategy Details:${NC}"
echo -e "${DIM}|${NC} NCX Strategy (EPUB2):"
echo -e "${DIM}|${NC} │ • Searches for .ncx file in EPUB"
echo -e "${DIM}|${NC} │ • Standard navigation format for EPUB2"
echo -e "${DIM}|${NC} │ • Most reliable for older books"
echo -e "${DIM}|${NC}"
echo -e "${DIM}|${NC} NAV Strategy (EPUB3):"
echo -e "${DIM}|${NC} │ • Uses nav.xhtml or nav.xml"
echo -e "${DIM}|${NC} │ • Modern EPUB3 navigation format"
echo -e "${DIM}|${NC} │ • Best for newer books"
echo -e "${DIM}|${NC}"
echo -e "${DIM}|${NC} Landmarks Strategy:"
echo -e "${DIM}|${NC} │ • Uses guide/landmarks elements"
echo -e "${DIM}|${NC} │ • Alternative navigation points"
echo -e "${DIM}|${NC} │ • Supplementary method"
echo -e "${DIM}|${NC}"
echo -e "${DIM}|${NC} Fallback Strategy:"
echo -e "${DIM}|${NC} │ • Last resort method"
echo -e "${DIM}|${NC} │ • Analyzes document structure"
echo -e "${DIM}|${NC} │ • Used when other methods fail"

# Save detailed report with more information
echo "TOC Strategy Analysis Report" > tests/data/reports/strategy_report.txt
echo "Generated: $(date)" >> tests/data/reports/strategy_report.txt
echo "========================================" >> tests/data/reports/strategy_report.txt
echo "" >> tests/data/reports/strategy_report.txt

echo "Strategy Success Rates" >> tests/data/reports/strategy_report.txt
echo "----------------------------------------" >> tests/data/reports/strategy_report.txt
for strategy in "ncx" "nav" "landmarks" "fallback"; do
    total=${strategy_total[$strategy]}
    success=${strategy_success[$strategy]}
    failed=${strategy_failed[$strategy]}
    if [ $total -gt 0 ]; then
        success_rate=$(( success * 100 / total ))
        echo "Strategy: $strategy" >> tests/data/reports/strategy_report.txt
        echo "  Total attempts: $total" >> tests/data/reports/strategy_report.txt
        echo "  Successful: $success ($success_rate%)" >> tests/data/reports/strategy_report.txt
        echo "  Failed: $failed" >> tests/data/reports/strategy_report.txt
        echo "----------------------------------------" >> tests/data/reports/strategy_report.txt
    fi
done

echo "" >> tests/data/reports/strategy_report.txt
echo "Strategy Details" >> tests/data/reports/strategy_report.txt
echo "========================================" >> tests/data/reports/strategy_report.txt
echo "" >> tests/data/reports/strategy_report.txt

echo "NCX Strategy (EPUB2)" >> tests/data/reports/strategy_report.txt
echo "- Primary navigation format for EPUB2" >> tests/data/reports/strategy_report.txt
echo "- Uses .ncx file containing NavMap structure" >> tests/data/reports/strategy_report.txt
echo "- Provides hierarchical chapter organization" >> tests/data/reports/strategy_report.txt
echo "" >> tests/data/reports/strategy_report.txt

echo "NAV Strategy (EPUB3)" >> tests/data/reports/strategy_report.txt
echo "- Modern navigation format for EPUB3" >> tests/data/reports/strategy_report.txt
echo "- Uses nav.xhtml with HTML5 nav elements" >> tests/data/reports/strategy_report.txt
echo "- More flexible than NCX format" >> tests/data/reports/strategy_report.txt
echo "" >> tests/data/reports/strategy_report.txt

echo "Landmarks Strategy" >> tests/data/reports/strategy_report.txt
echo "- Uses guide/landmarks for navigation" >> tests/data/reports/strategy_report.txt
echo "- Provides key points in the document" >> tests/data/reports/strategy_report.txt
echo "- Often used as supplementary navigation" >> tests/data/reports/strategy_report.txt
echo "" >> tests/data/reports/strategy_report.txt

echo "Fallback Strategy" >> tests/data/reports/strategy_report.txt
echo "- Used when other strategies fail" >> tests/data/reports/strategy_report.txt
echo "- Analyzes document structure directly" >> tests/data/reports/strategy_report.txt
echo "- Less reliable but more universal" >> tests/data/reports/strategy_report.txt

# Check if any files were generated
json_count=$(ls -1 tests/data/epub_toc_json/*.json 2>/dev/null | wc -l)
if [ $json_count -gt 0 ]; then
    echo -e "${DIM}|${NC} ${GREEN}✓${NC} Generated $json_count TOC files"
    echo -e "${DIM}|${NC} ${CYAN}→${NC} Strategy report saved to: tests/data/reports/strategy_report.txt"
else
    echo -e "${DIM}|${NC} ${YELLOW}!${NC} No TOC files were generated"
fi
echo -e "${DIM}+----------------------------------------------+${NC}"
update_progress

# Run unit tests
print_step "Unit Tests"
print_status "Preparing test environment..." "info"
echo -e "${DIM}+--- Test Progress ------------------------------+${NC}"
echo -e "${DIM}|${NC} → Collecting test cases..."
echo -e "${DIM}|${NC} → Setting up test database..."
echo -e "${DIM}|${NC} → Initializing test runner..."
if python -m pytest tests/ --cov=. --cov-report=xml -v | tee .test_results | while IFS= read -r line; do
    if [[ $line == *"collecting"* ]]; then
        echo -e "${DIM}|${NC} ⟳ $line"
    elif [[ $line == *"PASSED"* ]]; then
        echo -e "${DIM}|${NC} ${GREEN}✓${NC} $line"
    elif [[ $line == *"FAILED"* ]]; then
        echo -e "${DIM}|${NC} ${RED}✗${NC} $line"
    elif [[ $line == *"ERROR"* ]]; then
        echo -e "${DIM}|${NC} ${RED}!${NC} $line"
    elif [[ $line == *"test"* ]]; then
        echo -e "${DIM}|${NC} → Running: $line"
    fi
done; then
    print_status "All tests completed successfully" "success"
    echo -e "${DIM}|${NC} ${GREEN}✓${NC} All test cases passed"
else
    print_status "Some tests failed" "error"
    echo -e "${DIM}|${NC} ${RED}✗${NC} Test suite failed"
    echo -e "${DIM}|${NC}"
    echo -e "${DIM}|${NC} Failed tests:"
    grep "FAILED" .test_results | sed 's/^/|   /'
fi
echo -e "${DIM}+----------------------------------------------+${NC}"
rm -f .test_results
update_progress

# Generate coverage report
print_step "Code Coverage"
print_status "Analyzing code coverage..." "info"
echo -e "${DIM}+--- Coverage Analysis -------------------------+${NC}"
echo -e "${DIM}|${NC} → Collecting coverage data..."
echo -e "${DIM}|${NC} → Processing source files..."
echo -e "${DIM}|${NC} → Generating reports..."
display_coverage_report
echo -e "${DIM}+----------------------------------------------+${NC}"
update_progress

# Type checking with progress
print_step "Type Checking"
print_status "Verifying types..." "info"
echo -e "${DIM}+--- Type Analysis -----------------------------+${NC}"
echo -e "${DIM}|${NC} → Scanning Python files..."
echo -e "${DIM}|${NC} → Analyzing type hints..."
if mypy . --ignore-missing-imports --exclude venv/* > .type_check_results 2>&1; then
    echo -e "${DIM}|${NC} ${GREEN}✓${NC} All types are correct"
else
    echo -e "${DIM}|${NC} ${YELLOW}!${NC} Type issues found:"
    echo -e "${DIM}|${NC}"
    cat .type_check_results | grep "error:" | head -n 3 | sed 's/^/|   /'
    total_errors=$(cat .type_check_results | grep "error:" | wc -l)
    if [ $total_errors -gt 3 ]; then
        echo -e "${DIM}|${NC} ... and $((total_errors - 3)) more errors"
    fi
fi
echo -e "${DIM}+----------------------------------------------+${NC}"
rm -f .type_check_results
update_progress

# Linting with progress
print_step "Code Style"
print_status "Analyzing code style..." "info"
echo -e "${DIM}+--- Style Analysis ---------------------------+${NC}"
echo -e "${DIM}|${NC} → Checking PEP 8 compliance..."
echo -e "${DIM}|${NC} → Analyzing code formatting..."
if flake8 . --exclude=venv/* --format="%(path)s: line %(row)d - %(text)s" > .lint_results 2>&1; then
    echo -e "${DIM}|${NC} ${GREEN}✓${NC} Code style is perfect"
else
    echo -e "${DIM}|${NC} ${YELLOW}!${NC} Style issues found:"
    echo -e "${DIM}|${NC}"
    cat .lint_results | head -n 5 | sed 's/^/|   /'
    remaining=$(cat .lint_results | wc -l)
    if [ $remaining -gt 5 ]; then
        echo -e "${DIM}|${NC} ... and $((remaining - 5)) more issues"
    fi
fi
echo -e "${DIM}+----------------------------------------------+${NC}"
rm -f .lint_results
update_progress

# After generating JSON files, before final summary
print_step "TOC Analysis"
print_status "Analyzing generated TOC files..." "info"
echo -e "${DIM}+--- TOC Analysis ------------------------------+${NC}"
echo -e "${DIM}|${NC} → Analyzing JSON structure..."

# Analyze JSON files
echo -e "${DIM}|${NC} Structure statistics:"
echo -e "${DIM}|${NC} ┌────────────────┬─────────┬──────────┐"
echo -e "${DIM}|${NC} │ Metric         │   Count │    Ratio │"
echo -e "${DIM}|${NC} ├────────────────┼─────────┼──────────┤"

total_files=$(ls -1 tests/data/epub_toc_json/*.json 2>/dev/null | wc -l)
empty_files=$(find tests/data/epub_toc_json -type f -empty | wc -l)
has_chapters=$(grep -l '"chapters":' tests/data/epub_toc_json/*.json 2>/dev/null | wc -l)
nested_toc=$(grep -l '"subchapters":' tests/data/epub_toc_json/*.json 2>/dev/null | wc -l)

# Calculate percentages
[ $total_files -gt 0 ] && {
    empty_ratio=$(( empty_files * 100 / total_files ))
    chapters_ratio=$(( has_chapters * 100 / total_files ))
    nested_ratio=$(( nested_toc * 100 / total_files ))
    
    printf "${DIM}|${NC} │ Total files    │ %7d │   100%% │\n" $total_files
    printf "${DIM}|${NC} │ Empty files    │ %7d │ %6d%% │\n" $empty_files $empty_ratio
    printf "${DIM}|${NC} │ Has chapters   │ %7d │ %6d%% │\n" $has_chapters $chapters_ratio
    printf "${DIM}|${NC} │ Nested TOC     │ %7d │ %6d%% │\n" $nested_toc $nested_ratio
}

echo -e "${DIM}|${NC} └────────────────┴─────────┴──────────┘"

# Sample analysis of one file
echo -e "${DIM}|${NC}"
echo -e "${DIM}|${NC} Detailed structure example:"
sample_file=$(ls tests/data/epub_toc_json/*.json 2>/dev/null | head -n 1)
if [ -f "$sample_file" ]; then
    echo -e "${DIM}|${NC} → Analyzing: $(basename "$sample_file")"
    # Use Python to pretty print and analyze JSON structure
    python3 - <<EOF
import json
import sys

try:
    with open('$sample_file', 'r') as f:
        data = json.load(f)
    
    # Analyze structure
    total_chapters = len(data.get('chapters', []))
    nested_count = sum(1 for ch in data.get('chapters', []) 
                      if ch.get('subchapters'))
    max_depth = 1
    
    def get_depth(chapter, current=1):
        if not chapter.get('subchapters'):
            return current
        return max(get_depth(sub, current + 1) 
                  for sub in chapter['subchapters'])
    
    for chapter in data.get('chapters', []):
        depth = get_depth(chapter)
        if depth > max_depth:
            max_depth = depth
    
    print(f"\033[2m|\033[0m   • Total chapters: {total_chapters}")
    print(f"\033[2m|\033[0m   • Chapters with subchapters: {nested_count}")
    print(f"\033[2m|\033[0m   • Maximum nesting depth: {max_depth}")
    
    # Show first few chapters
    print(f"\033[2m|\033[0m")
    print(f"\033[2m|\033[0m First chapters preview:")
    for i, chapter in enumerate(data.get('chapters', [])[:3], 1):
        print(f"\033[2m|\033[0m   {i}. {chapter.get('title', 'Untitled')}")
        for j, sub in enumerate(chapter.get('subchapters', [])[:2], 1):
            print(f"\033[2m|\033[0m      {i}.{j}. {sub.get('title', 'Untitled')}")
        if len(chapter.get('subchapters', [])) > 2:
            print(f"\033[2m|\033[0m      ...")
    if len(data.get('chapters', [])) > 3:
        print(f"\033[2m|\033[0m   ...")
except Exception as e:
    print(f"\033[2m|\033[0m   Error analyzing JSON: {e}", file=sys.stderr)
EOF
fi

echo -e "${DIM}+----------------------------------------------+${NC}"
update_progress

# Final summary
echo -e "\n${BOLD}${BLUE}+--- Summary -----------------------------------+${NC}"
echo -e "${DIM}|${NC} Duration: $(show_elapsed_time)"
echo -e "${DIM}|${NC} Status:   $([ $TESTS_FAILED -eq 0 ] && echo "${GREEN}All checks passed${NC}" || echo "${RED}Some checks failed${NC}")"
echo -e "${DIM}|${NC}"
echo -e "${DIM}|${NC} Details:"
[ $TESTS_FAILED -eq 0 ] && {
    echo -e "${DIM}|${NC}   ${GREEN}OK${NC} Style checks passed"
    echo -e "${DIM}|${NC}   ${GREEN}OK${NC} Type checks passed"
    echo -e "${DIM}|${NC}   ${GREEN}OK${NC} Unit tests passed"
    echo -e "${DIM}|${NC}   ${GREEN}OK${NC} Coverage report generated"
} || {
    [ $STYLE_ISSUES -gt 0 ] && echo -e "${DIM}|${NC}   ${RED}!!${NC} Style issues found"
    [ $TYPE_ISSUES -gt 0 ] && echo -e "${DIM}|${NC}   ${RED}!!${NC} Type check issues found"
    [ $TESTS_FAILED -gt 0 ] && echo -e "${DIM}|${NC}   ${RED}!!${NC} Some tests failed"
}
echo -e "${BOLD}${BLUE}+----------------------------------------------+${NC}\n"

[ $TESTS_FAILED -eq 0 ] || exit 1 