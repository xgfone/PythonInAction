
# 第 6 章 C/C++ 扩展

学习过 Python，我们都知道，Python 有以下缺点：
1. 动态语言，运行慢，而且还没有 JIT。
2. 虽然有多线程机制，但由于 GIL 的存在，导致多线程不能在同一时刻充分利用多核 CPU。

在对性能要求比较苛刻的业务逻辑上，我们可以使用 Python 中的 C/C++ 扩展机制来实现。由于 C/C++ 扩展是由 C/C++ 实现的，所以在性能上要远优于 Python 代码，不亚于其它存 C/C++ 实现的代码；同时，在避免访问 Python 解析器中数据下，就可以绕过 GIL 的限制，从而充分利用多核 CPU。

另外，在 C/C++ 扩展的帮助下，我们的 Python 程序不仅能调用 Python 模块，而且还可以调用其它 C/C++ 模块，进而使用那些非 Python 编写的模块或库。

在编译 C/C++ 扩展模块时，系统须要事先安装 C/C++ 编译环境和 Python 开发头文件和链接库。C++ 兼容于 C，所以这里我们使用 C 语言来作讲解，C++ 同理。后文的讲解的示例原则上可以在 Unix/Linux、MacOS、Windows 上编译，但在实验时建议在 Linux 下进行，这样会避免一些环境安装不正确的错误。

注意，本章所讲的 C/C++ 扩展特定于 Python 的官方实现 CPython，它可以并不工作于其它的 Python 实现。同时，要注意，C/C++ 扩展可能不利于系统的移植，且更难移植到其它的 Python 实现；所以，除非必要，尽量不要使用 C/C++ 扩展。


## 6.1 扩展模块格式

当然，C 扩展模块的前提必须是个 C 源文件，但这个 C 源文件作为 Python C 扩展模块时，却是有一些格式要求：

1. 必须包含 Python 头文件（`#include<Python>`），而且这个头文件必须在任何标准头文件之前被包含，因为 Python 可能会做一些预处理，从而在一些系统上来影响标准头文件。
2. 定义一个模块初始化函数（一个 C/C++ 扩展即为一个 Python 模块），并在该函数中初始化此模块。
3. 模块名必须是一个合法的 Python 标识符，因为它可以作为一个变量名被使用。

注意，模块名尽量都是小写字母，因为 Python 是区分大小的，而一些系统对文件名却不区分大小，此时有可能造成名字错误。

模块初始化函数的接口原型为 `PyMODINIT_FUNC ModuleName(void)`。但是，在 Python 2 和 3 下却有些区别：
1. 返回值 `PyMODINIT_FUNC`，在 Python 2 中是 `void`，在 Python 3 中是 `PyObject *`；所以，在函数中执行 `return` 时要特别注意。
2. 模块名 `ModuleName`，在 Python 2 必须以 `init` 开头，在 Python 3 中必须以 `PyInit_` 开头；它们其后的字符串才是真正的模块名。

除了模块初始化函数接口原型，Python 模块的注册在 Python 2 和 3 中也有所不同：
1. 在 Python 2 中，由于初始化函数没有返回值，因此使用函数 `Py_InitModule`、`Py_InitModule3` 或 `Py_InitModule4` 创建并注册 C/C++ 扩展模块。
2. 在 Python 3 中，初始化函数的返回值即为 C/C++ 扩展模块，因此，不需要显式地注册，在加载 C/C++ 扩展模块时，Python 会自动地把初始化函数的返回值作为一个模块进行注册。

所以，在 Python 3 的模块初始化函数中，只须使用函数 `PyModule_Create` 或 `PyModule_Create2` 创建好 C扩展模块即可。`Py_InitModule` 系列函数有两个功能：创建模块和注册模块。而 `PyModule_Create` 系列函数只会创建模块，并不会注册。

在第一次 `import` 一个 C/C++ 扩展模块时，Python 解析器会首先运行该模块的初始化函数，初始化并注册该模块到 Python 的模块系统中。但是，Python C/C++ 扩展模块并没有卸载函数。在 Python 中，所有已加载的模块都保存在 `sys.modules` 中；我们只要把相应的模块从 `sys.modules` 中删除，该模块就相当于被卸载。当该模块再次被 `import` 时，它的模块初始化函数会再次被调用。不过，虽然我们把一个模块从 `sys.modules` 中删除，但只要还有其它模块引用它，该模块就会一直存在；只有所有模块都不再引用它时，GC 就会将其回收，相应的析构函数也会被调用。所以，为了在模块被完全卸载（即模块被 GC 回收）时清理模块，我们可以为该模块设置一个析构函数。

