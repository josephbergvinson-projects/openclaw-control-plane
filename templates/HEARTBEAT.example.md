# Heartbeat monitoring instructions

The installer puts this example in `runbook/heartbeat-scratch.md`. To use it, save the applicable instructions as scratch on the intended monitoring job. The job owns its schedule and delivery settings. [Heartbeat documentation](https://docs.openclaw.ai/gateway/heartbeat)

Read the configured attention sources using the permitted bounded read paths. Report a material change, failure, decision or requested reminder in natural prose. A no-change success stays silent unless the schedule explicitly promises a report. Do not repeat unchanged alerts or treat stale evidence as proof of failure.

If a task remains active, its own supported task/session primitive owns continuation and delivery. Do not create a second worker, replay a possible effect or infer liveness from an old status file. Use the existing native status and reconciliation paths. Any repair must remain inside an authenticated instruction or explicitly configured standing grant; this file creates neither.
