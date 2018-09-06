# 第 3 章 产生器 Generator

从版本 2.5 开始，Python 就已经通过关键字 `yield` 支持产生器（Generator）功能了。但在 Python 2.2 中，须要从 `__future__` 中引入 `generators`（即 `from __future__ import generators`），然后才可以使用产生器功能。

> Generator 可以翻译成 **产生器**，也可以翻译成 **生成器**，后文我们使用产生器作为其中文翻译。

注意，产生器是一种延迟计算，即只有在调用时才真正地计算值，而且调用一次，计算一次，不调用，不计算。


## 3.1 定义

首先产生器是一个函数，因此，定义一个产生器的方式和定义一个函数相同，而且定义函数的约束条件也适用于定义产生器。

其次，在定义函数时，只要函数体中包含 `yield` 关键字，这个函数就不再是一个普通函数，而是一个产生器函数。

从上我们可以得出，产生器就是一个函数体中包含了 `yield` 关键字的普通函数。

我们来看一个示例：

```python
>>> def generator(*args):
...     for arg in args:
...         yield arg
...         print(arg)
...
>>> print(type(generator))
<class 'function'>
>>> g = generator(1, 2, 3)
>>> print(type(g))
<class 'generator'>
>>> hasattr(g, '__iter__')
True
>>> hasattr(g, '__next__')
True
```

函数 `func` 原本就是一个普通函数，其类型也是 `<function>`，但是它其中包含了 `yield` 关键字，因此，它变成了产生器函数。尽管它是产生器函数，但仍然本质上还是一个函数，正如上述示例中展示的一样，`func` 的类型是个函数类型。

当我们调用产生器函数时，它将返回一个具体地产生器实例对象（对象 `f` 是一个 `<generator>` 类型的实例）给调用者，而且该实例对象实现了迭代器协议（方法中包含 `__iter__` 和 `__next__`），可以用在任何可以使用迭代器的地方。

因此，产生器的使用可分为三步：
1. 通过 `yield` 关键字定义一个产生器函数。
2. 调用产生器函数以便得到一个产生器对象（它实现了迭代器协议）。
3. 调用产生器对象上的方法（如迭代器协议的方法 `__next__`）。

## 3.2 `yield` 语句和 `yield` 表达式

`yield` 关键字即可以用作语句（即 `yield` 语句），也可以用作表达式（即 `yield` 表达式）。其二者在语义和功能是上相同的，但在使用上几乎是相同的、略有不同。

我们知道，语句是不能被嵌套的，即一个语句不能包含另外一个语句；一个语句必须是完整的，类似于一句完整的话。然而，表达式是可以被嵌套的，即一个表达式可以包含另外一个表达式，而且一个表达式也可以包含在一个语句中。因此，对于 `yield` 语句，它不能用于其它语句中，而 `yield` 表达式可以用于其他语句（如赋值语句）中，甚至是另外一个 `yield` 表达式或语句中。

### 3.2.1 `yield` 表达式

`yield` 表达式须要用一对圆括号（`()`）括起来，且它有三种语法形式：
1. `(yield)`
2. `(yield <expr1>[, <expr2>, ...])`
3. `(yield from <expr>)`

对于第一种情况，它等同于第二种，只不过它假定 `yield` 关键字后面的 `<expr1>` 为 `None`。所以，`yield` 表达式也可以看作有两种：带 `from` 和 不带 `from`。后文介绍时，我们不再单独介绍第一种形式，而把它归到第二种形式中（把它当作其特例来对待即可）；另外，我们假定不带 `from` 的语法形式为第一种，带 `from` 的语法形式为第二种。

对于第一种语法形式，`yield` 后面可以只跟一个表达式，也可以跟用逗号分隔的一组表达式，Python 会将它们当成一个元组对待。如：`yield 123` 返回的值就是整数值 `123`，而 `yield 123, 456, 789` 返回的值就是元组 `(123, 456, 789)`。不管是单个值，还是一个元组，一个 `yield` 表达式一次只能返回一个值，即其后的所有表达式值都被当作是一个普通值来对待。

对于第二种语法形式，是从 Python 3.3 版本才开始支持的，与第一种语法不同，`yield from` 后面的表达式只能是单个表达式，不能是用逗号分隔的一组表达式。

第一种语法是第二种语法的基础，我们暂时先讲解第一种语法，后文我们会专门来讲解第二种语法。掌握了第一种语法，第二种语法也就很好理解了。

### 3.2.2 `yield` 语句

