# 第 2 章 属性管理

Python 2 中既有旧式类，又有新式类；而 Python 3 中只有新式类，旧式类已经过时了。因此，本文只讨论新式类的属性管理，暂不考虑旧式类。

Python 管理属性的方法一般有三种：

1. 操作符重载（即，`__getattr__`、`__setattr__`、`__delattr__` 和 `__getattribute__`，有点类似于 C++ 中的重载操作符）
2. `property` 类
3. 类属性 `__slots__`
4. 描述符协议

在 Python 中，类本身也是实例对象，因此类和类实例都可以有属性。而且，一个类或类实例中的属性是动态的，你可以随意地往一个类或类实例中添加或删除一个属性。

一个对象是否含有某个属性，其判断依据是，根据属性查找规则，Python 解析器是否能够从此对象中找到该属性。如果能找到，则表示此对象含有（或定义了）该属性，也即是该属性在此对象中是可访问的，否则不含有（或未定义），即不能通过此对象访问该属性。


## 2.1 操作符重载

在 Python 中，重载 `__getattr__`、`__setattr__`、`__delattr__`和`__getattribute__` 等方法可以用来管理一个自定义类中的属性访问。其中，`__setattr__` 方法将拦截所有的属性赋值；`__delattr__` 方法将拦截所有的属性删除；而 `__getattr__` 和 `__getattribute__` 将拦截所有的属性获取，但它们是有区别的：`__getattr__` 用于拦截所有未定义的属性，而 `__getattribute__` 用于拦截所有属性的获取，不管该属性是否已经定义，只要获取它的值，该方法都会被调用。换句话说就是，如果定义了 `__getattribute__` 方法，`__getattr__` 方法将失效，`__getattr__` 方法只有在 `__getattribute__` 未定义的时候才会被调用。

如果我们想使用这方法来管理自定义类的属性，就须要我们在自定义类中重新定义这些方法的实现。由于 `__getattribute__`、`__setattr__`、`__delattr__` 等方法会对所有的属性访问进行拦截，所以，在重载它们时，不能再像往常的编码一样，要注意避免递归调用（如果出现递归，则会引起死循环）；然而对 `__getattr__` 方法，则没有这么多的限制。

在讲解重载操作符之前，我们要理解一下实例方法的调用。在 Python 中，实例方法的调用实际上是函数的调用，只不过，实例方法的调用只是一个语法糖。如下：

```python
>>> class C(object):
...     def method(self):
...         pass
...
>>> obj = C()
>>> obj.method()   # 通过实例调用方法
>>> C.method(obj)  # 通过类调用实例方法
```

从上述示例中可以看出，调用实例的方法，有两种方式，一种是通过实例来调用，另一个是通过类来调用。看似有两种，实际上只有一种，即第二种调用方式。在 Python 执行到第一种调用方式时，Python 解析器会自动地将其转换为第二种方式（如：`obj.__class__.method(obj)`，即先通过实例对象获取其类型，然后再调用该类型的方法 `method`），对于程序员或解析器来说，第一种调用方式只是一个语法糖而已。

对于第二种调用方式，实则是一个普通的函数调用，只不过这个函数被定义在类的作用域中，如果要想访问该函数，必须通过类名来引用它。

但是，这两种调用方式是有区别的。当调用一个方法时，首先要根据方式名在相应的作用域中去查找方法的实现，然后才调用它。对于第二种调用方式，只会在当前类中查找该方法，如果找到就调用；如果当前类中没有定义，则查找失败，就会抛出 `AttributeError` 异常。但是，对于第一种调用方式，Python 会先从实例对象中查找，然后再从它的类中查找，紧接着根据 MRO 规则沿着继承链向上，从它的父类中查找，直到找到第一个方法定义或者到达 `object` 类也没有找到（此时会抛出 `AttributeError` 异常）为止。

因此，一般情况下，应尽可能的通过实例来调用方法。


### 2.1.1 重载 `__setattr__` 方法

在重载 `__setattr__` 方法时，不能使用 `self.name = value` 格式；否则，它将会导致递归调用而陷入死循环。正确的应该是：

```python
def __setattr__(self, name, value):
    # do-something
    object.__setattr__(self, name, value)
    # do-something
```

