class Name(object):
    def __init__(self, value):
        self._name = value

    def __get__(self, instance, owner):
        print('get the name')

        # Return the attribute value from the instance of the custom class.
        return instance._name

    def __set__(self, instance, value):
        print("set the name to '%s'" % value)

        # Store the value into the instance of the custom class.
        instance._name = value

        # Store the value into the instance of the descriptor class.
        self._name = value

    def __delete__(self, instance):
        print('delete the name')

        # Delete the value from the instances of the custom
        # and the descriptor class.
        del instance._name
        del self._name


class Person(object):
    def __init__(self, name):
        self._name = name

    name = Name('')


person = Person('Aaron')
print(person.name)
person.name = 'John'
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