相比于 `yield` 表达式，`yield` 语句的语法形式就简单地多了；它就只有一种形式，即 `<yeild_expr>`。也就是说，`yield` 表达式本身就可以单独成为一个语句；如果 `yield` 表达式没有被用于其它语句中，那么它将自成一个语句，即是 `yield` 语句。

在当作 `yield` 语句使用时，`yield` 表达式两边的圆括号是可以省略。注意，省略是可选的，但不是必须的。

在赋值语句中，如果 `yield` 表达式是等号右边唯一的表达式，那么，其两边的圆括号也是可以省略的；否则，是不可以省略的。

因此，我们可以得出，
1. `yield 123` 和 `(yield 123)` 既可以作为 `yield` 表达式，也可以作为 `yield` 语句。
2. `value = (yield 123)` 和 `value = yield 123` 是等效的，且其中的 `yield` 是 `yield` 表达式，而不是 `yield` 语句。
3. 在非赋值语句中使用 `yield` 表达式，必须使用圆括号引起来，如 `return (yield 123)`。

```python
>>> def gen1(*args):
...     (yield args)
...
>>> def gen2(*args):
...     yield args
...
>>> def gen3(*args):
...     v = (yield args)
...
>>> def gen4(*args):
...     v = yield args
...
>>> def gen5(*args):
...     return (yield args)
...
>>> g1 = gen1(1)
>>> g2 = gen2(2)
>>> g3 = gen3(3)
>>> g4 = gen4(4)
>>> g5 = gen5(5)
>>> next(g1)
(1,)
>>> next(g2)
(2,)
>>> next(g3)
(3,)
>>> next(g4)
(4,)
>>> next(g5)
(5,)
>>> def gen6(*args):
...     return yield args
  File "<stdin>", line 2
    return yield args
               ^
SyntaxError: invalid syntax
```


## 3.3 产生器对象

产生器对象有四个主要方法：`__next__()`、`send(value)`、`throw(type[, value[, traceback]])` 和 `close()`。

在 Python 2 中，使用 `next()` 而不是 `__next__()` 来返回下一个迭代值。它们仅仅是名字不同，其它的都是一样的。

> 在 Python 2 中，迭代器协议使用 `next()` 方法来获取下一个值。然而，根据 Python 规定，Python 实现的内部协议方法名一般是名字前后各有双下划线。迭代器协议是 Python 实现的内部协议之一，因此，使用 `next()` 这个方法名不是特别规范的。为了更加符合规范，Python 3 将 `next()` 方法改为了 `__next__()` 方法。下面的讲解中，我们统一使用 `__next__()` 这个方法名。

产生器实例对象控制着产生器函数的执行；当它的任何一个方法被调用的时候，函数体的执行流程将被启动，直到第一次遇到 `yield` 表达式的地方，执行 `yield` 表达式并把 `yield` 关键字后面的表达式的值返回给产生器对象的调用者，然后执行流程被暂停。注意：此时的 `yield` 表达式刚被执行完毕，但其所在语句还没有执行完毕。此后，如果产生器对象的方法又被调用，则从上次暂停的地方继续执行，并重复上述动作。

当产生器被暂停时，其内部状态也将会被冻结，即所有的本地状态都会被保留，包括本地变量的当前绑定、指令指针、内部的计算栈：足够的信息会被保存，以便产生器下一次被激活时重新执行。

如果产生器函数体执行完函数的最后一个语句，或者遇到 `return` 语句，产生器函数将执行结束，并抛出 `StopIteration` 异常，且会把返回值作为 `StopIteration` 异常的参数；如果没有 `return` 语句，其参数就是 `None`。比如：

```python
>>> def generator(*args):
...     for arg in args:
...         yield arg
...     return args
...
>>> g = generator(1, 2, 3)
>>> next(g)
1
>>> next(g)
2
>>> next(g)
3
>>> next(g)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
StopIteration: (1, 2, 3)
```

对于一个已经执行结束的产生器对象，后续对方法 `__next__()` 和 `send(value)` 的调用，都将抛出 `StopIteration` 异常。比如：

```python
>>> def generator(*args):
...     for arg in args:
...         yield arg
...
>>> g = generator(1, 2, 3)
>>> next(g)
1
>>> next(g)
2
>>> next(g)
3
>>> next(g)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
StopIteration
>>> g.send(4)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
StopIteration
```

