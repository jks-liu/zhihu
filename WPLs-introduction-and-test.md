#! https://zhuanlan.zhihu.com/p/390528313

![Along the River During the Qingming Festival](pics/Along-the-River-During-the-Qingming-Festival.jpg)

# VS Code插件WPL/s介绍及测试

注：本插件尚在开发中，尚未发布，敬请期待。20210718-4

WPL/s是一个在VS Code中发布知乎文章/回答的插件。

# 插件特色功能

## 测试01：题图
如支持，应该可以在标题上面看到清明上河图。


# Markdown功能测试

## 测试01：六级标题

### 三级标题
#### 四级标题
##### 五级标题
###### 六级标题

## 测试02：分割线

---

## 测试03：引用
> 引用

## 测试04：链接
[链接](http://www.baidu.com)

## 测试05：图片
![图片](pics/Along-the-River-During-the-Qingming-Festival.jpg)

## 测试06：表格
| 左边 | 右边 |
| --- | --- |
| 左边 | 右边 |
| 左边 | 右边 |


颜色|颜色名称|颜色值
:--:|:--:|:--:
#FF0000|红色|#FF0000
#00FF00|绿色|#00FF00
#0000FF|蓝色|#0000FF
#FFFF00|黄色|#FFFF00
#FF00FF|粉红色|#FF00FF
#00FFFF|青色|#00FFFF
#000000|黑色|#000000
#800000|红红红色|#800000
#808080|灰色|#808080
#808000|绿绿绿色|#808000
#800080|紫色|#800080
#C0C0C0|灰灰灰色|#C0C0C0
#008080|蓝蓝蓝色|#008080
#FFFFFF|白色|#FFFFFF
#F0F0F0|灰灰灰灰灰灰灰色|#F0F0F0
#FF00FF|粉色|#FF00FF
#00FFFF|青色|#00FFFF

## 测试07：公式
行内公式：$\alpha = \beta$

行间公式：
$$
\alpha = \beta
$$

## 测试08：代码
行内代码：`var a = 1;`。

行间代码：

```py
print("Hello, World!")
```

## 测试09：**加粗**， *斜体*， ~~删除线~~
**加粗**， *斜体*， ~~删除线~~，_斜体_，__加粗__，_斜体组合**加粗**_，__加粗组合*斜体*__

## 测试10：列表
* 第一项
* 第二项

1. 第一项
2. 第二项

* 嵌套
    1. 嵌套  
    换行

## 测试11：参考文献
这里[^1]你可以找到本文的Markdown原文。

## 测试12：任务列表
- [ ] 未完成的任务
- [x] 已完成的任务

## 测试13：Emoji表情
:+1: :smile: :heart_eyes: :sweat_smile: :joy: :sad: :wink: :cry: :disappointed: :sweat: :pensive: :confused: :heart: :relaxed: :blush: :grin: :unamused: :sob: :joy_cat: :heart_eyes_cat: :smirk_cat: :scream_cat :speak_no_evil: :see_no_evil:


[^1]: https://github.com/jks-liu/zhihu/blob/master/WPLs-introduction-and-test.md
