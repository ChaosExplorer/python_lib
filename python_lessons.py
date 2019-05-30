#   ====>     9 Classes
"""
a means of bundling data and functionality together.
attributes attached to it for maintaining its state.

It is a mixture of the class mechanisms found in C++ and Modula-3.
Python classes provide all the standard features of Object Oriented Programming:
the class inheritance mechanism allows multiple base classes, a derived class can override
any methods of its base class or classes, and a method can call the method of a base class
with the same name. Objects can contain arbitrary amounts and kinds of data. As is true for modules,
classes partake of the dynamic nature of Python: they are created at runtime, and can be
modified further after creation

built-in types can be used as base classes for extension by the user. Also, like in C++, most built-in operators with
special syntax (arithmetic operators, subscripting etc.) can be redefined for class instances

"""

# Scopes and Namespaces
"""
def scope_test():
    def do_loca():
        spam = "local spam"

    def do_nolocal():
        nonlocal spam
        spam = "nonlocal spam"

    def do_global():
        global spam
        spam = "global spam"

    spam = "test spam"
    do_loca()
    print("local assignment : ", spam)
    do_nolocal()
    print("nonlocal assignment : ", spam)
    do_global()
    print("global assignment : ", spam)


scope_test()
print("In global scope : ", spam)
"""

"""
-->The nonlocal assignment changed scope_test’s binding of spam, 
and the global assignment changed the module-level binding.
You can also see that there was no previous binding for spam 
before the global assignment.

If a name is declared global, then all references and assignments 
go directly to the middle scope containing the module’s global names. 
To rebind variables found outside of the innermost scope, the nonlocal statement can be used
"""



