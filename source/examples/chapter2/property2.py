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
