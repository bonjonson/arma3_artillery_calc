from math import sqrt, asin, pow


class CalculateMethod:
    def __init__(self, x, x1, y, y1):
        self.__x = x
        self.__x1 = x1
        self.__y = y
        self.__y1 = y1

    def __checkValue(x):
        '''Приватный метод проверки значений'''
        if isinstance(x, int) or isinstance(x, float):
            return True
        return False

    def setCoords(self, x, x1, y, y1):
        if CalculateMethod.__checkValue(x) and CalculateMethod.__checkValue(x1) and CalculateMethod.__checkValue(y) \
                and CalculateMethod.__checkValue(y1):
            self.__x = x
            self.__x1 = x1
            self.__y = y
            self.__y1 = y1

    def getCoords(self):
        return self.__x, self.__x1, self.__y, self.__y1

    def get_target_distance(self):
        '''Метод вычисления и округления дистанции до цели'''
        target_distance = sqrt(pow(self.__x1 - self.__x, 2) + pow(self.__y1 - self.__y, 2))

        if 100 <= target_distance <= 9999:
            if target_distance % 100 < 41:
                target_distance = target_distance - (target_distance % 100)
            elif 40 < target_distance % 100 < 50 or 50 <= target_distance % 100 < 91:
                target_distance = target_distance - (target_distance % 100) + 50
            else:
                target_distance = target_distance - (target_distance % 100) + 100
        else:
            print('value is our of target_distance')
        return target_distance

    def get_target_angle(self):
        '''Метод нахождения угла наведения на цель'''

        alpha_angle = asin(
            (self.__x1 - self.__x) / sqrt(pow(self.__x1 - self.__x, 2) + pow(self.__y1 - self.__y, 2))) * 1018.591636
        if self.__x < self.__x1 and self.__y < self.__y1:
            target_angle = 0 + abs(alpha_angle)
        elif self.__x < self.__x1 and self.__y > self.__y1:
            target_angle = 3200 - abs(alpha_angle)
        elif self.__x > self.__x1 and self.__y > self.__y1:
            target_angle = 3200 + abs(alpha_angle)
        else:
            target_angle = 6400 - abs(alpha_angle)
        return target_angle

    def get_table_elev(self):
        '''Метод поиска табличного значения elevation'''
        pass

    def get_correct_elev(self):
        '''Метод определения корректного elevation'''
        pass
