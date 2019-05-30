dic = {'a':1, 'c': 2, 'b': 3, 'z':4, 'd': 5}

a = []

def getlist(dic):
    global a
    a = list(dic.keys())
    print(a)
    del dic['a']

getlist(dic)

print(a)

def changelist2(l):
    l += [1]

def changelist(l):
    l = l + [1]

l = [2, 3 , 4]

changelist(l)
print(id(l))
print(l)

changelist2(l)
print(l)

d = {'chr13':1, 'chr2':2}
print(sorted(d.keys()))

import difflib
cases = [('one', 'ore'), ('two', 'Tho')]

for a, b in cases:
    print('{} => {}'.format(a, b))
    re = difflib.ndiff(a, b)
    for i, s in enumerate(re):
        if s[0] == ' ': continue
        if s[0] == '-':
            print('- "{}" from position {}'.format(s[-1], i))
        if s[0] == '+':
            print('+ "{}" to position {}'.format(s[-1], i))