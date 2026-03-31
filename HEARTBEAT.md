# HEARTBEAT.md

# Quantitative Analysis Phase 4 (check until delivered)
# - Read memory/2026-03-30.md for current status
# - If Phase 4 not complete, continue working:
#   1. Review charts in projects/advisory-board/research/reports/charts/
#   2. Rerun sequence-of-returns with 3% withdrawal + healthcare bridge costs
#   3. Clean up report narrative
#   4. Generate .docx and deliver
# - Work at measured pace — do NOT spawn parallel jobs (rate limit concern)
# - When final .docx is delivered, remove this block

# IPO Research Agent Health Check (check once daily, skip weekends)
# - Verify daily research file was created in projects/ipo-research/daily/
# - Check cron run history for failures: openclaw cron runs --id 558a418a-57f2-45b7-8617-ee125e8ea5f5
# - If a daily file is missing or a run failed, flag it to John
# - Monday mornings: also verify the weekly report (job 4ea1a810-10ec-4cfa-bce5-334ea833b957) delivered successfully

# Security Checks (rotate through, 1-2x daily)
# 1. Google Drive permissions — check all financial docs are owner-only:
#    gog drive permissions 1AXTMNvptIqqQeZHdRQGJ_LoAt7HwPnR- --account clearyclaw@gmail.com
#    If any doc has >1 permission, ALERT JOHN IMMEDIATELY.
# 2. PII scan on any new files created since last check:
#    grep -rE '[0-9]{3}-[0-9]{2}-[0-9]{4}|sk-[a-zA-Z0-9]{20,}' projects/ --include="*.md" --include="*.txt"
# 3. Workspace file permissions — nothing should be world-readable:
#    find projects/advisory-board/ -perm -o+r -type f
# Before ANY Google Drive upload, run: bash projects/security/pre-upload-scan.sh <file>
