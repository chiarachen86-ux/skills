#!/usr/bin/env python3
"""Bounded macOS idle-sleep guard for one authorized local batch."""
import argparse
import json
import os
from pathlib import Path
import signal
import subprocess


def identity(pid):
    p = subprocess.run(['/bin/ps','-p',str(pid),'-o','lstart=','-o','command='],capture_output=True,text=True)
    return p.stdout.strip() if p.returncode == 0 else ''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=['start','status','stop'])
    parser.add_argument('--state',required=True,type=Path,help='Private local work file; do not upload')
    parser.add_argument('--seconds',type=int,default=7200)
    args = parser.parse_args()
    if not 1 <= args.seconds <= 14400:
        parser.error('Duration must be 1..14400 seconds')
    state = json.loads(args.state.read_text()) if args.state.exists() else {}
    current = identity(state['pid']) if state.get('pid') else ''
    active = bool(current and current == state.get('identity') and '/usr/bin/caffeinate -i -t ' in current)
    if args.action == 'start' and not active:
        if not Path('/usr/bin/caffeinate').is_file():
            raise SystemExit('macOS caffeinate is unavailable')
        args.state.parent.mkdir(parents=True,exist_ok=True)
        proc = subprocess.Popen(['/usr/bin/caffeinate','-i','-t',str(args.seconds)],stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,start_new_session=True)
        try:
            ident = identity(proc.pid)
        except OSError:
            proc.terminate()
            raise SystemExit('Cannot inspect the guard process in this environment; retry with required execution permission.')
        if '/usr/bin/caffeinate -i -t ' not in ident:
            proc.terminate()
            raise SystemExit('Could not verify the started guard')
        state = dict(pid=proc.pid,identity=ident,seconds=args.seconds)
        args.state.write_text(json.dumps(state,indent=2)+'\n')
        active = True
    elif args.action == 'stop' and active:
        try:
            os.kill(state['pid'],signal.SIGTERM)
        except ProcessLookupError:
            pass
        active = False
    print(json.dumps(dict(active=active,pid=state.get('pid'),idle_sleep_only=True,prevents_lid_sleep=False)))


if __name__ == '__main__':
    main()
