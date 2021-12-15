---
title: 在 Docker 里编译 AOSP：踩坑记录
zhihu-title-image: https://github.com/MobileDevOps/android-sdk-image/blob/master/docs/images/android-sdk-image.png?raw=true
zhihu-tags: AOSP, Docker, Android
---

本文介绍如何在 Docker 中编译 i.MX 8QuadXPlus[^1] 的 AOSP。

背景是这样的，由于最近需要做一个安卓相关的硬件项目，所以需要编译个 AOSP。根据 NXP 官方给出的文档，编译这个 Android 的 Image 最好使用 Ubuntu 18.04。但是，手边高性能的服务器（安卓编译很慢，所以放弃使用普通机器）只有一台 Ubuntu 16.04，并且我无法升级这个系统。


于是，便决定使用 Docker。这便是万恶之源。

Ubuntu 18.04[^2] 的 Docker 基于官方镜像，不再赘述。根据 NXP 的官方手册，将各种依赖，编译器配置等等写入 Dockerfile 中，启动 Docker。

# 第一个坑
于是我便按照手册编译 AOSP。

```sh
$ source build/envsetup.sh
$ lunch mek_8q_car-userdebug
```

根据手册，依次运行上面的命令。第二个命令，就有了错误。

```sh
Build sandboxing disabled due to nsjail error.
```

搜索一番，应该是 Docker 的原因[^3]，于是从 <https://github.com/google/nsjail> 自己构建了一个 `nsjailcontainer` 的 Docker Image，幸好构建过程很简单，就一条命令。然后，我把我 Dockerfile 中的 `ubuntu:18.04` 依赖改成了 `nsjailcontainer`，刚好 `nsjailcontainer` 自己依赖了 `ubuntu:18.04`。

# 第二个坑

然后我接着按照手册所示，下载预编译的 clang 编译器。

```sh
sudo git clone https://android.googlesource.com/platform/prebuilts/clang/host/linux-x86 /opt/
prebuilt-android-clang -b master
cd /opt/prebuilt-android-clang
sudo git checkout bceb7274dda5bb587a5473058bd9f52e678dde98
export CLANG_PATH=/opt/prebuilt-android-clang
```

然后等呀等呀，明明百兆的网速在全速运行（真的是全速，毫不夸张），可是一直没有尽头。于是我决定放弃，去网站下载了一个 `bceb7274dda5bb587a5473058bd9f52e678dde98` 的压缩包，好家伙，1G 多，可以想象整个仓库（都是预编译的二进制文件）有多大。怪不得文档要求至少需要 450G 的硬盘空间（实际我最终使用了 250G 左右）。

# 第三个坑

配置好了环境，终于可以编译了。编译也不是一帆风顺，经常编译一会儿就会提示 `xxx not found`。最后经过我一点一点地试错，还需要以下的软件包：

```sh
python3 bc cpio rsync unzip zip wget
```

保险起见，我还加上了 `build-essential`。上面提到的包好多在 Ubuntu 18.04 应该是有的，不知道为什么 Docker 版本的没有。

PS：上面讲的都是基于 NXP 的手册。Google 官方[^4]建议安装下面这些包

```sh
sudo apt-get install git-core gnupg flex bison build-essential zip curl zlib1g-dev gcc-multilib g++-multilib libc6-dev-i386 libncurses5 lib32ncurses5-dev x11proto-core-dev libx11-dev lib32z1-dev libgl1-mesa-dev libxml2-utils xsltproc unzip fontconfig
```


标题图片来自 <https://github.com/MobileDevOps/android-sdk-image>，作者是 messeb。

[^1]: https://www.nxp.com/design/development-boards/i-mx-evaluation-and-development-boards/i-mx-8quadxplus-multisensory-enablement-kit-mek:MCIMX8QXP-CPU
[^2]: https://hub.docker.com/_/ubuntu
[^3]: https://groups.google.com/g/android-building/c/2L2xbuG5Q8k
[^4]: https://source.android.com/setup/build/initializing
