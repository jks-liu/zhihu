# 使用C++20协程（Coroutine）实现线程池

[C++20的协程](https://en.cppreference.com/w/cpp/language/coroutines)出来了也有好一段时间了，不过说实话，那几个关键字的语义过于复杂了，基础设施严重不足呀。

废话不多说，下面就用协程来实现一个线程池吧。

本文分为两个部分：第一部分是协程的简明教程，第二部分是使用协程实现一个thread pool。已经熟悉协程的朋友可以跳过第一部分。

# 一、C++20协程

## 协程定义

> 一个事物没有定义，那便失去了灵魂。
> .....................................................—— 鲁迅

协程是一个**函数**，是一个可以暂停（**suspend**）和恢复（**resume**）的函数。

从C++语法的角度来讲，协程是包含下面三个关键字中一个或多个的函数。

- `co_await`
- `co_yield`
- `co_return`

例，下面的函数是一个协程

```c++
int add1(x)
{
    co_return x+1
}
```

## 协程的其它重要概念

协程总是和下面三个东东相关联：

- Promise对象：用于返回结果，或异常，需要我们自己定义
- 协程handle：[`std::coroutine_handle`](https://en.cppreference.com/w/cpp/coroutine/coroutine_handle)，我们通过这个handle来**resume**或**destroy**这个协程
- 协程状态：我们把它交给编译器，暂时无需考虑

另外还有一个很重要的概念是`Awaitable`对象。

上面的这些概念，我们会一个一个地讲解。

## Promise对象

Promise对象的类型是编译器根据协程自动推导出来的。一种简单的情况如下：

```c++
struct my_return_t{
  struct promise_type {
      // ......
  };
};

my_return_t my_coro(x)
{
    co_yield 1
}
```

上面这个例子中，协程`my_coro`的Promise对象的类型就是`my_return_t::promise_type`。即如果一个协程的返回类型是`R`，那么它的Promise类型就是`R::promise_type`。

当然上面只是一种常用的情形，更复杂的比如上面的`int add1(x)`协程，根本不存在`int::promise_type`。这个这里暂时就不介绍了，喜欢刨根问底的亲们可以参考[`std::coroutine_traits`](https://en.cppreference.com/w/cpp/coroutine/coroutine_traits)。

更进一步，`promise_type`需要定义如下函数：

```c++
struct my_return_t{
  struct promise_type {
    my_return_t get_return_object();
    awaitable initial_suspend();
    awaitable final_suspend() noexcept;
    void return_void();
    awaitable return_value(some_type);
    awaitable yield_value(some_type);
    void unhandled_exception();
  };
};
```

注意`return_void`和`return_value`不会同时存在。关于awaitable见下一小节，其余函数的意义，后面再讲解。

## Awaitable对象

可以Awaitable理解成一个类，名字不重要，但必须定义了以下三个函数：

```c++
struct my_awaitable_t {
    bool await_ready();
    void await_suspend(std::coroutine_handle<> h);
    void await_resume();
};
```

注意上面的函数可能会有不同的返回值类型，我们先忽略这个问题。

本文又是也将Awaitable对象称为awaiter，大家自行联系上下文。

## 协程handle

我们注意到上一节的`await_suspend`函数，其参数是`std::coroutine_handle<> h`，这便是协程handle了。如上所说，通过它可以实现两个重要的操作：恢复/销毁一个协程。

```c++
h.resume();
h.destroy();
h(); // 等同于h.resume();
```

## `co_await`

有了上面的讲解，我们到了协程的核心部分，`co_await`操作符。它的作用是**暂停当前协程，并将控制权交给调用者（Caller）或恢复者（Resumer）**。

语法：`co_await expr`

第一步，`expr`会通过某种规则转换为awaitable对象，或者简单一点说，`co_await`后接一个awaitable对象：`co_await awaitable`。

我们知道Awaitable对象包含三个函数，我们正式通过这三个函数来控制协程的交互。

我们以下面这个例子介绍`co_await`如何执行

```c++
auto x = co_await awaitable
```

- 执行`awaitable.await_ready()`，这个函数通常返回`false`，表示`co_await`还没有准备好计算一个值给`x`，所以协程会暂停并准备准备交出控制权；
- 在交出控制权之前会执行`awaitable.await_suspend(handle)`，这个函数会将协程handle保存在某个地方，以便后续的恢复或销毁。简便起见，`await_suspend`函数返回`void`（对其它返回值感兴趣的亲们可以参考[这里](https://zh.cppreference.com/w/cpp/language/coroutines)）
- 返回控制权给调用者或回复者

~~然后~~，如果在其它地方有人调用了`handle.resume()`，那么这个协程就又被恢复了，被恢复的协程立刻执行以下操作：

- 执行`awaitable.await_resume()`
- 将`await_resume()`的返回值赋值给`x`

自此，`auto x = co_await awaitable`就算执行完毕。

那如果`awaitable.await_ready()`返回`true`呢？那就更简单了，说明`c0_await`已经准备好了，直接执行`awaitable.await_resume()`并赋值给`x`，就不暂停了。

**注意**：有时候`handle.resume()`在`awaitable.await_suspend(handle)`返回前就被执行了，比如你在`await_suspend`中开了一个线程来执行`resume()`。如果你有类似的操作，那你就要注意。这意味着有一定的可能性`auto x = co_await awaitable`已经（在另一个上下文中）执行完毕，而你的`await_suspend`还没有返回，此时，`awaitable`临时对象可能已经被销毁，那么`awaitable.await_suspend`就不能安全地访问`this`指针。这条注意要多看几遍，可能你第一次看的时候会觉得看不懂，只要你看懂了，你的协程知识就算入门了。

## 协程的执行

了解了上面的Promise和Awaitable之后，就可以一探协程的执行了。

```c++
my_return_t my_coro()
{
    co_await my_awaitable_t()
}
```

下面我只列出`my_coro`执行的关键步骤
 - 以类型`my_return_t::promise_type`构造`promise`对象
 - 由于我们的协程返回一个`my_return_t`的对象，所以调用`promise.get_return_object`生成一个。
 - 执行`co_await promise.initial_suspend()`
