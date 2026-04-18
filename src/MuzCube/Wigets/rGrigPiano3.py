
import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget,
                             QHBoxLayout, QVBoxLayout, QFrame, QGraphicsScene,
                             QGraphicsRectItem )
from PyQt6.QtCore import Qt,  QRectF
from PyQt6.QtGui import QPainter, QColor, QBrush,  QPen
from src.MuzCube.Wigets.rGrigEvents import LinkedView
from src.MuzCube.UtilClasses.rGrigPyKeys import  KeyData, KeyColorsObj
def get_hover_color_hsl(base_color, lightness_change=0.1):
    h, s, l, a = base_color.getHslF()
    if l > 0.5:
        new_lightness = max(0.0, l - lightness_change)
    else:
        new_lightness = min(1.0, l + lightness_change)
    new_color = QColor.fromHslF(h, s, new_lightness, a)
    return new_color

class KeyRect(QGraphicsRectItem):
    def __init__(self, rect, is_black=False, level=0, max_level=1, colors = None):
        super().__init__(rect)
        self.is_black = is_black
        self.level = level
        self.max_level = max_level
        self.is_hovered = False
        self.setAcceptHoverEvents(True)
        self.pen = QPen(QColor(0,0,0))
        self.pen.setCosmetic(True)
        self.setPen(self.pen)

        self.colors = colors
        if colors is None:
            self.colors = KeyColorsObj()
        self.setBrush(QBrush(self.colors.get_col(self.level)))

    def setColors(self,colors):
        self.colors = colors

    def hoverEnterEvent(self, event):
        self.is_hovered = True
        self.updateColor()
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        self.is_hovered = False
        self.updateColor()
        super().hoverLeaveEvent(event)

    def updateColor(self):
        if self.is_hovered:
            self.setBrush(QBrush(self.colors.get_hov(self.level)))
        else:
            self.setBrush(QBrush(self.colors.get_col(self.level)))

class VerticalKeyScene(QGraphicsScene):
    octave_pixels = 600
    cf_h = 0.33
    width_pixels = 400 * cf_h
    black_level = 270 * cf_h
    black_off_set = 200 * cf_h
    black_cf = 0.7
    def __init__(self, parent=None):
        super().__init__(parent)
        self.edo = 31
        self.oct = 2
        self.one_key = self.octave_pixels / self.edo
        self.oct_up = 2
        self.oct_down = 2
        self.data = KeyData(self.edo, self.oct)
        self.draw_piano(self.oct_up,self.oct_down)

    def set_Y_Space(self,start,height):
        rect = self.sceneRect()
        self.setSceneRect(rect.x(),start,rect.width(),height)
    def rectDrawPianoDown(self):

        w_b = self.data.get_black_white_keys()
        white = w_b[0]
        black = w_b[1]
        # Рисуем белые клавиши
        for ct in range(len(white)):
            key = white[ct]
            item = KeyRect(
                QRectF(0, ct * self.octave_pixels / len(white), self.width_pixels, self.octave_pixels / len(white)),
                is_black=False
            )
            self.addItem(item)

        # Рисуем черные клавиши
        for bl in black:
            ## print(bl.level)
            shir_cf = 1 - (bl.max_level - bl.level) * 0.2
            shir_cf = 1
            item = KeyRect(
                QRectF(0, bl.step * self.one_key, self.black_level - (bl.level-1) * (self.black_off_set / bl.max_level),
                       bl.key_shir * self.one_key *  shir_cf),
                is_black=True,
                level=bl.level,
                max_level=bl.max_level
            )
            self.addItem(item)

    def rectDrawPiano(self,offset_oct):
        real_offset = offset_oct * self.octave_pixels
        w_b = self.data.get_black_white_keys()
        white = w_b[0]
        black = w_b[1]

        # Рисуем белые клавиши (перевернутые)
        for ct in range(len(white)):
            key = white[ct]
            # Переворачиваем по вертикали: y = общая высота - позиция - высота
            y_pos = self.octave_pixels - (ct * self.octave_pixels / len(white)) - (self.octave_pixels / len(white))
            item = KeyRect(
                QRectF(0, real_offset + y_pos, self.width_pixels, self.octave_pixels / len(white)),
                is_black=False
            )
            self.addItem(item)

        # Рисуем черные клавиши (перевернутые)

        for bl in black:
            ## print(bl.level)
            cf_defence = bl.max_level / 2
            shir_cf = 1 - (bl.max_level - bl.level) * 0.2
            shir_cf = 1
            if bl.level == 1 and  bl.max_level - bl.local_max_level >= cf_defence:
                shir_cf = (shir_cf - shir_cf/bl.key_shir) + (shir_cf/bl.key_shir * 1.5)
            # Переворачиваем по вертикали: y = общая высота - позиция - высота
            y_pos = self.octave_pixels - (bl.step * self.one_key) - (bl.key_shir * self.one_key * shir_cf)
            item = KeyRect(
                QRectF(0, real_offset + y_pos, self.black_level - (bl.level - 1) * (self.black_off_set / bl.max_level),
                       bl.key_shir * self.one_key * shir_cf),
                is_black=True,
                level=bl.level,
                max_level=bl.max_level
            )
            self.addItem(item)
    def draw_piano(self,octave_up,octave_down):
        for i in range(octave_up):
            self.rectDrawPiano(i)
        for i in range(octave_down):
            self.rectDrawPiano(-i-1)
    def set_key_data(self,data):
        if self.data != data:
            self.data = data
            self.edo = data.edo
            self.oct = data.oct
            self.one_key = self.octave_pixels / self.edo
            self.clear()
            self.draw_piano(self.oct_up,self.oct_down)




class PianoView(LinkedView):
    def __init__(self, main_scene,scene):
        super().__init__(main_scene,scene)
        rect = main_scene.sceneRect()
        rect2 = scene.sceneRect()
        scene.setSceneRect(rect2.x(),rect.y(),rect2.width(),rect.height())
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setFixedWidth(rect2.width())
        self.setFrameShape(QFrame.Shape.NoFrame)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Вертикальное пианино")
        self.setGeometry(100, 100, 800, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QHBoxLayout()
        central_widget.setLayout(layout)

        # Создаем сцену и вид
        scene = VerticalKeyScene()
        piano_view = PianoView(QGraphicsScene(),scene)

        # Добавляем виджет настроек
        settings_widget = QFrame()
        settings_widget.setFrameStyle(QFrame.Shape.Box)
        settings_widget.setFixedWidth(0)
        settings_widget.setStyleSheet("background-color: #f0f0f0; padding: 10px;")

        layout.addWidget(piano_view)
        layout.addWidget(settings_widget)

        # Информация о системе
        info_text = f"""
        <h3>Настройки пианино</h3>
        <p>EDO: {scene.edo}</p>
        <p>Октав: {scene.oct}</p>
        <p>Высота октавы: {scene.octave_pixels}px</p>
        <p>Ширина клавиш: {scene.width_pixels}px</p>
        """
        settings_widget.setLayout(QVBoxLayout())
        info_label = QWidget()
        info_label.setStyleSheet("font-family: Arial; font-size: 12px;")
        settings_widget.layout().addWidget(info_label)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())