其中的 `object.__setattr__(self, name, value)` 一句可以换成 `self.__dict__[name] = value`；但前提是，必须保证 `__getattribute__` 方法没有重载或者重载正确，否则，在赋值时就是出错，因为 `self.__dict__` 将会触发对 `self` 的 `__dict__` 属性进行获取操作，进而引发对 `__getattribute__` 方法的调用。如果 `__getattribute__` 方法重载错误，`__setattr__` 方法自然而然地也就会失败。

注意：`__setattr__` 方法不须要返回一个值。


### 2.1.2 重载 `__delattr__` 方法

在重载 `__delattr__` 方法时，不能使用 `del self.name` 格式；否则，它将会导致递归调用而陷入死循环。正确的应该是：

```python
def __delattr__(self, name):
    # do-something
    object.__delattr__(self, name)
    # do-something
```

其中的 `object.__delattr__(self, name)` 一句可以换成 `del self.__dict__[name]`，其要求同 `__setattr__`。

注意：`__delattr__` 方法不须要返回一个值。


### 2.1.3 重载 `__getattribute__` 方法

```python
def __getattribute__(self, name):
    # do-something
    return object.__getattribute__(self, name)
    # do-something
```

在 `__getattribute__` 方法中不能把 `return object.__getattribute__(self, name)` 一句替换成 `return self.__dict__[name]`，因为 `self.__dict__` 也会触发属性获取，进而还是会导致递归调用。

注意：`__getattribute__` 方法要么返回一个值，要么抛出一个 `AttributeError` 异常。


### 2.1.4 重载 `__getattr__` 方法

```python
def __getattr__(self, name):
    # TODO
    raise AttributeError("'%s' object has no attribute '%s'" % (self.__class__, name))
```

由于 `__getattr__` 方法是拦截 **未定义** 的属性，所以它没有其他三个操作符方法中那么多的限制，因此，你可以像正常的代码一样编写它。它的作用就是，当一段代码（用户写的，可能是故意，也可以是无意）获取了类或类实例中没有定义的属性时，程序将做出怎样的反应，而这个回应就在 `__getattr__` 方法中，由你来定。

注意：`__getattribute__` 方法要么返回一个值，要么抛出一个 `AttributeError` 异常。


### 2.1.5 默认的属性访问拦截

上述四个属性拦截方法各自独立，互不影响，在自定义类时，既可以完全不用重载，也可以只重载一个或多个，还可以完全重载。

`object` 类是所有类的基类，而 `object` 中已经含有此四个方法的默认实现，如果其中的某个方法未被重载，会调用 `object` 中的默认实现。

`__setattr__` 的默认实现会在实例对象的 `__dict__` 属性中添加一个键值对。

`__delattr__` 的默认实现会从实例对象的 `__dict__` 属性中删除相应的键值对，即删除该属性值。如果 `__dict__` 中没有要删除的属性名，则抛出 `AttributeError` 异常。

`__getattr__` 的默认实现直接抛出 `AttributeError` 异常。

`__getattribute__` 的默认实现参见后文。


### 2.1.6 示例

```python
class Person(object):
    def __init__(self, defaults=None):
        self.__defaults = defaults or {}

    def __setattr__(self, name, value):
        if name != '_Person__defaults':
            print("set the attribute '%s' to '%s'" % (name, value))
        object.__setattr__(self, name, value)

    def __delattr__(self, name):
        print("delete the attribute '%s'" % name)
        object.__delattr__(self, name)

    def __getattr__(self, name):
        print("get the attribute '%s'" % name)
        if name in self.__defaults:
            return self.__defaults[name]
        raise AttributeError("AttributeError: no attribute '%s'" % name)


person = Person({'attr1': 123, 'attr2': 'abc'})
person.attr0 = 'value'
print("person.attr0=", person.attr0)
print("person.attr1=", person.attr1)
print("person.attr2=", person.attr2)
try:
    print("person.attr3=", person.attr3)
except AttributeError as err:
    print(err)

# Output:
# set the attribute 'attr0' to 'value'
# person.attr0 = value
# get the attribute 'attr1'
# person.attr1 = 123
# get the attribute 'attr2'
# person.attr2 = abc
# get the attribute 'attr3'
# AttributeError: no attribute 'attr3'
```


## 2.2 Property

在 Python 中，除了用重载操作符来管理类实例属性的访问控制外，也可以使用内建函数 `property`。

### 2.2.1 property 类

