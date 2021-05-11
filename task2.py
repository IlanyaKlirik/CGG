import sys

from math import sin, cos, pi, asin, fabs, sqrt
from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtGui import QPainter
from PyQt5.QtCore import QPoint

A = 200
B = 0.1
C = 0
D = 0


class Graph(QWidget):
    def __init__(self, a, b, c, d):
        super().__init__()
        self.init_ui()
        self.k = 1  # коэффициент не нужен. это если вдруг вздумается масшатбировать график
        self.A = a
        self.B = b
        self.C = c
        self.D = d
        self.ka = 1
        self.kb = 1
        if a < 0:
            self.A = -a
            self.ka = -1
        if b < 0:
            self.B = -b
            self.kb = -1

    def f(self, x):
        """Функция синуса без смещения"""
        return self.A * sin(self.B * x)

    def i_f(self, y):
        """Обратная функция без смещения"""
        return (asin(y / self.A)) / self.B

    def d_f_x(self, x):
        """Первая производная функции"""
        return self.A * self.B * cos(self.B * x)

    def init_ui(self):
        self.setGeometry(250, 150, 800, 800)
        self.setWindowTitle('График функции. Алгоритм Брезенхема')
        self.show()

    def paintEvent(self, e):
        qp = QPainter()
        qp.begin(self)
        self.draw(qp)
        qp.end()

    def draw(self, qp):
        # print('draw')
        self.draw_axes(qp)
        self.draw_graph(qp)

    def draw_graph(self, qp):
        """
        Рисуем от точки (0,0), потом смещаем на нужное нам расстояние по х и у
        Рисуем в обе стороны до упора
        """
        # print('start draw')
        h = pi*self.k/2/self.B
        # заносим все методы в отдельный список, чтобы потом было удобно их перебирать
        f = [self.draw_up, self.draw_down, self.get_h]
        f_s = 0
        # смотрим, как нам рисовать от начала, вверх или вниз
        if self.d_f_x(0) < 0:
            f_s = 1
        xi, yi = f[f_s](qp, 0, 0, (int(h)))
        f_s += 1
        i = 1
        # рисуем график вправо, одновременно отражаем его относительно стартовой точки.
        while xi <= int(self.width() / 2):
            tek = int(f_s % 2)
            xi, yi = f[tek](qp, int(i*h)+1, yi, (int(i+2)*h))
            f_s += 1
            i += 2

    def draw_up(self, qp, x_start, y_start, x_finish):
        """
        Алгоритм Брезенехма, рисующий возрастающий участок функции
        На вход даются стартовые точки и граница по х, до которой нужно отрисовывать
        """
        # print('start draw up')
        # задаем стартовую точку
        xx = x_start
        yy = y_start

        while xx <= x_finish:
            # проверим, что не вылезли за пределы окна
            if xx >= self.width():
                break
            # рисуем текующую точку и ее отражение
            qp.drawPoint(
                QPoint(int(self.width() / 2) - self.C + self.kb * xx, int(self.height() / 2) - self.D - self.ka * yy))
            qp.drawPoint(
                QPoint(int(self.width() / 2) - self.C - self.kb * xx, int(self.height() / 2) - self.D + self.ka * yy))
            # Определяем тангенс угла наклона касательной, по нему определяем, какую пару точек выбрать
            # выбор из двух точек осуществляем по расстоянию до реальной функции
            # Аппроксимация - высота в треугольнике. Пример - в файле task2_sample.png
            x = xx / self.k
            y = yy / self.k
            x1 = (xx + 1) / self.k
            y1 = (yy + 1) / self.k
            if fabs(y1) > self.A:
                xx += 1
                continue

            t = self.d_f_x(x)
            fxx = self.f(x)*self.k
            fxx1 = self.f(x1)*self.k
            ifyy = self.i_f(y)*self.k
            ifyy1 = self.i_f(y1)*self.k
            if t >= 1:
                # (x, y+1) и (x+1, y+1)
                h1 = self.get_h(xx, yy+1, xx, fxx, ifyy1, yy+1)
                h2 = self.get_h(xx+1, yy+1, xx+1, fxx1, ifyy1, yy+1)
                if h1 - h2 < 0:
                    yy += 1
                else:
                    xx += 1
                    yy += 1
            else:
                # (x+1, y) и (x+1, y+1)
                h1 = self.get_h(xx+1, yy, ifyy, yy, xx+1, fxx1)
                h2 = self.get_h(xx+1, yy+1, ifyy1, yy, xx+1, fxx1)
                if h1 - h2 < 0:
                    xx += 1
                else:
                    xx += 1
                    yy += 1

        return xx, yy

    def draw_down(self, qp, x_start, y_start, x_finish):
        """
        Алгоритм Брезенехма, рисующий убывающий участок функции
        На вход даются стартовые точки и граница по х, до которой нужно отрисовывать
        """
        # print('start draw down')
        # задаем стартовую точку
        xx = x_start
        yy = y_start

        while xx <= x_finish:
            # проверим, что не вылезли за пределы окна
            if xx >= self.width():
                break
            # рисуем текующую точку и ее отражение
            qp.drawPoint(
                QPoint(int(self.width() / 2) - self.C + self.kb * xx, int(self.height() / 2) - self.D - self.ka * yy))
            qp.drawPoint(
                QPoint(int(self.width() / 2) - self.C - self.kb * xx, int(self.height() / 2) - self.D + self.ka * yy))

            # Определяем тангенс угла наклона касательной, по нему определяем, какую пару точек выбрать
            # выбор из двух точек осуществляем по расстоянию до реальной функции
            # Аппроксимация - высота в треугольнике. Пример - в файле task2_sample.png
            x = xx / self.k
            y = yy / self.k
            x1 = (xx + 1) / self.k
            y1 = (yy - 1) / self.k
            if fabs(y1) > self.A:
                xx += 1
                continue

            t = self.d_f_x(x)
            fxx = self.f(x) * self.k
            fxx1 = self.f(x1) * self.k
            ifyy = self.i_f(y) * self.k
            ifyy1 = self.i_f(y1) * self.k

            if t < -1:
                # (x, y-1) и (x+1, y-1)
                h1 = self.get_h(xx, yy - 1, xx, fxx, ifyy1, yy - 1)
                h2 = self.get_h(xx + 1, yy - 1, xx + 1, fxx1, ifyy1, yy - 1)
                if h1 - h2 < 0:
                    yy -= 1
                else:
                    xx += 1
                    yy -= 1
            else:
                # (x+1, y) и (x+1, y-1)
                h1 = self.get_h(xx + 1, yy, ifyy, yy, xx + 1, fxx1)
                h2 = self.get_h(xx + 1, yy - 1, ifyy1, yy - 1, xx + 1, fxx1)
                if h1 - h2 < 0:
                    xx += 1
                else:
                    xx += 1
                    yy -= 1

        return xx, yy

    def get_h(self, x0, y0, x1, y1, x2, y2):
        """Высота в теругольнике"""
        a = y2 - y1
        b = x1 - x2
        c = y1 * (x2 - x1) - x1 * (y2 - y1)
        return fabs(a*x0 + b*y0 + c) / sqrt(a**2 + b**2)

    def draw_axes(self, qp):
        """Метод, рисующий координатные оси. Начало координат всегда расположено по центру"""
        qp.drawLine(QPoint(int(self.width() / 2), 0), QPoint(int(self.width() / 2), self.height()))
        qp.drawLine(QPoint(0, int(self.height() / 2)), QPoint(self.width(), int(self.height() / 2)))


def main():
    app = QApplication(sys.argv)

    graph = Graph(A, B, C, D)

    app.exec_()


if __name__ == "__main__":
    main()