注意，最终编译生成的 C/C++ 扩展模块的名字，除了后缀扩展名外，剩余的名字必须是模块名的名字，否则在导入时会失败。因为，当我们在通过模块名导入一个模块时，Python 会先通过模块名找到对应的文件；如果该文件是一个 C/C++ 扩展模块文件，则根据模块名拼接出初始化函数名，然后调用它。这也是我们要求模块文件的名字必须是模块名的原因。

至此，我们就可以创建一个最小的 C/C++ 扩展模块了（假定模块名为 hello）。如:

```c
// For python 2
#include<Python.h>

PyMODINIT_FUNC
inithello(void)
{
    (void)Py_InitModule("hello", NULL);
}
```

或

```c
// For Python 3
#include<Python.h>

static struct PyModuleDef hello = {
    PyModuleDef_HEAD_INIT,

    .m_name = "hello",
    .m_size = -1,
};

PyMODINIT_FUNC
PyInit_hello(void)
{
    return PyModule_Create(&hello);
}
```

为了兼容 Python 2 和 3，我们可以通过版本判断将其合在一起，如:

```c
#include<Python.h>

#if PY_MAJOR_VERSION < 3
PyMODINIT_FUNC
inithello(void)
{
    (void)Py_InitModule("hello", NULL);
}
#else
static struct PyModuleDef hello = {
    PyModuleDef_HEAD_INIT,

    .m_name = "hello",
    .m_size = -1,
};

PyMODINIT_FUNC
PyInit_hello(void)
{
    return PyModule_Create(&hello);
}
#endif
```

为了便捷，我们可以定义如下几个宏：

```c
#if PY_MAJOR_VERSION < 3
#   define MOD_INIT_FUNC(name) PyMODINIT_FUNC init##name(void)
#   define MOD_INIT_RETURN(value) return;
#else
#   define PYTHON3
#   define MOD_INIT_FUNC(name) PyMODINIT_FUNC PyInit_##name(void)
#   define MOD_INIT_RETURN(value) return value;
#endif
```

我们现在来改写一下上述 C 模块（假定其文件名为 `hello.c`）：

```c
#include<Python.h>

#if PY_MAJOR_VERSION < 3
#   define MOD_INIT_FUNC(name) PyMODINIT_FUNC init##name(void)
#   define MOD_INIT_RETURN(value) return;
#else
#   define PYTHON3
#   define MOD_INIT_FUNC(name) PyMODINIT_FUNC PyInit_##name(void)
#   define MOD_INIT_RETURN(value) return value;
#endif

MOD_INIT_FUNC(hello)
{
#ifndef PYTHON3
    (void)Py_InitModule("hello", NULL);
#else
    static struct PyModuleDef hello = {
        PyModuleDef_HEAD_INIT,

        .m_name = "hello",
        .m_size = -1,
    };
    return PyModule_Create(&hello);
#endif
}
```


## 6.2 编写 `setup.py` 脚本

编写完 C/C++ 扩展模块的源代码，我们还要把它编译成动态链接库；它和普通的动态链接库有点不同：它可以被 Python 导入。

编译 C/C++ 扩展模块有两种方式：一种手工调用命令行编译器和链接器，另一种是使用 Python 内建的打包脚本 `setup.py`。其中，手工编译方式需要针对不同的平台调用不同的编译器和链接器，须要编写大量的平台兼容编译脚本；而且，当源代码文件比较多时，管理起来比较繁琐且易出错。相反，Python 内建的 `setup.py` 脚本已经针对不同的平台做了兼容处理，且能自动化编译 C/C++ 源代码；因此，使用 `setup.py` 脚本可以快速地编写 C/C++ 扩展模块的编译方式。

> **setup.py 脚本**
>
> `setup.py` 脚本使用的是 Python 的标准库 `distutils`，它不仅能编译 C/C++ 扩展模块，还是一个官方的打包工具。
>
> `setup.py` 脚本的名字并不一定叫 `setup.py`，也可以是其它的名字，这并不是强制的。虽是如此，但 `setup.py` 却是约定成俗的名字，而且当使用 Python 的包管理工具安装 Python 包时，将会自动运行名为 `setup.py` 的脚本。所以，我们还是尽量把我们的打包脚本命名为 `setup.py` 为好。

