import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *
import math
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtOpenGLWidgets import  QOpenGLWidget
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QKeyEvent, QMouseEvent


class State:
    def __init__(self):
        # Камера
        self.camera_pos = np.array([5, 5, 5], dtype=np.float32)
        self.camera_front = np.array([0, 0, -1], dtype=np.float32)
        self.camera_up = np.array([0, 1, 0], dtype=np.float32)
        self.yaw = -90.0
        self.pitch = 0.0
        self.last_mouse_x = 400
        self.last_mouse_y = 300

        # Управление
        self.keys = {
            Qt.Key.Key_W: False,
            Qt.Key.Key_S: False,
            Qt.Key.Key_A: False,
            Qt.Key.Key_D: False,
            Qt.Key.Key_Space: False,
            Qt.Key.Key_C: False
        }

        # Геометрия
        self.spheres = np.array([
            [0.0, 0.0, 0.0, 0.5, 1.0, 0.0, 0.0],  # x,y,z,radius,r,g,b
            [2.0, 0.0, 0.0, 0.5, 0.0, 1.0, 0.0],
            [0.0, 2.0, 0.0, 0.5, 0.0, 0.0, 1.0],
            [0.0, 0.0, 2.0, 0.5, 1.0, 1.0, 0.0]
        ], dtype=np.float32)

        self.selected_sphere = -1  # Индекс выделенной сферы
        self.sphere_quad = gluNewQuadric()