`property` 本质上和 `object` 一样，都是一个类，即可以用它来实例化出一个对象，它可以用来管理实例的属性访问。

在 `property` 类中，有三个成员方法和三个装饰器函数。三个成员方法分别是：`fget`、`fset`、`fdel`，它们分别用来管理属性的访问；三个装饰器函数分别是：`getter`、`setter`、`deleter`，它们分别用来把三个同名的类方法装饰成 `property`，以管理某一个属性。

```python
>>> property
<class 'property'>
>>> dir(property)
['__class__', '__delattr__', '__delete__', '__dir__', '__doc__', '__eq__',
'__format__', '__ge__', '__get__', '__getattribute__', '__gt__', '__hash__',
'__init__', '__init_subclass__', '__isabstractmethod__', '__le__', '__lt__',
'__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__set__',
'__setattr__', '__sizeof__', '__str__', '__subclasshook__', 'deleter', 'fdel',
'fget', 'fset', 'getter', 'setter']
```

其中，`fget` 方法用来控制实例属性的获取，`fset` 方法用来控制实例属性的赋值，`fdel` 方法用来控制实例属性的删除；`getter` 装饰器把一个自定义的实例方法装饰成 `fget` 操作，`setter` 装饰器把一个自定义的实例方法装饰成 `fset` 操作，`deleter` 装饰器把一个自定义的实例方法装饰成 `fdel` 操作。

同前文的操作符重载一样，一旦在自定义类中实现这些方法，就可以在其中做任何事情，而不仅仅是管理实例属性。不管这三个函数完成什么的功能，只要在获取实例的属性时就会自动调用 `fget` 方法，给实例的属性赋值时就会自动调用 `fset` 方法，删除实例的属性时就会自动调用 `fdel` 方法。如果某个方法没有被实现，则对应的操作也就被禁止，即如果执行这些操作，就会触发异常。


### 2.2.2 property 类的使用

根据 `property` 类中的成员属性类别，我们将其分为 **普通方法** 和 **装饰器方法**。

#### 2.2.2.1 使用普通方法

`property` 是一个类，每实例化一个对象，就相当于实例化出一个属性访问控制，它可以控制一个变量的访问、赋值、删除等操作。其原型如下：
```python
property(fget=None, fset=None, fdel=None, doc=None)
```

为了控制属性的获取、赋值和删除，可以分别将相应的控制函数传递给 `fget`、`fset` 和 `fdel` 三个参数即可。

```python
class Person(object):
    def __init__(self, name, age):
        self._name = name
        self._age = age

    def _get_name(self):
        print('get the name')
        return self._name

    def _set_name(self, name):
        print("set the name to '%s'" % name)
        self._name = name

    def _del_name(self):
        print('delete the name')
        del self._name

    name = property(fget=_get_name, fset=_set_name, fdel=_del_name)

    def _get_age(self):
        print('get the age')
        return self._age

    def _set_age(self, age):
        print("set the age to '%s'" % age)
        self._age = age

    def _del_age(self):
        print('delete the age')
        del self._age

    age = property(fget=_get_age, fset=_set_age, fdel=_del_age)


print('name', id(Person.name), type(Person.name))
print('age', id(Person.age), type(Person.age))

person = Person('Aaron', 123)
print(person.name)
person.name = 'John'
print(person.name)

del person.name
try:
    print(person.name)
except AttributeError:
    print("no the atrribute 'name'")

print(person.age)

# Output:
# name 2640632190440 <class 'property'>
# age 2640632397400 <class 'property'>
# get the name
# Aaron
# set the name to 'John'
# get the name
# John
# delete the name
# get the name
# no the atrribute 'name'
# get the age
# 123
```

如果某个参数没有设置，则对应的操作则是被禁止的。比如：

```python
class Person(object):
    def __init__(self, name):
        self._name = name

    def _get_name(self):
        print('get the name')
        return self._name

    def _set_name(self, name):
        print("set the name to '%s'" % name)
        self._name = name

    name = property(fget=_get_name, fset=_set_name)


person = Person('Aaron')
print(person.name)
person.name = 'John'
print(person.name)

try:
    del person.name
except AttributeError as err:
    print("AttributeError:", err)

# Output:
# get the name
# Aaron
# set the name to 'John'
# get the name
# John
# AttributeError: can't delete attribute
```

