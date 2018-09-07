# 第 4 章 装饰器 Decorator

本质上，装饰器是处理其他的可调用对象的可调用对象。也即是，

1. 装饰器本身是一个可调用对象。
2. 装饰器是用来装饰另一个可调用对象（如函数）的，但目前在语法上仅支持装饰 **函数** 和 **类**。

注意，方法本质上也是函数，只不过其第一个参数是类的实例对象而已。所以，这里我把方法归到函数中。


## 4.1 装饰器定义

在语法形式上，装饰器单独占一行，并以字符 `@` 开头，后面紧跟着一个可调用对象（即不带参数的装饰器），或者一个返回可调用对象的函数调用（带参数的装饰器）；下一行紧跟一个可调用对象（如函数或类）的定义或者另一个装饰器定义。比如:

```python
>>> @callable_obj1
... def function1(*args, **kwargs):
...     pass
...
>>> @callable_obj2(arg1, arg2=value)
... def function2(*args, **kwargs):
...     pass
...
>>> @callable_obj1
... @callable_obj2(arg1, arg2=value)
... def function3(*args, **kwargs):
...     pass
...
```

装饰器本质上是一个语法糖，它只是在函数或类定义的时候进行名称重新绑定，提供一个逻辑层来管理函数或类以及随后对它们的调用。简而言之，装饰器提供了一种方法，在函数和类定义语句的末尾插入自动运行代码。我们完全可以不用装饰器，自己手工来实现它。比如：

```python
@callable_obj1
def function1(*args, **kwargs):
    pass


@callable_obj2(arg1, arg2=value)
def function2(*args, **kwargs):
    pass
```

等价于

```python
def function1(*args, **kwargs):
    pass
function1 = callable_obj1(function1)


tmp_callable_obj = callable_obj2(arg1, arg2=value)
def function2(*args, **kwargs):
    pass
function2 = tmp_callable_obj(function2)
```

从上面可以看出，用作装饰器的可调用对象，须要至少接受一个参数，它就是被装饰者。如果用于装饰的可调用对象可以接受多个参数，则其它参数必须是可选的，因为在装饰时，只会传递一个参数，即被装饰者。因此，只要一个对象是可调用的，那么它都有可能作为装饰器来使用，但不是一定可以，它还要受到参数的限制：（1）至少接受一个参数；（2）如果还有更多参数，则必须是可选的。只有这样的可调用对象才能用作装饰器。

另外，装饰器应当返回一个被包装过后的被装饰者，它可能是另一个可调用对象，但其参数也应当和被装饰者的参数保持一致；当然，这不是必须的。比如：

```python
def decorator(f):
    def wrapper(*args, **kwargs):
        ...
    return wrapper


@decorator
def function(*args, **kwargs):
    ...
```

我们也可以在装饰器中什么也不做，而是直接返回被装饰者。如：
```python
def decorator(f):
    return f
```

甚至什么也可以不返回。如：
```python
def decorator(f):
    pass
```

此时，被装饰者将会完全变成 `None`。所以，千万不要这么做。如：
```python
>>> def decorator(f):
...     print('hello')
...
>>> @decorator
... def function(*args, **kwargs):
...     print(args, kwargs)
...
hello
>>> print(type(function))
<class 'NoneType'>
>>> print(function)
None
```

总之，装饰器可以是任何类型的可调用对象（一般是函数或类及其实例），也可以返回任何类型的值，但一般是被包装过的被装饰者（它既可以是装饰者本身，也可以是另外一个可调用对象）。

到此，我们要明白以下几点：
1. 装饰器是一个可调用对象，因此，它既可以是函数也可以类，甚至是类的实例（此时必须包含方法 `__call__`）。
2. 装饰器可以用来装饰一个可调用对象，因此，装饰器既可以装饰函数（包括方法），也可以装饰类。

因此，我们可以得出，
1. 一个函数可以装饰另一个函数。
2. 一个函数可以装饰一个类。
3. 一个类可以装饰一个函数。
4. 一个类可以装饰另一个类。

在 Python 中，可调用对象主要包括类（及其实例）和函数。所以，根据装饰器的实现方式，我们也可以把装饰器分为两种：**函数装饰器** 和 **类装饰器**。

### 4.1.1 函数装饰器

函数装饰器即是用函数来定义的装饰器。其大致结构如下：

```python
def decorator(f):
    def wrapper(*args, **kwargs):
        ...
    return wrapper
```

或

```python
def decorator(*args, **kwargs):
    def inner_decorator(f):
        def wrapper(*args, **kwargs):
            ...
        return wrapper
    return inner_decorator
```

前者是不带参数的函数装饰器，后者是带参数的函数装饰器。

#### 4.1.1.1 装饰函数

其用法分别为：

```python
@decorator
def decorated_function(*args, **kwargs):
    ...
```

或

```python
@decorator(arg1, arg2=value)
def decorated_function(*args, **kwargs):
    ...
```

#### 4.1.1.2 装饰类

其用法分别为：

```python
@decorator
def DecoratedClass(object):
    ...
```

或

