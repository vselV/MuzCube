import numpy as np
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QWidget
from PyQt5.QtWidgets import QOpenGLWidget
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QSurfaceFormat
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import math
import sys


class SphereEditor3D(QOpenGLWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Настройки OpenGL
        fmt = QSurfaceFormat()
        fmt.setVersion(3, 3)
        fmt.setProfile(QSurfaceFormat.CoreProfile)
        self.setFormat(fmt)

        # Камера
        self.camera_pos = np.array([5.0, 5.0, 5.0], dtype=np.float32)
        self.camera_front = np.array([0.0, 0.0, -1.0], dtype=np.float32)
        self.camera_up = np.array([0.0, 1.0, 0.0], dtype=np.float32)
        self.yaw = -90.0
        self.pitch = 0.0
        self.last_mouse_pos = None

        # Сферы
        self.spheres = np.array([
            [0.0, 0.0, 0.0, 0.5, 1.0, 0.0, 0.0],
            [2.0, 0.0, 0.0, 0.5, 0.0, 1.0, 0.0],
            [0.0, 2.0, 0.0, 0.5, 0.0, 0.0, 1.0],
            [0.0, 0.0, 2.0, 0.5, 1.0, 1.0, 0.0]
        ], dtype=np.float32)

        self.selected_sphere = -1
        self.keys_pressed = set()

        # Таймер
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(16)  # ~60 FPS

        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.StrongFocus)

    def initializeGL(self):
        glClearColor(0.1, 0.1, 0.1, 1.0)
        glEnable(GL_DEPTH_TEST)

        # Шейдеры
        vertex_shader = """
        #version 330 core
        layout (location = 0) in vec3 aPos;
        uniform mat4 projection;
        uniform mat4 view;
        uniform mat4 model;
        void main() {
            gl_Position = projection * view * model * vec4(aPos, 1.0);
        }
        """

        fragment_shader = """
        #version 330 core
        out vec4 FragColor;
        uniform vec3 color;
        void main() {
            FragColor = vec4(color, 1.0);
        }
        """

        self.shader = compileProgram(
            compileShader(vertex_shader, GL_VERTEX_SHADER),
            compileShader(fragment_shader, GL_FRAGMENT_SHADER)
        )

        # Создание геометрии сферы
        self.create_sphere(radius=1.0, sectors=32, stacks=32)

    def create_sphere(self, radius, sectors, stacks):
        vertices = []

        sector_step = 2 * math.pi / sectors
        stack_step = math.pi / stacks

        for i in range(stacks + 1):
            stack_angle = math.pi / 2 - i * stack_step
            xy = radius * math.cos(stack_angle)
            z = radius * math.sin(stack_angle)

            for j in range(sectors + 1):
                sector_angle = j * sector_step
                x = xy * math.cos(sector_angle)
                y = xy * math.sin(sector_angle)
                vertices.extend([x, y, z])

        self.sphere_vertices = np.array(vertices, dtype=np.float32)

        # Индексы
        indices = []
        for i in range(stacks):
            k1 = i * (sectors + 1)
            k2 = k1 + sectors + 1

            for j in range(sectors):
                if i != 0:
                    indices.extend([k1, k2, k1 + 1])
                if i != (stacks - 1):
                    indices.extend([k1 + 1, k2, k2 + 1])
                k1 += 1
                k2 += 1

        self.sphere_indices = np.array(indices, dtype=np.uint32)

        # VAO, VBO, EBO
        self.vao = glGenVertexArrays(1)
        self.vbo = glGenBuffers(1)
        self.ebo = glGenBuffers(1)

        glBindVertexArray(self.vao)

        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.sphere_vertices.nbytes, self.sphere_vertices, GL_STATIC_DRAW)

        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ebo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.sphere_indices.nbytes, self.sphere_indices, GL_STATIC_DRAW)

        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 3 * sizeof(GLfloat), None)
        glEnableVertexAttribArray(0)

        glBindVertexArray(0)

    def resizeGL(self, w, h):
        glViewport(0, 0, w, h)
        self.projection = self.perspective_matrix(45, w / h, 0.1, 100.0)

    def perspective_matrix(self, fov, aspect, near, far):
        f = 1.0 / math.tan(math.radians(fov) / 2.0)
        return np.array([
            [f / aspect, 0, 0, 0],
            [0, f, 0, 0],
            [0, 0, (far + near) / (near - far), (2 * far * near) / (near - far)],
            [0, 0, -1, 0]
        ], dtype=np.float32)

    def look_at(self, position, target, up):
        zaxis = (position - target) / np.linalg.norm(position - target)
        xaxis = np.cross(up, zaxis) / np.linalg.norm(np.cross(up, zaxis))
        yaxis = np.cross(zaxis, xaxis)

        return np.array([
            [xaxis[0], yaxis[0], zaxis[0], 0],
            [xaxis[1], yaxis[1], zaxis[1], 0],
            [xaxis[2], yaxis[2], zaxis[2], 0],
            [-np.dot(xaxis, position), -np.dot(yaxis, position), -np.dot(zaxis, position), 1]
        ], dtype=np.float32)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Матрица вида
        view = self.look_at(self.camera_pos, self.camera_pos + self.camera_front, self.camera_up)

        glUseProgram(self.shader)
        glUniformMatrix4fv(glGetUniformLocation(self.shader, "projection"), 1, GL_FALSE, self.projection)
        glUniformMatrix4fv(glGetUniformLocation(self.shader, "view"), 1, GL_FALSE, view)

        # Отрисовка сфер
        glBindVertexArray(self.vao)
        for i, sphere in enumerate(self.spheres):
            x, y, z, radius, r, g, b = sphere

            model = np.eye(4, dtype=np.float32)
            model[:3, :3] *= radius
            model[:3, 3] = [x, y, z]

            glUniformMatrix4fv(glGetUniformLocation(self.shader, "model"), 1, GL_FALSE, model)
            color = [1.0, 1.0, 0.0] if i == self.selected_sphere else [r, g, b]
            glUniform3f(glGetUniformLocation(self.shader, "color"), *color)

            glDrawElements(GL_TRIANGLES, len(self.sphere_indices), GL_UNSIGNED_INT, None)

        glBindVertexArray(0)
        glUseProgram(0)

    def mouseMoveEvent(self, event):
        if self.last_mouse_pos:
            dx = event.x() - self.last_mouse_pos.x()
            dy = event.y() - self.last_mouse_pos.y()

            sensitivity = 0.1
            self.yaw += dx * sensitivity
            self.pitch -= dy * sensitivity
            self.pitch = max(-89, min(89, self.pitch))

            front = np.array([
                math.cos(math.radians(self.yaw)) * math.cos(math.radians(self.pitch)),
                math.sin(math.radians(self.pitch)),
                math.sin(math.radians(self.yaw)) * math.cos(math.radians(self.pitch))
            ])
            self.camera_front = front / np.linalg.norm(front)

        center = self.rect().center()
        if event.pos() != center:
            self.cursor().setPos(self.mapToGlobal(center))

        self.last_mouse_pos = event.pos()

    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            for i, sphere in enumerate(self.spheres):
                x, y, z, radius, _, _, _ = sphere
                sphere_pos = np.array([x, y, z])
                ray_dir = self.camera_front

                L = sphere_pos - self.camera_pos
                tca = np.dot(L, ray_dir)
                d2 = np.dot(L, L) - tca * tca
                radius_squared = radius * radius

                if d2 <= radius_squared:
                    self.selected_sphere = i
                    break
            else:
                self.selected_sphere = -1

        elif event.button() == Qt.LeftButton:
            new_sphere = np.array([
                self.camera_pos[0] + self.camera_front[0] * 2,
                self.camera_pos[1] + self.camera_front[1] * 2,
                self.camera_pos[2] + self.camera_front[2] * 2,
                0.5,
                np.random.rand(),
                np.random.rand(),
                np.random.rand()
            ], dtype=np.float32)

            self.spheres = np.vstack([self.spheres, new_sphere])

    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_W:
            self.keys_pressed.add(b'w')
        elif key == Qt.Key_S:
            self.keys_pressed.add(b's')
        elif key == Qt.Key_A:
            self.keys_pressed.add(b'a')
        elif key == Qt.Key_D:
            self.keys_pressed.add(b'd')
        elif key == Qt.Key_Space:
            self.keys_pressed.add(b' ')
        elif key == Qt.Key_C:
            self.keys_pressed.add(b'c')
        elif key == Qt.Key_Escape:
            self.close()

    def keyReleaseEvent(self, event):
        key = event.key()
        if key == Qt.Key_W and b'w' in self.keys_pressed:
            self.keys_pressed.remove(b'w')
        elif key == Qt.Key_S and b's' in self.keys_pressed:
            self.keys_pressed.remove(b's')
        elif key == Qt.Key_A and b'a' in self.keys_pressed:
            self.keys_pressed.remove(b'a')
        elif key == Qt.Key_D and b'd' in self.keys_pressed:
            self.keys_pressed.remove(b'd')
        elif key == Qt.Key_Space and b' ' in self.keys_pressed:
            self.keys_pressed.remove(b' ')
        elif key == Qt.Key_C and b'c' in self.keys_pressed:
            self.keys_pressed.remove(b'c')

    def process_movement(self):
        speed = 0.1
        move_vec = np.zeros(3, dtype=np.float32)

        if b'w' in self.keys_pressed: move_vec += self.camera_front
        if b's' in self.keys_pressed: move_vec -= self.camera_front
        if b'a' in self.keys_pressed: move_vec -= np.cross(self.camera_front, self.camera_up)
        if b'd' in self.keys_pressed: move_vec += np.cross(self.camera_front, self.camera_up)
        if b' ' in self.keys_pressed: move_vec += self.camera_up
        if b'c' in self.keys_pressed: move_vec -= self.camera_up

        if np.any(move_vec):
            move_vec = move_vec / np.linalg.norm(move_vec) * speed
            self.camera_pos += move_vec

    def update(self):
        self.process_movement()
        super().update()


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("3D Sphere Editor")
        self.resize(800, 600)
        layout = QVBoxLayout()
        self.gl_widget = SphereEditor3D()
        layout.addWidget(self.gl_widget)
        self.setLayout(layout)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    fmt = QSurfaceFormat()
    fmt.setVersion(3, 3)
    fmt.setProfile(QSurfaceFormat.CoreProfile)
    QSurfaceFormat.setDefaultFormat(fmt)

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())