`property` 一旦被实例化后，其对象中的 `fget`、`fset`、`fdel` 等成员属性均是只读的，不允许再次修改它们的值。因此，如果想要通过 `property` 来控制实例属性的某个操作，就必须在实例化 `property` 类时指定其控制函数，不允许创建后再设置。

但这并不代表完全不能修改其属性的控制。如果确实想要改变，就必须完全重新创建一个 property 实例，然后用这个新实例替换旧实例即可。如下：

```python
class Person(object):
    def __init__(self, name):
        self._name = name

    def _get_name(self):
        print('get the name')
        return self._name

    def _set_name(self, name):
        print("set the name to '%s'" % name)
        self._name = name

    name = property(fget=_get_name, fset=_set_name)


person = Person('Aaron')
print(person.name)
person.name = 'John'
print(person.name)

try:
    del person.name
except AttributeError as err:
    print("AttributeError:", err)


def _del_name(self):
    print('delete the name')
    del self._name

# Use a new property instance instead of the old one.
Person.name = property(fget=Person.name.fget, fset=Person.name.fset,
                       fdel=_del_name)

del person.name
try:
    print(person.name)
except AttributeError:
    print("no the atrribute 'name'")

# Output:
# get the name
# Aaron
# set the name to 'John'
# get the name
# John
# AttributeError: can't delete attribute
# delete the name
# no the atrribute 'name'
```

从以上的示例可以看出，`property` 属性管理是在自定义类中通过定义一个类属性而完成的，虽然`property` 实例是自定义类的类属性，但对 `property` 实例的操作将作用于自定义类的实例的属性上。其实，自定义类的实例的属性的信息仍然是存储于自定义类的实例中，`property` 实例只不过在管理它的操作（获取、赋值、删除）。也就是说，由 `property` 创建的属性是属于自定义类的，而不是属于自定义类的实例的。但是，它却可以管理自定义类的实例的属性，而不管理自定义类的属性，即 `property` 不会作用在自定义类的属性上，只会作用在自定义类的实例的属性上。

总之，我们可以简单地认为，`property` 把实例对象的属性的存储与控制进行了分离：数据仍然存储在实例对象中，而属性的访问或操作控制则委托给了 `property` 来完成。


#### 2.2.2.2 使用装饰器方法

我们看到，在使用普通方法来管理属性时，对于每一个要管理的属性，都要添加一行类属性赋值的操作。相比于普通方法，装饰器方法的操作会更为简洁、紧凑。

`property` 不仅是可以作为类来实例化，还可以作为装饰器来使用。如：

```python
class Person(object):
    def __init__(self, name):
        self._name = name

    @property
    def name(self):
        return self._name
```

当我们把 `property` 当作装饰器来使用时，它将会隐式地创建一个 `property` 实例，然后进行 `property` 属性控制绑定。上述代码等价于：

```python
class Person(object):
    def __init__(self, name):
        self._name = name

    def name(self):
        return self._name

    # 将类的属性 name 重新绑定到 property 实例上
    name = property(fget=name)
```

当使用装饰器来管理 `property` 属性时，`getter`、`setter` 和 `deleter` 所装饰的自定义方法名要一致。比如：

```python
class Person(object):
    def __init__(self, name):
        self._name = name

    @property
    def name(self):
        print('get the name')
        return self._name

    @name.setter
    def name(self, value):
        print("set the name to '%s'" % value)
        self._name = value

    @name.deleter
    def name(self):
        print('delete the name')
        del self._name


person = Person('Aaron')
print(person.name)
person.name = 'John'
del person.name
try:
    print(person.name)
except AttributeError:
    print('no attribute name')

# Output:
# get the name
# Aaron
# set the name to 'John'
# delete the name
# get the name
# no attribute name
```

如果不一致，装饰时是什么方法名，操作时就要用什么属性名。比如，当把 `name.setter` 装饰的方法名改为 `other_name` 时，设置 `name` 属性时，就要使用 `other_name`。示例如下：

```python
class Person(object):
    def __init__(self, name):
        self._name = name

    @property
    def name(self):
        print('get the name')
        return self._name

    @name.setter
    def other_name(self, value):
        print("set the name to '%s'" % value)
        self._name = value

    @name.deleter
    def name(self):
        print('delete the name')
        del self._name


person = Person('Aaron')
print(person.name)
person.other_name = 'John'
print(person.name)
del person.name
try:
    print(person.name)
except AttributeError:
    print('no attribute name')

# Output:
# get the name
# Aaron
# set the name to 'John'
# get the name
# John
# delete the name
# get the name
# no attribute name
```

