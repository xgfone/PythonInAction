
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
#define MOD_INIT_FUNC(name) PyMODINIT_FUNC init##name(void)
#else
#define PYTHON3
#define MOD_INIT_FUNC(name) PyMODINIT_FUNC PyInit_##name(void)
#endif
```

我们现在来改写一下上述 C 模块（假定其文件名为 `hello.c`）：

```c
#include<Python.h>

#if PY_MAJOR_VERSION < 3
#define MOD_INIT_FUNC(name) PyMODINIT_FUNC init##name(void)
#else
#define PYTHON3
#define MOD_INIT_FUNC(name) PyMODINIT_FUNC PyInit_##name(void)
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

在 Python 的模块中，定义一个函数，就相当于在这个模块中做一个赋值操作，其中，变量名为函数的名字，赋的值就是所定义的函数。

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

把 Python 函数变成一个方法，就是重新定义一个 `PyMethodDef` 类型的变量，并填充其四个成员，如：
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
#define MOD_INIT_FUNC(name) PyMODINIT_FUNC init##name(void)
#else
#define PYTHON3
#define MOD_INIT_FUNC(name) PyMODINIT_FUNC PyInit_##name(void)
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
