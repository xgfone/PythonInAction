# 第 5 章 元类 MetaClass

> **元类** 比 99% 的用户所担心的魔力要更深。如果你犹豫是否需要它们，那你就不需要它们；真正需要元类的人，能够确定地知道需要它们，并且不需要说明为什么需要。  —— Time Peters

元类能允许我们拦截并扩展类的创建，为各种没有它而难以实现或不可能实现的编码模式打开了大门，并且对于那些追求编写灵活的 API 或编程工具供其他人使用的程序员来说，它特别有用。所以说，**`元类主要是针对那些构建 API 和工具供他人使用的程序员，而不是所有的程序员`**。

在大多数情况下，它们可能不是应用程序工作的最佳选择，甚至会不利于后续对使用元类的代码的维护。所以，尽管元类的威力强大且灵活，除非必要，不建议使用元类。

与装饰器的相同之处：都允许我们拦截并扩展类的创建。

与类装饰器的不同之处：类装饰器通常是在类的实例创建时运行，而元类是在类创建时运行。

## 5.1 介绍

在面向对象语言中，对象又叫实例，对象的类型叫类，类的类型也是类。也就是说，对象是由类创建，类是由另外一种特殊的类创建的。为了区分这种特殊的类，我们称之为元类（MetaClass）；元类控制着整个类的创建流程。

> 在一些非完全面向对象语言中，如 C++、Java，并没有类的类型这一概念，因此也没有元类的说法。这并不是说它们不是面向对象编程语言，而是说，它们不完全是，其主要原因是，在这些语言中，并不是一切皆对象，如 C++、Java 中的基本类型。

> **关于类和类型：**
>
> 在 Python 3 中，所有的类都是新式类，而且类和类型的概念已经合并了，基本上是同义词，即类是类型，类型也是类，所以我们没有必要过分地区分它们。

像所有的类都是 `object` 的子类一样，所有的元类都是 `type` 的子类。而且，所有的类都有元类来创建，甚至是元类自身也是由元类来创建；默认地，所有的类及元类都是由元类 `type` 来创建；`type` 的元类还是它自身。

在定义类时，如果没有指定元类，则默认为 `type`。如：
```python
>>> class Class(object):
...     pass
...
>>> type(Class)
<class 'type'>
```

但我们也可以在定义类时，通过 `meatclass` 关键字参数来指定一个特定的元类。如：
```python
>>> class Meta(type):
...     pass
...
>>> class Class(metaclass=Meta):
...      pass
...
>>> type(Class)
<class '__main__.Meta'>
```

如果一个类在定义时没有指定元类，则其元类继承为它的父类的元类。如：

```python
>>> class Meta(type):
...     pass
...
>>> class Class(metaclass=Meta):
...     pass
...
>>> class SubClass(Class):
...     pass
...
>>> type(SubClass)
<class '__main__.Meta'>
```

`Class` 在定义时通过关键字参数 `metaclass` 指定了其元类 `Meta`；而 `SubClass` 继承自 `Class`，但没有指定自己的元类，因此，它将继承自它的父类（`Class`）的元类（`Meta`）。但 `SubClass` 在继承的同时，也可以重载其元类。比如：

```python
>>> class SubMeta(Meta):
...     pass
...
>>> class SubClass(Class, metaclass=SubMeta):
...     pass
...
>>> type(SubClass)
<class '__main__.SubMeta'>
```

此时，`SubClass` 的元类就是 `SubMeta`，而不再是 `Meta`。

在定义类 `SubClass` 时，我们可以指定其父类以实现继承，这个大家都很理解。但后面却又可以指定关键字参数，这可能会让大家有些困惑。这一点和其它编程语言不同。下面我们来解释一下。

不仅函数和方法是可调用对象，其实类本身也是可调用对象，而且可调用性不仅体现在实例化时，还体现在类创建时。

我们看到，类的定义头 `class SubClass(Class, metaclass=SubMeta)` 和函数的定义头很像，都是一个关键字开头（`def` 或 `class`），后面跟着一个函数名或类名，以及一个参数列表；在参数列表中，既可以指定位置参数，也可以指定关键字参数，且位置参数在前，关键字参数在后。不同的是，在类的定义中，参数必须是明确的，不能像函数定义一样写成 `*args` 和 `**kwargs`，而且位置参数必须是已定义好的父类（用于继承），关键字参数是必须 `metaclass` 或者传递给元类的参数（最终传递给了父类中的 `__init_subclass__` 方法，见后文）。


