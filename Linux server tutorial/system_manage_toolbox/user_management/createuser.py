import os
import subprocess
import json
from subprocess import Popen
import time
# laod
with open('/home/yrz/resources_allocation.json','r') as f:
    resources_allocation = json.load(f)
# username password
username=input('input username:')
password = '123'#subprocess.check_output("gpg --gen-random --armor 1 12", shell=True).decode('ascii').replace('\n','')
Popen('{} | adduser "{}"'.format(password,username),shell=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
time.sleep(10)
with open('/home/{}/.bashrc'.format(username),'a') as f:
    f.write('# show resources allocation\npython /home/yrz/show_resources_allocation.py\n')
# ssd
ssddirnum_dict = {os.path.join('/ssd',dirname):len(os.listdir(os.path.join('/ssd',dirname))) for dirname in os.listdir('/ssd')}
ssddir = min(ssddirnum_dict, key=ssddirnum_dict.get)
ssddir = os.path.join(ssddir,username)
os.system('mkdir {} && chmod 770 {} && chown {} {} && chgrp {} {}'.format(ssddir,ssddir,username,ssddir,username,ssddir))
resources_allocation['ssd'][username] = ssddir
# hdd
hdddirnum_dict = {os.path.join('/hdd',dirname):len(os.listdir(os.path.join('/hdd',dirname))) for dirname in os.listdir('/hdd')}
hdddir = min(hdddirnum_dict, key=hdddirnum_dict.get)
hdddir = os.path.join(hdddir,username)
os.system('mkdir {} && chmod 770 {} && chown {} {} && chgrp {} {}'.format(hdddir,hdddir,username,hdddir,username,hdddir))
resources_allocation['hdd'][username] = hdddir
# gpu
gpuusage = subprocess.check_output("gpustat --json", shell=True)
gpuusage = eval(gpuusage.decode('ascii').replace('\n',''))
gpu_allocation_count = {gpu['index']:0 for gpu in gpuusage['gpus']}
for gpuid_list in resources_allocation['gpu'].values():
    for gpuid in gpuid_list:
        gpu_allocation_count[gpuid] += 1
gpu_id = min(gpu_allocation_count, key=gpu_allocation_count.get)
resources_allocation['gpu'][username] = [gpu_id]
# write
with open('/home/yrz/resources_allocation.json','w') as f:
    json.dump(resources_allocation,f,indent=4)
print('=================================')
print('username:{}\npassword:{}\nssd direvtory:{}\nhdd direvtory:{}\npermitted gpu:{}'.format(username,password,ssddir,hdddir,[gpu_id]))
print('=================================')
