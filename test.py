d = {}
d.setdefault('dns')
if 'dns' in d.keys():
    print('good')
d.update({'lan': {'inlan': None}})
print(d)

d['lan']['inlan'] = 1
print(d)


if 'inlan' in d['lan']:
    print('cool')

d.setdefault('b')
print(d)
d['b'] = {'bb': 1}
print(d)
d['b']['bb'] += 1
print(d)
d['b'].update({'aa': 1})
print(d)