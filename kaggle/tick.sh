#!/usr/bin/env bash
# Scheduled every 30 min: (re)start queues; each is single-instance and idempotent (skips done, attaches to running).
cd "$(dirname "$0")/.."
nohup bash kaggle/queue_coauthor_bistw_g2.sh >> runs/queue_coauthor_bistw_g2.log 2>&1 &
nohup bash kaggle/queue_primary_g34.sh >> runs/queue_primary_g34.log 2>&1 &
wait
