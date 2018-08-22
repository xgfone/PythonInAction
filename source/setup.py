try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='ppia',
    version='1.0.0',
    description='The source of Python Programming In Action.',
    author='xgfone',
    author_email='xgfone@126.com',
    maintainer='xgfone',
    maintainer_email='xgfone@126.com',
    url='https://github.com/xgfone/PythonProgrammingInAction',
    packages=['ppia'],

    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
)
