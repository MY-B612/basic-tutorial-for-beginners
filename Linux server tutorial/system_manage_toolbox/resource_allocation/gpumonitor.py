import subprocess
import psutil
import json
import os
import time
with open('/home/yrz/resources_allocation.json','r') as f:
    resources_allocation = json.load(f)
gpu_allocation = resources_allocation['gpu']
users = gpu_allocation.keys()
def killpid(pid):
    if psutil.pid_exists(pid):
        proc = psutil.Process(pid)
        children = proc.children(recursive=True)
        children.append(proc)
        for proc in children:
            proc.terminate()
        # logging.info('Task:{} Terminate!'.format(self.task.name,))
        gone, alive = psutil.wait_procs(children, timeout=1)
        for p in alive:
            p.kill()
            # logging.info('Task:{} Kill!'.format(self.task.name,))

gpuusage = subprocess.check_output("/usr/local/bin/gpustat --json", shell=True)
gpuusage = eval(gpuusage.decode('ascii').replace('\n',''))
for gpu in gpuusage['gpus']:
    gpuid = gpu['index']
    for process in gpu['processes']:
        user = process['username']
        command = process['command']
        pid = process['pid']
        if 'python' in command:
            if user in users:
                if gpuid not in gpu_allocation[user]:
                    print(time.strftime("%Y-%m-%d-%H:%M:%S: {} 's pid: {} use the not permitted gpu {}. Kill it!").format(user,pid,gpuid)) 
                    killpid(pid)
                    break