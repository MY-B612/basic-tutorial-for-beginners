# 服务器使用指南

> Zhihong Zhang @ BBNC

##### 1.  准备工作：熟悉下基本的命令和操作

  * linux系统的基本常识和常用命令，pwd, ls, mv, cd, rm, cp等: [linux基本命令](https://www.cnblogs.com/hzy168/p/10313441.html)
  * 熟悉 tmux的使用：[tmux使用教程](http://www.ruanyifeng.com/blog/2019/10/tmux.html)
  * 熟悉自己所需的编程环境，如python的IDE anaconda等的基本操作

##### 2. 安装软件 Mobaxterm，并配置服务器账户
- 询问学长如下的账户信息
  - remote host: \****
  - user name: \****
  - password: \****
-   配置服务器账户： session->SSH-> 填写 remote host; specify name; port->OK 左侧边栏会出现配置好的服务器列表，双击连接，首次连接需要输入密码
- 注意：远程非校园网访问需要下载vpn软件并连接[vpn](http://info.tsinghua.edu.cn/out/help.jsp)

##### 3. 个人文件夹

  - 用户文件夹主要有两个，主目录: /home/guest, 数据目录: /data/guest， 个人文件放在数据目录下，主目录空间较小，一般不放东西
  - 服务器文件查看与上传：直接从mobaxtrem左侧边栏选到sftp项目可以看到服务器目录树，切到相应目录下将本地文件直接拖入即可上传，基本的重命名和删除操作也可以从此处操作（内网不费流量）

##### 4. 常用命令

  - linux

    - ls, 查看当前目录下的文件； 
    - cd [dir]，切换到dir目录下；
    - cp/mv file [dir]，复制/移动file文件到dir目录下；
    - gedit [file]， 编辑file文件内容（也可以从侧边栏双击打开）； 
    - clear，清屏
    - ...
  - tmux（会话管理软件，保证程序长时间运行不中断）
    - tmux new-session -s [name]：创建一个名字为name的tmux 会话
    - tmux kill-session -t [name]：关闭[name]会话
    - tmux ls：查看当前所有tmux会话列表
    - tmux a -t [name]：转到[name]会话下
    -  tmux detach (快捷键 ctrl+b，松手按d）：切出tmux会话
    - tmux split-window / tmux split-window -h: 划分上下（左右）两个窗格 
    - ...

##### 5. 运行代码

   - 首先切到代码所在目录下: cd [directory]
   - python（anaconda）：
     - 激活python环境 conda activate dvp
     - 查看并指定GPU：
       - gpustat -cpu -i 3 （查看GPU占用情况，选择没人占用的GPU）
       - export CUDA_VISIBLE_DEVICES=1, 2 （指定使用编号为1和2的GPU）
     - ​	输入 python  your_file.py， 回车即可运行
     - 也可以通过运行 CUDA_VISIBLE_DEVICES=1   python  your_file.py 在每次运行程序时，给该程序指定不同GPU
   - matlab：运行 matlab，出来图形界面； 或者运行 mrun [name], (注意不需要加.m), 直接执行代码（无图形界面）

##### 6. 注意事项

  - 只在自己的目录下进行工作，不要随便更改非个人目录下的文件 （特别注意慎用删除命令，尽量在侧边栏的图形化文件列表里删）
  - 服务器的各种软件运行环境（如TensorFlow等）基本都是配置好的，一般不需要自己配置，可以先查看是不是可以用，不行再自己配置
  - GPU只有4块，尽量不要自己占完，GPU状态监控可以运行 gpustat -cpu -i 3 查看实时状态
  - 不懂的地方先自己百度下，不确定的操作可以问学长

##### 7. 其他操作如通过VScode，Pycharm远程连接服务器如有需要，请自行学习

   
