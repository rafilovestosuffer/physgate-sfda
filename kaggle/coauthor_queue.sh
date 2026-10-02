#!/usr/bin/env bash
# Runs the remaining GPU work (C83 seed 1, C85 SHOT) on the co-author account once ~/.kaggle_coauthor/access_token exists.
# The token is read only by the Kaggle CLI (KAGGLE_CONFIG_DIR). Nothing here prints or copies it.
set -u
cd "$(dirname "$0")/.."
export PHYSGATE_RUNNER=coauthor PHYSGATE_KAGGLE_USER=rhrhrhrhrh PYTHONUTF8=1
until [ -s "$HOME/.kaggle_coauthor/access_token" ]; do sleep 60; done
echo "$(date) token file present; verifying account"
python -c "import sys;sys.path.insert(0,'kaggle');import _cli;cp=_cli.run('kernels','list','--mine','--page-size','1',check=False);print('auth rc',cp.returncode)"
python -u kaggle/sync_runner.py
sleep 180   # let dataset versions finish processing
U=rhrhrhrhrh
for k in m2seed_FA_s1 m2seed_FB_s1 shot_FA shot_FB; do
  n=physgate-$(echo $k | tr 'A-Z_' 'a-z-')
  python -u kaggle/push.py --code kaggle/kernels/$k.py --name $n --title $n --dataset $U/physgate-m0-code --dataset $U/physgate-m1-data --timeout-s 30600 || { echo "push failed $n"; continue; }
  python -u kaggle/poll.py --name $n --interval 300 --timeout 33000
  python -u kaggle/pull.py --name $n
done
echo "$(date) coauthor queue done"
