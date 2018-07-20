import sys


def rm_dup(infile, outfile):
    inf = open(infile, 'r', encoding='utf-8')
    outf = open(outfile, 'w+', encoding='utf-8')
    list_1 = []

    for line in inf.readlines():
        if line not in list_1:
            list_1.append(line)
            if len(list_1) > 10000:
                outf.write(''.join(list_1))
                list_1.clear()

    outf.write(''.join(list_1))

    inf.close()
    outf.close()


if __name__ == '__main__':
    rm_dup(sys.argv[1], sys.argv[2])