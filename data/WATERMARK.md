# This directory stores runtime data files used by the Client Nurturing Engine.
#
# watermark.json — Persists runtime state for the background jobs so they survive server restarts:
#   - welcome_job : Tracks the last processed lead's `last_stage_changed_at` timestamp so welcome messages aren't re-sent.
#   - birthday_job: Tracks the `birthday_sent_date` and `birthday_sent_ids` so duplicate birthday messages aren't sent on the same day, even if the server restarts.
# 
# This file is auto-generated. Do NOT manually edit watermark.json.
