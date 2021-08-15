#! https://zhuanlan.zhihu.com/p/400036665
# markdown-it源码分析及插件编写：parse和token（1/3）

[markdown-it](https://github.com/markdown-it/markdown-it)可能是最流行的 JavaScript Markdown 库，它的使用很简单，并支持插件。

但由于它的文档很是晦涩，想写一个插件也不知从何下手。所以这里只能使用最笨办法，读源代码。下面的内容希望能给编写插件的你带来一些启发。

# 使用 markdown-it


在解释源码之前，先来看一下 markdown-it 的用法。这样，你就会对 markdown-it 有一个大体的了解。

使用时可以直接调用 render 将 Markdown 转换成 HTML。也可以先调用 parse 将 Markdown 转换成 token，再调用 renderer.render 将 token 转换成 HTML。

![markdown-it使用流程](./pics/markdown-it-using-flow.png)

其实上面两个流程是一样的，`render`只是调用了`parse`和`renderer.render`而已。

为了清晰，这里把它们分开来讲。先讲解如何将markdown `parse`到 tokens，再讲解如何`render`tokens 到 HTML。

```js
// 步骤1. 导入markdown-it库
var MarkdownIt = require("markdown-it");
// 步骤2. 实例化，这一步可以传入相应的配置
md = new MarkdownIt();
// 步骤3. 将Markdown解析为token
t = md.parse("# xxx");
// 步骤4. 将token转换为HTML
md.renderer.render(t);
```

下面我们就开始深入源代码。建议读者在阅读下面内容之前，先试着使用一下，不至于下面的阅读云里雾里。强烈建议读者从上面的链接 clone 一份源码，并跟着下文一起阅读。

步骤 1 没什么好说的，我们从步骤 2 开始。

# 步骤 2. 实例化

实例化做的事情并不复杂，初始化了几个变量，再对 config 进行了处理。由于本部分对代码逻辑的理解没有太大影响，所以不做过多解释。下面是大致的框图：

![markdown-it实例化](./pics/markdown-it-instance.png)

# 步骤 3. 将 Markdown 解析为 token

## token 介绍

在分析具体的代码之前，我们不妨看看生成的 token 是什么样子。

例一
```md
我是一个普通句子。
```

这个例子 parse 完之后得到的是一个长度为 3 的 token，为了简洁，仅保留了关键内容，你可以在<https://markdown-it.github.io/>查看完整的 token 内容。查看 token，请点击右上角的 debug。

```js
[
  // token 1
  {
    type: "paragraph_open",
    tag: "p",
    map: [0, 1],
    nesting: 1,
  },
  // token 2
  {
    type: "inline",
    map: [0, 1],
    nesting: 0,
    children: [
      {
        type: "text",
        content: "我是一个普通句子。",
      },
    ],
    content: "我是一个普通句子。",
  },
  // token 3
  {
    type: "paragraph_close",
    tag: "p",
    nesting: -1,
  },
];
```

一头一尾很好理解。中间的token类型为`inline`，它包含一个`children`乘员，里面是子token。这里首先强调，我们可以认为子token和`inline`类型是绑定在一起的。子token的作用可以通过下面的例子理解。

例二
```md
我是一个**不普通**句子。
```

```js
[
  // token 1
  {
    "type": "paragraph_open",
  },
  // token 2
  {
    "type": "inline",
    // 下面的内容是子token
    "children": [
      {
        "type": "text",
        "content": "我是一个",
      },
      {
        "type": "strong_open",
        "tag": "strong",
        "nesting": 1,
        "markup": "**",
      },
      {
        "type": "text",
        "nesting": 0,
        "content": "不普通",
      },
      {
        "type": "strong_close",
        "tag": "strong",
        "nesting": -1,
        "markup": "**",
      },
      {
        "type": "text",
        "content": "句子。",
      }
    ],
    "content": "我是一个**不普通**句子。",
  },
  // token 3
  {
    "type": "paragraph_close",
  }
]
```

这里我们可以看到，由于有标记的存在，需要子token进行处理。所以，整个parse的框架大概是这样的：

1. 先识别出大的block，并生成最顶层的token，如上例有三个顶层token
2. 第二个token类型为`inline`，需要进一步处理为子token

上面两个步骤，就是parse的核心规则。

上面的token，我还保留了其它一些重要（对理解源码而言）字段，如`map`，`nesting`等。这里简单介绍，只望大家有个印象。

- `nesting`：嵌套级别，对应html就很好理解。Html标签有开有闭，开就对应1，闭对应-1，中间就是0.
- `map`：表示token对应的markdown文本的位置，分别是开始行（包括），结束行（不包括）。
- `tag`：对应html标签，如`<p>`，`<strong>`等。如果没有特别指定，renderer.render将使用这个tag直接生成对应的html文本。

## parse核心流程
parse调用是我们的重点。分为两步

1. 初始化state（`core.State`）
2. 调用`core.process`

![markdown-it parse的核心流程](./pics/markdown-it-parse-core-flow.png)

我们不妨看看这个两部走的模式。markdown-it库的好多地方都是类似这样的，先初始化一个state，用于保存状态信息，再进行具体的处理。但要注意，不同的地方它们的state也是完全不同的，除了名字。

对于`core.state`，我们只要知道token就保存在`core.state.tokens`中，tokens是一个Array。

`core.process`也是相当的简单，仅仅是应用了预定义的规则（规则列表在`lib/parser_core.js`中），这些规则就是重中之重。

下面我们介绍主要规则。除了下面的两个规则，其它规则不影响代码的理解，这里不做过多介绍，比如第一个规则是`normalize`，这个规则很简单，就是统一换行符（我们知道不同的操作系统，默认的换行符是不一样的），并且删除没用的空字符。

回忆上面说的parse的框架

    1. 先识别出大的block，并生成最顶层的token
    2. 对于类型为`inline`的token，需要进一步处理为子token

所以最主要的两个规则就是`block`规则和`inline`规则。

## `block`规则

### 1. block规则首先会初始化自己的State
注意parser_core, parser_inline, parser_block的State是不同的

- this.src保存了normalize之后的markdown全文
- this.lineMax保存了行数
- this.line初始化为0

在State中，保存了每一行的下列信息：

- bMarks：每一行开始的index（包括行首空格）
- eMarks：每一行行尾index（指向换行，最后一行可能没有换行符，那就指向最后一个字符）
- tShift：每一行行首的空白符数量，tab算一个，程序中位置跳转会用到
- sCount：每一行行首的空白符数量，tab展开，视位置算1~4个。分析markdown逻辑时需要用到

### 2. this.tokenize(state, state.line, state.lineMax);
tokenize会调用各个block规则（规则列表在`lib/parser_block.js`中），block规则按顺序匹配，如果一个匹配成功（返回true）就不再匹配下一个。

如果匹配成功：

- 更新state.line为匹配block的最后一行的后一行
- 往state push一个新token，并修改
  * content为整个block的内容
  * map为[开始行， 结束行下一行]

当block规则匹配完成后，我们可以确保所有的行都被包含在token之内，因为有paragraph规则托底。

如果希望token进一步使用inline规则，需要在push token的时候设置规则为inline。inline规则的结果会保存在children中。

## `inline`规则
这个规则和block规则是紧密练习在一起的。与block不同，`ParserBlock.prototype.parse`只调用了一次，而`ParserInline.prototype.parse`针对每个inline类型的token都调用了一次。同时我们注意到state与parse的调用是绑定在一起的，所以每个inline token都有自己独立的state。

整体而言，inline的parse和block差不多，都是先new一个state，再tokenize。但inline多了一个post process的过程，即应用ruler2。

### 1. 初始化state

- src：当前token的content
- pos：初始化为0
- posMax：src的长度

### 2. this.tokenize(state);
这个和block的流程几乎是一样的。

### 3. Post规则
`inline`和`block`不一样的地方在于`inline`多了post规则。根本原因是在解析inline本文时，很多标记是上下文相关的，如`**`。每一个合法的强调标记`**`必须是一对儿，而token是从前往后按顺序匹配规则的，所以需要这个post规则做后处理

# 结语

本系列的第一个部分到这里就结束了，但感觉还是有点乱的，后期还会继续完善，欢迎追更。

本系列还会再有两篇文章，分别讲述渲染（renderer）和插件编写，欢迎关注本专栏以待后续更新。