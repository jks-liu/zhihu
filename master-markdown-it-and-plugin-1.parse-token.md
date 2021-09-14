---
title: markdown-it源码分析及插件编写：parse和token（1/3）
zhihu-url: https://zhuanlan.zhihu.com/p/400036665
zhihu-title-image: pics/wpls-introduction.png
---

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
注意这个规则定义在`rules_core/block`中，它会调用`parser_block`。

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
  * map为[开始行， 结束行下一行]，遵循惯例是一个左闭右开区间

当block规则匹配完成后，我们可以确保所有的行都被包含在token之内，因为有paragraph规则托底。

如果希望token进一步使用inline规则，需要在push token的时候设置规则为inline。inline规则的结果会保存在children中。

### 嵌套 block 的处理

上面我们可以看到，block是挨个匹配的，如果一个block里面有另一个block怎么办呢？
比如下面的，在list block中有一个代码（markdown-it里称其为fence）

```md
- ```js
  var a
  ```
```

在parse_block.js中查看其规则：

```js
 [ 'fence',      require('./rules_block/fence'),      [ 'paragraph', 'reference', 'blockquote', 'list' ] ],
```

我们可以看到，规则的最后是个`list`，我们称其为`alt`。上面那一行规则的意思就是：一个名为`'fence'`的规则，其定义在`require('./rules_block/fence')`中，它可以嵌套在规则`'paragraph'`，`'reference'`，`'blockquote'`和`'list'`中。

## `inline`规则
这个规则和block规则是紧密练习在一起的。与block不同，`ParserBlock.prototype.parse`只调用了一次，而`ParserInline.prototype.parse`针对每个inline类型的token都调用了一次。同时我们注意到state与parse的调用是绑定在一起的，所以每个inline token都有自己独立的state。

整体而言，inline的parse和block差不多，都是先new一个state，再tokenize。但inline多了一个post process的过程，即应用ruler2。

Inline 规则也有一个类似 block 的托底规则（`lib\rules_inline\state_inline.js`）,当向 state 中push 新的 token 时，会将当前未处理的（pending）的字符串作为文本（`text`）类型先push到 token 中。
```js
// Push new token to "stream".
// If pending text exists - flush it as text token
//
StateInline.prototype.push = function (type, tag, nesting) {
  if (this.pending) {
    this.pushPending();
  }
  ...
}
```

### 1. 初始化state

- src：当前token的content
- pos：初始化为0
- posMax：src的长度

### 2. this.tokenize(state);
这个和block的流程几乎是一样的。下面讲几个重点的规则：

#### Inline rule：text
第一个规则叫 **text**。text 规则的主要目的是为了加快 parse 的速度。还记得上面我们说过，block 的规则是一行一行匹配的，照此类推，inline 就是一个字符一个字符地匹配。但显然这样做的话会对速度有明显的影响。所以，这个规则的作用就是跳过普通字符，停留在特殊字符，然后在特殊字符的位置匹配其它规则，这也是这个规则排在第一个的原因。

这些特殊字符包括：
```md
!, ", #, $, %, &, ', (, ), *, +, ,, -, ., /, :, ;, <, =, >, ?, @, [, \, ], ^, _, `, {, |, }, or ~
```

其中，`{}$%@~+=:` 虽然没有被标准的 markdown 语法（[CommonMark](https://commonmark.org/)）用到，但它们也被当做特殊字符，以方便插件的开发。同样由于速度的原因，目前没有开放插件删减特殊字符的功能。

#### Inline rule：newline
这个规则就和他的名字一样，用于处理换行。这个规则很简单，就留给读者作为习题了。

#### Inline rule：escape
注意这个转义规则指的的Markdown自己的转义，和HTML的转义没有关系。

当反斜杠遇到下面字符时会转义：```\!"#$%&\'()*+,./:;<=>?@[]^_`{|}~-```。

反斜杠的另一个作用和换行有关。如果反斜杠后面紧跟一个换行符，会促发一个`'hardbreak'`。

其它字符前的反斜杠会原样输出。

知道了上面的标准，这个规则也就很简单了。

#### Inline rule：backticks
一般用作行内的代码`` `int a;` ``。由于这个规则没有嵌套其它规则，也没有转义，所以比较简单。

但是这个规则有一些奇奇怪怪的规定，比如：

![``` `a``b` ```](pics/markdown-it-backtick-corner-case-1.png)

