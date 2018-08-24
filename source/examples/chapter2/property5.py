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