所以，虽然 Python 并不要求其名字都一致，但作为最佳实践，我们应当保持其一致。

我们已经知道，在使用普通方法来定义 `property` 属性时，可以通过生成一个新的 `property` 实例，并重新绑定自定义类的属性上，以此完成，修改原先的 `property` 属性控制。学习过装饰器方法后，我们也可以通过装饰器来达到此目的。如：

```python
# Use a new property instance instead of the old one.
# Person.name = property(fget=Person.name.fget, fset=Person.name.fset,
#                        fdel=_del_name)
Person.name = Person.name.deleter(_del_name)
```


## 2.3 描述符

通过前文，我们可以看到，通过 `property` 来控制每个属性的访问很方便，但它实质上是一个描述符，因此可以把 `property` 看作是创建一个特定属性的描述符的一种简化方式，即可以把 `property` 看成是简化了的、受限的描述符。

相比于 `property`，描述符的功能更加强大、灵活多变。下面我们来介绍一下描述符的使用。


### 2.3.1 描述符定义

描述符本质上是一个类，类中定义了三个成员方法：`__get__`、`__set__`、`__delete__`。也就是说，**只要一个类中定义了这三个方法中的任何一个，那么，这个类就自动地成为一个描述符**。

既然 `property` 是一个简化了的描述符，因此，它们也有相通之处：`__get__` 相当于 `fget`、`__set__` 相当于 `fset`、`__delete__` 相当于 `fdel`。但是，描述符却没有装饰器功能。

由于描述符可以是任何一个类，因此它可以使用所有的 OOP 功能；相比于 `property`，它就更加地自由、灵活了。因此，一般情况下，描述符所管理的自定义类的实例属性的值存储在描述符类的实例中，而不是自定义类的实例中。当然，也可以存储在自定义类的实例中，甚至可以同时在两者中都存储。反而 `property`，它所管理的自定义类的实例属性的值只能存储在自定义类的实例中。

描述符和 `property` 一样，一次只能用来管理一个单个的、特定的属性；如果想要管理多个属性，就必须定义多个 `property` 和描述符。


### 2.3.2 示例

下面我们展示一个示例，将属性值同时存储在描述符类的实例和自定义类的实例中。

```python
class Name(object):
    def __init__(self, value):
        self._name = value

    def __get__(self, instance, owner):
        print('get the name')

        # 从自定义类的实例中返回属性值
        return instance._name

    def __set__(self, instance, value):
        print("set the name to '%s'" % value)

        # 把属性值存储在自定义类的实例中
        instance._name = value

        # 把属性值存储在描述符类的实例中
        self._name = value

    def __delete__(self, instance):
        print('delete the name')

        # 把属性值从自定义类的实例和描述符类的实例中删除
        del instance._name
        del self._name


class Person(object):
    def __init__(self, name):
        self._name = name

    name = Name('')


person = Person('Aaron')
print(person.name)
person.name = 'John'
print(person.name)

del person.name
try:
    print(person.name)
except AttributeError:
    print('no attribute name')

# Output:
# get the name
# Aaron
# set the name to 'John'
# get the name
# John
# delete the name
# get the name
# no attribute name
```


## 2.4 `__slots__`

默认地，每个类实例都自动拥有一个字典属性（名为`__dict__`），用来存储该实例的属性。但我们可以通过在类定义中定义一个类属性 `__slots__` 来禁用这个默认特性。即，如果一个类中定义了 `__slots__` 属性，那么该类将会阻止每个类实例对象自动生成 `__dict__` 和 `__weakref__` 这两个实例属性。

一般来说，`__slots__` 是个包含实例所有属性名的序列，但一个字符串、迭代器或表示实例所使用的变量名的字符串序列也是可以接受的。

```python
>>> class A(object):
...     __slots__ = ['a', 'b']
...
>>> a = A()
>>> hasattr(a, '__dict__')
False
>>> hasattr(a, '__weakref__')
False
```

### 2.4.1 注意事项

#### 2.4.1.1 `__slots__` 不具有继承性

