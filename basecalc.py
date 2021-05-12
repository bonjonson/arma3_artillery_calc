from math import sqrt, asin, pow
import mortars_data

type_of_mortar = 'mortar_2b11'


class CalculateMethod:
    def __init__(self, mortar_x, target_x1, mortar_y, target_y1, mortar_z, target_z1, type_of_mortar):
        """В конструктор передаются следующие данные:
        координаты миномёта (x,y,z) и координаты цели (x1,y1,z1),
        так же передаётся выбранный тип миномёта в переменную type_of_mortar,
        создаются пустой список доступных Charges и пустой словарь доступных Elevation,
         по ключу Charges"""
        self.__mortar_x = mortar_x
        self.__target_x1 = target_x1
        self.__mortar_y = mortar_y
        self.__target_y1 = target_y1
        self.__mortar_z = mortar_z
        self.__target_z1 = target_z1
        self.__type_of_mortar = type_of_mortar
        self.__availableCharges = []
        self.__availableElevation = {}

    def __checkValue(x):
        """Приватный метод проверки допустимых значений"""
        if isinstance(x, int) or isinstance(x, float):
            return True
        return False

    def setCoords(self, x, target_x1, y, target_y1, z, target_z1):
        """Приватный метод изменения координат,
        также обнуляет список доступных Charges_,
        словарь доступных elevations"""
        if CalculateMethod.__checkValue(x) and CalculateMethod.__checkValue(target_x1) and CalculateMethod.__checkValue(y) \
                and CalculateMethod.__checkValue(target_y1) and CalculateMethod.__checkValue(z) \
                and CalculateMethod.__checkValue(target_z1):
            self.__mortar_x = x
            self.__target_x1 = target_x1
            self.__mortar_y = y
            self.__target_y1 = target_y1
            self.__mortar_z = z
            self.__target_z1 = target_z1
            self.__availableCharges = []
            self.__availableElevation = {}

    def getCoords(self):
        """Приватный метод просмотра координат экземпляра и допустимых Charges_"""
        return self.__mortar_x, self.__target_x1, self.__mortar_y, self.__target_y1, \
               self.__mortar_z, self.__target_z1, self.__availableCharges, self.__availableElevation

    def getTargetDistance(self):
        """Метод вычисления и округления дистанции до цели"""
        target_distance = sqrt(pow(self.__target_x1 - self.__mortar_x, 2) + pow(self.__target_y1 - self.__mortar_y, 2))

        if 100 <= target_distance <= 9999:
            if target_distance % 100 < 41:
                target_distance = target_distance - (target_distance % 100)
            elif 40 < target_distance % 100 < 50 or 50 <= target_distance % 100 < 91:
                target_distance = target_distance - (target_distance % 100) + 50
            else:
                target_distance = target_distance - (target_distance % 100) + 100
        else:
            print('value is out of target distance')
        return target_distance

    def getTargetAngle(self):
        """Метод нахождения угла наведения на цель.
        1) Вычисляем дельту угла по формуле:
        asin((x1-x)/sqrt(pow(x1-x)+pow(y1-y)))*1018.591636
        2) Определяем взаимное расположение миномёта и цели,
        относительно начала сетки координат,
        где началом координат служат координаты миномёта.
        """
        alpha_angle = asin(
            (self.__target_x1 - self.__mortar_x) / sqrt(pow(self.__target_x1 - self.__mortar_x, 2) + pow(self.__target_y1 - self.__mortar_y, 2))) * 1018.591636
        if self.__mortar_x < self.__target_x1 and self.__mortar_y < self.__target_y1:
            target_angle = 0 + abs(alpha_angle)
        elif self.__mortar_x < self.__target_x1 and self.__mortar_y > self.__target_y1:
            target_angle = 3200 - abs(alpha_angle)
        elif self.__mortar_x > self.__target_x1 and self.__mortar_y > self.__target_y1:
            target_angle = 3200 + abs(alpha_angle)
        else:
            target_angle = 6400 - abs(alpha_angle)
        return target_angle

    def getTypeOfCharge(self):
        """Метод нахождения подходящего type of charge по найденному distance
        Если указанный тип миномёта содержится в модуле mortars_data,
        то совершаем обход по всем ключам в указанном type_of_mortar,
        где проверяем, содержится ли обнаруженный distance в текущем ключе charge_,
        если содержится, то заносим его в список допустимых charge_,
        иначе возвращаем недопустимое значение distance.
        """
        try:
            if self.__type_of_mortar in mortars_data:
                for _keys in self.__type_of_mortar.keys():
                    try:
                        if self.getTargetDistance() in self.__type_of_mortar.get(_keys).keys():
                            self.__availableCharges.append(self.__type_of_mortar.get(_keys))
                    except ValueError:
                        print('Value of distance not in available list')
        except ValueError:
            print('Chosen type_of_mortar not in available list')

    def getElevation(self):
        """Метод нахождения подходящего Elevation,
        согласно найденным элементам в списке availableCharges."""
        try:
            if self.__availableCharges:
                # Заполняем словарь доступных Elevation по ключам из списка доступных Charges
                self.__availableElevation = self.__availableElevation.fromkeys(self.__availableCharges)
                # Находим соответствия distance среди значений по ключу Charges
                for _charges in self.__availableCharges:
                    # Пример использования
                    # self.__type_of_mortar.get('charge_0').get('1350')[0]
                    # Вернет значение elevation по указанному distance

                    # Найдем поправку за 100м
                    d_per_100 = self.__type_of_mortar.get(_charges).get(self.getTargetDistance())[1]
                    # Найдем поправку за 10м
                    d_per_10 = d_per_100 / 10
                    # Внесем поправки в Elevation
                    # Если mortar_z < target_z1, то elev - dper100
                    # Если mortar_z > target_z1, то elev + dper100
                    if self.__mortar_z < self.__target_z1:
                        difference = self.__target_z1 - self.__mortar_z
                    else:
                        difference = self.__mortar_z - self.__target_y1
                    # Вычисляем точную поправку на высоту
                    correctDElevevation = difference // d_per_10
                    if self.__mortar_z < self.__target_z1:
                        # Полученное значение нужно сохранить в соответствующий ключ в словаре доступных elevation
                        self.__availableElevation[_charges] = \
                            self.__type_of_mortar.get(_charges).get(self.getTargetDistance())[0] - correctDElevevation
                    else:
                        # Полученное значение нужно сохранить в соответствующий ключ в словаре доступных elevation
                        self.__availableElevation[_charges] = \
                            self.__type_of_mortar.get(_charges).get(self.getTargetDistance())[0] + correctDElevevation
        except ValueError:
            print('Chosen distance is not available or list of available charges is empty')
