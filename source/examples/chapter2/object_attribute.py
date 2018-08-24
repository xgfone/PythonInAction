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
