def distance_sq(a, b):
    return (a.x - b.x) ** 2 + (a.y - b.y) ** 2


def collides(a, b_list):
    return any(distance_sq(b, a) < (a.width / 2 + b.width / 2) ** 2 for b in b_list)
