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
print("person.attr0 =", person.attr0)
print("person.attr1 =", person.attr1)
print("person.attr2 =", person.attr2)
try:
    print("person.attr3 =", person.attr3)
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
