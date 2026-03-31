#!/bin/bash
# Pre-upload security scan — run before any file goes to Google Drive
# Usage: bash pre-upload-scan.sh <file_path>

FILE="$1"
ISSUES=0

if [ -z "$FILE" ]; then
  echo "Usage: pre-upload-scan.sh <file_path>"
  exit 1
fi

if [ ! -f "$FILE" ]; then
  echo "FAIL: File not found: $FILE"
  exit 1
fi

echo "=== Pre-Upload Security Scan ==="
echo "File: $FILE"
echo ""

# 1. Account numbers (4+ digits with dashes or long digit strings)
ACCT=$(grep -cE '[0-9]{4,}-[0-9]{4,}|acct.*[0-9]{6,}|account.*(number|#|no\.).*[0-9]{5,}' "$FILE" 2>/dev/null)
if [ "$ACCT" -gt 0 ]; then
  echo "⚠️  FOUND $ACCT possible account number patterns"
  grep -nE '[0-9]{4,}-[0-9]{4,}|acct.*[0-9]{6,}|account.*(number|#|no\.).*[0-9]{5,}' "$FILE"
  ISSUES=$((ISSUES + 1))
else
  echo "✅ No account numbers detected"
fi

# 2. SSNs
SSN=$(grep -cE '[0-9]{3}-[0-9]{2}-[0-9]{4}' "$FILE" 2>/dev/null)
if [ "$SSN" -gt 0 ]; then
  echo "⚠️  FOUND $SSN possible SSN patterns"
  ISSUES=$((ISSUES + 1))
else
  echo "✅ No SSN patterns detected"
fi

# 3. API keys / tokens
KEYS=$(grep -ciE 'sk-[a-zA-Z0-9]{20,}|api[_-]?key.*[=:]\s*["\x27]?[a-zA-Z0-9]{20,}|bearer [a-zA-Z0-9]{20,}|token.*[=:]\s*["\x27]?[a-zA-Z0-9]{30,}' "$FILE" 2>/dev/null)
if [ "$KEYS" -gt 0 ]; then
  echo "⚠️  FOUND $KEYS possible API key/token patterns"
  ISSUES=$((ISSUES + 1))
else
  echo "✅ No API keys/tokens detected"
fi

# 4. Email addresses
EMAILS=$(grep -coE '[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}' "$FILE" 2>/dev/null)
if [ "$EMAILS" -gt 0 ]; then
  echo "⚠️  Contains $EMAILS email address(es):"
  grep -oE '[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}' "$FILE" | sort -u
  ISSUES=$((ISSUES + 1))
else
  echo "✅ No email addresses detected"
fi

# 5. Phone numbers
PHONES=$(grep -cE '\b[0-9]{3}[-.]?[0-9]{3}[-.]?[0-9]{4}\b' "$FILE" 2>/dev/null)
if [ "$PHONES" -gt 0 ]; then
  echo "⚠️  Contains $PHONES possible phone number(s)"
  ISSUES=$((ISSUES + 1))
else
  echo "✅ No phone numbers detected"
fi

echo ""
if [ "$ISSUES" -gt 0 ]; then
  echo "🔴 $ISSUES potential issue(s) found — review before uploading"
  exit 1
else
  echo "🟢 Clean — safe to upload"
  exit 0
fi
