import json
import os
user = os.environ['USER']
with open('/home/yrz/resources_allocation.json','r') as f:
    resources_allocation = json.load(f)
if user in resources_allocation['ssd'].keys():
    print("Your ssd directory:\033[34m{}\033[0m".format(resources_allocation['ssd'][user]))
else:
    print("You have \033[31mNO\033[0m ssd directory, please contact Administrator")
if user in resources_allocation['hdd'].keys():
    print("Your hdd directory:\033[34m{}\033[0m".format(resources_allocation['hdd'][user]))
else:
    print("You have \033[31mNO\033[0m hdd directory, please contact Administrator")

if user in resources_allocation['gpu'].keys():
    print("Your permitted gpu id:\033[34m{}\033[0m".format(resources_allocation['gpu'][user]))
else:
    print("You have \033[31mNO\033[0m permitted gpu, please contact Administrator")