`setup.py` 脚本很简单，主要分为两步：
1. 从标准库 `distutils` 中导入打包函数 `setup`。
2. 调用 `setup` 函数。

现在，我们来为上一节中的 C/C++ 扩展模块 `hello` 编写 `setup.py` 脚本。

```python
from distutils.core import setup, Extension

hello_module = Extension('hello', sources=['hello.c'])

setup(name='hello',
      version='1.0',
      description='This is a hello package',
      ext_modules=[hello_module])
```

此时的目录结构为：
```shell
$ tree .
.
├── custom.c
└── setup.py

0 directories, 2 files
```

然后，我们就可以在当前目录下运行 `setup.py` 脚本来编译 `hello` 扩展模块了。如：
```shell
$ python setup.py build
```

运行结束后，在当前目录下就会出现一个 `build` 目录，最终构建出来的 Python 模块就位于其中；对于不同的平台、不同的 Python 版本，最终生成的 Python 模块名可以略有不同，但是仍然可以直接通过 `import hello` 来导入。


## 6.3 为扩展模块添加函数

在 Python 的模块中，定义一个函数，就相当于在这个模块中做一个赋值操作，其中，变量名为函数的名字，赋的值就是所定义的函数。

因此，在 C/C++ 扩展模块中，给模块添加一个函数，其步骤分解为：
1. 定义一个 Python C 函数；
2. 将 Python C 函数包装成一个方法（对于模块而言，它就相对于一个方法）；
3. 将该方法添加到模块中。

### 6.3.1 定义 C 函数

Python C 函数的原型有三种：
```c
PyObject* (FUNCTION_NAME)(PyObject *self)
PyObject* (FUNCTION_NAME)(PyObject *self, PyObject *args)
PyObject* (FUNCTION_NAME)(PyObject *self, PyObject *args, PyObject *kwargs)
```

至于是哪种原型，这依赖于函数的具体调用方式（依赖于方法的标志，见下一小节）：第一种是无参数（`METH_NOARGS`）调用，第二种是只有位置参数（`METH_VARARGS`）调用，第三种有位置参数（`METH_VARARGS`）和关键字参数（`METH_KEYWORDS`）调用。但是对于第一个参数 `self`，在 Python 2 中，它 `None` 对象；在 Python 3 中，它是当前的模块对象。

如果返回值为 `NULL`，一个异常应当被设置，此时当执行流程再次返回到 Python 运行时，就会抛出此异常。如果不想返回任何值（就像没有 `return` 语句的 Python 函数），可以返回 `Py_None`（即 Python 中的 `None`）。总之，如果返回值不是 NULL，它就会被作为函数的返回值返回给调用者。但是，要注意，这个返回值必须是一个新引用（A New Reference），即返回值如果不是新创建的，就要使用 `Py_INCREF` 宏增加其引用计数，以避免被 GC 回收。

下面我们来实现一个 Python C 函数，它将打印 `"hello, world"`。

```c
static
PyObject* hello_printf(PyObject* self, PyObject* args)
{
    // Print "hello, world" to stdout.
    PySys_WriteStdout("hello, world\n");

    // return None
    Py_INCREF(Py_None);
    return Py_None;
}
```

注意，在定义 Python C 函数时，如非特殊，一般建议将其定义为 `static`，此时该函数的作用域就会被限定在此源码文件中，不会与其它文件中的函数名发生冲突。


### 6.3.2 函数变方法
在 CPython 中，其方法类型为 `PyMethodDef`，它有四个成员，分别为：`ml_name`（方法的名字）、`ml_meth`（方法的实现，即一个 Python 函数）、`ml_flags`（标记，即如何调用 Python 函数）、`ml_doc`（方法的文档）。

把 Python 函数变成一个方法，就是重新定义一个 `PyMethodDef` 类型的变量，并填充其四个成员，如：
```c
static PyMethodDef hello_method = {
    "printf",
    (PyCFunction)hello_printf,
    METH_NOARGS, // call printf without arguments
    "Print the hello world.",
};
```

#### 6.3.2.1 方法标志

不管任何方法标志，三种函数接口原型都可以使用，但对参数的使用要求有些区别。

下面我们来介绍一下方法的标志是如何影响 Python C 函数接口以及调用的。

`METH_NOARGS` 表示以无任何参数调用函数，第二个参数 `args` 始终为 NULL，而第三个参数 `kwargs` 不能在函数体中访问，否则将可能出现段错误。

