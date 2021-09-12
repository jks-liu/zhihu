---
zhihu-url-1: https://www.zhihu.com/answer/2104845334
zhihu-url: https://www.zhihu.com/answer/2104853089
---
推荐一个 VS Code 插件：WPL/s，可以使用 Markdown 发布知乎文章，回答问题。支持几乎所有的知乎支持的编辑格式（包括参考文献，表格，任务列表，公式等等）。

测试使用[这个 Markdown 文件](https://github.com/jks-liu/zhihu/blob/master/WPLs-introduction-and-test.md)，测试结果可以查看[这篇知乎专栏文章](https://zhuanlan.zhihu.com/p/390528313)。

WPL/s 是一个在 VS Code 中发布知乎文章/回答的插件。在 VS Code 中搜索 `zhihu` ，安装即可，如下图。

![在VS Code中搜索`zhihu`](../../pics/vs-code-extension-search-zhihu.png)

| Markdown基础功能 | 支持与否 |
| :--- | :--- |
| 标题 | :heavy_check_mark: *1 |
| 分割线 | :heavy_check_mark: |
| 引用 | :heavy_check_mark: |
| 链接 | :heavy_check_mark: |
| 图片 | :heavy_check_mark: |
| 表格 | :heavy_check_mark: *2 |
| 公式 | :heavy_check_mark: |
| 代码块 | :heavy_check_mark: |
| 加粗 | :heavy_check_mark: |
| 斜体 | :heavy_check_mark: |
| 加粗斜体嵌套 | :heavy_check_mark: |
| 删除线 | :x: *3 |
| 列表 | :heavy_check_mark: |
| 参考文献 | :heavy_check_mark: *4 |

| 其它特色功能 | 支持与否 |
| :--- | :--- |
| 元数据 | :heavy_check_mark: *4 |
| 目录 | :x: *0 |
| 章节标题自动编号 | :x: *0 |
| Emoji表情 | :heavy_check_mark: *5 |
| 任务列表 | :heavy_check_mark: |


| 知乎特色功能 | 支持与否 |
| --- | --- |
| 回答问题 | :heavy_check_mark: |
| 发布文章 | :heavy_check_mark: |
| 题图 | :heavy_check_mark: |
| 链接卡片 | :x: *0 |
| 视频 | :x: |
| 好物推荐 | :x: |
| 附件 | :x: |
| 标签 | :x: *0 |
| 草稿 | :x: |
| 赞赏 | :x: |
| 追更 | :x: |

（0）打算近期支持，star，点赞，收藏，一键三连给我动力呀

1. 最多可支持4级标题
2. 表格暂时不支持对齐
3. 知乎本身不支持，请大家踊跃向[知乎小管家](https://www.zhihu.com/people/zhihuadmin)提意见
4. 格式见下一小节
5. 支持大部分Emoji（很多emoji刚发的时候可以看到，但一段时间过后就会被知乎过滤掉），具体列表请查看上面的链接。

# 部分格式提醒

最直接的方法是参考[上面提到的 Markdown 测试文件](https://github.com/jks-liu/zhihu/blob/master/WPLs-introduction-and-test.md)。

## [Jekyll 元数据](https://jekyllrb.com/docs/front-matter/)
目前仅支持如下元数据：
```md
---
title: 请输入标题（若是回答的话，请删除本行）
zhihu-url: 请输入知乎链接（删除本行发表新的知乎专栏文章）
zhihu-title-image: 请输入专栏文章题图（若无需题图，删除本行）
注意: 所有的冒号是半角冒号，冒号后面有一个半角空格
---
```

## 参考文献
```md
   用[^n]来引用。

[^n]: https://网址.com 说明文字

注意字符 ^ 不能少。冒号后面有一个空格。网址中不能有空格。网址和说明文字之间有一个空格，说明文字自己可以有空格。
```
