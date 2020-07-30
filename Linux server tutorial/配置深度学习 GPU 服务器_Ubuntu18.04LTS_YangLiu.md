# 如何配置一个用于深度学习的 GPU 服务器 [Ubuntu 18.04 LTS 为例]

[Y. Liu](https://liuyang12.github.io "Yang Liu") yliu@csail.mit.edu 创建于 2020 年 7 月 29 日

## 硬件配置
1. CPU of Intel i9-9980XE (18-core 36-thread, @3.0-4.4 GHz),
2. RAM of 128 GB (DDR4),
3. GPU of NVIDIA RTX 2080 Ti*4 (11 GB GDDR6*4), and
4. M.2 NVMe SSD of 1 TB (`/home` with 256 GB as `swap`), SATA3 SSD of 2 TB (`/ssd`) and HDD of 8 TB*2 (`/data` and `/proj`).

## 软件配置 [硬件驱动部分]
0. 下载当前最稳定的 Ubuntu 长时间支持版本 (Long Term Support, LTS) 的光盘镜像文件 `.iso`。 以当前 (2020.7.28) 为例，推荐使用 Ubuntu 18.04 LTS。尽管 Ubuntu 20.04 LTS 已于四月份发布，但是考虑各方面的稳定性和软件支持推荐已维护更新至第四个自版本的 Ubuntu 18.04 LTS。教育网建议使用国内 ipv6 镜像站下载，例如清华 `https://mirrors.tuna.tsinghua.edu.cn/ubuntu-releases/bionic/ubuntu-18.04.4-desktop-amd64.iso`。
1. 创建 U 盘启动镜像。可以参考 Ubuntu 官方指南 [Windows](https://ubuntu.com/tutorials/create-a-usb-stick-on-windows), [Ubuntu](https://ubuntu.com/tutorials/create-a-usb-stick-on-ubuntu) 和 [macOS](https://tutorials.ubuntu.com/tutorial/tutorial-create-a-usb-stick-on-macos)。其中 Windows 下推荐使用 [Rufus](https://rufus.ie/)，分区注意选择 MBR 和 UEFI。
2. 目标服务器重启引导进入 BIOS 选择 U 盘启动，开始安装 Ubuntu。安装过程同样可以参考 Ubuntu 官方指南 https://ubuntu.com/tutorials/install-ubuntu-desktop。注意选择系统安装盘为 M.2 NVMe SSD，并划分 RAM 一倍 (这里 SSD 较大，可划分两倍即 256 GB) 为 `swap` 分区，作为超出物理内存的临时缓存区。
3. 配置 ssh 远程，之后的操作均可远程完成。建议修改默认端口 `22`，比如 `2222`，可在 `/etc/ssh/sshd_config` 中找到 `Port 22` 并对应修改为 `Port 2222`，下面的防火墙端口已对应调整。
```bash
sudo apt-get install openssh-server
sudo service ssh restart
sudo ufw allow 2222
```
4. 硬盘分区并挂载（已有硬盘可直接挂载），也可通过图形界面操作。通过 UUID 与 `/etc/fstab` 绑定硬盘/分区和目录。例如 SATA SSD 2TB 拟挂载至 `/ssd`，首先 `sudo fdisk -l` 找到大小为 2TB 的盘，记录 `Disk /dev/sdc`，然后 `sudo blkid` 找到 `/dev/sdc` 的 UUID，接着创建挂载文件夹 `sudo mkdir /ssd`，再在 `/etc/fstab` 末追加一行 `UUID=b4c93...  /ssd  ext4  defaults  0  2`，如果同时挂载多个硬盘，依次记录 UUID 并创建挂载文件夹，最后重新挂载所有硬盘 `mount -av`，可通过重启确认是否挂载成功。
5. 显卡驱动以及 CUDA, CuDNN 和 TensorRT。强烈建议按照 TensorFlow 的最新的 GPU guide 安装 https://www.tensorflow.org/install/gpu#install_cuda_with_apt。以下摘录当前的 Ubuntu 18.04 (CUDA 10.1) 的安装步骤。
```bash
# Add NVIDIA package repositories
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu1804/x86_64/cuda-repo-ubuntu1804_10.1.243-1_amd64.deb
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

## 软件配置 [软件设置部分]
以下配置不分先后，按必要摘取。
### 新建用户
新建用户并在对应数据文件夹 (如 `/data`, `/proj` 和 `/ssd`) 创建对应用户名的文件夹并转移文件夹所有权。
```bash
sudo adduser $USERNAME
sudo mkdir /data/$USERNAME
sudo chown -R $USERNAME /data/$USERNAME
```
### 安装 `conda`
从官网 (https://www.anaconda.com/products/individual) 或者 ipv6 镜像站 (https://mirrors.tuna.tsinghua.edu.cn/anaconda/archive/?C=M&O=D) 下载并按提示安装。

### 安装 TensorFlow 和 PyTorch
以 CUDA 10.1 为例。
#### `pip` 安装 TensorFlow
参考 TensorFlow 官方指南 https://www.tensorflow.org/install/pip
TensorFlow (CPU 和 GPU) 2.x
```bash
pip install --upgrade tensorflow
```
TensorFlow (GPU) 1.15
```bash
pip install --upgrade tensorflow-gpu==1.15
```
#### `conda` 安装 PyTorch
参考 PyTorch 官方指南 https://pytorch.org/
```bash
conda install pytorch torchvision cudatoolkit=10.1 -c pytorch
```
### 远程访问
远程访问文件/文件夹/terminal，并像本地一样优雅地写代码调试的两个方法。
#### VS Code [体验几乎完美] 
1. install VS Code and its extension Remote Workspace.
    * [VS Code](https://code.visualstudio.com/), and  
    * [Remote - SSH](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-ssh)

#### JupyterLab (或者 Jupyter Notebook) [体验非常好但需要端口映射]
1. start JupyterLab (or Jupyter Notebook) on the remote server.  
    `jupyter-lab --no-browser --port=8889` (for JupyerLab) or  
    `jupyter-notebook --no-browser --port=8889` (for Jupyter Notebook)  
2. port mapping on the local computer to access the web content on the remote server
    `ssh -N -L localhost:8888:localhost:8889 -p 2222 $USERNAME@$REMOTEHOST`
3. start the browser and type `localhost:8888` to access the JupyterLab (or Jupyter Notebook) on the remote server.

### 安装 MATLAB
以 MATLAB R2018b 为例。
#### install from dual .iso files
0. cd to the directory which contains the two .iso package(s)
1. `sudo mkdir /mnt/matlab` make a directory to mount the matlab .iso package(s).
2. `sudo mount -t auto -o loop R2018b_glnxa64_dvd1.iso /mnt/matlab/` mount the first DVD .iso file.
3. `sudo /mnt/matlab/install` run the install file in the mounted directory.
4. install matlab using the key provided in the license package.
5. wait until reminding of mounting the second DVD .iso file.
6. `sudo umount /mnt/matlab` unmount the first DVD .iso file.
7. `sudo mount -t auto -o loop R2018b_glnxa64_dvd2.iso /mnt/matlab/` mount the second DVD .iso file ***at exactly the same directory***.
8. click *continue* to install the package from the second DVD .iso file.
9. `sudo umount /mnt/matlab` unmount the second DVD .iso file after installation.

#### license

10. ```bash
    sudo cp Matlab\ R2018b\ Linux64\ Crack/license_standalone.lic /usr/local/MATLAB/R2018b/licenses/
    sudo cp Matlab\ R2018b\ Linux64\ Crack/R2018b/bin/glnxa64/matlab_startup_plugins/lmgrimpl/libmwlmgrimpl.so /usr/local/MATLAB/R2018b/bin/glnxa64/matlab_startup_plugins/lmgrimpl/libmwlmgrimpl.so

### 更换更新源
将 Ubuntu 系统、PyPI 和 conda 更换为镜像站源，可以参考对应的使用帮助 。更换 Ubuntu 18.04 LTS 的更新源，参考 https://mirrors.tuna.tsinghua.edu.cn/help/ubuntu/

