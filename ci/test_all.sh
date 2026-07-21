#!/bin/bash
# Automated verification test runner for cfdvv-suite
# Runs self-comparison on all verification cases with analytical solutions

set -e

echo "=== cfdvv-suite Verification Tests ==="
echo "Available cases:"
cfdvv list --category verification

PASS=0
FAIL=0

# Self-compare analytical cases
for CASE_DIR in $(find $(python3 -c "import cfdvv,os; print(os.path.join(os.path.dirname(cfdvv.__file__),'cases'))") \( -path "*/reference/analytical" -o -path "*/reference/mms" \) | sed 's|/reference/.*||' | sort -u); do
    if [ ! -f "$CASE_DIR/case.yaml" ]; then continue; fi
    
    CASE_ID=$(grep "^id:" "$CASE_DIR/case.yaml" | head -1 | awk '{print $2}')
    REF_FILE=$(find "$CASE_DIR/reference" -name "*.csv" | head -1)
    
    if [ -z "$REF_FILE" ]; then continue; fi
    
    echo "--- Testing $CASE_ID ---"
    if cfdvv compare "$CASE_DIR" -r "$REF_FILE" --no-plot --tolerance 1e-8 2>/dev/null; then
        echo "  PASS: $CASE_ID"
        PASS=$((PASS+1))
    else
        echo "  FAIL: $CASE_ID"
        FAIL=$((FAIL+1))
    fi
done

echo ""
echo "=== Results: $PASS passed, $FAIL failed ==="
[ $FAIL -eq 0 ] || exit 1
