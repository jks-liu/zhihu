---
title: markdown-it源码分析及插件编写：render（2/3）
zhihu-url: https://zhuanlan.zhihu.com/p/401550182
zhihu-title-image: pics/wpls-introduction.png
zhihu-tags: Markdown 编辑器, Markdown语法, Markdown
---


1. [markdown-it 源码分析及插件编写：parse 和 token（1/3）](https://zhuanlan.zhihu.com/p/400036665)
2. markdown-it 源码分析及插件编写：render（2/3）《==本文
3. [markdown-it 源码分析及插件编写：Plugin 插件编写（3/3）](https://zhuanlan.zhihu.com/p/437391859)

下面我本来讲 render 的部分。核心部分很短，我不妨全部列在下面（lib\renderer.js 的最后）

```js
Renderer.prototype.render = function (tokens, options, env) {
  var i,
    len,
    type,
    result = "",
    rules = this.rules;

  for (i = 0, len = tokens.length; i < len; i++) {
    type = tokens[i].type;

    if (type === "inline") {
      result += this.renderInline(tokens[i].children, options, env);
    } else if (typeof rules[type] !== "undefined") {
      result += rules[tokens[i].type](tokens, i, options, env, this);
    } else {
      result += this.renderToken(tokens, i, options, env);
    }
  }

  return result;
};
```

可以看到，对于每一个 token，我们根据其类型做相应的处理。处理的结果就是普通的字符串（HTML 文本），最后将所有的字符串拼接起来而已：`result += ...`。

从`for`循环中我们很容易的可以看出一共有三种类型。

1. 首先看是不是 inline 类型：`type === 'inline'`。前一篇文章我们提到，inline 类型是有子 token 的，所以需要特别处理。
2. 然后再看一个类型有没有特殊规则：`typeof rules[type] !== 'undefined'`。如果 rule 存在（即不为`undefined`）,则使用特定的规则。
3. 最后如果不是上述两种类型，则使用默认规则。还记得我们上一篇说过，token 中有个`tag`字段：对应 html 标签，如`<p>`，`<strong>`等。如果没有特别指定，`renderer.render`将使用这个`tag`直接生成对应的 html 文本。

# inline token 的渲染

inline 的渲染就很简单了，和上面讲的一样，仅仅是对子 token 进行了同样的操作（当然，不在判断是不是 inline 类型，因为 inline 不嵌套）：

1. 先看一个有没有特殊规则
2. 如果没有就执行默认规则（子 token 也是有`tag`字段的）

# 特殊规则

这里包括子 token 的特殊规则，完全相同。

特殊规则的存在有两个原因：

一是有一些块没有有意义的`tag`块，如上一篇所讲，`nesting` 有`-1`，`0`，`1`。`tag`只在`-1` 和 `1` 时有意义，`nesting` 为 `0` 时就要特殊处理，一般是直接输出转义后的HTML。

`nesting` 为 `0` 的 token 一般就是上一篇所讲的大部分 block 规则直接匹配的 token。注意 block 规则要支持嵌套，而 inline 的 type 却没有嵌套（也许如果可以嵌套的话，处理可以更加简单）。

另一个原因就是方便插件的编写，我们可以很简单地通过赋值一个规则，修改默认的渲染方式。

比如 [WPL/s 项目](https://github.com/jks-liu/WPL-s)中（一个在 VS Code 中用 Markdown 写知乎文章，回答问题的插件），就修改了表格的规则。

在标准 HTML 中，表格是这样的

```html
<table>
  <thead>
    <tr>
      <th>头左</th>
      <th>头右</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>数据左</td>
      <td>数据右</td>
    </tr>
  </tbody>
</table>
```

但是通过抓包，知乎的表格格式是这样的

```html
<table data-draft-node="block" data-draft-type="table" data-size="normal">
  <tbody>
    <tr>
      <th>头左</th>
      <th>头右</th>
    </tr>
    <tr>
      <td>数据左</td>
      <td>数据右</td>
    </tr>
  </tbody>
</table>
```

所以就覆写了如下规则：<https://github.com/jks-liu/WPL-s/commit/64a4d0b59a62f0f475237e10ece1eb52e3f02ef0>

```js
this.zhihuMdParser.renderer.rules.table_open = function(tokens, options, env) {
    return '<table data-draft-node="block" data-draft-type="table" data-size="normal"><tbody>';
}
this.zhihuMdParser.renderer.rules.table_close = function(tokens, options, env) {
    return '</tbody></table>';
}
this.zhihuMdParser.renderer.rules.thead_open = function(tokens, options, env) { return ''; }
this.zhihuMdParser.renderer.rules.thead_close = function(tokens, options, env) { return ''; }
this.zhihuMdParser.renderer.rules.tbody_open = function(tokens, options, env) { return ''; }
this.zhihuMdParser.renderer.rules.tbody_close = function(tokens, options, env) { return ''; }
```

我们通过上面的方法修改了某个非 inline token 的 render，但可以是 inline token 的子 token 的类型。

# 默认规则

默认规则就很简单了，根据`tag`字段生成对应的HTML，并添加对应的属性。
