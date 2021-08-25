 ===== configuration ===== 
> By Runzhao Yang

1. 在 .bashrc 中添加如下内容，实现登录提示资源分配信息

# show gpu allocation
python /home/yrz/show_resources_allocation.py

2. 在定时任务中指定定时运行 gpumonitor.py 脚本，检测并处理GPU分配占用问题
