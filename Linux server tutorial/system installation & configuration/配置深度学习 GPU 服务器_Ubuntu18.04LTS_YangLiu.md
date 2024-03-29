# 如何配置一个用于深度学习的 GPU 服务器 [Ubuntu 18.04 LTS 为例]

[Yang Liu](https://liuyang12.github.io "Yang Liu") 创建于 2020 年 7 月 29 日

[Zhihong Zhang](https://github.com/dawnlh) 修改于 2020 年 8 月 1日

## 一、硬件配置

1. CPU of Intel i9-9980XE (18-core 36-thread, @3.0-4.4 GHz),
2. RAM of 128 GB (DDR4),
3. GPU of NVIDIA RTX 2080 Ti\*4 (11 GB GDDR6\*4), and
4. M.2 NVMe SSD of 1 TB (`/home` with 256 GB as `swap`), SATA3 SSD of 2 TB (`/ssd`) and HDD of 8 TB\*2 (`/data` and `/proj`).

## 二、系统配置 

#### 2.1 基本流程

0. 下载当前最稳定的 Ubuntu 长时间支持版本 (Long Term Support, LTS) 的光盘镜像文件 `.iso`。 以当前 (2020.7.28) 为例，推荐使用 Ubuntu 18.04 LTS。尽管 Ubuntu 20.04 LTS 已于四月份发布，但是考虑各方面的稳定性和软件支持推荐已维护更新至第四个自版本的 Ubuntu 18.04 LTS。教育网建议使用国内 ipv6 镜像站下载，例如[清华TUNA镜像源](https://mirrors.tuna.tsinghua.edu.cn/ubuntu-releases/)。
1. 创建 U 盘启动镜像。可以参考 Ubuntu 官方指南 [Windows](https://ubuntu.com/tutorials/create-a-usb-stick-on-windows), [Ubuntu](https://ubuntu.com/tutorials/create-a-usb-stick-on-ubuntu) 和 [macOS](https://tutorials.ubuntu.com/tutorial/tutorial-create-a-usb-stick-on-macos)。其中 Windows 下推荐使用 [Rufus](https://rufus.ie/)，分区注意选择 MBR 和 UEFI。
2. 目标服务器重启引导进入 BIOS 选择 U 盘启动，开始安装 Ubuntu。安装过程同样可以参考 [Ubuntu 官方指南](https://ubuntu.com/tutorials/install-ubuntu-desktop)。注意选择系统安装盘为 M.2 NVMe SSD，并划分 RAM 一倍 (这里 SSD 较大，可划分两倍即 256 GB) 为 `swap` 分区，作为超出物理内存的临时缓存区。
3. 配置 ssh 远程，之后的操作均可远程完成。建议修改默认端口 `22`，比如 `2222`，可在 `/etc/ssh/sshd_config` 中找到 `Port 22` 并对应修改为 `Port 2222`，下面的防火墙端口已对应调整。
    ```bash
    sudo apt-get install openssh-server
    # vi /etc/ssh/sshd_config -> change the default Port 22 to 2222
    sudo service ssh restart
    sudo ufw allow 2222
    ```
4. 硬盘分区并挂载（已有硬盘可直接挂载），也可通过图形界面操作。已有硬盘直接挂载即通过 UUID 与 `/etc/fstab` 绑定硬盘/分区和目录。例如 SATA SSD 2TB 拟挂载至 `/ssd`，首先 `sudo fdisk -l` 找到大小为 2TB 的盘，记录 `Disk /dev/sdc`，然后 `sudo blkid` 找到 `/dev/sdc` 的 UUID，接着创建挂载文件夹 `sudo mkdir /ssd`，再在 `/etc/fstab` 末追加一行 `UUID=b4c93...  /ssd  ext4  defaults  0  2`，如果同时挂载多个硬盘，依次记录 UUID 并创建挂载文件夹，最后重新挂载所有硬盘 `mount -av`，可通过重启确认是否挂载成功。
5. 显卡驱动以及 CUDA, CuDNN 和 TensorRT。强烈建议按照 TensorFlow 的最新的 [GPU guide 安装](https://www.tensorflow.org/install/gpu?hl=zh-cn)。以下摘录当前的 Ubuntu 18.04 (CUDA 10.1) 的安装步骤。（注意：安装包会下载到当前目录下，注意保证当前目录的空间足够用； 确保选择的 Ubuntu 版本和当前系统一致）
    ```bash
    # Add NVIDIA package repositories
    wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu1804/x86_64/cuda-repo-ubuntu1804_10.1.243-1_amd64.deb
    # the package will be downloaded to the current directory
    sudo apt-key adv --fetch-keys https://developer.download.nvidia.com/compute/cuda/repos/ubuntu1804/x86_64/7fa2af80.pub
    sudo dpkg -i cuda-repo-ubuntu1804_10.1.243-1_amd64.deb
    sudo apt-get update
    wget http://developer.download.nvidia.com/compute/machine-learning/repos/ubuntu1804/x86_64/nvidia-machine-learning-repo-ubuntu1804_1.0.0-1_amd64.deb
    sudo apt install ./nvidia-machine-learning-repo-ubuntu1804_1.0.0-1_amd64.deb
    sudo apt-get update

    # Install NVIDIA driver
    sudo apt-get install --no-install-recommends nvidia-driver-450
    # Reboot. Check that GPUs are visible using the command: nvidia-smi

    # Install development and runtime libraries (~4GB)
    sudo apt-get install --no-install-recommends \
        cuda-10-1 \
        libcudnn7=7.6.5.32+cuda10.1  \
        libcudnn7-dev=7.6.5.32-1+cuda10.1


    # Install TensorRT. Requires that libcudnn7 is installed above.
    sudo apt-get install -y --no-install-recommends libnvinfer6=6.0.1-1+cuda10.1 \
        libnvinfer-dev=6.0.1-1+cuda10.1 \
        libnvinfer-plugin6=6.0.1-1+cuda10.1
    ```


#### 2.2 可能出现的问题和解决方案

(1) **apt-get 命令报错，无法安装软件**

- 没联网（`connection timed out`）：记得联网并登录，即从 firefox 图形界面登录清华账户

- 官方软件源访问不了（`Failed to fetch xxx...`)：一般都会推荐使用国内的镜像源来提高访问速度，比如阿里云或者[清华的镜像服务器](https://mirrors.tuna.tsinghua.edu.cn/help/ubuntu/)（注意选择和 Ubuntu 版本对应的镜像 ）。备份`/etc/apt/sources.list`文件，并用下面的内容（清华或者阿里云其一，建议清华）覆盖原文件内容，然后更新软件列表 `sudo apt-get update`。

    清华（Ubuntu 18.04 LTS），[详细教程](https://mirrors.tuna.tsinghua.edu.cn/help/ubuntu/)：

    ```
    # 默认注释了源码镜像以提高 apt update 速度，如有需要可自行取消注释
    deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ bionic main restricted universe multiverse
    # deb-src https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ bionic main restricted universe multiverse
    deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ bionic-updates main restricted universe multiverse
    # deb-src https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ bionic-updates main restricted universe multiverse
    deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ bionic-backports main restricted universe multiverse
    # deb-src https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ bionic-backports main restricted universe multiverse
    deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ bionic-security main restricted universe multiverse
    # deb-src https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ bionic-security main restricted universe multiverse
    
    # 预发布软件源，不建议启用
    # deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ bionic-proposed main restricted universe multiverse
    # deb-src https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ bionic-proposed main restricted universe multiverse
    ```

    阿里云：

    ```
    deb http://mirrors.aliyun.com/ubuntu/ raring main restricted universe multiverse  
    deb http://mirrors.aliyun.com/ubuntu/ raring-security main restricted universe multiverse  
    deb http://mirrors.aliyun.com/ubuntu/ raring-updates main restricted universe multiverse  
    deb http://mirrors.aliyun.com/ubuntu/ raring-proposed main restricted universe multiverse  
    deb http://mirrors.aliyun.com/ubuntu/ raring-backports main restricted universe multiverse  
    deb-src http://mirrors.aliyun.com/ubuntu/ raring main restricted universe multiverse  
    deb-src http://mirrors.aliyun.com/ubuntu/ raring-security main restricted universe multiverse  
    deb-src http://mirrors.aliyun.com/ubuntu/ raring-updates main restricted universe multiverse  
    deb-src http://mirrors.aliyun.com/ubuntu/ raring-proposed main restricted universe multiverse  
    deb-src http://mirrors.aliyun.com/ubuntu/ raring-backports main restricted universe multiverse  
    ```

- DNS 配置问题：重新配置 DNS ，打开配置文件 /etc/resolv.conf，并做如下修改：

    ```
    # Dynamic resolv.conf(5) file for glibc resolver(3) generated by resolvconf(8)
    #     DO NOT EDIT THIS FILE BY HAND -- YOUR CHANGES WILL BE OVERWRITTEN
    nameserver 127.0.1.1
    #这里用的是阿里云的DNS服务器
    nameserver 223.5.5.5  
    nameserver 223.6.6.6
    ```

- 软件列表没更新：更新软件列表 `sudo apt-get update`

(2) **显卡驱动下载或者安装失败**

- 报错: `gpgkeys: protocol 'https' not supported`：安装所需的包 `sudo apt install gnupg-curl`

- 报错: `W: GPG error: https://developer.download.nvidia.cn/compute/machine-learning/repos/ubuntu1804/x86_64  Release: The following signatures were invalid: BADSIG F... `：更新ubuntu软件源为[清华镜像软件源](https://mirrors.tuna.tsinghua.edu.cn/help/ubuntu/)或者科学上网

- 报错 `Unable to locate package nvidia-xxx`“：查看 `/etc/apt/sources.list.d/` 文件夹下是不是有两个软件源列表文件 cuda.list 和 nvidia-machine-learning.list 并且不为空。如果不存在或者为空，需要卸载（`sudo dpkg -P cuda-repo-ubuntu1804` ；`sudo dpkg -P nvidia-machine-learning-repo-ubuntu1804` )并按照原教程重新安装 cuda-repo-ubuntu1804 或者 nvidia-machine-learning-repo-ubuntu1804 两个包并 `sudo apt-get update` 软件源。

- nvidia-smi 报错 `Failed to initialize NVML: Driver`：可能重启一下就好了，如果不行再考虑是不是显卡驱动不匹配的问题



## 三、应用配置

以下配置不分先后，按必要摘取。
### 3.1 新建用户
新建用户并在对应数据文件夹 (如 `/data`, `/proj` 和 `/ssd`) 创建对应用户名的文件夹并转移文件夹所有权。
```bash
sudo adduser $USERNAME
sudo mkdir /data/$USERNAME
sudo chown -R $USERNAME /data/$USERNAME
```
### 3.2 安装 Anaconda
从 [Anaconda 官网](https://www.anaconda.com/products/individual) 或者 [清华镜像站](https://mirrors.tuna.tsinghua.edu.cn/anaconda/archive/?C=M&O=D) 下载并按提示安装。具体步骤如下：

1. 找到所需版本的anaconda下载链接url，并在命令行中使用 `wget <url >` 将安装包下载到本地（当前目录下）

   > 提示：当前（2020.8.2）最新的 anaconda3 对应的 python 版本为 3.8.x， 该版本可能没有对应的 TensorFlow 版本支持。可选择低版本的 anaconda3 或者安装最新 anaconda3 后建立新的虚拟环境并使用较低版本的 python 如，3.6.7 再安装 TensorFlow

2. 命令行切换到安装包所在目录，运行` bash <package_name>` 按照提示开始安装。安装过程中提示选择安装位置，如果希望不同用户共享 conda 环境，建议安装在 `/usr/local/anaconda3/`目录下（如果没有权限，可以使用 sudo 安装）；如果希望每个用户独立使用，则每个用户需要独立安装在自己的 home 路径下。下面以第一种方法演示。

3. 安装完毕后，重启 shell，通过 `which python` 查看当前默认的 python 是不是 anaconda3 下的 python，如果是则说明安装正常

4. 当前安装的 anaconda3 只能由安装的用户使用，通过编辑系统环境变量或者其他用户的环境变量，可以使得所有用户均能使用anaconda3。具体方法如下（以编辑系统环境变量为例，此时其他用户环境变量无需再次编辑）：
   ```bash
   vim /etc/profile
   # 编辑系统配置文件，在最后添加 'export PATH=/usr/local/anaconda3/bin:$PATH' 其中路径为 anaconda3 的 python 路径
   source /etc/profile
   # 更新系统配置文件，使配置生效
   # 切换到其他用户(已登录用户需要重新打开 shell)，使用 'which python' 查看其他用户的默认 python 路径是不是以及更改为 anaconda3 的 python 路径
   ```

5. （可选）修改 `/usr/local/anaconda3` 目录权限为 所有用户可读可写可执行 (`drwxrwxrwx`)，即`chmod -R 777 /usr/local/anaconda3`，这样所有用户建立的虚拟环境都会保存在 `/usr/local/anaconda3` 目录下，并且为所有用户可见、可用，避免重复建立虚拟环境浪费空间资源（但是这样会导致环境安全性降低，也可以根据需求配置其他权限类型来保护自己的虚拟环境不被其他人修改）。

   > 关于虚拟环境的创建位置和使用权限：
   >
   > (1) conda 默认将虚拟环境保存在 anaconda 的安装目录下,如 `/usr/local/anaconda3/envs/base2`，所有用户对anaconda 安装目录（如 `/usr/local/anaconda3/envs`）下的虚拟环境一般是默认可读可执行 (`drwxr-xr-x`) 的，通过更改该目录权限为`drwxrwxrwx`，任何用户也可以（默认）在该目录下创建虚拟环境并为所有人可用。但是如果当前用户没有对该目录的操作权限，则 conda 会将虚拟环境保存在当前用户的 home 目录下，如 `/home/<username>/.conda/envs/dvp`，此时虚拟环境仅对拥有者可见。
   >
   > (2) 此外，也可以在指定位置创建虚拟环境（不推荐），命令形式为，`conda create --prefix=/data/env2 python=3.6`, 但是后续激活环境等操作时，需要使用绝对路径，如 `activate /data/env2`, 相对麻烦。

### 3.3 安装 TensorFlow 和 PyTorch
注意选择和当前显卡型号及驱动匹配的CUDA版本，下面以 CUDA 10.1 为例。
#### `pip` 安装 TensorFlow
参考 [TensorFlow 官方指南](https://www.tensorflow.org/install)
TensorFlow (CPU 和 GPU) 2.x
```bash
pip install --upgrade tensorflow
```
TensorFlow (GPU) 1.15
```bash
pip install --upgrade tensorflow-gpu==1.15
```
#### `conda` 安装 PyTorch
参考 [PyTorch 官方指南](https://pytorch.org/) 
```bash
conda install pytorch torchvision cudatoolkit=10.1 -c pytorch
```
#### 可能出现的问题和解决方案

(1) 报错 `ERROR: Could not find a version that satisfies the requirement tensorflow-gpu==1.15`：可能是当前环境的 python 版本过高，没有匹配的 TensorFlow 版本。可新建虚拟环境并使用低版本的 python

(2) 报错 `NotWritableError: The current user does not have write permissions to a required path.`：可能是安装 anaconda3 的时候使用了管理员权限，导致当前用户没有写入权限。可修改该 anaconda3 文件夹权限为当前管理员用户 `sudo chown -R <username> /usr/local/anaconda3 `  

(3) 报错 `PackagesNotFoundError: The following packages are not available from current channels: ... `：更换conda源为清华源，即打开/创建源配置文件 `vim ~/.condarc`，然后用下面的内容替换原文件内容，保存退出。（注意：如需安装 pytorch 还需要运行以下命令再添加一个源 `conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/pytorch/`)：

```
channels:
  - defaults
show_channel_urls: true
channel_alias: https://mirrors.tuna.tsinghua.edu.cn/anaconda
default_channels:
  - https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main
  - https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free
  - https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/r
  - https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/pro
  - https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/msys2
custom_channels:
  conda-forge: https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud
  msys2: https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud
  bioconda: https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud
  menpo: https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud
  pytorch: https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud
  simpleitk: https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud
```


### 3.4 安装 VS Code

可以远程访问文件/文件夹/terminal，并像本地一样优雅地写代码调试的两个方法。
#### VS Code [体验几乎完美] 
1. 服务器端 安装 VS Code

    1. 从 [VS Code 的官网](https://code.visualstudio.com/download)下载 .deb 安装包

    2. 切到安装包所在目录，运行如下命令进行安装 (\<file> 为安装包的名称)

        ```bash
        sudo apt install ./<file>.deb
        
        # If you're on an older Linux distribution, you will need to run this instead:
        # sudo dpkg -i <file>.deb
        # sudo apt-get install -f # Install dependencies
        ```

2. 将远程服务器联网，并在远程终端输入 `code` 打开 vscode，安装需要的插件，如 `python` 插件。否则无法在远程调试相关代码

3. 本地端安装 VS Code 并配置远程访问插件，参考[官方教程](https://code.visualstudio.com/docs/remote/remote-overview)或者网络教程。


#### JupyterLab (或者 Jupyter Notebook) [体验非常好但需要端口映射]
1. start JupyterLab (or Jupyter Notebook) on the remote server.  
    `jupyter-lab --no-browser --port=8889` (for JupyerLab) or  
    `jupyter-notebook --no-browser --port=8889` (for Jupyter Notebook)  
2. port mapping on the local computer to access the web content on the remote server
    `ssh -N -L localhost:8888:localhost:8889 -p 2222 $USERNAME@$REMOTEHOST`
3. start the browser and type `localhost:8888` to access the JupyterLab (or Jupyter Notebook) on the remote server.

### 3.5 安装 MATLAB
以 MATLAB R2018b 为例，安装包可以从 bt 站等处下载linux版本。
#### 从 .iso 文件 安装 MATLAB
0. cd to the directory which contains the two .iso package(s)
1. `sudo mkdir /mnt/matlab` make a directory to mount the matlab .iso package(s).
2. `sudo mount -t auto -o loop R2018b_glnxa64_dvd1.iso /mnt/matlab/` mount the first DVD .iso file.
3. `sudo /mnt/matlab/install` run the install file in the mounted directory  (the graphic interface pops up).
4. install matlab using the key provided in the license package (choose "Use a File Installation Key" -> "I have the File Installation Key for my lcense" -> fill the blank with the key).
5. wait until reminding of mounting the second DVD .iso file.
6. `sudo umount /mnt/matlab` unmount the first DVD .iso file.
7. `sudo mount -t auto -o loop R2018b_glnxa64_dvd2.iso /mnt/matlab/` mount the second DVD .iso file ***at exactly the same directory***.
8. click *continue* install the package from the second DVD .iso file.
9. `sudo umount /mnt/matlab` unmount the second DVD .iso file after installation.

#### 将 license 文件复制到 MATLAB 安装目录
```
# change current woring directory to the license's directory
sudo cp license_standalone.lic /usr/local/MATLAB/R2018b/licenses/
sudo cp ./R2018b/bin/glnxa64/matlab_startup_plugins/lmgrimpl/libmwlmgrimpl.so /usr/local/MATLAB/R2018b/bin/glnxa64/matlab_startup_plugins/lmgrimpl/libmwlmgrimpl.so
```

#### 将 MATLAB 加入 PATH 中

```
sudo vim /etc/environment
# add matlab's bin directory path to the end of PATH, like
# PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/usr/local/MATLAB/R2018b/bin/"
source /etc/environment
# now you can start matlab by typing 'matlab' in the command line
```


### 3.6 安装其他应用软件

- 安装 tmux ，用于会话 session 管理： `sudo apt-get install tmux`
- 安装 gpustat，用于GPU状态监控：`pip install gpustat`

> 关于软件源：为了访问更快，可以将 Ubuntu 系统、PyPI 和 conda 更换为国内镜像站源 。更换源之后需要进行软件源更新 `sudo apt-get update`。