`METH_VARARGS` 表示只能以位置参数的方式调用函数（位置参数可以为空），而且，第二个参数 `args` 的类型是一个元组。但对于第三个参数 `kwargs`，在 Python 2 和 3 中却略有不同：在 Python 2 中，该参数不能访问，否则将可能出现段错误；在 Python 3 中，它为 `NULL`。

`METH_KEYWORDS` 表示可以以位置参数和关键字参数的方式调用函数，并且，第二个参数 `args` 的类型是元组，第三个参数 `kwargs` 的类型是字典。

因此，为了兼容性，在定义 Python C 函数时，均可以使用最后一种原型。但在函数体中，对于无参数调用，不要访问后两个参数；对于仅位置参数调用，不要访问最后一个参数。


### 6.3.3 添加方法到模块
注意，当把方法添加到模块中时，不是一个一个地添加，而是所有的方法作为一个方法集（即数组）一起被添加进去。所以，方法集可以写作：
```c
static PyMethodDef hello_methods[] = {
    {
        "printf",
        (PyCFunction)hello_printf,
        METH_NOARGS, // call printf without arguments
        "Print the hello world.",
    },
    {NULL} // it's said to end.
};
```

在 Python 2 中，当调用 `Py_InitModule` 系列函数初始化模块时，可以为该模块指定相应的模块方法。如：
```c
Py_InitModule('hello', hello_methods);
```

但是在 Python 3 中，我们须要明确地定义一个模块类型的变量，因此，可以在该变量的方法字段中指明，如：
```c
static struct PyModuleDef hello = {
    PyModuleDef_HEAD_INIT,

    .m_name = "hello",
    .m_size = -1,
    .m_methods = hello_methods,
};
```

从 3.5 版本开始，Python 支持多阶段模块创建。也即是，原本的模块创建是一步到位，现在可以将其分多步进行，就像创建对象时可以分成 `__new__` 和 `__init__` 两步一样。为了支持多阶段模块创建，CPython 添加了一个 C/C++ 方法 `PyModule_AddFunctions`，它可以为已经创建好的模块再次添加方法集，其原型为
```c
int PyModule_AddFunctions(PyObject *module, PyMethodDef *methods)
```

在 3.5 版本以后，我们也可以这样写：
```c
static struct PyModuleDef hello = {
    PyModuleDef_HEAD_INIT,

    .m_name = "hello",
    .m_size = -1,
};
PyObject *module = PyModule_Create(&hello);
if (module != NULL) {
    PyModule_AddFunctions(module, hello_methods);
}
```

### 6.3.4 完整示例：

```c
// hello.c

#include<Python.h>

#if PY_MAJOR_VERSION < 3
#   define MOD_INIT_FUNC(name) PyMODINIT_FUNC init##name(void)
#   define MOD_INIT_RETURN(value) return;
#else
#   define PYTHON3
#   define MOD_INIT_FUNC(name) PyMODINIT_FUNC PyInit_##name(void)
#   define MOD_INIT_RETURN(value) return value;
#endif

static
PyObject* hello_printf(PyObject* self, PyObject* args, PyObject *kwargs)
{
    // Print "hello, world" to stdout.
    PySys_WriteStdout("hello, world\n");

    // return None
    Py_INCREF(Py_None);
    return Py_None;
}

static PyMethodDef hello_methods[] = {
    {"printf", (PyCFunction)hello_printf, METH_NOARGS, "Print the hello world."},
    {NULL},  // denote the end of the method set.
};

MOD_INIT_FUNC(hello)
{
#ifndef PYTHON3
    (void)Py_InitModule("hello", hello_methods);
#else
    static struct PyModuleDef hello = {
        PyModuleDef_HEAD_INIT,

        .m_name = "hello",
        .m_size = -1,
        .m_methods = hello_methods,
    };
    return PyModule_Create(&hello);
#endif
}
```

```python
from distutils.core import setup, Extension

module1 = Extension('hello', sources=['hello.c'])

setup(name='hello',
      version='1.0',
      description='This is a hello package',
      ext_modules=[module1])
```

## 6.4 为扩展模块添加属性

相比添加函数，为 C/C++ 扩展模块添加属性就简单地多了，只须两步即可：
1. 创建一个 PyObject 对象；
2. 调用 `PyModule_AddObject` 函数将其添加到模块对象中。

