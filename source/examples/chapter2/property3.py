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
