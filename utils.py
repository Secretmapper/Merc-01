import math


def distance_sq(a, b):
    return (a.x - b.x) ** 2 + (a.y - b.y) ** 2


def collides(a, b_list):
    return any(distance_sq(b, a) < (a.width / 2 + b.width / 2) ** 2 for b in b_list)


def normalize(x, y):
    l = math.sqrt(x * x + y * y)
    if not l == 0:
        return x / float(l), y / float(l)
    else:
        return 0, 0


def trunc(a, n, m=None):
    if m == None:
        return max(min(a, n), -n)
    else:
        return max(min(a, m), n)


def truncate(a, n):
    i = n / 2
    i = 1 if i < 1 else i
    return [a[0] * i, a[1] * i]