## 5.2 元类创建自定义类的流程

在学习 Python 中，我们始终要在心中记住一句话：**Python 中所有的语句都是可以运行的，且是实时运行的。** 因此，类的定义也是可运行的。在用 `class` 关键字定义类时，就像是在调用一个函数来创建类，其参数指明了用什么来创建（即哪个元类）、继承哪些父类、以及子类初始化参数有哪些。调用结束，类也就创建完成了，其创建流程（或顺序）如下：

1. 确定 `MRO`（Python 3.7 新增）；
2. 确定合适的元类；
3. 准备类的命名空间（其实就是为类创建一个字典来存放属性）；
4. 执行类的定义体（类定义体作用域中的所有赋值语句都会存储到类的命名空间中）；
5. 创建类对象（因为类本身也是一个对象）。

### 5.2.1 确定 `MRO`

Python 是一门面向对象编程语言，因此是支持继承特性的，甚至支持多继承。但多继承会产生一些问题，如二义性，因此，Python 使用 `MRO`（Method Resolution Order，方法解析顺序）方法来解决这些问题。

定义类时，如果没有指定了父类，则默认为 `object`。所以，无论是否指定父类，在定义一个新类时，始终会有一个父类元组（即一组父类的集合列表）用来表示这个新类的多继承关系，哪怕这个父类元组中只有一个父类（即 `object`）。此时，Python 就会在运行时（即创建此类时）根据父类元组中父类的顺序计算出 `MRO`。这个算法在 Python 内部实现，改变 `MRO` 的唯一方式就是改变父类元组，即父类及其顺序。

这在 3.7 版本之前是不可能的；但从 3.7 版本开始，Python 解析器才添加了这个步骤，允许用户改变原始的父类元组，进而改变 `MRO`。其算法如下：如果在类定义中的父类不是 `type` 的实例，则查找 `__mro_entries__` 方法是否存在；如果存在，则以原始父类元组作为参数来调用它，而且它必须返回一个用于代替原始父类元组的新的类型元组；但它可以返回空，此时将会忽略原始的父类元组。

关于 `MRO`，有兴趣地可以参考一下这方面的文章，但不用过分地关心它，了解一下即可。


### 5.2.2 确定合适的元类

元类的确定将会按照下面的顺序来执行：

1. 如果没有父类且没有显示通过 `metaclass` 关键字参数来指定，则使用 `type`。
2. 如果通过 `metaclass` 关键字参数显示指定元类，但它又不是 `type` 的实例（也即是它不是一个元类类型），则该实例直接使用元类来使用。
3. 如果通过 `metaclass` 关键字参数显示指定的元类是 `type` 的实例，或者父类被指定，则最终派生出的元类会被使用。

对于第二种情况，就是说我们通过 `metaclass` 关键字参数指定的值不是元类类型，比如它可能是一个函数，但该函数却可以返回一个自定义类。如：
```python
>>> def func(classname, supers, classdict):
...     print('The metaclass is a function.')
...     return type(classname, supers, classdict)
...
>>> class Class(metaclass=func):
...     pass
...
The metaclass is a function.
>>> type(Class)
<class 'type'>
```

对于第三种情况，无论是通过 `metaclass` 关键字参数指定元类，还是从父类中继承元类，它些元类都是真正的元类类型，而不会是其它的可调用对象（如函数）。但是这些元类必须构成一条继承链，**最终派生出的元类** 即是继承链最底部的那个元类类型，同时也是自定义类的元类。如：
```python
... class MetaClass1(type):
...     pass
...
>>> class MetaClass2(MetaClass1):
...     pass
...
>>> class MetaClass3(MetaClass2):
...     pass
...
>>> class ParentClass1(metaclass=MetaClass1):
...     pass
...
>>> class ParentClass2(object, metaclass=MetaClass3):
...     pass
...
>>> class ChildClass(ParentClass1, ParentClass2,
...                  metaclass=MetaClass2):
...     pass
...
>>> type(ChildClass)
<class '__main__.MetaClass3'>
```

我们可以看出，`ChildClass` 的父类是 `ParentClass1` 和 `ParentClass2`，它们的元类分别是 `MetaClass1` 和 `MetaClass3`。因此，`ChildParent` 的元类集合为 `(MetaClass1, MetaClass3, MetaClass2)`，它们构成了一条继承链，`MetaClass1 -> MetaClass2 -> MetaClass3`，而最终派生出的元类就是 `MetaClass3`，也即是自定义类 `ChildClass` 的元类。

