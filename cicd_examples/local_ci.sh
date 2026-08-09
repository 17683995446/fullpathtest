#!/bin/bash
# FullPathTest CI Integration Script
# 用于本地CI/CD系统集成

set -e

echo "======================================"
echo "FullPathTest CI Integration"
echo "======================================"
echo ""

# Configuration
PROJECT_DIR="${PROJECT_DIR:-.}"
OUTPUT_DIR="${OUTPUT_DIR:-fullpathtest_output}"
TOOLS="${TOOLS:-flake8,mypy,bandit}"

# Create output directory
mkdir -p "$OUTPUT_DIR"

echo "Project: $PROJECT_DIR"
echo "Output: $OUTPUT_DIR"
echo "Tools: $TOOLS"
echo ""

# Install dependencies
echo "Installing dependencies..."
pip install --quiet -e .

# Run analysis
echo "Running FullPathTest analysis..."
fullpathtest \
    --project "$PROJECT_DIR" \
    --tools "$TOOLS" \
    --output "$OUTPUT_DIR/report.json" \
    --format html \
    --output "$OUTPUT_DIR/report.html"

# Check results
if [ $? -eq 0 ]; then
    echo ""
    echo "======================================"
    echo "✓ Analysis completed successfully!"
    echo "======================================"
    echo ""
    echo "Reports:"
    echo "  - JSON: $OUTPUT_DIR/report.json"
    echo "  - HTML: $OUTPUT_DIR/report.html"
    echo ""
    
    # Display summary
    if [ -f "$OUTPUT_DIR/report.json" ]; then
        echo "Summary:"
        cat "$OUTPUT_DIR/report.json" | python -m json.tool | head -20
    fi
else
    echo ""
    echo "======================================"
    echo "✗ Analysis failed!"
    echo "======================================"
    exit 1
fi
