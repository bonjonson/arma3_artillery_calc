from math import sqrt, asin, pow


def get_range(x, x1, y, y1):
    target_distance = sqrt(pow(x1 - x) + pow(y1 - y))
    return target_distance


def get_target_angle(x, x1, y, y1):
    alpha_angle = asin((x1 - x) / sqrt(pow(x1 - x) + pow(y1 - y)))
    if x < x1 and y < y1:
        target_angle = 0 + abs(alpha_angle)
    elif x < x1 and y > y1:
        target_angle = 3200 - abs(alpha_angle)
    elif x > x1 and y > y1:
        target_angle = 3200 + abs(alpha_angle)
    else:
        target_angle = 6400 - abs(alpha_angle)
    return target_angle


if __name__ == '__main__':
    pass