![``` `a``b`` ```](pics/markdown-it-backtick-corner-case-1.png)

为了实现上面的corner case，里面有些比较啰嗦的东西，大家无需纠结。关于这个奇奇怪怪的规则，我们在后面会详细讲解。

#### Inline rule：~~strike through~~
匹配到`~~`的时候，先push一个类型是`text`的token，再将`content`设置为`~~`。然后还push了一个delimiter，包含以下字段

```json
marker: marker, // 标记符号，这里就是~
length: 0,     // disable "rule of 3" length checks meant for emphasis
jump:   i / 2, // for `~~` 1 marker = 2 characters，一般情况下就是0
token:  state.tokens.length - 1, // 对应token的索引
end:    -1, // 假如这是个开标记的话，用于balance pair这个post规则存储对应的闭标记索引，见下文
open:   scanned.can_open, // 见下面的解释
close:  scanned.can_close // 见下面的解释
```

根据规定，`~~`需要紧连着文本。如`~~a~~`是有效的标记。`~~ a~~`和`~~a ~~`就都是无效的标记，其中前者`can_open`为false，后者`can_close`为false。所以`~~a ~~ d~~`会被渲染为：![`~~a ~~ d~~`](pics/markdown-it-strike-through-1.png)。

同时要注意的是，在tokenize阶段，不会对标记的开闭进行匹配。

虽然没有每个规则都讲一遍，但上面这些规则几乎已经涵盖了方方面面的内容了。其余的规则读者有空可以自己研究。

### 3. Post规则
`inline`和`block`不一样的地方在于`inline`多了post规则。根本原因是在解析inline本文时，很多标记是上下文相关的，如`**`。每一个合法的强调标记`**`必须是一对儿，而token是从前往后按顺序匹配规则的，所以需要这个post规则做后处理。

所以 post 规则最关键的一个规则就是给各种标记配对。上面的 tokenize 阶段，已经把所有的标记都给匹配了，但是还没有给每个标记正确地左右配对。

#### 标记配对

简单介绍以下CommonMark，Markdown有很多的实现，每个实现的细节都有细微的不同。所以一些人试图对其进行标准化，CommonMark便是其中的一个使用比较广泛的标准。Markdown-It也遵循CommonMark标准。其它采纳CommonMark的实体包括：GitHub，Qt，Stack Overflow等等。比如GitHub Flavored Markdown (GFM)是CommonMark的[超集](https://github.blog/2017-03-14-a-formal-spec-for-github-markdown/)。

这里我们不妨把inline规则暂且放一放，来看看标记的开闭是如何匹配的。

这个规则叫做balance pair，属于post 规则，是post规则的第一个规则。Post规则在所有的inline规则执行后才执行。

为了讲解这个规则，需要介绍一个CommonMark中的一个规划：「三的规则（rule of 3）」。CommonMark一个Markdown标准化的实践，「三的规则」定义在当前规范（v0.30）的6.2小结《Emphasis and strong emphasis 》的规则9和10中。

> 9. Emphasis begins with a delimiter that can open emphasis and ends with a delimiter that can close emphasis, and that uses the same character (_ or *) as the opening delimiter. The opening and closing delimiters must belong to separate delimiter runs. If one of the delimiters can both open and close emphasis, then the sum of the lengths of the delimiter runs containing the opening and closing delimiters must not be a multiple of 3 unless both lengths are multiples of 3.

10和9类似，只是把Emphasis 改成了Strong emphasis 。这段话还是比较晦涩的，我通过一个官方的例子进行讲解。

在`*foo**bar**baz*`中可以有以下两种解释方法，

1. 三个单独的`*foo*`，`*bar*`，`*baz*`。
2. 就一个`*xxx*`，其中xxx是`foo**bar**baz`。当然中间还有一个嵌套的`**bar**`。

显然，这就有歧义了。CommonMark标准更偏向于第二种，即Strong emphasis被嵌套在Emphasis 之中，于是便有了上面的规则。我们继续看这个例子是如何排除第一中情况的。在第一种情况中，`*foo*`的开标记（左边的星号）所属的组（即delimiter runs）是它自己，即`*`，而闭标记（右边的星号）的delimiter runs是`**`。它们的长度加起来就是3，规则9的规定就是这个长度不能是三的倍数（除非开闭标记的长度都是三的倍数），从而排除了第一种情况。

当然还是建议大家写Markdown的时候还是不要依赖这些奇奇怪怪的规则为好，毕竟我们使用Markdown的初衷就是简洁，勿忘初心。


到了这里，标记配对所作的工作就很好理解了，就是为每一个开标记找到对应的闭标记，保存index在上面讲到的`end`字段中。源代码由于上面乱七八糟规则的原因同样是优点晦涩，大家看的时候也不用纠结。

#### Inline rule：~~strike through~~ 续

我们再回到strike through这个规则，继续讲解与之对应的post规则。上面我们说到，balance pair帮我们匹配好了对应的开闭标记，strike through的post规则就把对应的token的类型改成了`s_open`和`s_close`，回顾前面，原先我们push的token的类型都是`text`。

理解了上面这些规则，其它的规则就很好理解了，都是类似的，就不再重复分析了。

# 结语

本系列的第一个部分到这里就结束了，但感觉还是有点乱的，后期还会继续完善，欢迎追更。

本系列还会再有两篇文章，分别讲述渲染（renderer）和插件编写，欢迎关注本专栏以待后续更新。
