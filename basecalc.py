from math import sqrt, asin, pow


class CalculateMethod:
    def __init__(self, x, x1, y, y1):
        self.x = x
        self.x1 = x1
        self.y = y
        self.y1 = y1

    def get_range(self):
        target_distance = sqrt(pow(self.x1 - self.x, 2) + pow(self.y1 - self.y, 2))
        return target_distance

    def get_target_angle(self):
        alpha_angle = asin((self.x1 - self.x) / sqrt(pow(self.x1 - self.x, 2) + pow(self.y1 - self.y, 2))) * 1018.591636
        if self.x < self.x1 and self.y < self.y1:
            target_angle = 0 + abs(alpha_angle)
        elif self.x < self.x1 and y > self.y1:
            target_angle = 3200 - abs(alpha_angle)
        elif self.x > self.x1 and self.y > self.y1:
            target_angle = 3200 + abs(alpha_angle)
        else:
            target_angle = 6400 - abs(alpha_angle)
        return target_angle

    def get_table_elev(self):
        '''метод поиска табличного значения elevation'''
        pass

    def get_correct_elev(self):
        '''метод определения корректного elevation'''
        pass