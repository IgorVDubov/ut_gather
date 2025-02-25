d=[1,1,1,1,1,1,1,1,1,2]


def middle():
    summ=0
    n=0
    def count(x):
        nonlocal summ, n
        summ+=x
        n+=1
        print(summ, n, summ/n)
        return summ/n
    return count


if __name__ == '__main__':
    m=middle()
    for x in d:
        print(m(x))