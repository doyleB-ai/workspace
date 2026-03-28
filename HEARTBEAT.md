# HEARTBEAT.md

# IPO Research Agent Health Check (check once daily, skip weekends)
# - Verify daily research file was created in projects/ipo-research/daily/
# - Check cron run history for failures: openclaw cron runs --id 558a418a-57f2-45b7-8617-ee125e8ea5f5
# - If a daily file is missing or a run failed, flag it to John
# - Monday mornings: also verify the weekly report (job 4ea1a810-10ec-4cfa-bce5-334ea833b957) delivered successfully
