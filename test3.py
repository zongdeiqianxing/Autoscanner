a = (1,'date','333')
b= 222
if 'date' in a:
    l = list(a)
    index = l.index('date')
    l[index] = b
    a = tuple(l)
    print(a)