如果在产生器函数中抛出任何异常，它都将会被传播给产生器对象的调用者，并且导致产生器函数执行结束，后续对 `__next__()` 和 `send(value)` 方法的调用会导致抛出 `StopIteration` 异常。如：

```python
>>> def generator(*args):
...     yield args
...     raise ValueError(args)
...     yield args
...
>>> g = generator(1, 2, 3)
>>> next(g)
(1, 2, 3)
>>> next(g)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "<stdin>", line 3, in generator
ValueError: (1, 2, 3)
>>> next(g)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
StopIteration
```

### 3.3.1 `__next__` 方法

开始执行产生器函数，或者从上次暂停的 `yield` 表达式处继续执行函数体代码，直到遇到下一个 `yield` 表达式，此时产生器函数再次被暂停，并将 `yield` 关键字后面的表达式的值返回给 `__next__()` 方法的调用者。

**当调用 `__next__()` 方法重新执行产生器函数时，当前的 `yield` 表达式的值总是计算为 `None`**。注意，这里有两个 **表达式的值**：一个 `yield` 表达式的值，另一个是 `yield` 关键字后面的表达式的值。比如：对于 `yield 1 + 2`，yield 表达式的值是 `None`，而 `yield` 关键字后面的表达式（即 `1 + 2`）的值却是 3，这个 3 是要返回给 `__next__()` 方法的调用者的。

```python
>>> def generator(*args):
...     for arg in args:
...         v = yield arg
...         print(v)
...
>>> g = generator(1, 2, 3)
>>> next(g)
1
>>> next(g)
None
2
```

### 3.3.2 `send` 方法

`send` 方法几乎等同于 `__next__` 方法，它除了拥有 `__next__` 方法的所有功能外，还可以向产生器对象传递外界的信息，即 `send` 不仅可以获取产生器中的下一个值，而且还可以把外界的信息传递到产生器内部。

`send` 方法有一个必选的参数，该参数即是向产生器内部传递的值（即作为 `yield` 表达式的值），它可以是任何值。如果此参数值为 `None`，它等同于 `__next__` 方法。换句话说就是，`__next__() == send(None)`。

```python
>>> def generator(*args):
...     for arg in args:
...         v = yield arg
...         print(v)
...
>>> g1 = generator(1, 2, 3)
>>> g1.send(None)
1
>>> g1.send(None)
None
2
>>> g1.send(None)
None
3
>>> g1.send(None)
None
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
StopIteration
>>> g2 = generator(1, 2, 3)
>>> g2.send(None)
1
>>> g2.send('a')
a
2
>>> g2.send('b')
b
3
>>> g2.send('c')
c
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
StopIteration
```

虽然 `send(None)` 调用可以用来替换 `__next__()` 且可以向产生器内部传递信息值，但在第一次启动产生器对象执行流程时，如果使用 `send` 方法，其参数必须是 `None`，即必须以 `send(None)` 方式来调用。否则将抛出 `TypeError` 异常。比如：

```python
>>> def generator(*args):
...     for arg in args:
...         v = yield arg
...         print(v)
...
>>> g = generator(1, 2, 3)
>>> g.send('a')
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
TypeError: can't send non-None value to a just-started generator
```

之所以其参数必须是 `None`，主要是因为此时产生器对象刚被初始化，还没有启动执行流程（即产生器对象的暂停点不是 `yield` 表达式处），也就没有 `yield` 表达式能接收其参数。

注意，如果产生器函数内部不处理 `send` 方法发送的值，那么 `send` 方法就不会改变产生器函数的执行流程（即产生器函数生产的值及其顺序）。这时，具体是用 `send` 还是用 `__next__` 来获取生产器的下一个值，是没有什么区别的。

```python
>>> def generator(*args):
...     for arg in args:
...         yield arg
...
>>> g = generator(1, 2, 3)
>>> next(g)
1
>>> g.send(4)
2
>>> next(g)
3
>>> next(g)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
StopIteration
```

如果产生器函数内部处理了 `send` 发送给它的值，产生器的执行流程就有可能发生变化。比如：

```python
>>> def generator_int(*args):
...     i = 0
...     args = list(args)
...     for arg in args:
...         v = yield arg
...         i += 1
...         if v is not None:
...             if i % 2 == 0:
...                 args.append(v)
...             else:
...                 args.insert(i, v)
...
>>> g = generator_int(1, 2, 3)
>>> next(g)
1
>>> g.send(4)
4
>>> g.send(5)
2
>>> next(g)
3
>>> next(g)
5
>>> next(g)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
StopIteration
```