如果一个没有 `__slots__` 的子类继承一个拥有 `__slots__` 的父类，那么该子类将总是拥有一个 `__dict__` 属性并可访问。所以，对于一个子类，只有在该子类中再重新定义一个 `__slots__` 才有意义。换句话说，`__slots__` 的声明动作被限制在定义它的类中。一般情况下，子类中的 `__slots__` 只须包含父类中没有定义的其它额外的名字即可。

```python
>>> class A(object):
...     __slots__ = ['a', 'b']
...
>>> class B(A): pass
...
>>> hasattr(B(), '__dict__')
True
>>> class C(A):
...     __slots__ = ['c', 'd']
...
>>> c = C()
>>> hasattr(c, '__dict__')
False
>>> c.a = 1
>>> c.b = 2
>>> c.c = 3
>>> c.d = 4
>>> c.e = 5
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
AttributeError: 'C' object has no attribute 'e'
>>>
```

#### 2.4.1.2 `__slots__` 限制新增属性

实例对象如果没有 `__dict__` 属性，就不能新增（或赋值）不存在于 `__slots__` 中的属性。如果试图给不存在于 `__slots__` 中的属性赋值，则将引发 `AttributeError` 异常。如果希望能够对实例的新属性进行动态性地赋值，则可以在 `__slots__` 的声明中增加 `__dict__`。此时，有无 `__slots__` 特性，其区别已经并不太大了。

```python
>>> class A(object):
...     __slots__ = ["a", "b"]
...
>>> a = A()
>>> a.a = 1
>>> a.b = 2
>>> a.c = 3
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
AttributeError: 'A' object has no attribute 'c'
>>>
>>> class B(object):
...    __slots__ = ['a', 'b', '__dict__']
...
>>> b = B()
>>> b.a = 1
>>> b.b = 2
>>> b.c = 3
>>> print(b.c)
3
>>> 'c' in b.__dict__
True
>>> hasattr(b, 'c')
True
```

之所以有了 `__dict__` 还会有 `__slots__`，主要是为了节省内存，`__dict__` 是一个字典，会占据大量的内存。一般情况下，无须使用 `__slots__` 来管理属性，只有当某个类型有少量实例属性，但又有大量实例对象时，才会使用 `__slots__` 来节省内存。


#### 2.4.1.3 `__slots__` 使用描述符来管理属性

对于在 `__slots__` 中列出的每一个属性名，`__slots__` 会将其实现为一个描述符，即在类属性中通过创建一个描述符来管理该属性。正由于这种实现方式，因此，不能为定义在 `__slots__` 中的实例属性设置一个默认值。不过，这种限制不是强制的：如果想要强制为定义在 `__slots__` 序列中的实例属性设置一个默认值，那么应该在类属性中重新为其赋值。

```python
>>> class A(object):
...     __slots__ = ['a', 'b']
...
>>> a = A()
>>> a.a = 1
>>> type(a.a)
<class 'member_descriptor'>
```

#### 2.4.1.4 定义在子类 `__slots__` 中的属性会隐藏父类 `__slots__` 中的同名属性

如果基类的 `__slots__` 中声明了某个属性，并在子类的 `__slots__` 中再次进行声明，即子类和基类同时在 `__slots__` 中声明了一个相同的名字，那么，定义在基类中的实例属性将不可访问，除非通过基类来直接获取它的描述符；但这将引发程序的未定义行为。在将来，Python 可能会增加一个检查来阻止这种情况。


## 2.5 四者之间的关系

`__slots__` 本质上是通过描述符来管理属性的，因此，可以将其看作是一组描述符集合。

`property` 充当个特定角色，而描述符更为通用。`property` 定义特定属性的获取、设置和删除功能。描述符也提供了一个类，带有完成这些操作的方式；但是，它提供了额外的灵活性以支持更多任意行为。实际上，`property` 真的的只是创建特定描述符的一种简单方法——即在属性访问上运行的一个描述符。编码上也有区别：`property` 通过一个内置函数（或者说是内建类）来创建，而描述符用一个自定义类来创建，因此描述符可以利用类的所有常用 OOP 功能，如继承。此外，除了实例的状态信息，描述符有它自己的本地状态，所以，它可以避免与实例中的名称冲突。

