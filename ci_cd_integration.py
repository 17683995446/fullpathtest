"""
GitHub Actions CI/CD Integration Example
GitHub Actions CI/CD 集成示例
"""

# GitHub Actions Workflow File
GITHUB_ACTIONS_WORKFLOW = """
name: FullPathTest Code Quality

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]
  schedule:
    - cron: '0 2 * * *'  # 每天凌晨2点运行

jobs:
  fullpathtest-analysis:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install flake8 mypy pylint bandit
        pip install -e .
    
    - name: Run FullPathTest Analysis
      run: |
        fullpathtest --project . --tools flake8,mypy,bandit --output report.json
    
    - name: Upload analysis report
      if: always()
      uses: actions/upload-artifact@v3
      with:
        name: fullpathtest-report
        path: report.json
    
    - name: Post summary
      if: always()
      run: |
        echo "## FullPathTest Analysis Summary" >> $GITHUB_STEP_SUMMARY
        echo "" >> $GITHUB_STEP_SUMMARY
        if [ -f report.json ]; then
          echo "### Results:" >> $GITHUB_STEP_SUMMARY
          cat report.json | jq -r '.summary' >> $GITHUB_STEP_SUMMARY
        fi

  incremental-analysis:
    runs-on: ubuntu-latest
    if: github.event_name == 'push'
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v3
      with:
        fetch-depth: 0
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install FullPathTest
      run: |
        python -m pip install --upgrade pip
        pip install -e .
    
    - name: Run incremental analysis
      run: |
        fullpathtest --project . --incremental --only-changed
    
    - name: Comment on PR
      if: github.event_name == 'pull_request'
      uses: actions/github-script@v6
      with:
        script: |
          github.rest.issues.createComment({
            issue_number: context.issue.number,
            owner: context.repo.owner,
            repo: context.repo.repo,
            body: '## FullPathTest Incremental Analysis\\n\\nChanged files have been analyzed. Check the workflow logs for details.'
          })

  security-scan:
    runs-on: ubuntu-latest
    if: github.event_name == 'schedule'
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install bandit safety
    
    - name: Run security scan
      run: |
        bandit -r . -f json -o bandit_report.json
        safety check --json --output safety_report.json || true
    
    - name: Upload security reports
      uses: actions/upload-artifact@v3
      with:
        name: security-reports
        path: |
          bandit_report.json
          safety_report.json
        retention-days: 30

  nightly-full-analysis:
    runs-on: ubuntu-latest
    if: github.event_name == 'schedule'
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install FullPathTest
      run: |
        python -m pip install --upgrade pip
        pip install -e .
    
    - name: Run full analysis
      run: |
        fullpathtest --project . --full --output full_report.json
    
    - name: Generate HTML report
      run: |
        fullpathtest --project . --format html --output full_report.html
    
    - name: Upload full report
      uses: actions/upload-artifact@v3
      with:
        name: full-analysis-report
        path: |
          full_report.json
          full_report.html
        retention-days: 90
"""

# GitLab CI/CD Example
GITLAB_CI_YAML = """
stages:
  - test
  - quality
  - security

fullpathtest:
  stage: quality
  image: python:3.11-slim
  before_script:
    - pip install --no-cache-dir -e .
  script:
    - fullpathtest --project . --tools flake8,mypy --output report.json
  artifacts:
    reports:
      json: report.json
    expire_in: 1 week
  allow_failure: false

bandit-scan:
  stage: security
  image: python:3.11-slim
  before_script:
    - pip install bandit
  script:
    - bandit -r . -f json -o bandit_report.json
  artifacts:
    reports:
      json: bandit_report.json
    expire_in: 1 week

nightly-full-scan:
  stage: quality
  image: python:3.11-slim
  only:
    - schedules
  before_script:
    - pip install --no-cache-dir -e .
  script:
    - fullpathtest --project . --full --format html --output nightly_report.html
  artifacts:
    paths:
      - nightly_report.html
    expire_in: 30 days
"""

# Local CI Script Example
LOCAL_CI_SCRIPT = """#!/bin/bash
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
fullpathtest \\
    --project "$PROJECT_DIR" \\
    --tools "$TOOLS" \\
    --output "$OUTPUT_DIR/report.json" \\
    --format html \\
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
"""

import os

def create_cicd_examples(output_dir="cicd_examples"):
    """创建CI/CD集成示例"""
    os.makedirs(output_dir, exist_ok=True)
    
    # GitHub Actions
    with open(os.path.join(output_dir, "github-actions.yml"), "w") as f:
        f.write(GITHUB_ACTIONS_WORKFLOW)
    
    # GitLab CI
    with open(os.path.join(output_dir, "gitlab-ci.yml"), "w") as f:
        f.write(GITLAB_CI_YAML)
    
    # Local script
    with open(os.path.join(output_dir, "local_ci.sh"), "w") as f:
        f.write(LOCAL_CI_SCRIPT)
    
    print(f"✓ Created CI/CD examples in {output_dir}/")
    print(f"  - github-actions.yml")
    print(f"  - gitlab-ci.yml")
    print(f"  - local_ci.sh")


if __name__ == "__main__":
    create_cicd_examples()
