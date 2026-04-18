import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import sys
import math


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
            b'w': False, b's': False, b'a': False, b'd': False,
            b' ': False, b'c': False
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


state = State()


def init():
    glClearColor(0.1, 0.1, 0.1, 1.0)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glLightfv(GL_LIGHT0, GL_POSITION, [1, 1, 1, 0])
    glutSetCursor(GLUT_CURSOR_NONE)


def draw_crosshair():
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 800, 600, 0)

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    glDisable(GL_DEPTH_TEST)
    glDisable(GL_LIGHTING)
    glColor3f(1, 1, 1)

    glLineWidth(2)
    glBegin(GL_LINES)
    glVertex2f(395, 300)
    glVertex2f(405, 300)
    glVertex2f(400, 295)
    glVertex2f(400, 305)
    glEnd()

    glEnable(GL_LIGHTING)
    glEnable(GL_DEPTH_TEST)
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()


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


def draw_spheres():
    for i, sphere in enumerate(state.spheres):
        x, y, z, radius, r, g, b = sphere

        glPushMatrix()
        glTranslatef(x, y, z)

        if i == state.selected_sphere:
            glMaterialfv(GL_FRONT, GL_DIFFUSE, [1.0, 1.0, 0.0, 1.0])  # Желтый
        else:
            glMaterialfv(GL_FRONT, GL_DIFFUSE, [r, g, b, 1.0])

        gluSphere(state.sphere_quad, radius, 32, 32)
        glPopMatrix()


def draw():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, 800 / 600, 0.1, 100.0)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(
        *state.camera_pos,
        *(state.camera_pos + state.camera_front),
        *state.camera_up
    )

    draw_grid()
    draw_spheres()
    draw_crosshair()

    glutSwapBuffers()


def mouse_motion(x, y):
    if x != 400 or y != 300:
        glutWarpPointer(400, 300)

    sensitivity = 0.1
    state.yaw += (x - 400) * sensitivity
    state.pitch += (300 - y) * sensitivity
    state.pitch = max(-89, min(89, state.pitch))

    front = np.array([
        math.cos(math.radians(state.yaw)) * math.cos(math.radians(state.pitch)),
        math.sin(math.radians(state.pitch)),
        math.sin(math.radians(state.yaw)) * math.cos(math.radians(state.pitch))
    ])
    state.camera_front = front / np.linalg.norm(front)


def keyboard(key, x, y):
    if key in state.keys:
        state.keys[key] = True
    if key == b'\x1b':
        sys.exit(0)


def keyboard_up(key, x, y):
    if key in state.keys:
        state.keys[key] = False


def process_movement():
    speed = 0.1
    move_vec = np.zeros(3, dtype=np.float32)

    if state.keys[b'w']: move_vec += state.camera_front
    if state.keys[b's']: move_vec -= state.camera_front
    if state.keys[b'a']: move_vec -= np.cross(state.camera_front, state.camera_up)
    if state.keys[b'd']: move_vec += np.cross(state.camera_front, state.camera_up)
    if state.keys[b' ']: move_vec += state.camera_up
    if state.keys[b'c']: move_vec -= state.camera_up

    if np.any(move_vec):
        move_vec = move_vec / np.linalg.norm(move_vec) * speed
        state.camera_pos += move_vec


def mouse_click(button, state_btn, x, y):
    if button == GLUT_RIGHT_BUTTON and state_btn == GLUT_DOWN:
        # Проверяем попадание в сферу
        for i, sphere in enumerate(state.spheres):
            x, y, z, radius, _, _, _ = sphere
            sphere_pos = np.array([x, y, z])
            ray_dir = state.camera_front

            # Простой рейкастинг
            L = sphere_pos - state.camera_pos
            tca = np.dot(L, ray_dir)
            d2 = np.dot(L, L) - tca * tca
            radius_squared = radius * radius

            if d2 <= radius_squared:
                state.selected_sphere = i
                break
        else:
            state.selected_sphere = -1

    elif button == GLUT_LEFT_BUTTON and state_btn == GLUT_DOWN:
        # Добавляем новую сферу перед камерой
        new_sphere = np.array([
            state.camera_pos[0] + state.camera_front[0] * 2,
            state.camera_pos[1] + state.camera_front[1] * 2,
            state.camera_pos[2] + state.camera_front[2] * 2,
            0.5,  # radius
            np.random.rand(),  # r
            np.random.rand(),  # g
            np.random.rand()  # b
        ], dtype=np.float32)

        state.spheres = np.vstack([state.spheres, new_sphere])


def timer(value):
    process_movement()
    glutPostRedisplay()
    glutTimerFunc(16, timer, 0)


def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(800, 600)
    glutCreateWindow(b"3D Spheres Editor")

    glutWarpPointer(400, 300)
    glutSetCursor(GLUT_CURSOR_NONE)

    glutDisplayFunc(draw)
    glutPassiveMotionFunc(mouse_motion)
    glutKeyboardFunc(keyboard)
    glutKeyboardUpFunc(keyboard_up)
    glutMouseFunc(mouse_click)
    glutTimerFunc(0, timer, 0)

    init()
    glutMainLoop()


if __name__ == "__main__":
    main()