如果此时，我们把 `MetaClass3` 继承自 `MetaClass1`，而非 `MetaClass2`，则它们就构成不一条继承链，而是两个，此时就无法确定自定义类 `ChildClass` 的元类，因而会抛出 `TypeError` 异常。


### 5.2.3 准备类的命名空间

一旦确定了元类，就可以准备类的命名空间。如果元类含有 `__prepare__` 属性，则调用它来产生类的命名空间，方式为 `namespace = metaclass.__prepare__(name, bases, **kwargs)`，其中的 `kwargs` 关键字参数均来自于类定义中的关键字参数。

如果元类没有 `__prepare__` 属性，默认就初始化一个可排序的空字典来作为类的命名空间。


### 5.2.4 执行类的定义体

类定义体的执行有点类似于 `exec(body, globals(), namespace)`，但与 `exec()` 相比，类定义体的执行有个主要区别：当在函数内定义一个类时，词法作用域允许类的定义体（包括任何方法的定义）直接引用当前作用域或外围作用域中的变量名。但是，不管一个类是否被定义在函数中，在类定义体中定义的方法都不能直接访问定义在类作用域中的名字（即这些名字属于类本身的属性）；如果要想访问它们，必须通过类或类的实例来引用。

在执行类的定义体时，将填充类的命名空间。


### 5.2.5 创建类对象

一旦执行完类的定义体，类的所有属性值（包括所有的方法定义）都会存储在类的命名空间中。此时 Python 解析器就会调用元类来创建类对象（即一个类型），如 `metaclass(name, bases, namespace, **kwargs)`，其中的 `kwargs` 关键字参数同 `__prepare__` 一样，也均是来自于类定义中的关键字参数。

> **Python 3.6 新增：**
>
> 如果元类是 `type` 或者自定义元类最终调用了 `type.__new__`，则在创建类对象后，`type.__new__` 还会执行以下额外的步骤：
> 1. 收集类命名空间中所有定义了 `__set_name__()` 方法的描述符并调用它们；
> 2. 调用刚创建的类对象的父类中的 `__init_subclass__()` 方钩子。见后文。

最后，如果类定义中还指定了装饰器，则将其作为参数调用装饰器，然后将装饰器返回的值作为自定义类重新绑定到本地命名空间（见《装饰器》一章）。

至此，有了类对象（即类型），我们就可以通过它来创建实例了。


## 5.3 手工创建自定义类

我们已经学习到，可以通过 `class` 关键字来自定义一个类，而且 `class` 类定义语句本身是实时运行的（相当于一个函数或方法调用）。所以，我们也可以不用 `class` 关键字，直接通过元类按照创建类的流程来手工创建一个新类。

说明：
1. 确定 `MRO`：这个是为了改变原始的父类元组，但我们在手工创建新类时，可以指定父类元组，因此这一步可以忽略。
2. 确定合适的元类：我们本身就是使用特定的元类来创建新类的，因此这一步也可以忽略。
3. 准备类的命名空间：我们新建一个空字典即可。
4. 执行类的定义体：由于执行类的定义体时，其作用域中的变量赋值和函数或方法定义都存储到了类的命名空间中。所以，我们可以直接把类的属性和方法都放到上一步的空字典中。
5. 创建类对象：直接调用特定的元类即可。

注意：对我们手工创建类来说，第三步和第四步可以合为一步。因此，上述五步可以简化成两步：
1. 准备一个字典，里面存放类的所有属性和方法。
2. 调用特定的元类。

元类的原型是：`metaclass(name, bases, namespace, **kwargs)`。其中，`name` 是自定义类的名字，它最终会变成自定义类的 `__name__` 属性；`bases` 是自定义类的父类元组或列表，它最终会变成自定义类的 `__bases__` 属性；`namespace` 是一个字典，用来存放自定义类的属性和方法，它最终会变成自定义类的 `__dict__` 属性；`kwargs` 和 `class` 定义中的关键字参数一样。

我们来看一个示例：