`__getattr__`、`__getattribute__`、`__setattr__` 和 `__delattr__` 方法更为通用：它们用来捕获任意多的属性。相反，每个 `property` 或描述符只针对一个特定属性提供访问拦截——我们不能用一个单个的 `property` 或描述符捕获每一个属性访问。而且，其实现也不同：`__getattr__`、`__getattribute__`、`__setattr__` 和 `__delattr__` 是操作符重载方法，`property` 和描述符是手动赋给类属性的对象。


## 2.6 类和实例的属性

类的属性包括 **类属性**、**静态方法**、**类方法**、**实例方法**。

实例的属性包括 **实例属性**。

这里注意一点，方法其实也属于 **属性**，之不过，这个属性的值比较特殊——它是可调用的。因此，我们可以这样使用：

```python
>>> class A(object):
...     def show(self, *args, **kwargs):
...         print(args, kwargs)
...
>>> A.show = lambda self, *args, **kwargs: print(self, 'the new method')
>>> show = A().show
>>> show(1, 2, 3, a=11, b=22, c=33)
<__main__.A object at 0x000001A749F7F588> the new method
```

由于 **类属性**、**静态方法**、**类方法** 均是定义在类的作用域中的，因此，它们都是类的属性。同理，**实例方法** 也是定义在类的作用域中的，因此，它也应该是类的属性。而且，前面我们已经提到，当通过实例对象来调用实例的方法时，Python 会自动将其转换为通过类来调用，不同的是，它会将实例对象作为第一个参数传递给实例方法，这也正是在定义实例方法时，为什么第一个参数被认为是实例参数（之所以约定为 `self`，正是为了表示实例对象本身）。从这一方面，也正说明了，**实例方法** 是属于类的，而不是实例对象的，只不过，在传递参数时，多传入了一个实例对象而已。

参考上述分析，**静态方法**、**类方法**、**实例方法** 其实是相似的，唯一不同的是，是否多传递一个参数作为第一个参数，以及第一个参数是谁（如果传递的话）。对于 **静态方法** 而言，不多传递一个参数，调用方法时，有多少个参数就传递多少个参数；对于 **类方法** 而言，除了调用方法时的参数外，再额外传递一个参数作为第一个参数，且此参数是类对象本身；对于 **实例方法** 而言，它等同于 **类方法**，只是把类对象换成了实例对象，其二者的名字，也正因此而得名。

```python
class A(object):
    attr1 = 1

    def __init__(self):
        self.attr2 = 2

    def print1(self):
        print(self.attr1, self.attr2)

    @classmethod
    def print2(cls):
        print(cls.attr1)

    @staticmethod
    def print3():
        print("staticmethod")

a = A()
print('attr2' in a.__dict__, 'attr2' in A.__dict__)
print('attr1' in a.__dict__, 'attr1' in A.__dict__)
print('print1' in a.__dict__, 'print1' in A.__dict__)
print('print2' in a.__dict__, 'print2' in A.__dict__)
print('print3' in a.__dict__, 'print3' in A.__dict__)

# Output:
# True False
# False True
# False True
# False True
# False True
```

通过以上示例可以发现，attr1（类属性）、print1（实例方法）、print2（类方法）、print3（静态方法）都存在于类对象的属性集合中，而只有 attr2（实例属性）才是存在于实例对象的属性集合中。


## 2.7 Python 是如何获取实例的属性

从前文我们知道，当访问一个实例对象的属性时，`__getattribute__` 方法会拦截所有属性的获取。因此，一旦要获取一个实例对象的属性，那就会触发该实例对象的 `__getattribute__` 方法的调用，即使该实例对象没有定义 `__getattribute__` 方法。尽管没有定义 `__getattribute__` 方法，但是由于是每个类都是 `object` 的子类，因此它最终将会调用 `object` 类中的 `__getattribute__` 方法（这是 Python 中 `__getattribute__` 的默认实现）。

### 2.7.1 `__getattribute__` 的默认实现

`object.__getattribute__` 默认会按下面列出的顺序依次查找属性，直到找到第一个为止，如果没有找到，就抛出一个 `AttributeError` 异常。

1. 数据描述符（即含有 `__set__` 方法的描述符）
2. 实例属性
3. 非数据描述符（即不含有 `__set__` 方法的描述符）
4. 默认调用 `__getattr__` 方法。

由于 `property` 是简化了的描述符，且 `__slots__` 本质上就是通过描述符来管理属性的，因此，可以把 `property` 和 `__slots__` 等同处理。