### 3.3.3 `throw` 方法

`throw` 方法几乎等同于 `__next__` 方法，它除了拥有 `__next__` 方法的所有功能外，还可以引发产生器函数在其内部暂停处抛出一个指定的异常，就像产生器内部本身抛出的异常一样。因此，如果产生器函数内部没有处理该异常，它将传播给 `throw` 方法的调用者。比如：

```python
>>> def generator1(*args):
...     for arg in args:
...         yield arg
...
>>> g1 = generator(1, 2, 3)
>>> next(g1)
1
>>> g1.throw(ValueError, ValueError('value error'))
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "<stdin>", line 3, in generator1
ValueError: value error
>>> def generator2(*args):
...     for arg in args:
...         try:
...             yield arg
...         except ValueError as err:
...             print(err)
...
>>> g2 = generator2(1, 2, 3)
>>> next(g2)
1
>>> g2.throw(ValueError, ValueError('value error'))
value error
2
```

注意，`throw` 方法必须在调用过 `__next__()` 或 `send(None)` 方法之后才能被调用，因为此时产生器对象被暂停在开始处，还没有被启动，根本就无法在产生器函数内部捕获这个异常，从而它被传播到 `throw` 方法的调用者处，就相当于在本地抛出一个异常一样。比如：

```python
>>> def generator(*args):
...     for arg in args:
...         try:
...             yield arg
...         except Exception as err:
...             print(err)
...
>>> g1 = generator(1, 2, 3)
>>> next(g1)
1
>>> g1.throw(ValueError, ValueError('value error'))
value error
2
>>> g2 = generator(1, 2, 3)
>>> g2.throw(ValueError, ValueError('value error'))
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "<stdin>", line 1, in generator
ValueError: value error
```

### 3.3.4 `close` 方法

`close()` 的主要功能就是在产生器对象被暂停的地方抛出一个 `GeneratorExit` 异常。如果产生器函数已经执行结束（即产生器对象已经处于 `close` 状态），则该方法默默地返回到它的调用者；否则就在暂停处抛出 `GeneratorExit` 异常，然后关闭产生器对象并返回到它的调用者。

```python
>>> def generator(*args):
...     for arg in args:
...         yield arg
...
>>> g1 = generator(1, 2, 3)
>>> next(g1)
1
>>> g1.close()
>>> g1.close()
>>> g2 = generator(1, 2, 3)
>>> g2.close()
>>> g2.close()
```

同时，我们也可以在产生器内部来捕获这个 `GeneratorExit` 异常。注意，要想捕获 `GeneratorExit` 异常，与 `throw` 方法类似，必须在调用过 `__next__()` 或 `send(None)` 方法之后才能调用 `close()` 方法。如下：

```python
>>> def generator(*args):
...     for arg in args:
...         try:
...             yield arg
...         except GeneratorExit:
...             print('catch GeneratorExit')
...             return
...
>>> g1 = generator(1, 2, 3)
>>> next(g1)
1
>>> g1.close()
catch GeneratorExit
```

如果在捕获了 `GeneratorExit` 异常后，仍然 `yield` 一个值，则会抛出一个 `RuntimeError` 异常给调用者。如下：

```python
>>> def generator(*args):
...     for arg in args:
...         try:
...             yield arg
...         except GeneratorExit:
...             print('catch GeneratorExit')
...             # return
...
>>> g1 = generator(1, 2, 3)
>>> next(g1)
1
>>> g1.close()
catch GeneratorExit
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
RuntimeError: generator ignored GeneratorExit
```

说明：我们注释掉 `return`，在捕获了 `GeneratorExit` 异常后，它仍然会进行循环并执行 `yield` 语句，从而引发 `RuntimeError` 异常。

如果捕获了 `GeneratorExit` 异常，在处理过程中，又抛出了其他异常，则 Python 将会关闭该产生器对象（即结束产生器函数的执行），并把该新异常传播给调用者。


### 3.3.5 各方法间的异同

**相同点：**
1. `__next__`、`send` 和 `throw` 都会消耗并计算一次 `yield` 表达式以便获取产生器对象生产的下一个值。

**不同点：**
1. `__next__` 仅用来第一次启动产生器对象和获取下一个值。
2. `send` 不仅可以用来第一次启动产生器对象和获取下一个值，而且还能向产生器函数内部发送一个值。
3. `throw` 不能用来第一次启动产生器对象，但它可以向产生器函数内部抛出一个特定的异常以及获取下一个值。
4. `close` 只能向产生器函数内部抛出一个 `GeneratorExit` 异常以便于关闭产生器对象（即结束产生器函数的执行）。

