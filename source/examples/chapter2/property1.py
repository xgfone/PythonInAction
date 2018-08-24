class Person(object):
    def __init__(self, name, age):
        self._name = name
        self._age = age

    def _get_name(self):
        print('get the name')
        return self._name

    def _set_name(self, name):
        print("set the name to '%s'" % name)
        self._name = name

    def _del_name(self):
        print('delete the name')
        del self._name

    name = property(fget=_get_name, fset=_set_name, fdel=_del_name)

    def _get_age(self):
        print('get the age')
        return self._age

    def _set_age(self, age):
        print("set the age to '%s'" % age)
        self._age = age

    def _del_age(self):
        print('delete the age')
        del self._age

    age = property(fget=_get_age, fset=_set_age, fdel=_del_age)


print('name', id(Person.name), type(Person.name))
print('age', id(Person.age), type(Person.age))

person = Person('Aaron', 123)
print(person.name)
person.name = 'John'
print(person.name)

del person.name
try:
    print(person.name)
except AttributeError:
    print("no the atrribute 'name'")

print(person.age)

# Output:
# name 2640632190440 <class 'property'>
# age 2640632397400 <class 'property'>
# get the name
# Aaron
# set the name to 'John'
# get the name
# John
# delete the name
# get the name
# no the atrribute 'name'
# get the age
# 123
