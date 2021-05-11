import sys
from math import sin, cos, pi, sqrt, fabs

from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtGui import QPainter
from PyQt5.QtCore import QPoint


class Graph(QWidget):
    def __init__(self):
        super().__init__()
        self.polygon = [(0, 0), (300, 50), (600, 300), (0, 400)]
        self.sides = []
        for i in range(len(self.polygon)):
            self.sides.append(self.get_line(self.polygon[i-1][0], self.polygon[i-1][1],
                                            self.polygon[i][0], self.polygon[i][1]))
        self.init_ui()

    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)
        self.draw(qp)
        qp.end()

    def init_ui(self):
        self.setGeometry(250, 150, 800, 800)
        self.setWindowTitle('Многоугольники')
        self.show()

    def draw(self, qp):
        # print('draw')
        # рисуем многоугольник
        self.draw_fig(qp, self.sides)
        # ищем треугольник
        triangle = self.find_triangle()
        # по координатам строим стороны алгоритмом Брезенхема
        t_sides = []
        for i in range(len(triangle)):
            t_sides.append(self.get_line(triangle[i - 1][0], triangle[i - 1][1],
                                         triangle[i][0], triangle[i][1]))

        self.draw_fig(qp, t_sides)

    def get_line(self, x1, y1, x2, y2):
        """Метод получает две точки и возвращает координаты всех точек линии, полученной алгоритмом Брезенхема"""
        line = []
        dx = x2 - x1
        dy = y2 - y1

        sign_x = 1 if dx > 0 else -1 if dx < 0 else 0
        sign_y = 1 if dy > 0 else -1 if dy < 0 else 0

        if dx < 0:
            dx = -dx
        if dy < 0:
            dy = -dy
        if dx > dy:
            pdx, pdy = sign_x, 0
            es, el = dy, dx
        else:
            pdx, pdy = 0, sign_y
            es, el = dx, dy

        x, y = x1, y1
        error, t = el / 2, 0
        line.append((x, y))

        while t < el:
            error -= es
            if error < 0:
                error += el
                x += sign_x
                y += sign_y
            else:
                x += pdx
                y += pdy
            t += 1
            line.append((x, y))

        return line

    def draw_fig(self, qp, data):
        """
        Строит фигуру по сторонам. Стороны получены алгоритмом Брезенхема.
        data - список списков, в каждом списке набор кортежей - координата х и координата у
        """
        for i in data:
            for x, y in i:
                qp.drawPoint(QPoint(x, y))

    def find_triangle(self):
        """
        Метод ищет координаты трех точек правильного треугольника.
        Внешний цикл перебирает по вершинам многоугольника. Ее берем как основную.
        Внутренний перебирает все точки на всех сторонах. По двум точкам строится правильный треугольник
        (рассматриваются два варианта, с одной и другой стороны от прямой, проходящей через эти точки)
        Если какая-то из полученных точек попала на сторону многоугольника, считаем длину стороны получившегося
        треугольника и заносим данные в vertexes.
        Метод возвращает список кортежей, кортеж - координаты вершины.
        """
        vertexes = []
        for v in self.sides:
            # проходим по всем сторонам и берем за стартовую координату начало стороны - вершину
            fix_x, fix_y = v[0]

            # перебираем все координаты других сторон
            for side in self.sides:
                for i in range(len(side)):
                    # текущая координата - сх, су
                    cx, cy = side[i]
                    if cx == fix_x and cy == fix_y:
                        continue

                    res = self.find_vertex(fix_x, fix_y, cx, cy)
                    # если результат False, значит, вершинка не нашлась
                    if not res:
                        continue

                    # сразу считаем длину стороны
                    cl = self.get_length(fix_x, fix_y, cx, cy)
                    # если мы до этого не находили вершин, закинем текущий сет как решение
                    if not vertexes:
                        vertexes = [(fix_x, fix_y), (cx, cy), (res[0], res[1]), cl]

                    else:
                        # иначе, будем проверять до длине стороны. Если найденная больше - заменяем
                        if vertexes[3] < cl:
                            vertexes = [(fix_x, fix_y), (cx, cy), (res[0], res[1]), cl]

        return vertexes[:-1]

    def find_vertex(self, x1, y1, x2, y2):
        """Находим две вершины и проверяем, находятся ли на стороне многоугольника"""
        x3 = (x1 + x2 + (y1 - y2) * sqrt(3)) / 2
        y3 = (y1 + y2 + (x2 - x1) * sqrt(3)) / 2
        ix3 = (x1 + x2 - (y1 - y2) * sqrt(3)) / 2
        iy3 = (y1 + y2 - (x2 - x1) * sqrt(3)) / 2

        coords = [(x, y) for x in range(int(x3)-1, int(x3)+2) for y in range(int(y3)-1, int(y3)+2)]
        coords.extend([(x, y) for x in range(int(ix3)-1, int(ix3)+2) for y in range(int(iy3)-1, int(iy3)+2)])

        for c in coords:
            for s in self.sides:
                res = self.is_on_line(s, c)
                if res:
                    return c

        return False

    def is_on_line(self, side, coord):
        """Проверяем, находится ли точка на стороне"""
        return coord in side

    def get_length(self, x1, y1, x2, y2):
        """Возвращает расстояние между двумя точками, заданными координатами"""
        return sqrt((x1 - x2)**2 + (y1 - y2)**2)


def main():
    app = QApplication(sys.argv)

    graph = Graph()

    app.exec_()


if __name__ == "__main__":
    main()
