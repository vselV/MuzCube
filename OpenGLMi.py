import numpy as np
from PyQt6.QtWidgets import QApplication, QVBoxLayout, QWidget
from PyQt6.QtOpenGLWidgets import QOpenGLWidget
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QSurfaceFormat
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import math
import sys
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from OpenGL import GL

class SphereEditor3D(QOpenGLWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        fmt = QSurfaceFormat()
        fmt.setVersion(3, 3)
        fmt.setProfile(QSurfaceFormat.OpenGLContextProfile.CoreProfile)
        self.setFormat(fmt)

        # Camera setup
        self.camera_pos = np.array([5.0, 5.0, 5.0], dtype=np.float32)
        self.camera_front = np.array([0.0, 0.0, -1.0], dtype=np.float32)
        self.camera_up = np.array([0.0, 1.0, 0.0], dtype=np.float32)
        self.yaw = -90.0
        self.pitch = 0.0

        # Sphere data
        self.spheres = np.array([
            [0.0, 0.0, 0.0, 0.5, 1.0, 0.0, 0.0],
            [2.0, 0.0, 0.0, 0.5, 0.0, 1.0, 0.0],
            [0.0, 2.0, 0.0, 0.5, 0.0, 0.0, 1.0],
            [0.0, 0.0, 2.0, 0.5, 1.0, 1.0, 0.0]
        ], dtype=np.float32)

        self.selected_sphere = -1
        self.keys_pressed = set()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(16)

        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def initializeGL(self):
        glClearColor(0.5, 0.1, 0.1, 1.0)
        glEnable(GL_DEPTH_TEST)

        # Create a simple shader program
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

        # Create a simple sphere VAO/VBO (you should replace this with actual sphere geometry)
        self.sphere_vao = glGenVertexArrays(1)
        glBindVertexArray(self.sphere_vao)

        # For simplicity, we'll just draw a point
        vertices = np.array([0.0, 0.0, 0.0], dtype=np.float32)
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)
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

    def draw_grid(size=10, step=1):
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
       # GL.glDrawArrays(GL.GL_TRIANGLES, 0, 1)
      #  self.draw_grid()
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Calculate view matrix
        view = self.look_at(self.camera_pos, self.camera_pos + self.camera_front, self.camera_up)

        glUseProgram(self.shader)

        # Set projection and view uniforms
        glUniformMatrix4fv(glGetUniformLocation(self.shader, "projection"), 1, GL_FALSE, self.projection)
        glUniformMatrix4fv(glGetUniformLocation(self.shader, "view"), 1, GL_FALSE, view)

        # Draw spheres (simplified - just points for now)
        glBindVertexArray(self.sphere_vao)
        for i, sphere in enumerate(self.spheres):
            x, y, z, radius, r, g, b = sphere

            # Create model matrix
            model = np.eye(4, dtype=np.float32)
            model[:3, 3] = [x, y, z]

            glUniformMatrix4fv(glGetUniformLocation(self.shader, "model"), 1, GL_FALSE, model)
            color = [1.0, 1.0, 0.0] if i == self.selected_sphere else [r, g, b]
            glUniform3f(glGetUniformLocation(self.shader, "color"), *color)

            glDrawArrays(GL_POINTS, 0, 1)

        glBindVertexArray(0)
        glUseProgram(0)


    # ... (keep your existing mouse and keyboard event handlers)


class MainWindow(QOpenGLWidget):
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
    fmt.setProfile(QSurfaceFormat.OpenGLContextProfile.CoreProfile)
    QSurfaceFormat.setDefaultFormat(fmt)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())