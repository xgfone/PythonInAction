
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

```python
#if PY_MAJOR_VERSION < 3
#define MOD_INIT_FUNC(name) PyMODINIT_FUNC init##name(void)
#else
#define PYTHON3
#define MOD_INIT_FUNC(name) PyMODINIT_FUNC PyInit_##name(void)
#endif
```

我们现在来改写一下上述 C 模块（假定其文件名为 `hello.c`）：

```python
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