`PyModule_AddObject` 的原型是
```c
int PyModule_AddObject(PyObject *module, const char *name, PyObject *value)
```

下面我们来看一个示例：

```c
#include<Python.h>

#if PY_MAJOR_VERSION < 3
#   define MOD_INIT_FUNC(name) PyMODINIT_FUNC init##name(void)
#   define MOD_INIT_RETURN(value) return;
#else
#   define PYTHON3
#   define MOD_INIT_FUNC(name) PyMODINIT_FUNC PyInit_##name(void)
#   define MOD_INIT_RETURN(value) return value;
#endif

MOD_INIT_FUNC(hello)
{
    PyObject *module = NULL;

#ifndef PYTHON3
    module = Py_InitModule("hello", NULL);
#else
    static struct PyModuleDef hello = {
        PyModuleDef_HEAD_INIT,

        .m_name = "hello",
        .m_size = -1,
    };
    module = PyModule_Create(&hello);
#endif

    PyModule_AddObject(module, "intattr", PyLong_FromLong(123));
    PyModule_AddObject(module, "strattr", PyUnicode_FromString("abc"));

    MOD_INIT_RETURN(module)
}
```

如果属性值是一个整数或字符串常量，可以分别使用函数 `PyModule_AddIntConstant` 或 `PyModule_AddStringConstant` 为模块添加属性。其原型分别是
```c
int PyModule_AddIntConstant(PyObject *module, const char *name, long value)
int PyModule_AddStringConstant(PyObject *module, const char *name, const char *value)
```

所以，我们也可以这样添加一个整数常量或字符串常量：

```c
PyModule_AddIntConstant(module, "intattr", 123);
PyModule_AddStringConstant(module, "strattr", "abc");
```

## 6.5 为扩展模块添加一个新类型

定义一个新的 Python 类型，可以分为以下几个步骤：
1. 定义一个存放新类型数据的结构体 `struct`；
2. 定义新类型对象（它是元类的一个实例）；
3. 调用 `PyModule_AddObject` 函数把新类型对象添加到模块中。

下面我们添加一个新类型 `Person`。

**第一步：** 定义一个存放新类型数据的结构体。

```c
typedef struct {
    PyObject_HEAD
    PyObject *name;
    long age;
} PersonObject;
```

**第二步：** 定义新类型对象。

```c
static PyObject *
Person_new(PyTypeObject *type, PyObject *args, PyObject *kwargs)
{
    PersonObject *self;

    self = (PersonObject*)type->tp_alloc(type, 0);
    if (self != NULL) {
        self->name = PyUnicode_FromString("");
        if (self->name == NULL) {
            Py_DECREF(self);
            return NULL;
        }
        self->age = 0;
    }

    return (PyObject*)self;
}

static int
Person_init(PersonObject *self, PyObject *args, PyObject *kwargs)
{
    static char *kwlist[] = {"name", "age", NULL};
    PyObject *name = NULL, *tmp = NULL;
    int ok = 0;

    ok = PyArg_ParseTupleAndKeywords(args, kwargs, "|Ul", kwlist,
                                     &name, &self->age);
    if (!ok) {
        return -1;
    }

    if (name) {
        tmp = self->name;
        Py_INCREF(name);
        self->first = name;
        Py_XDECREF(tmp);
    }

    return 0;
}

static void
Person_dealloc(PersonObject *self)
{
    Py_XDECREF(self->name);
    Py_TYPE(self)->tp_free((PyObject*)self);
}

static PyTypeObject PersonType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "hello.Person",
    .tp_doc = "Person object",
    .tp_basicsize = sizeof(PersonObject),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
    .tp_new = Person_new,
    .tp_init = (initproc)Person_init,
    .tp_dealloc = (destructor)Person_dealloc,
};
```

注意，`Py_TPFLAGS_BASETYPE` 标志意味着此类 `Person` 能被其它类继承；如果没有此位，它就不能被继承。

**第三步：** 调用 `PyModule_AddObject` 函数把 `PersonType` 添加到模块 `hello` 中。如：

```c
Py_INCREF(&PersonType);
PyModule_AddObject(module, "Person", (PyObject *) &PersonType);
```

### 6.5.1 为新类型添加属性

`PyTypeObject` 类型有一个成员属性 `tp_members`，我们只要为其赋个值（即 `PyMemberDef` 类型的数组），其中包含可以访问的属性即可。

