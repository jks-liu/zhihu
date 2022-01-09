---
title: 安装 Ubuntu 后必做的几件事（2023年版）
zhihu-title-image: pics/ubuntu-hero-banner.jpg
zhihu-title-image-origin: https://assets.ubuntu.com/v1/2a202263-hero-banner.jpg
zhihu-tags: Ubuntu
zhihu-url: https://zhuanlan.zhihu.com/p/455052145
---

问：今年是2022，为什么标题中是2023

答：我曾在超市买到明天生产的面包，所以你看到明年写的文章也是有可能的，毕竟这个世界其实不是你认为的样子。


# 设置代理

将下面两行添加到：`~/.bashrc` 或者 `~/.zshrc` 中，即可设置代理。

```sh
export http_proxy=http://ip:port
export https_proxy=http://ip:port
```

设置代理永远是第一步。但请记住，此代理只对非 Root 用户有效，这意味着在使用 `sudo` 命令的时候，是无法使用上面代理的，因为 `sudo` 环境没有继承这两个环境变量。

## 设置sudo继承环境变量

```sh
$ sudo visudo
```
[然后添加下面内容并保存：](https://wiki.archlinux.org/title/Sudo#Environment_variables)
```config
Defaults env_keep += "ftp_proxy http_proxy https_proxy no_proxy"
```
当然你可以在这里添加你想要继承的任何环境变量。

# 非本地桌面用户
如果你从 ssh 登录你的机器，或使用 WSL （Windows Subsystem Linux），你可能需要以下设置。

## 配置 DISPLAY
如果你从 Windows 登录你的机器或使用 WSL，你可能需要 [VcXsrv Windows X Server](https://sourceforge.net/projects/vcxsrv/)。同时需要配置 DISPLAY 环境变量。

```sh
export DISPLAY=http://ip:port
```

当然使用 WSL 的用户可以试试 [WSLg](https://github.com/microsoft/wslg)，WSLg 不需要设置 DISPLAY，虽然它只支持 [Windows 11](https://zhuanlan.zhihu.com/p/437362868)。




<!-- # 配置export LIBGL_ALWAYS_INDIRECT=1

# 配置 export PYTHONDONTWRITEBYTECODE=1 -->

题图来自 Ubuntu 官网。
