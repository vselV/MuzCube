import sys

import numpy as np
from OpenGL import GL
from PyQt6.QtOpenGL import QOpenGLWindow
from PyQt6.QtOpenGLWidgets import QOpenGLWidget
from PyQt6.QtWidgets import QMainWindow, QHBoxLayout, QApplication
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set-up MainWindow
        self.setWindowTitle("ORCAgui")
        self.mainwindow_layout = QHBoxLayout()

        self.show()


class OpenGLWindow(QOpenGLWidget):

    def __init__(self):
        super().__init__()

    def draw_grid(self,size=10, step=1):
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
    def initializeGL(self):
        vertices = np.array([0.0, 1.0, -1.0, -1.0, 1.0, -1.0], dtype=np.float32)

        bufferId = GL.glGenBuffers(1)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, bufferId)
        GL.glBufferData(GL.GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL.GL_STATIC_DRAW)

        GL.glEnableVertexAttribArray(0)
        GL.glVertexAttribPointer(0, 2, GL.GL_FLOAT, GL.GL_FALSE, 0, None)

    def paintGL(self):
        self.draw_grid()
        #GL.glDrawArrays(GL.GL_TRIANGLES, 0, 3)


if __name__ == '__main__':
    app = QApplication(sys.argv)
   # window = MainWindow()
    GLwindow = OpenGLWindow()
    GLwindow.show()
    app.exec()