```python
>>> def instance_method(self, *args, **kwargs):
...     print(args, kwargs)
...
>>> @classmethod
... def class_method(cls, *args, **kwargs):
...     print(args, kwargs)
...
>>> @staticmethod
... def static_method(cls, *args, **kwargs):
...     print(args, kwargs)
...
>>> def init(self, name):
...     self.name = name
...
>>> namespace = {
...     'attr': 123,
...     '__init__': init,
...     'instance_method': instance_method,
...     'class_method': class_method,
...     'static_method': static_method,
... }
...
>>> Class = type('Class', (object,), namespace)
>>> Class
<class '__main__.Class'>
>>> type(Class)
<class 'type'>
>>> obj = Class('Aaron')
>>> obj.name
'Aaron'
>>> obj.instance_method
<bound method instance_method of <__main__.Class object at 0x0000021A43B5D198>>
>>> obj.class_method
<bound method class_method of <class '__main__.Class'>>
>>> obj.static_method
<function static_method at 0x0000021A437BB730>
```

除了使用元类 `type` 外，我们也可以用自定义的元类来创建一个普通类。比如：
```python
>>> class MetaClass(type):
...     pass
...
>>> Class = MetaClass('Class', (object,), namespace)
>>> obj = Class('Aaron')
>>> obj.name
Aaron
```

甚至，我们还可以用自定义的元类再创建出另外一个元类，只要其父类指定为 `type` 或其它的元类类型即可，如：
```python
>>> class MetaClass(type):
...     pass
...
>>> Meta = MetaClass('Meta', (type,), {})
>>> Class = Meta('Class', (object,), namespace)
>>> obj = Class('Aaron')
>>> obj.name
Aaron
```

因此，我们不仅可以使用 `class` 关键字来创建一个自定义类（普通类或元类），而且还可以手工一步步创建。从这点来看，`class` 定义法可以看作是一个语法糖。


## 5.4 元类方法

### 5.4.1 `__new__` 和 `__init__`

在自定义元类时，我们可以重载 `__new__` 和 `__init__` 方法以达到修改或扩展自定义类的目的。

`__new__` 和 `__init__` 的原型分别是
```python
metaclass.__new__(metaclass, classname, superclasses, classdict)
metaclass.__init__(cls, classname, superclasses, classdict)
```
其中，`metaclass` 就是自定义的元类本身，`classname` 是自定义类的名称，`superclassess` 是自定义类的父类（又叫基类、超类）元组集合，`classdict` 是自定义类的属性字典集合；`cls` 是自定义类。

一个对象的创建主要分为两步：一是分配内存，二是初始化内存。其中，`__new__` 就是用于分配内存，而 `__init__` 用于初始化内存。因此，`__new__` 必须返回一个新的自定义类，而 `__init__` 只须初始化 `__new__` 返回的自定义类，并不须要返回任何值。

```python
>>> class MetaClass(type):
...     def __new__(mcs, classname, supers, classdict, **kwargs):
...         print('before calling metaclass_new')
...         cls = type.__new__(mcs, classname, supers, classdict, **kwargs)
...         print('after calling metaclass_new')
...         return cls
...     def __init__(cls, classname, supers, classdict, **kwargs):
...         print('before calling metaclass_init')
...         type.__init__(cls, classname, supers, classdict, **kwargs)
...         print('after calling metaclass_init')
...
>>> Class = MetaClass('Class', (object,), namespace)
before calling metaclass_new
after calling metaclass_new
before calling metaclass_init
after calling metaclass_init
>>> type(C)
<class '__main__.MetaClass'>
```

### 5.4.2 `__call__`

元类不仅能控制自定义类的创建，还能影响自定义类创建对象，只要在元类中定义一个 `__call__` 方法即可，其原型为：
```python
metaclass.__call__(cls, *args, **kwargs)
```
其中，`cls` 为自定义类，`args` 和 `kwargs` 均是自定义类实例时的参数。如：

```python
>>> class Meta(type):
...     def __call__(cls, *args, **kwargs):
...         print('before calling methclass __call__')
...         obj = type.__call__(cls, *args, **kwargs)
...         print('after calling methclass __call__')
...         return obj
...
>>> class Class(metaclass=Meta):
...     def __new__(cls):
...         print('allocating the memory')
...         return super().__new__(cls)
...
...     def __init__(self):
...         print('initializing the instance')
...
>>> obj = Class()
before calling methclass __call__
allocating the memory
initializing the instance
after calling methclass __call__
```

### 5.4.3 `__init_subclass__`

> 这是从 Python 3.6 开始新增的一个类方法。

这个方法可以用来在父类中控制子类的行为，所以，它是作为一个类方法定义在父类中的，并在发生继承时被调用。它有点类似于类装饰器，但类装饰器仅仅影响被它装饰的类，而 `__init_subclass__` 却可以影响它的所有子类。