下面我们以 `property` 为例表示描述符，来说明上述顺序的查找。

#### 2.7.1.1 数据描述符与实例属性

```python
>>> class Person(object):
...     def __init__(self, name):
...         self._name = name
...
...     @property
...     def name(self):
...         return self._name
...
...     @name.setter
...     def name(self, value):
...         self._name = value
...
...     @name.deleter
...     def name(self):
...         del self._name
...
>>> person = Person('Aaron')
>>> person.__dict__['name'] = 'John'
>>> print(vars(person))
{'name': 'John', '_name': 'Aaron'}
>>> print(Person.name)
<property object at 0x1020f4b50>
>>> print(person.name)
Aaron
```

从上述示例中，我们可以看出，`person` 实例含有两个实例属性，即 `name` 和 `_name`；而 `Person` 类含有 `name` 属性，它是一个 `property` 类型的实例对象。原本上来说，当我们访问 `person` 实例的 `name` 属性时，返回的应该是 `person` 实例的 `name` 属性的值（`John`）才对，但实际上却是 `_name` 属性的值。因为数据描述符的查找顺序要优先于实例属性，因此首先找到了 `Person` 类的描述符属性 `name`，然后它又是用来控㓡 `person` 实例对象中 `_name` 属性的访问的，所以最终才会 `Aaron`，而不是 `John`。


#### 2.7.1.2 实例属性与非数据描述符

```python
>>> class Name(object):
...     def __init__(self, value):
...         self._name = value
...
...     def __get__(self, instance, owner):
...         return instance._name
...
>>> class Person(object):
...     def __init__(self, name):
...         self._name = name
...
...     name = Name('')
...
>>> person = Person('Aaron')
>>> person.__dict__['name'] = 'John'
>>> print(person.name)  # (1)
John
>>> person.__dict__.pop('name')
>>> print(person.name)  # (2)
Aaron
```

从上述示例中，我们可以看出，由于描述符类 `Name` 没有 `__set__`，因此是非数据描述符，所以它的查找顺序在实例属性之后，这正符合我们在第 (1) 步看到的结果，它显示的是 `person` 实例对象中的 `name` 属性。当我们把 `person` 实例对象中的 `name` 属性删除后，在第 (2) 步处，我们再次通过 `person` 实例来访问 `name` 属性的值，此时，它就显示描述符所管理的属性值。

我们再通过 `property` 来看看结果如何。

```python
>>> class Person(object):
...     def __init__(self, name):
...         self._name = name
...
...     @property
...     def name(self):
...         return self._name
...
>>> person = Person('Aaron')
>>> person.__dict__['name'] = 'John'
>>> print(person.name)
Aaron
```

虽然我们没有通过 `name.setter` 装饰器来设置 `fset` 成员属性，但 `property` 所控制的属性仍然优先于实例属性。从这里我们就应该知道，虽然我们没设置 `fset` 成员属性，但 `property` 仍然实现了 `__set__` 方法，因此它本身还是数据描述符。总结一下，不管我们是否设置 `fget`、`fset`、`fdel` 成员属性，`property` 始终会实现 `__get__`、`__set__`、`__del__` 等方法，然后在这些方法中分别调用 `fget`、`fset`、`fdel` 等成员属性；如果这些成员属性没有被设置（即为 `None`），在相应的 `__get__`、`__set__` 或 `__del` 方法中就会抛出异常。

#### 2.7.1.3 非数据描述符与 `__getattr__` 方法

```python
>>> class Name(object):
...     def __init__(self, value):
...         self._name = value
...
...     def __get__(self, instance, owner):
...         return instance._name
...
>>> class Person(object):
...     def __init__(self, name):
...         self._name = name
...
...     name = Name('')
...
...     def __getattr__(self, name):
...         return 'no found'
...
>>> person = Person('Aaron')
>>> print(person.name)
Aaron
>>> delattr(Person, 'name')  # Delete the non-data descriptor from the class.
>>> print(person.name)
no found
```

从上述示例中，我们可以看出，当存在非数据描述符时，它将显示非数据描述符所控制的属性的值；当我们删除非数据描述符后，`__getattr__` 方法将会被调用。这就说明了，非数据描述符的优先级要高于 `__getattr__` 方法的调用。