注意，**获取产生器的下一个值** 意味着它将消耗并计算一次 `yield` 表达式，所以，`__next__`、`send` 和 `throw` 都会消耗并计算一次 `yield` 表达式。


### 3.3.6 暂停点

1. 当调用产生器函数返回一个产生器实例对象时，产生器的函数体并不会被执行，而是在第一次调用产生器实例对象的任何一个方法的时候。我们可以认为，产生器被暂停在函数体的第一条语句之前。比如：
```python
>>> def generator(*args):
...     print('start generator')
...     yield args
...     print('generator ends')
...
>>> g = generator(1, 2, 3)
>>> next(g)  # calling g.__next__()
start generator
(1, 2, 3)
>>> next(g)
generator ends
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
StopIteration
```

2. 当产生器被暂停时，其暂停点是在 `yield` 关键字处，即 `yield` 后面的表达式刚执行完，但 `yield` 所在的语句还未执行完。比如：
```python
>>> def generator(v1, v2, v3):
...     print('before yield')
...     v = yield v1
...     print('after yield')
...     print('yield value is %s' % v)
...     yield v2
...     print('second yield')
...     yield v3
...
>>> g = generator(1, 2, 3)
>>> next(g)
before yield
1
>>> g.send('abc')
after yield
yield value is abc
2
```
我们已经知道，`send` 方法可以向产生器内部传递一个值，该值会被作为 `yield` 表达式的值。如果在执行完 `yield` 所在的语句后暂停产生器，那么，`yield` 表达式的值就已经确定了，`send` 方法也就无法把值传递给当前暂停处的 `yield` 表达式了。从上面的示例中，我们可以看出，在调用 `next(g)` 后，表达式 `v1` 的值被计算了出来（即 `1`），并返回给了调用者，然后产生器被暂停了；当调用 `g.send('abc')` 后，第一个 `yield` 表达式的值才被计算出来（即 `send` 方法的参数 `abc`），紧接着才执行赋值语句，在遇到第二个 `yield` 关键字后，计算了其后的表达式 `v2` 的值（即 `2`）并返回给了调用者，然后产生器又被暂停了。


## 3.4 产生器表达式

创建产生器有一个快速的方法，就是使用产生器表达式；它是一种紧凑的产生器定义法。其语法是：

```python
(expression  for target  in iterator)
(expression1 for target  in iterator  if  expression2)
(expression  for target1 in iterator1 for target2 in iterator2)
```

这三种方式均可使用。对于后两种，右边的 `if` 和 `for` 可以互相无限次嵌套，但一般情况下，尽量保持只嵌套一次，以避免深度过深，影响可读性。

下面我们来看一个示例。

```python
>>> data = {'a': 1, 'b': 2, 'c': 3}
>>> g = (data[k] for k in data)
>>> type(g)
<class 'generator'>
>>> next(g)
1
>>> next(g)
2
>>> next(g)
3
>>> next(g)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
    next(g)
StopIteration
```

从上述示例中，我们可以看到，与 `yield` 定义的产生器函数所带来的效果完全一样。但相比较而言，产生器表达式的格式相对固定，没有 `yield` 的实现方式灵活、多变。对于简单的迭代需求，我们可以使用简明的产生器表达式，但对逻辑相对复杂的情况，就只能使用 `yield` 来实现了。


## 3.5 `yield from`

讲完了 `yield`，我们来看看 `yield from`。

其语法格式为：`(yield from <expr>)`。其中，`<expr>` 表达式必须返回一个迭代器对象（即实现了迭代器协议的对象——拥有 `__next__()` 方法），否则在运行时，会抛出 `TypeError` 异常。该迭代器对象会被当作子迭代器进行迭代，它的每个迭代值都会被直接的返回给产生器对象的调用者，这就像似在此处写了多个 `yield` 一样。比如:

```python
>>> def generator(*args):
...     for arg in args:
...         if hasattr(arg, '__next__'):
...             yield from arg
...         else:
...             yield arg
...
>>> sub_gen = (i for i in [3, 4])
>>> g = generator(1, 2, sub_gen, 5, 6)
>>> next(g)
1
>>> next(g)
2
>>> next(g)
3
>>> next(g)
4
>>> next(g)
5
>>> next(g)
6
>>> next(g)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
    next(g)
StopIteration
>>>
```