class OpenGLWidget(QOpenGLWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setFocus()

        self.state = State()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(16)  # ~60 FPS

        # Настройки мыши
        self.setMouseTracking(True)
        self.setCursor(Qt.CursorShape.BlankCursor)

        # Центрируем курсор
        self.center_pos = self.rect().center()
        self.cursor_pos = self.center_pos

    def initializeGL(self):
        glClearColor(0.1, 0.1, 0.1, 1.0)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glLightfv(GL_LIGHT0, GL_POSITION, [1, 1, 1, 0])

    def resizeGL(self, w, h):
        glViewport(0, 0, w, h)

    def paintGL(self):
        self.process_movement()
        self.draw()

    def draw_crosshair(self):
        width, height = self.width(), self.height()
        center_x, center_y = width // 2, height // 2

        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, width, height, 0, -1, 1)

        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()

        glDisable(GL_DEPTH_TEST)
        glDisable(GL_LIGHTING)
        glColor3f(1, 1, 1)

        glLineWidth(2)
        glBegin(GL_LINES)
        glVertex2f(center_x - 5, center_y)
        glVertex2f(center_x + 5, center_y)
        glVertex2f(center_x, center_y - 5)
        glVertex2f(center_x, center_y + 5)
        glEnd()

        glEnable(GL_LIGHTING)
        glEnable(GL_DEPTH_TEST)
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()

    def draw_grid(self, size=10, step=1):
        glDisable(GL_LIGHTING)
        glBegin(GL_LINES)
        glColor3f(0.3, 0.3, 0.3)
        for i in range(-size, size + 1, step):
            glVertex3f(i, 0, -size)
            glVertex3f(i, 0, size)
            glVertex3f(-size, 0, i)
            glVertex3f(size, 0, i)
        glEnd()
        glEnable(GL_LIGHTING)

    def draw_spheres(self):
        for i, sphere in enumerate(self.state.spheres):
            x, y, z, radius, r, g, b = sphere

            glPushMatrix()
            glTranslatef(x, y, z)

            if i == self.state.selected_sphere:
                glMaterialfv(GL_FRONT, GL_DIFFUSE, [1.0, 1.0, 0.0, 1.0])  # Желтый
            else:
                glMaterialfv(GL_FRONT, GL_DIFFUSE, [r, g, b, 1.0])

            gluSphere(self.state.sphere_quad, radius, 32, 32)
            glPopMatrix()

    def draw(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, self.width() / self.height(), 0.1, 100.0)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        gluLookAt(
            *self.state.camera_pos,
            *(self.state.camera_pos + self.state.camera_front),
            *self.state.camera_up
        )

        self.draw_grid()
        self.draw_spheres()
        self.draw_crosshair()

    def mouseMoveEvent(self, event: QMouseEvent):
        pos = event.pos()
        delta = pos - self.cursor_pos

        if delta.x() != 0 or delta.y() != 0:
            self.cursor_pos = self.center_pos
            self.cursor().setPos(self.mapToGlobal(self.center_pos))

        sensitivity = 0.1
        self.state.yaw += delta.x() * sensitivity
        self.state.pitch -= delta.y() * sensitivity
        self.state.pitch = max(-89, min(89, self.state.pitch))

        front = np.array([
            math.cos(math.radians(self.state.yaw)) * math.cos(math.radians(self.state.pitch)),
            math.sin(math.radians(self.state.pitch)),
            math.sin(math.radians(self.state.yaw)) * math.cos(math.radians(self.state.pitch))
        ])
        self.state.camera_front = front / np.linalg.norm(front)

    def keyPressEvent(self, event: QKeyEvent):
        # Игнорируем автоповторы
        print(event.key())
        if not event.isAutoRepeat():
            if event.key() in self.state.keys:
                self.state.keys[event.key()] = True
        event.accept()

    def keyReleaseEvent(self, event: QKeyEvent):
        # Игнорируем автоповторы
        if not event.isAutoRepeat():
            if event.key() in self.state.keys:
                self.state.keys[event.key()] = False
        event.accept()

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.RightButton:
            # Проверяем попадание в сферу
            for i, sphere in enumerate(self.state.spheres):
                x, y, z, radius, _, _, _ = sphere
                sphere_pos = np.array([x, y, z])
                ray_dir = self.state.camera_front

                # Простой рейкастинг
                L = sphere_pos - self.state.camera_pos
                tca = np.dot(L, ray_dir)
                d2 = np.dot(L, L) - tca * tca
                radius_squared = radius * radius

                if d2 <= radius_squared:
                    self.state.selected_sphere = i
                    break
            else:
                self.state.selected_sphere = -1

        elif event.button() == Qt.MouseButton.LeftButton:
            # Добавляем новую сферу перед камерой
            new_sphere = np.array([
                self.state.camera_pos[0] + self.state.camera_front[0] * 2,
                self.state.camera_pos[1] + self.state.camera_front[1] * 2,
                self.state.camera_pos[2] + self.state.camera_front[2] * 2,
                0.5,  # radius
                np.random.rand(),  # r
                np.random.rand(),  # g
                np.random.rand()  # b
            ], dtype=np.float32)

            self.state.spheres = np.vstack([self.state.spheres, new_sphere])

    def process_movement(self):
        speed = 0.1
        move_vec = np.zeros(3, dtype=np.float32)

        if self.state.keys[Qt.Key.Key_W]: move_vec += self.state.camera_front
        if self.state.keys[Qt.Key.Key_S]: move_vec -= self.state.camera_front
        if self.state.keys[Qt.Key.Key_A]: move_vec -= np.cross(self.state.camera_front, self.state.camera_up)
        if self.state.keys[Qt.Key.Key_D]: move_vec += np.cross(self.state.camera_front, self.state.camera_up)
        if self.state.keys[Qt.Key.Key_Space]: move_vec += self.state.camera_up
        if self.state.keys[Qt.Key.Key_C]: move_vec -= self.state.camera_up

        if np.any(move_vec):
            move_vec = move_vec / np.linalg.norm(move_vec) * speed
            self.state.camera_pos += move_vec


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("3D Spheres Editor")
        self.setGeometry(100, 100, 800, 600)

        self.opengl_widget = OpenGLWidget(self)
        self.setCentralWidget(self.opengl_widget)

    def keyPressEvent(self, event):
        print("Window key press")
        self.centralWidget().keyPressEvent(event)

    def keyReleaseEvent(self, event):
        self.centralWidget().keyReleaseEvent(event)


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()