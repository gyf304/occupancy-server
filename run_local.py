"""Run Heroku app locally"""
import subprocess
import sys
import os
from time import sleep
import json

def main():
    proc_file = ''
    env_json = ''
    env = os.environ.copy()
    with open('Procfile.local') as f:
        proc_file = f.read()
    with open('app.local.json') as f:
        env_json = f.read()
    env.update(json.loads(env_json)['env'])
    procs = {}
    popens = []
    for line in proc_file.splitlines():
        (type, args) = line.split(':', 1)
        procs[type] = args.strip()
    for type, args in procs.items():
        print('Launching {}'.format(type))
        popens.append(subprocess.Popen(args, shell=True, env=env))
    try:
        while True:
            sleep(100)
    except KeyboardInterrupt:
        for p in popens:
            # give sigterm to all processes
            p.send_signal(subprocess.signal.SIGTERM)
        try:
            # and wait for each to die...
            for p in popens:
                p.wait()
        except KeyboardInterrupt:
            # if that didn't do it, kill all
            for p in popens:
                p.kill()
        print('Processes Closed')
        return

if __name__ == '__main__':
    main()