```python
@decorator(arg1, arg2=value)
def DecoratedClass(object):
    ...
```

说明：当（函数或类）装饰器用来装饰类时，主要用途是实例单例模式。如：

```python
>>> def decorator(cls):
...     instance = cls()
...     def _cls_proxy():
...         return instance
...     return _cls_proxy
...
>>> @decorator
... class DecoratedClass(object): pass
...
>>> id(DecoratedClass())
1598853018288
>>> id(DecoratedClass())
1598853018288
>>> type(DecoratedClass)
<class 'function'>
```

我们可以发现，所有类的实例对象都是同一个（它们的 ID 是一样的）。但是，这种方式有一个缺点，就是被装饰后，该类的类型变成了函数。所以，在实例单例时，不推荐使用这种方式，使用元类会更好一些，后续在元类章节，我们会深入探讨一下。

### 4.1.2 类装饰器

类装饰器即是用类来定义的装饰器。其大致结构如下：

```python
class Decorator(object):
    def __init__(self, function):
        self._function = function

    def __call__(self, *args, **kwargs):
        ...
```

或

```python
class Decorator(object):
    def __init__(self, *args, **kwargs):
        ...

    def __call__(self, function):
        def wrapper(*args, **kwargs):
            ...
        return wrapper
```

前者是不带参数的类装饰器，后者是带参数的类装饰器。

#### 4.1.2.1 装饰函数

其用法分别为：

```python
@Decorator
def decorated_function(*args, **kwargs):
    ...
```

或

```python
@Decorator(arg1, arg2=value)
def decorated_function(*args, **kwargs):
    ...
```

#### 4.1.2.2 装饰类

其用法分别为：

```python
@Decorator
def DecoratedClass(object):
    ...
```

或

```python
@Decorator(arg1, arg2=value)
def DecoratedClass(object):
    ...
```

### 4.1.3 注意事项

1. 当普通函数装饰器应用到类中的方法上时，会多传递一个参数（即类的实例）给包装函数，且作为第一个参数。一般不建议将普通函数装饰器应用到类中的方法上；如果确实有需求，则需要特别设计。
```python
>>> def decorator(func):
...     def wrapper(*args):
...         print('called arguments:', args)
...         return func(*args)
...     return wrapper
...
>>> @decorator
... def func(x, y):
...     print(x, y)
...
>>> class C(object):
...     @decorator
...     def method(self, x, y):
...         print(x, y)
...
>>> func(6, 7)  # ==> wrapper(6, 7)
called arguments: (6, 7)
6 7
>>> obj = C()
>>> obj.method(6, 7)  # ==> wrapper(obj, 6, 7)
called arguments: (<__main__.C object at 0x000001744310F3C8>, 6, 7)
6 7
```

2. 类装饰器支持多个实例时，要特别设计。下面的示例是有问题的（`y` 覆盖了 `x`）。
```python
>>> class Decorator:
...     def __init__(self, C):
...         self.C = C
...         self.wrapped = None
...     def __call__(self, *args, **kwargs):
...         self.wrapped = self.C(*args, **kwargs)
...         return self
...     def __getattr__(self, attrname):
...         return getattr(self.wrapped, attrname)
...
>>> @Decorator
... class C: pass
...
>>> print(C.wrapped)
None
>>> x = C()
>>> x.wrapped
<__main__.C object at 0x0000017443143198>
>>> y = C()
<__main__.C object at 0x00000174431431D0>
>>> x.wrapped
<__main__.C object at 0x00000174431431D0>
```

3. 在 Python 中，函数或类本身也是一个对象，所以它们也有属性（比如表示函数或类文档的 `__doc__`）；而且函数或类不同，它们的属性也不同。在对函数或类使用装饰器时，为了使装饰者更像被装饰者（即，从名字到属性等等，装饰者和被装饰者一样），使其二者看起来不分彼此，可以使用标准库 `functools` 中的 `wraps` 装饰器来装饰我们的装饰器，它（`wraps`）能捕获被我们的装饰器所装饰的函数或类，并将其属性等信息赋值给我们的装饰器。否则，可以通过查看装饰者和被装饰者的属性来辨别出：被装饰者装饰过的东西不再是原来的模样了。
```python
>>> import functools
>>> def decorator(f):
...     @functools.wraps(f)
...     def inner_decorator(*args, **kwargs):
...         """inner_decorator doc"""
...         print("decorator")
...         return f(*args, **kwargs)
...     return inner_decorator
...
>>> @decorator
... def add(a, b):
...     """add doc"""
...     return a+b
...
>>> add(1, 2)
decorator
3
>>> add.__doc__  # not "inner_decorator doc"
add doc
>>> add.__name__  # not "inner_decorator"
add
```

## 4.2 应用

装饰器有多种用途，比如：日志跟踪、审计、单例模式、属性管理。

### 4.2.1 拦截

装饰器最基本也是最常用的一个功能就是拦截可调用对象的调用，如拦截一个函数或 API 的调用。在其它一些语言中，也有类似的实现（如 Java 中的 `Proxy` 类，但它是在标准库中，而不是在核心语言规范中）。