注意，为了实现上述的子迭代效果，迭代器对象必须是一个产生器对象，否则，`yield from <iterable>` 将退化成 `yield <iterable>`。接着上述示例如下所示：

```python
>>> g = generator(1, 2, [3, 4], 5, 6)
>>> next(g)
1
>>> next(g)
2
>>> next(g)  # Notice: the list is regarded as a whole value.
[3, 4]
>>> next(g)
5
>>> next(g)
6
>>> next(g)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
    next(g)
StopIteration
```

当产生器暂停在 `yield from` 处，如果此时通过 `send` 方法向产生器内部传递一个值，或者通过 `throw` 方法向产生器内部抛出一个异常，则产生器会将它们传播给 `yield from` 后面的迭代器对象（即子产生器对象）。如下所示：

```python
>>> def generator(*args):
...     for arg in args:
...         if hasattr(arg, '__next__'):
...             yield from arg
...         else:
...             yield arg
...
>>> def sub_gen(*args):
...     for arg in args:
...         try:
...             v = yield arg
...             if v is not None:
...                 print('receive the value: %s' % v)
...         except Exception as err:
...             print('receive an exception: %s' % err)
...
>>> g = generator(1, 2, sub_gen(3, 4, 5, 6), 7, 8)
>>> next(g)
1
>>> next(g)
2
>>> next(g)
3
>>> g.send('abc')
receive the value: abc
4
>>> next(g)
5
>>> g.throw(ValueError, ValueError('value error'))
receive an exception: value error
6
>>> next(g)
7
>>> next(g)
8
```


## 3.6 异步 `yield`

从 3.5 版本开始，Python 已支持协程（Coroutine），用于异步函数调用。因此，`yield` 也可以用于协程函数中，其用法几乎和在普通函数中一样。

当 `yield` 用在异步函数中时，这样的函数就叫 **异步产生器函数**；调用异步产生器函数返回的值叫 **异步产生器对象**。典型地，异步产生器对象用于 `async for` 语句中，就像普通产生器对象用于 `for` 语句一样。

与普通产生器对象不同，调用异步产生器对象的方法，其返回值是 `awaitable`，可用于 `await` 上下文中。而且，`yield from` 语法不能用于异步产生器函数中；在异步产生器函数中，只能使用 `yield` 的普通格式；异步产生器函数抛出 `StopAsyncIteration` 异常以代替 `StopIteration` 异常。。

另外，异步产生器对象的方法也有所不同，它们不再是 `__next__`、`send`、`throw` 和 `close`，而是 `__anext__`、`asend`、`athrow` 和 `aclose`，且它们的类型是一个协程，也即是说，它们必须用于异步函数（即用 `async` 定义的函数）中。虽然，方法名和其类型不同的，但它们的参数还是和旧的一致的。

我们来看一个例子：

```python
>>> import asyncio
>>> async def generator(*args):
...     for arg in args:
...         try:
...             v = yield arg
...             if v is not None:
...                 print('receive a value: %s -> ' % v, end='')
...         except Exception as err:
...             print('receive an exception: %s -> ' % err, end='')
...
>>> async def main():
...     g = generator(1, 2, 3, 4, 5, 6)
...     print(await g.__anext__())  # Output: 1
...     print(await g.__anext__())  # Output: 2
...     print(await g.asend('a'))   # Output: receive a value: a -> 3
...     print(await g.__anext__())  # Output: 4
...     # Output: receive an exception: value error -> 5
...     print(await g.athrow(ValueError, ValueError('value error')))
...     print(await g.__anext__())  # Output: 6
...     g = generator(1, 2, 3, 4, 5, 6)
...     async for v in g: print(v, end=' ')  # Output: 1 2 3 4 5 6
...
>>> print(type(generator))
<class 'function'>
>>> loop = asyncio.get_event_loop()
>>> loop.run_until_complete(main())
1
2
receive a value: a -> 3
4
receive an exception: value error -> 5
6
1 2 3 4 5 6
>>> loop.close()
```

注意，异步产生器函数虽是个协程，但它仍然是个函数。由于 `await` 和 `async for` 必须运行在异步函数（即协程）中，所以我们定义了一个异步函数 `main`，然后在其中执行异步产生器操作。


## 3.7 产生器与协程的区别

产生器和协程很相似，它们都能 `yield` 多次，有多个入口点，且执行可以被暂停。唯一不同的是，产生器函数在 `yield` 之后不能控制执行流程是否要继续执行，而是总是交给产生器的调用者来决定。
