#! https://zhuanlan.zhihu.com/p/385835344
# 无需安装任何软件，即可在Windows 10访问远程ssh（Linux）文件目录

假设我们有一个Linux系统，其IP地址为`5.5.5.5`，我们如何才能访问上面的文件系统呢。传统的方法一般是

1. 在Linux安装一个[Smaba](https://www.samba.org/)服务器，缺点是我们需要有ROOT权限，但有时候我们没有。
2. 使用[WinSCP](https://winscp.net/eng/index.php)。

自从Windows 10有了WSL，我们又有了一种新的方法。

- 首先，[安装WSL](https://docs.microsoft.com/en-us/windows/wsl/install-win10)。
- 然后我们就可以在Windows资源管理器中用`\\wsl$`访问WSL中的文件
- 在WSL中安装`sshfs`  
  `$ sudo apt install sshfs`
- 然后在WSL中挂在`5.5.5.5`，（先创建`/mnt/test`文件夹，如果没有的话）  
  `sudo sshfs -o allow_other username@5.5.5.5:/ /mnt/test`
- 然后我们就可以在资源管理器中用如下地址访问远程Linux系统的文件  
  `\\wsl$\Ubuntu\mnt\test`