同时，拦截调用的一个最常见的情景就是日志处理。有时候，我须要通过日志来跟踪一个 API 的调用；此时，我们要在 API 调用的前后添加一些日志。传统上，为了实现这一需求，须要在 API 调用的每个点的前后都添加日志处理，这将会影响业务的处理，同时也是冗余的，而且有时候会由于疏忽可能被遗漏。有了拦截器，就方便多了；日志跟踪的逻辑可以单独抽取出来，放到拦截器中统一处理，而且只需要编写一次，不影响其它业务代码。

下面我们来看一个简单的日志跟踪。

```python
>>> def decorator(f):
...     def wrapper(v1, v2, v3):
...         print('before calling')  # print log before calling
...         result = f(v1, v2, v3)
...         print('after calling')  # print log after calling
...         return result
...     return wrapper
...
>>> @decorator1
... def add(v1, v2, v3):
...     print('%i + %i + %i = %i' % (v1, v2, v3, v1 + v2 + v3))
...
>>> add(1, 2, 3)
before calling
1 + 2 + 3 = 6
after calling
```

同时，我们也可以给日志跟踪添加一个名字。如下：

```python
>>> def decorator(name):
...     def inner_dec(f):
...         def wrapper(v1, v2, v3):
...             print('%s: before calling' % name)
...             result = f(v1, v2, v3)
...             print('%s: after calling' % name)
...             return result
...         return wrapper
...     return inner_dec
...
>>> @decorator('add')
... def add(v1, v2, v3):
...     print('%i + %i + %i = %i' % (v1, v2, v3, v1 + v2 + v3))
...
>>> add(1, 2, 3)
add: before calling
1 + 2 + 3 = 6
add: after calling
```

类似地，除了日志跟踪外，此方法也可以用于审计等功能，原理是一样的，这里就不再详细阐述了。


### 4.2.2 单例模式

装饰器的另一个功能就是用来实现单例模式。

前面我们已经看一个例子，但它有明显的缺点。这里我们来对它进行改进一下：使用类装饰器来代替函数装饰器。

```python
>>> class Singleton(object):
...     def __init__(self, cls):
...         self._cls = cls
...         self._obj = cls()
...     def __call__(self):
...         return self._obj
...
>>> @Singleton
... class C(object): pass
...
>>> obj1 = C()
>>> obj2 = C()
>>> obj1 is obj2
True
>>> isinstance(obj1, C)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
TypeError: isinstance() arg 2 must be a type or tuple of types
```

我们看到，通过类 `C` 来创建两个实例，但它们显示是同一个对象，这说明，我们的单例装饰器成功了。但是，当判断实例与类之间的关系时，又报错了。

学过 Python 后，我们知道，`isinstance` 函数将会调用实例对象的 `__instancecheck__` 方法，也就是说，我们可以实现 `__instancecheck__` 方法以完成实例与类关系的自定义判断。我们对上面的 `Singleton` 类添加一个 `__instancecheck__` 方法。代码如下：

```python
class Singleton(object):
    def __init__(self, cls):
        self._cls = cls
        self._obj = cls()

    def __call__(self):
        return self._obj

    def __instancecheck__(self, instance):
        return isinstance(instance, self._cls)
```

再次执行 `isinstance` 函数时，就不会报错了。如:

```python
>>> obj = C()
>>> isinstance(obj, C)
True
```

### 4.2.3 标签化

有时候，我们可能会给某些函数或方法打标签，以区别这些函数或方法。在定义函数或方法时，我们通过装饰器可以快速给它们打上标签。比如：

```python
>>> def tag(name):
...     def wrapper(func):
...         func._tag = name
...         return func
...     return wrapper
...
>>> @tag('add')
... def func1(*args):
...     print(func1._tag, args)
...
>>> func1(1, 2)
add (1, 2)
```

我们也可以打多个标签，比如：
```python
>>> def tag(name):
...     def wrapper(func):
...         if hasattr(func, '_tag'):
...             func._tag.append(name)
...         else:
...             func._tag = [name]
...         return func
...     return wrapper
...
>>> @tag('add')
... @tag('+')
... def func1(*args):
...     print(func1._tag, args)
...
>>> func1(1, 2)
['+', 'add'] (1, 2)
```

上述直接打标签的示例，没有太大的用途，它只是一个原理讲解，我们可以换一种用途。`OpenStack` 中也使用了这种方式，不过它不是用来打标签，而是重载某个方法的 `action` 名称。如：

```python
def action(name):
    def wrapper(func):
       func._action = name
       return func
    return wrapper


class C(object):
    @action('create')
    def method(self, *args, **kwargs):
        ...
```

这种方式看起来似乎也没有太大的用途，但是我们可以对类 `C` 使用元类（后续章节会详细讲解），在元类中收集所有 `action` 名称，然后可以统一进行方法调度。


### 4.2.4 属性管理

在属性管理一章，我们已经看到，`property` 即可通过装饰器功能来管理实例属性的获取、赋值、删除等功能。这里就不再详细介绍了。