注意，如果我们把 `__init_subclass__` 定义成一个普通的实例方法，Python 会隐式地将其转换成类方法。也就是说，不管我们如何定义 `__init_subclass__` 方法，最终它都会变成一个类方法。其中，第一个参数即是子类，其余参数为来源于子类，其原型为
```python
metaclass.__init_subclass__(cls, *args, **kwargs)
```

当在子类继承父类时，如果指定了关键字参数，这些关键字参数将传递给父类的 `__init_subclass__` 方法，即原型中的 `args` 和 `kwargs` 参数。比如：

```python
class ParentClass:
    def __init_subclass__(cls, default_name):
        cls.default_name = default_name


class ChildClass(ParentClass, default_name='Aaron'):
    pass
```

当然，`__init_subclass__` 也可以接收多个关键字参数，此时它既可以处理全部参数，也可以只处理部分参数，然后把剩余的关键字参数传递给更上一级的父类。比如：

```python
class ParentClass:
    @classmethod
    def __init_subclass__(cls, default_name, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.default_name = default_name


class ChildClass(ParentClass, default_name='Aaron', default_age=0):
    pass
```

但是，要注意，要想把多余的关键字参数传递给上一级的父类，上一级的父类一定要能处理，否则将会抛出一个 `TypeError` 异常。比如，上面的示例中就会抛出 `TypeError` 异常。原因是，`ChildClass` 在继承时指定了两个关键字参数 `default_name` 和 `default_age`，在 `ParentClass` 父类中只处理了 `default_name`，并把 `default_age` 传递给了上一级父类（即 `object`）。然而，`object` 中的 `__init_subclass__` 默认不做任何事，且也不接收任何参数。

我们来看一下完整的例子：

```python
>>> class ParentClass:
...     @classmethod
...     def __init_subclass__(cls, default_name):
...         cls.default_name = default_name
...
>>> class ChildClass(ParentClass, default_name='Aaron'):
...     pass
...
>>> obj = ChildClass()
>>> obj.default_name
Aaron
```

#### 5.4.3.1 `__init_subclass__` 与 `metaclass` 的区别

`__init_subclass__` 和 `metaclass` 共同完成对子类行为的改变，并不冲突；它们只是被调用的先后顺序不同而已。

我们可以这样理解，原先的一套元类处理类型的机制与流程不变，现在，我们只不过在执行元类的过程中，又添加了对 `__init_subclass__` 方法的调用，而其之前的类定义的执行顺序仍然不变。

我们来验证一下：
```python
>>> class MetaClass(type):
...     def __new__(mcs, classname, supers, classdict, **kwargs):
...         print('start to call metaclass')
...         cls = super().__new__(mcs, classname, supers, classdict, **kwargs)
...         print('end to call metaclass')
...         return cls
...
>>> class ParentClass:
...     def __init_subclass__(cls, default_name):
...         print('calling __init_subclass__')
...         cls.default_name = default_name
...     def __new__(cls, *args, **kwargs):
...         print('calling ParentClass.__new__')
...         return super().__new__(cls, *args, **kwargs)
...     def __init__(self):
...         print('calling ParentClass.__init__')
...         super().__init__()
...
>>> class ChildClass(ParentClass, metaclass=MetaClass, default_name='Aaron'):
...     def __new__(cls, *args, **kwargs):
...         print('calling ChildClass.__new__')
...         return super().__new__(cls, *args, **kwargs)
...     def __init__(self):
...         print('calling ChildClass.__init__')
...         super().__init__()
...
start to call metaclass
calling __init_subclass__
end to call metaclass
>>> obj = ChildClass()
calling ChildClass.__new__
calling ParentClass.__new__
calling ChildClass.__init__
calling ParentClass.__init__
>>> obj.default_name
Aaron
```

从上面的示例中可以看出，在创建子类 `ChildClass` 时，先调用了元类 `MetaClass`，然后在其处理过程中调用父类 `ParentClass` 的 `__init_subclass__` 方法。这个调用是在元类 `type` 的 `__new__` 默认实现中完成的（见前文）。

另外，我们须要注意的是，在继承时，如果既指定了自定义的元类，又使用了带关键字的参数，那么在自定义元类中，`__new__` 必须能够接纳这些关键字参数，就像上面示例的中 `**kwargs` 一样。

我们再以手工创建类的方式来验证一下：