`PyMemberDef` 结构有五个成员：`name`（属性名）、`type`（属性值的类型）、`offset`（属性在类型结构体中的偏移量，以字节为单位）、`flags`（读写标志）、`doc`（属性的文档说明）。

关于 `type`，请具体参见 Python 的 [C API 文档](https://docs.python.org/3/c-api/structures.html#c.PyMemberDef)。

对于 `flags`，如果设为 `READONLY`，则该属性只能读取，不能修改；如果设为 `0`，表示既可以读取也可以修改。如果属性的类型 `type` 为 `T_STRING`（表示常量字符串），则 `flags` 会变为 `READONLY`（因为常量值不能被修改）。另外，只有当属性的类型 `type` 为 `T_OBJECT` 或 `T_OBJECT_EX` 时，才会允许删除属性，之后它们的值会被设为 `NULL`；此时，访问 `type` 为 `T_OBJECT` 的属性会返回 `None`，而访问 `type` 为 `T_OBJECT_EX` 的属性，则会抛出 `AttributeError` 异常。

有了这些，我们可以定义两个属性用来访问实例对象内部的信息。如：

```c
static PyMemberDef Person_members[] = {
    {
        "name",
        T_OBJECT_EX,
        offsetof(PersonObject, name),
        0,
        "person name",
    },
    {NULL} // Sentinel
};

static PyTypeObject PersonType = {
    // ...
    .tp_members = Person_members,
};
```

注意，当使用 `PyMemberDef` 结构体类型时，必须先包含头文件 `structmember.h`，如 `#include<structmember.h>`。

### 6.5.2 为新类型添加方法

为新类型添加方法的方式和步骤，与模块的相似，不同的是：（1）把模块对象换成新类型对象，（2）把方法集赋值到新类型的 `tp_methods` 成员。

第一步：先定义 Python C 函数。如：

```c
static
PyObject* Person_get_age(PersonObject* self, PyObject* Py_UNUSED(ignored))
{
    return PyLong_FromLong(self->age);
}
```

注意，由于我们的方法不需要参数，所以，这里我们可以明确告诉 Python 解析器忽略后面的参数。但是，这在 Python 2 下会出错编译警告或错误；所以，这个 `Py_UNUSED` 宏尽量只在 Python 3 下使用，不要在 Python 2 用。为了兼容 Python 2 和 3，就不要使用 `Py_UNUSED` 了。

第二步：定义一个方法集（即方法数组）变量。如：

```c
static PyMethodDef Person_methods[] = {
    {
        "get_age",
        (PyCFunction)Person_get_age,
        METH_NOARGS,
        "Return the age of the person.",
    },
    {NULL} // Sentinel
};
```

第三步：添加方法集到新类型的 `tp_methods` 成员。如：

```c
static PyTypeObject PersonType = {
    // ...
    .tp_methods = Person_methods,
};
```

### 6.5.3 控制新类型属性访问

在 CPython 中，我们仍可以像在 Python 代码中一样来控制类实例属性的访问，而且也有多种方式。这里我们先讲解一下类似于 `property` 的属性控制，即 `tp_getset` 成员，它是一个 `PyGetSetDef` 类型的数组。

`PyGetSetDef` 有五个成员：`name`（属性的名字）、`get`（类似于 `property` 中的 `fget`）、`set`（类似于 `property` 中的 `fset`）、`doc`（可选的文档）、`closure`（可选，为 `get` 和 `set` 提供额外的数据）。

`get` 和 `set` 均是一个 C 函数，其原型分别是
```c
typedef PyObject *(*getter)(PyObject *instance, void *func);
typedef int (*setter)(PyObject *instance, PyObject *new_value, void *func);
```
其中，参数 `instance` 是新类型的实例对象，`func` 是 `closure` 的值，`new_value` 是将要设置的新的属性值，如果它为 `NULL`，表示一个删除操作。

定义新类型实例的属性访问的方式，和定义属性很相似。我们假定新类型中包含一个名为 `id` 的属性，下面我们来实现属性 `id` 的访问控制：实例创建后，只允许获取其值，但不允许修改其值。

```c
static PyObject *
Person_getid(PersonObject *self, void *closure)
{
    return PyLong_FromLong(self->id);
}

static PyGetSetDef Person_getsetters[] = {
    {"id", (getter)Person_getid, NULL, "get id", NULL},
    {NULL}  /* Sentinel */
};

static PyTypeObject PersonType = {
    // ...
    .tp_getset = Person_getsetters,
};
```

注意，如果某个属性已在 `tp_members` 中定义，则在 `tp_getset` 中再次定义将会无效，因为 Python 解析器会优先使用 `tp_members` 成员中的定义。


### 6.5.4 支持循环垃圾收集器 CGC

Python 是一门自带垃圾回收（GC）的动态语言，它可以互相引用，甚至是自身引用自身，从而可能会导致循环引用。默认情况下，GC 无法侦测循环引用，这就是须要我们帮助 GC 来侦测它，从而使得 GC 可以做到处理循环引用的情况：当引用只剩下循环引用时，GC 就会回收它。这就是 CGC。

为了支持 CGC，很简单，只须完成四步即可：
1. 定义一个 `traverse` 方法；
2. 定义一个 `clear` 方法；
3. 在新类型的标志中添加 `Py_TPFLAGS_HAVE_GC`。

我们假定新类型中含有一个 `next` 属性，它可以是任何类型的值，所以它可能引用它自身，从而导致循环引用。下面我们实现对 CGC 的支持。

#### 6.5.4.1 定义 `traverse` 方法

`traverse` 方法的原型是
```c
int (PyObject *self, visitproc visit, void *arg)
```

如果 `traverse` 方法返回 `0`，表示没有循环引用；否则，就表示发生了循环引用。

`traverse` 方法的原理也很简单，就是把可以出现循环引用的字段（这里是 `next`）依次和第三个参数 `arg` 传递给第二个参数 `visit` 函数，以此根据它的返回值判断某个字段是否发生了循环引用：如果是 `0`，则说明该字段未发生循环引用；否则就是发生了循环引用。

只要有一次调用 `visit` 的返回值不是 `0`，`traverse` 就可以直接返回其值，以表明发生了循环引用；否则返回 `0` 即可。如：

```c
static int
Person_traverse(PersonObject *self, visitproc visit, void *arg)
{
    int vret;
    if (self->next) {
        vret = visit(self->next, arg);
        if (vret != 0)
            return vret;
    }
    return 0;
}
```

为了方便，CPython 标准头文件中已经内建了便捷宏 `Py_VISIT()`，我们只要将第二、三个参数的名字分别命名为 `visit` 和 `arg` 即可。如：
```c
static int
Person_traverse(PersonObject *self, visitproc visit, void *arg)
{
    Py_VISIT(self->next);
    return 0;
}
```

最终，将 `Person_traverse` 新类型的 `tp_traverse` 字段成员即可。

#### 6.5.4.2 定义 `clear` 方法

当发生循环引用，我们就须要打破这个环，清除循环引用链中的对象，即哪些属性会发生循环引用，就要清除哪些属性的值。`clear` 方法就是做这个事情的。如：

```c
static int
Person_clear(PersonObject *self)
{
    Py_CLEAR(self->next);
    return 0;
}
```

注意，原本我们也可以直接使用 `Py_DECREF` 或 `Py_XDECREF` 来清除引用，但这并不是很安全。为了能更安全的清除循环引用的对象，CPython 内建宏 `Py_CLEAR` 来做这件事情。建议：始终使用宏 `Py_CLEAR`。

最终，将 `Person_clear` 新类型的 `tp_clear` 字段成员即可。

#### 6.5.4.3 添加新标志 `Py_TPFLAGS_HAVE_GC`

这一步比较简单，在新类型定义时，在 `tp_flags` 字段处增加 `Py_TPFLAGS_HAVE_GC` 标志即可。如：
```c
.tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE | Py_TPFLAGS_HAVE_GC,
```


## 6.6 完整示例

```c
#include<Python.h>
#include<structmember.h>

#if PY_MAJOR_VERSION < 3
#   define MOD_INIT_FUNC(name) PyMODINIT_FUNC init##name(void)
#   define MOD_INIT_RETURN(value) return;
#else
#   define PYTHON3
#   define MOD_INIT_FUNC(name) PyMODINIT_FUNC PyInit_##name(void)
#   define MOD_INIT_RETURN(value) return value;
#endif

typedef struct {
    PyObject_HEAD
    PyObject *next;
    PyObject *name;
    long age;
    long id;
} PersonObject;

static PyObject *
Person_new(PyTypeObject *type, PyObject *args, PyObject *kwargs)
{
    PersonObject *self;

    self = (PersonObject*)type->tp_alloc(type, 0);
    if (self != NULL) {
        self->name = PyUnicode_FromString("");
        if (self->name == NULL) {
            Py_DECREF(self);
            return NULL;
        }
        self->next = NULL;
        self->age = 0;
        self->id = 0;
    }

    return (PyObject*)self;
}

static int
Person_init(PersonObject *self, PyObject *args, PyObject *kwargs)
{
    static char *kwlist[] = {"id", "name", "age", "next", NULL};
    PyObject *name = NULL, *tmp = NULL, *next = NULL;
    int ok = 0;

    ok = PyArg_ParseTupleAndKeywords(args, kwargs, "l|UlO", kwlist,
                                     &self->id, &name, &self->age,
                                     &next);
    if (!ok) {
        return -1;
    }

    if (name) {
        tmp = self->name;
        Py_INCREF(name);
        self->name = name;
        Py_XDECREF(tmp);
    }

    if (next) {
        tmp = self->next;
        Py_INCREF(next);
        self->next = next;
        Py_XDECREF(tmp);
    }

    return 0;
}

static void
Person_dealloc(PersonObject *self)
{
    PySys_WriteStdout("deallocate %ld\n", self->id);
    Py_XDECREF(self->name);
    Py_XDECREF(self->next);
    Py_TYPE(self)->tp_free((PyObject*)self);
}

static int
Person_traverse(PersonObject *self, visitproc visit, void *arg)
{
    Py_VISIT(self->next);
    return 0;
}

static int
Person_clear(PersonObject *self)
{
    Py_CLEAR(self->next);
    return 0;
}

static PyObject *
Person_getid(PersonObject *self, void *closure)
{
    return PyLong_FromLong(self->id);
}

static PyGetSetDef Person_getsetters[] = {
    {"id", (getter)Person_getid, NULL, "id", NULL},
    {NULL}  /* Sentinel */
};

static
PyObject* Person_get_age(PersonObject* self, PyObject* ignored)
{
    return PyLong_FromLong(self->age);
}

static PyMethodDef Person_methods[] = {
    {
        "get_age",
        (PyCFunction)Person_get_age,
        METH_NOARGS,
        "Return the age of the person.",
    },
    {NULL} // Sentinel
};

static PyMemberDef Person_members[] = {
    {
        "name",
        T_OBJECT_EX,
        offsetof(PersonObject, name),
        0,
        "person name",
    },{
        "next",
        T_OBJECT,
        offsetof(PersonObject, next),
        0,
        "next person",
    },
    {NULL} // Sentinel
};

static PyTypeObject PersonType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "hello.Person",
    .tp_doc = "Person object",
    .tp_basicsize = sizeof(PersonObject),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT | \
                Py_TPFLAGS_BASETYPE | \
                Py_TPFLAGS_HAVE_GC,
    .tp_new = Person_new,
    .tp_init = (initproc)Person_init,
    .tp_dealloc = (destructor)Person_dealloc,
    .tp_traverse = (traverseproc)Person_traverse,
    .tp_clear = (inquiry)Person_clear,
    .tp_members = Person_members,
    .tp_methods = Person_methods,
    .tp_getset = Person_getsetters,
};

MOD_INIT_FUNC(hello)
{
    PyObject *module = NULL;

    if (PyType_Ready(&PersonType) < 0) {
        MOD_INIT_RETURN(NULL)
    }

#ifndef PYTHON3
    module = Py_InitModule("hello", NULL);
#else
    static struct PyModuleDef hello = {
        PyModuleDef_HEAD_INIT,

        .m_name = "hello",
        .m_size = -1,
    };
    module = PyModule_Create(&hello);
#endif

    // Add the class Person into the module.
    PyModule_AddObject(module, "Person", (PyObject *) &PersonType);
    Py_INCREF(&PersonType);

    MOD_INIT_RETURN(module)
}
```

在上述示例中，我们加入一条调试语句 `PySys_WriteStdout("deallocate %ld\n", self->id);`。然后，我们编译后，会生成一个 `hello` 模块。这样，我们就可以使用它了。

```python
>>> import hello
>>> p = hello.Person(1, name=u'Aaron', age=18)
>>> p.name
Aaron
>>> p.get_age()
18
>>> print(p.next)
None
>>> q = hello.Person(2, name=u'John', age=28, next=p)
>>> q.next is p
True
>>> p.next = q
>>> del p  # delete the variable p
>>> del q  # delete the variable q
>>> import gc
>>> gc.collect()  # run GC to free p & q
deallocate 2
deallocate 1
2
```
