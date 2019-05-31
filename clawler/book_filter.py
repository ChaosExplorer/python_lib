filename='booklist.txt'

with open(filename, 'r', encoding='utf-8') as r:
    lines = r.readlines()
with open(filename, 'w+', encoding='utf-8') as f:
    for l in lines:
        l = filter()
        if l:
            f.write(l)


def filter(l):
    l = l.replace('（作者）', '')
    l = l.replace('（作者', '')
    i = l.find('天翼云盘')
    if i != -1:
        l = l[:i] + l[i + 12:]
    if '大冰' in l or '张嘉佳' in l:
        return None
    else:
        return l