```python
>>> class MetaClass(type):
...     def __new__(mcs, classname, supers, classdict, **kwargs):
...         print('start to call metaclass')
...         cls = super().__new__(mcs, classname, supers, classdict, **kwargs)
...         print('end to call metaclass')
...         return cls
...
>>> class ParentClass:
...     def __init_subclass__(cls, default_name):
...         print('calling __init_subclass__')
...         cls.default_name = default_name
...     def __new__(cls, *args, **kwargs):
...         print('calling ParentClass.__new__')
...         return super().__new__(cls, *args, **kwargs)
...     def __init__(self):
...         print('calling ParentClass.__init__')
...         super().__init__()
...
>>> def _init(self):
...     print('calling ChildClass.__init__')
...     ParentClass.__init__(self)
...
>>> def _new(cls, *args, **kwargs):
...     print('calling ChildClass.__new__')
...     return ParentClass.__new__(cls, *args, **kwargs)
...
>>> namespace = {
...     '__init__': _init,
...     '__new__': _new,
... }
...
>>> ChildClass = MetaClass('ChildClass', (ParentClass, object),
...                        namespace, default_name='Aaron')
start to call metaclass
calling __init_subclass__
end to call metaclass
>>> obj = ChildClass()
calling ChildClass.__new__
calling ParentClass.__new__
calling ChildClass.__init__
calling ParentClass.__init__
>>> obj.default_name
Aaron
```

注意，通过这种方式来自定义类时，在自定义类的方法（如 `_init` 和 `_new`）中，我们不能使用 `super()` 来自动计算出 `MRO` 中正确的父类，必须指定特定的父类。其实，只有在继承多个类时，我们才考虑具体调用哪个父类，而父类只有一个时，至于是用 `super()` 还是用父类，就没有什么太大的区别了。


### 5.4.3 总结

虽然元类是用来创建类的特殊类，但它本质上仍然还是一个类，因此，它仍具备类的特性和约束。

1. 当我们调用元类创建自定义类时，元类会像自定义类一样，先调用 `__new__` 方法，后调用 `__init__` 方法；前者为自定义类分配存储，后者初始化自定义类。从这方面，我们也可以看出，自定义类就是元类的实例对象，元类就是自定义类的类型。
2. 既然自定义类是元类的实例对象，那么，当调用自定义类时（也即是用自定义类实例化一个对象时），其实是在调用自定义类的类型中定义的 `__call__` 方法,即元类的 `__call__` 方法，而不是自定义类中定义的 `__call__` 方法；只有当调用自定义类的实例时，才是在调用自定义类中的 `__call__` 方法。所以，我们才可以在元类中定义一个 `__call__` 方法来控制自定义类如何创建一个实例对象。
3. `__init_subclass__` 方法是在 `type` 元类的 `__new__` 方法中调用的，它本质上和元类机制并不冲突，只不过是元类机制中新增的一个步骤，可以允许用户在不显示地使用元类的情况下通过父类就可以控制子类的创建。


## 5.5 Python 2 中的元类使用

在 Python 3 中是通过 `metaclass` 关键字参数在自定义类头中指定，但在 Python 2 中，则是通过 `__metaclass__` 属性来指定。如：
```python
class MetaClass(type):
    pass

class Class(object):
    __metaclass__ = MeatClass
```

无论是 `metaclass`，还是 `__metaclass__`，它们的值的要求和约束都是一致的，只是名字和使用方式不同罢了。

在 Python 2 中，也是可以按照之前的步骤进行手工创建一个自定义类的。因为这时不再使用 `metaclass` 或 `__metaclass__` 了，所以也就没有什么区别了。


## 5.6 小结

元类是用来创建类的类，并且所有的类都是由元类创建，甚至元类本身也是由元类创建的。

所有的元类都继承自 `type`，即所有的元类都是 `type` 的子类，就像所有的普通类都是 `object` 的子类一样。注意，元类不是 `object` 的子类。

在派生子类时，元类的声明是可以被继承，但它的属性是不会被子类继承的；子类只会继承父类中的属性，而不是元类中的属性，它继承的元类仅仅是一个声明而已，即父类用什么样的元类，子类也会用什么样的元类。因此，在子类中查找某个属性时，如果没有找到，则会从父类查找，但不会从它的元类中查找。

`class` 关键只是一个快速创建类的语法糖。除了这种方式外，我们也可以手工一步步来创建一个类。
