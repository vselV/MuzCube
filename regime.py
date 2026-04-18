import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *
import math
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtOpenGLWidgets import QOpenGLWidget
from PyQt6.QtCore import Qt, QTimer, QPoint
from PyQt6.QtGui import QKeyEvent, QMouseEvent


class State:
    def __init__(self):
        # Камера
        self.camera_pos = np.array([5, 5, 5], dtype=np.float32)
        self.camera_front = np.array([0, 0, -1], dtype=np.float32)
        self.camera_up = np.array([0, 1, 0], dtype=np.float32)
        self.yaw = -90.0
        self.pitch = 0.0

        # Управление
        self.keys = {
            Qt.Key.Key_W: False,
            Qt.Key.Key_S: False,
            Qt.Key.Key_A: False,
            Qt.Key.Key_D: False,
            Qt.Key.Key_Space: False,
            Qt.Key.Key_C: False,
            Qt.Key.Key_Q: False  # Клавиша для переключения режима
        }

        # Геометрия
        self.spheres = np.array([
            [0.0, 0.0, 0.0, 0.5, 1.0, 0.0, 0.0],
            [2.0, 0.0, 0.0, 0.5, 0.0, 1.0, 0.0],
            [0.0, 2.0, 0.0, 0.5, 0.0, 0.0, 1.0],
            [0.0, 0.0, 2.0, 0.5, 1.0, 1.0, 0.0]
        ], dtype=np.float32)

        self.selected_sphere = -1
        self.sphere_quad = gluNewQuadric()
        self.rotate_mode = True  # Флаг режима вращения


class OpenGLWidget(QOpenGLWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.state = State()

        # Настройки фокуса и таймера
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setFocus()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(16)

        # Инициализация курсора
        self.center_pos = QPoint(self.width() // 2, self.height() // 2)
        self.update_cursor_mode()

    def update_cursor_mode(self):
        """Обновляет режим курсора в зависимости от состояния rotate_mode"""
        if self.state.rotate_mode:
            self.setCursor(Qt.CursorShape.BlankCursor)
            self.setMouseTracking(True)
            self.cursor().setPos(self.mapToGlobal(self.center_pos))
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)
            self.setMouseTracking(False)

    def initializeGL(self):
        glClearColor(0.1, 0.1, 0.1, 1.0)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glLightfv(GL_LIGHT0, GL_POSITION, [1, 1, 1, 0])

    def resizeGL(self, w, h):
        glViewport(0, 0, w, h)
        self.center_pos = QPoint(w // 2, h // 2)

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
    # ... (остальные методы рисования остаются без изменений) ...

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.state.rotate_mode:
            # Режим вращения камеры
            pos = event.pos()
            delta = pos - self.center_pos

            # Всегда возвращаем курсор в центр
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

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            if not self.state.rotate_mode:
                # В режиме курсора проверяем клик по сфере
                self.check_sphere_click(event.pos())
            else:
                # В режиме вращения - добавляем новую сферу
                self.add_sphere_in_front()

        elif event.button() == Qt.MouseButton.RightButton:
            # В любом режиме - выделение сферы
            self.select_sphere(event.pos())

    def check_sphere_click(self, pos):
        """Проверяет клик по сфере в режиме курсора"""
        # Преобразуем координаты экрана в координаты OpenGL
        x = pos.x()
        y = self.height() - pos.y()

        # Буфер для хранения идентификаторов объектов
        select_buf = glSelectBuffer(512)
        glRenderMode(GL_SELECT)
        glInitNames()
        glPushName(0)

        # Настраиваем матрицу проекции для селекции
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        viewport = glGetIntegerv(GL_VIEWPORT)
        gluPickMatrix(x, y, 5.0, 5.0, viewport)
        gluPerspective(45, self.width() / self.height(), 0.1, 100.0)

        # Рендерим сцены с идентификаторами
        glMatrixMode(GL_MODELVIEW)
        for i, sphere in enumerate(self.state.spheres):
            glLoadName(i)
            x, y, z, radius, _, _, _ = sphere
            glPushMatrix()
            glTranslatef(x, y, z)
            gluSphere(self.state.sphere_quad, radius, 32, 32)
            glPopMatrix()

        # Восстанавливаем обычный режим
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        hits = glRenderMode(GL_RENDER)

        # Обрабатываем попадания
        if hits:
            names = []
            for hit in hits:
                names.extend(hit[2])
            if names:
                self.state.selected_sphere = names[0]

    def select_sphere(self, pos):
        """Выделяет сферу с помощью рейкастинга"""
        # ... (ваш существующий код для выделения сфер) ...

    def add_sphere_in_front(self):
        """Добавляет новую сферу перед камерой"""
        # ... (ваш существующий код для добавления сфер) ...

    def keyPressEvent(self, event: QKeyEvent):
        if not event.isAutoRepeat():
            if event.key() == Qt.Key.Key_Q:
                # Переключаем режим по нажатию Q
                self.state.rotate_mode = not self.state.rotate_mode
                self.update_cursor_mode()
            elif event.key() in self.state.keys:
                self.state.keys[event.key()] = True
        event.accept()

    def keyReleaseEvent(self, event: QKeyEvent):
        if not event.isAutoRepeat() and event.key() in self.state.keys:
            self.state.keys[event.key()] = False
        event.accept()
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
    # ... (остальные методы остаются без изменений) ...


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("3D Spheres Editor (Q - toggle mode)")
        self.setGeometry(100, 100, 800, 600)
        self.opengl_widget = OpenGLWidget(self)
        self.setCentralWidget(self.opengl_widget)


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()