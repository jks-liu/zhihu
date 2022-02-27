---
title: 也许 VS Code 才是最好的 TeX IDE - 附模板
zhihu-title-image: ../pics/1024px-XeTeX_Logo.svg.png
图片信息: https://upload.wikimedia.org/wikipedia/commons/thumb/9/9f/XeTeX_Logo.svg/1024px-XeTeX_Logo.svg.png 公有领域
zhihu-tags: TeX, XeTeX, XeLaTeX
zhihu-url: https://zhuanlan.zhihu.com/p/448709781
---

最近试着用 VS Code 编写一个 $\TeX$  文档，发现它几乎可以实现所见即所得的编辑。由于据说 XeLaTeX 对 Unicode （中文）支持较好，所以决定试试。 

我使用的环境是 WSL/Ubuntu，通过下面的命令安装的 $\TeX$。

```sh
$ sudo apt install texlive
```

然后在 VS Code 安装 「LaTeX Workshop」插件。[![zhihu-link-card: LaTeX Workshop - James Yu](https://james-yu.gallerycdn.vsassets.io/extensions/james-yu/latex-workshop/8.22.0/1636984769378/Microsoft.VisualStudio.Services.Icons.Default)](https://marketplace.visualstudio.com/items?itemName=James-Yu.latex-workshop)

然后新建一个 TeX 文件，在开头加上如下的 `magic comments`

```tex
%!TeX encoding = utf8
%!TEX TS-program = xelatex
```


然后继续编写文档，文档保存时就会自动编译，点击预览按钮还能实时预览。

下面是一个支持中文的最小模板

```tex
%!TeX encoding = utf8
%!TEX TS-program = xelatex

\documentclass{article}
\usepackage{ctex}

\begin{document}
默认是宋体；\textsf{衬线字体显示为黑体}；\texttt{等宽字体显示为仿宋}。
\end{document}
```

---

**2022年2月5日更新**

由于安全原因，`magic comments` 在最新的 `LaTeX Workshop` 插件中已默认关闭，详见 [#3027](https://github.com/James-Yu/LaTeX-Workshop/issues/3027)。如果你需要这个功能，请按照如下设置手动打开。

```json
latex-workshop.latex.build.forceRecipeUsage: false
```

