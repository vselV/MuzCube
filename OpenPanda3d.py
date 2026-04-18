import numpy as np
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout
from PyQt6.QtCore import Qt, QTimer
from direct.showbase.ShowBase import ShowBase
from panda3d.core import (
    NodePath,
    PerspectiveLens,
    Vec3,
    Material,
    AmbientLight,
    DirectionalLight
)
import sys
from direct.gui.DirectGui import DirectButton


class Panda3DWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("3D Editor with Panda3D")
        self.resize(800, 600)

        # Создаем базовый класс Panda3D
        self.panda = ShowBase(windowType='offscreen')
        self.panda.disableMouse()

        # Настройка камеры
        self.camera_pos = Vec3(5, 5, 5)
        self.camera_target = Vec3(0, 0, 0)
        self.camera_up = Vec3(0, 1, 0)

        # Сферы
        self.spheres = []
        self.selected_sphere = None

        # Управление
        self.keys_pressed = set()

        # Таймер
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_scene)
        self.timer.start(16)  # ~60 FPS

        self.init_scene()
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def init_scene(self):
        # Настройка камеры
        self.panda.cam.setPos(self.camera_pos)
        self.panda.cam.lookAt(self.camera_target, self.camera_up)

        # Освещение
        ambient = AmbientLight("ambient")
        ambient.setColor((0.2, 0.2, 0.2, 1))
        self.panda.render.setLight(self.panda.render.attachNewNode(ambient))

        directional = DirectionalLight("directional")
        directional.setColor((0.8, 0.8, 0.8, 1))
        directional_np = self.panda.render.attachNewNode(directional)
        directional_np.setPos(1, 1, 1)
        directional_np.lookAt(0, 0, 0)
        self.panda.render.setLight(directional_np)

        # Создаем начальные сферы
        self.create_sphere(Vec3(0, 0, 0), (1, 0, 0))
        self.create_sphere(Vec3(2, 0, 0), (0, 1, 0))
        self.create_sphere(Vec3(0, 2, 0), (0, 0, 1))
        self.create_sphere(Vec3(0, 0, 2), (1, 1, 0))

    def create_sphere(self, position, color):
        sphere = self.panda.loader.loadModel("models/misc/sphere")
        sphere.setPos(position)
        sphere.setScale(0.5)

        material = Material()
        material.setDiffuse(color)
        sphere.setMaterial(material)

        sphere.reparentTo(self.panda.render)
        self.spheres.append(sphere)
        return sphere

    def update_scene(self):
        # Обработка движения
        speed = 0.1
        move_vec = Vec3(0, 0, 0)

        if 'w' in self.keys_pressed: move_vec.y += 1
        if 's' in self.keys_pressed: move_vec.y -= 1
        if 'a' in self.keys_pressed: move_vec.x -= 1
        if 'd' in self.keys_pressed: move_vec.x += 1
        if ' ' in self.keys_pressed: move_vec.z += 1
        if 'c' in self.keys_pressed: move_vec.z -= 1

        if move_vec.length() > 0:
            move_vec.normalize()
            self.camera_pos += move_vec * speed
            self.panda.cam.setPos(self.camera_pos)
            self.panda.cam.lookAt(self.camera_target, self.camera_up)

    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key.Key_W:
            self.keys_pressed.add('w')
        elif key == Qt.Key.Key_S:
            self.keys_pressed.add('s')
        elif key == Qt.Key.Key_A:
            self.keys_pressed.add('a')
        elif key == Qt.Key.Key_D:
            self.keys_pressed.add('d')
        elif key == Qt.Key.Key_Space:
            self.keys_pressed.add(' ')
        elif key == Qt.Key.Key_C:
            self.keys_pressed.add('c')
        elif key == Qt.Key.Key_Escape:
            self.close()

    def keyReleaseEvent(self, event):
        key = event.key()
        if key == Qt.Key.Key_W:
            self.keys_pressed.discard('w')
        elif key == Qt.Key.Key_S:
            self.keys_pressed.discard('s')
        elif key == Qt.Key.Key_A:
            self.keys_pressed.discard('a')
        elif key == Qt.Key.Key_D:
            self.keys_pressed.discard('d')
        elif key == Qt.Key.Key_Space:
            self.keys_pressed.discard(' ')
        elif key == Qt.Key.Key_C:
            self.keys_pressed.discard('c')

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.RightButton:
            # Выделение сферы
            if self.selected_sphere:
                self.selected_sphere.setColor(1, 1, 1, 1)

            # Простейший выбор ближайшей сферы
            closest = None
            min_dist = float('inf')

            for sphere in self.spheres:
                dist = (sphere.getPos() - self.camera_pos).length()
                if dist < min_dist:
                    min_dist = dist
                    closest = sphere

            if closest:
                closest.setColor(1, 1, 0, 1)  # Желтый
                self.selected_sphere = closest

        elif event.button() == Qt.MouseButton.LeftButton:
            # Добавление новой сферы
            new_pos = self.camera_pos + Vec3(0, 2, 0)  # Перед камерой
            color = (np.random.random(), np.random.random(), np.random.random(), 1)
            self.create_sphere(new_pos, color)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Для Applications можно попробовать:
    # app.setAttribute(Qt.ApplicationAttribute.AA_UseOpenGLES)

    window = Panda3DWidget()
    window.show()

    sys.exit(app.exec())