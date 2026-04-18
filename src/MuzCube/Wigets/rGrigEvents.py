from PyQt6.QtCore import  QRectF, QPointF
from PyQt6.QtGui import QPainter
from PyQt6.QtWidgets import (QComboBox,  QDockWidget, QVBoxLayout,
                             QHBoxLayout, QWidget,  QGraphicsView,   QGraphicsRectItem, QLabel, QPushButton,  QStyleOptionGraphicsItem, QStyle,  QGridLayout, QFrame)

from src.MuzCube.UtilClasses.rGrigDataEvt import EvtVariants
from src.MuzCube.UtilClasses.rGrigGrids import *
from src.MuzCube.UtilClasses.QtKeyTest import *
from src.MuzCube.UtilClasses.rGrigMixins import *

#DefaultColorGrid()

class ResizeRect(QGraphicsRectItem,MixinRemove):
    def __init__(self, rect, parent=None, colors = DefaultColorRect()):
        super().__init__(rect, parent)
        MixinRemove.__init__(self)

        self.colors = colors


        self.transforms = QTransform()
        # Настройки внешнего вида
        self._normal_color = QColor(100, 150, 255, 150)
        self._hover_color = QColor(100, 200, 255, 200)
        self._selected_color = QColor(255, 150, 50, 200)
        self._mute_color = QColor(100, 200, 150, 200)

        self.normal_color = self._normal_color
        self.hover_color = self._hover_color
        self.selected_color = self._selected_color
        self.mute_color = self._mute_color
        self.muted = False

        self.setBrush(self.colors.normal_brush)
        self.setPen(self.colors.normal_pen)

        self.text_item = None

    def mute(self):
        self.muted = True
    def unmute(self):
        self.muted = False
    def dark(self):
        self.normal_color = QColor(self._normal_color.red(), self._normal_color.green(), self._normal_color.blue(),self._normal_color.alpha()/2)
    def normal(self):
        self.normal_color = self._normal_color


    def paint(self, painter, option, widget):
        self.transforms = painter.transform()
        if self.isSelected():
            self.setBrush(self.colors.selected_brush)
        elif self.muted:
            self.setBrush(self.colors.mute_brush)
            self.setPen(self.colors.mute_pen)
        else:
            self.setBrush(self.colors.normal_brush)
            self.setPen(self.colors.normal_pen)
        custom_option = QStyleOptionGraphicsItem(option)
        if custom_option.state & QStyle.StateFlag.State_Selected:
            custom_option.state &= ~QStyle.StateFlag.State_Selected
        super().paint(painter, custom_option, widget)

    def paint6(self, painter, option, widget):
        painter.save()

        # Применяем прозрачность
        painter.setOpacity(self._opacity)

        # Сбрасываем трансформацию
        self.transforms = painter.transform()
        painter.resetTransform()

        # Получаем view
        view = self.scene().views()[0] if self.scene() and self.scene().views() else None
        if view:
            # Преобразуем координаты в экранные (QPoint -> QPointF)
            rect = self.rect()
            pos = self.pos()
            top_left = view.mapFromScene(rect.topLeft() + pos)
            bottom_right = view.mapFromScene(rect.bottomRight() + pos)
            # Создаем QPointF из QPoint
            top_left_f = QPointF(top_left)
            bottom_right_f = QPointF(bottom_right)
            # Создаем прямоугольник в экранных координатах
            screen_rect = QRectF(top_left_f, bottom_right_f)

            # Рисуем
            painter.setPen(self.pen())
            if self.muted:
                painter.setBrush(self.mute_color)
            else:
                if self.isSelected():
                    painter.setBrush(self.selected_color)
                else:
                    painter.setBrush(self.brush())
            painter.drawRect(screen_rect)
        else:
            # Fallback
            super().paint(painter, option, widget)

        painter.setTransform(self.transforms)
        painter.restore()

class RectangleEvtItem(ResizeRect):
    def __init__(self, rect, parent=None):
        super().__init__(rect, parent)
        self.vel = 100
        self.chan = 0
        self.duration = 0
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.RightButton:
            self.fade_out_and_remove()
            return

class SnappedScene(QGraphicsScene):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.h_lines_snap = True
        self.v_lines_snap = True
        self.grid_evts = evts
        self.rect_height = 30
    def snap_to_grid(self, point, **kwargs):
        x, y = point.x(), point.y() + self.rect_height
        time = kwargs.get('time', None)
        x1,y1 = self.grid_evts.get_snap(x,y,time = time)
        if self.v_lines_snap:
            x2 = x1
        else:
            x2 = x
        if self.h_lines_snap:
            y2 = y1
        else:
            y2 = y
        return QPointF(x2, y2 - self.rect_height)

class EvtGridScene(SnappedScene):
    def __init__(self, parent=None, colors = DefaultColorGrid()):
        super().__init__(parent)
        self.colors = colors
        '''self.pens = [QPen(QColor(220, 220, 220)), QPen(QColor(242, 242, 242))]
        self.text_pen = QPen(QColor(100, 100, 100))
        self.evt_pen = QPen(QColor(50, 120, 150))

        self.head_brush = QBrush(QColor(230, 230 , 230, 200))
        self.loop_brush = QBrush(QColor(250, 250 , 250, 100))
        self.solid_loop = QBrush(self.evt_pen.color())'''

        self.loop_rad = 1

        self.is_events = False

        self.h_lines_draw = True
        self.v_lines_draw = True


        self.g_lines_draw = True



        self.keys = None
        self.font_grid = QFont("Arial", 8)


        self.rect_width = 0

        self.head_draw = True
        self.head_h = 24
        self.loop_down = self.head_h / 2
        self.loop = True
        self.loop_start = 0
        self.loop_end = 0

    def set_evts(self,evtts):
        self.grid_evts = evtts
    def put_grid_evt(self, evt):
        self.grid_evts.add(evt)
    def remove_grid_evt(self, evt):
        self.grid_evts.remove(evt)
    def loop_fix(self):
        if self.loop_end < self.loop_start:
            a = self.loop_end
            self.loop_end = self.loop_start
            self.loop_start = a
    def loop_legal(self):
        return self.loop and self.loop_start != self.loop_end

    def on_head(self,event):
        view = self.views()[0]
        screen_rect = view.viewport().rect()
        screen_top_left = screen_rect.topLeft()
        scene_top_left = view.mapToScene(screen_top_left)
        if self.head_draw:
            return self.head_h > (event.scenePos().y() - scene_top_left.y())
        return False

    def is_evt(self):
        self.is_events = True
        self.h_lines_draw = False
    def set_grid_evts(self, events):
        self.grid_events = events
    def set_pens(self,pens):
        self.pens = pens
    def set_font(self,name,size):
        self.font_grid = QFont(name,size)
    def drawBackground(self, painter, rect):
        # Сохраняем текущую трансформацию
        painter.save()

        # Сбрасываем трансформацию
        original_transform = painter.transform()
        painter.resetTransform()

        if not self.views():
            painter.restore()
            return

        view = self.views()[0]

        # Преобразуем координаты
        screen_rect = view.viewport().rect()
        screen_top_left = screen_rect.topLeft()
        screen_bottom_right = screen_rect.bottomRight()

        # Преобразуем экранные координаты в сценовые для evts.get_grid
        scene_top_left = view.mapToScene(screen_top_left)
        scene_bottom_right = view.mapToScene(screen_bottom_right)

        # Получаем линии в сценовых координатах
        a = int(scene_top_left.x())
        b = int(scene_bottom_right.x())
        d = int(scene_top_left.y())
        c = int(scene_bottom_right.y())

        lines = self.grid_evts.get_grid(a, b, d, c)
        h_lines = lines[0]
        v_lines = lines[1]
        grids = lines[2]

        painter.setPen(self.pens[0])

        painter.setFont(self.font_grid)

        # Вертикальные линии
        if self.v_lines_draw:
            for line_data in v_lines:
                # Преобразуем сценовые координаты в экранные
                scene_p1 = QPointF(line_data[0][0], line_data[0][1])
                scene_p2 = QPointF(line_data[1][0], line_data[1][1])

                screen_p1 = view.mapFromScene(scene_p1)
                screen_p2 = view.mapFromScene(scene_p2)

                painter.setPen(self.pens[line_data[2][0] - 1])
                painter.drawLine(screen_p1, screen_p2)

        # Горизонтальные линии с текстом

        if self.h_lines_draw:
            painter.setPen(self.pens[0])
            for line_data in h_lines:
                scene_p1 = QPointF(line_data[0][0], line_data[0][1])
                scene_p2 = QPointF(line_data[1][0], line_data[1][1])

                screen_p1 = view.mapFromScene(scene_p1)
                screen_p2 = view.mapFromScene(scene_p2)

                painter.drawLine(screen_p1, screen_p2)

                if len(line_data) > 2:
                    painter.setPen(self.text_pen)
                    # Текст также рисуем в экранных координатах
                    painter.drawText(screen_p1.x() + 10, screen_p1.y() - 5, line_data[2][0])
                    painter.setPen(self.pens[0])


        if self.g_lines_draw:
            painter.setPen(self.evt_pen)
            for line_data in grids:
                scene_p1 = QPointF(line_data[0][0], line_data[0][1])
                scene_p2 = QPointF(line_data[1][0], line_data[1][1])

                screen_p1 = view.mapFromScene(scene_p1)
                screen_p2 = view.mapFromScene(scene_p2)

                painter.drawLine(screen_p1, screen_p2)
        if self.loop and self.loop_start != self.loop_end:
            painter.setBrush(self.loop_brush)
            painter.setPen(self.loop_brush.color())
            point1 = view.mapFromScene(QPointF(self.loop_start,scene_top_left.y()))
            point2 = view.mapFromScene(QPointF(self.loop_end,scene_bottom_right.y()))
            painter.drawRect(QRectF(point1.x(), point1.y() + self.head_h, point2.x() - point1.x(), point2.y() - point1.y()))
        # Восстанавливаем трансформацию
        painter.setTransform(original_transform)
        painter.restore()

    def drawBackground(self, painter, rect):

        view = self.views()[0]

        # Преобразуем координаты
        screen_rect = view.viewport().rect()
        screen_top_left = screen_rect.topLeft()
        screen_bottom_right = screen_rect.bottomRight()

        # Преобразуем экранные координаты в сценовые для evts.get_grid
        scene_top_left = view.mapToScene(screen_top_left)
        scene_bottom_right = view.mapToScene(screen_bottom_right)

        #a = int(scene_top_left.x())
        #b = int(scene_bottom_right.x())
        #d = int(scene_top_left.y())
        #c = int(scene_bottom_right.y())

        a = int(self.sceneRect().x())
        b = int(a + self.sceneRect().width())
        d = int(self.sceneRect().y())
        c = int(d + self.sceneRect().height())

        lines = self.grid_evts.get_grid(a, b, d, c)
        h_lines = lines[0]
        v_lines = lines[1]
        grids = lines[2]

        painter.setPen(self.colors.grid_pen)

        painter.setFont(self.font_grid)

        # Вертикальные линии
        if self.v_lines_draw:
            for line_data in v_lines:
                # Преобразуем сценовые координаты в экранные
                scene_p1 = QPointF(line_data[0][0], line_data[0][1])
                scene_p2 = QPointF(line_data[1][0], line_data[1][1])
                painter.setPen(self.colors.get_pen(line_data[2][0] - 1))
                painter.drawLine(scene_p1, scene_p2)

        # Горизонтальные линии с текстом

        if self.h_lines_draw:
            painter.setPen(self.colors.grid_pen)
            for line_data in h_lines:
                scene_p1 = QPointF(line_data[0][0], line_data[0][1])
                scene_p2 = QPointF(line_data[1][0], line_data[1][1])
                painter.drawLine(scene_p1,  scene_p2)
                if len(line_data) > 2:
                    painter.setPen(self.colors.text_pen)
                    painter.drawText(scene_p1.x() + 10, scene_p2.y() - 5, line_data[2][0])
                    painter.setPen(self.colors.grid_pen)

        if self.g_lines_draw:
            painter.setPen(self.colors.evt_pen)
            for line_data in grids:
                scene_p1 = QPointF(line_data[0][0], line_data[0][1])
                scene_p2 = QPointF(line_data[1][0], line_data[1][1])
                painter.drawLine(scene_p1, scene_p2)

        if self.loop and self.loop_start != self.loop_end:
            painter.setBrush(self.colors.loop_brush)
            painter.setPen(self.colors.loop_pen)
            point1 = QPointF(self.loop_start, scene_top_left.y())
            point2 = QPointF(self.loop_end, scene_bottom_right.y())
            painter.drawRect(
                QRectF(point1.x(), point1.y() + self.head_h, point2.x() - point1.x(), point2.y() - point1.y()))

    def drawForeground2(self, painter, rect):
        painter.save()
        original_transform = painter.transform()
        painter.resetTransform()
        if not self.views():
            painter.restore()
            return
        view = self.views()[0]
        screen_rect = view.viewport().rect()
        screen_top_left = screen_rect.topLeft()
        screen_bottom_right = screen_rect.bottomRight()
        scene_top_left = view.mapToScene(screen_top_left)
        scene_bottom_right = view.mapToScene(screen_bottom_right)
        if self.head_draw:
            # painter.setPen(QColor(0,0,0))
            painter.setBrush(self.head_brush)
            painter.setPen(self.head_brush.color())
            painter.drawRect(QRectF(screen_top_left.x(), screen_top_left.y(), screen_bottom_right.x(), self.head_h))
        if self.loop and self.loop_start != self.loop_end:
            painter.setBrush(self.loop_brush)
            painter.setPen(self.loop_brush.color())
            point1 = view.mapFromScene(QPointF(self.loop_start, scene_top_left.y()))
            point2 = view.mapFromScene(QPointF(self.loop_end, scene_bottom_right.y()))
            #   painter.setBrush(self.pens[0].color())
            painter.drawRect(QRectF(point1.x(), point1.y(), point2.x() - point1.x(), point1.y() + self.head_h))
            painter.setPen(self.solid_loop.color())
            point1 = view.mapFromScene(QPointF(self.loop_start, scene_top_left.y()))
            point2 = view.mapFromScene(QPointF(self.loop_end, scene_top_left.y()))
            # painter.setFont(QFont())
            font = painter.font()
            font.setPixelSize(20)
            painter.setFont(font)
            painter.drawText(QPointF(point1.x(), point1.y()+ self.loop_down), ":")
            painter.drawText(QPointF(point2.x(), point2.y()+ self.loop_down), ":")
        painter.setTransform(original_transform)
        painter.restore()



class ForRootScene(EvtGridScene):
    def __init__(self, parent=None):
        super().__init__(parent)

    def drawBackground(self, painter, rect):
        a = int(rect.left())
        b = int(rect.right())
        c = int(rect.bottom())
        d = int(rect.top())
        lines = evts.get_grid_colors(a, b, d, c)
        h_lines = lines[0]
        v_lines = lines[1]
        changes = lines[2]
        last_x = None
        for x in h_lines:
            if last_x is not None and last_x.coord[0][0] == x.coord[0][0]:
                painter.setBrush(last_x.brush)
                painter.setPen(QPen(QColor(0,0,0,0)))
                painter.drawRect(last_x.coord[0][0], last_x.coord[0][1], x.coord[1][0] - last_x.coord[0][0],
                                 x.coord[1][1] - last_x.coord[0][1])
            last_x = x
        for x in h_lines:
            painter.setPen(x.pen)
            painter.drawLine(x.coord[0][0], x.coord[0][1], x.coord[1][0], x.coord[1][1])
        for y in v_lines:
            painter.setPen(y.pen)
            painter.drawLine(y.coord[0][0], y.coord[0][1], y.coord[1][0], y.coord[1][1])
        for s in changes:
            painter.setPen(s.pen)
            painter.drawLine(s.coord[0][0], s.coord[0][1], s.coord[1][0], s.coord[1][1])


class EvtOverlay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.size_x = 100
        self.size_y = 30
        self.evt_var = EvtVariants()
        self.setup_ui()

    def setup_ui(self):
        # Устанавливаем стиль для полупрозрачного фона
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(240, 240, 240, 200);
                border: 1px solid #cccccc;
                border-radius: 5px;
            }
        """)

        # Устанавливаем флаги, чтобы виджет был поверх всего
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowFlags(Qt.WindowType.SubWindow | Qt.WindowType.FramelessWindowHint)

        # Создаем layout для козырька
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Добавляем элементы меню
        combo_box = QComboBox()
        combo_box.addItems(self.evt_var.dict_num.keys())
        layout.addWidget(combo_box)

        # Устанавливаем фиксированный размер
        self.setFixedSize(self.size_x, self.size_y)

class TrueEvtGridScene(EvtGridScene):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.all_evt_mass = []
        self.drawing = False
        self.current_values = []
        self.last_point = None
        self.widget = None

        self.repoint = True

        self.dict_rect = {}

        self.head_draw = False
        self.midi_data = None

    def add_widget(self,widget):
        self.widget = widget

    def mouseMoveEvent(self, event):
        if self.drawing:
            # self.del_events(self.last_point.x(), event.pos().x())
            self.add_midi_event(event.scenePos())
        if self.widget.snapping:
            point = self.snap_to_grid(event.scenePos())
            self.repoint = self.last_point.x() != point.x()
            self.last_point = point
        else:
            self.last_point = event.scenePos()
        if self.repoint:
            self.del_events(self.last_point.x(), event.scenePos().x())
        super().mouseMoveEvent(event)
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drawing = True
            self.add_midi_event(event.scenePos())
        if self.widget.snapping:
            point =self.snap_to_grid(event.scenePos())
            if self.last_point != point:
                self.last_point = point
        else:
            self.last_point = event.scenePos()
        super().mousePressEvent(event)
    def mouseReleaseEvent(self, event):
        self.drawing = False
        super().mouseReleaseEvent(event)
    def del_events(self,x1,x2):
        x11 = min(x1,x2)
        x22 = x1 + x2 - x11
        remo = []
        for i in self.widget.current_values:
            if self.drawing:
                if x11 < i[0] < x22:
                    i[2]._final_remove()
                    del self.dict_rect[i[0]]
                    remo.append(i)
            else:
                if x11 <= i[0] <= x22:
                    i[2]._final_remove()
                    del self.dict_rect[i[0]]
                    remo.append(i)
        for i in remo:
            self.widget.current_values.remove(i)
    def addItem(self, item):
        if self.midi_data is not None:
            self.midi_data.append_evt(item)
        super().addItem(item)
    def removeItem(self, item):
        if self.midi_data is not None:
            self.midi_data.remove_evt(item)
        super().removeItem(item)
    def add_midi_event(self, pos):
        """Добавляет MIDI событие в позиции мыши"""
        scene_pos = pos
        x = scene_pos.x()
        if self.widget.snapping:
            x = self.snap_to_grid(QPointF(x, 0)).x()
        else:
            x = int(x) // 10
      #  height = (1.0 - pos.y() / self.widget.maximumHeight()) * self.widget.max_value
        bar_width = 50 * 0.8
       # bar_height = (height / self.widget.maximumHeight()) * self.widget.maximumHeight()
        bar_height = min(self.widget.maximumHeight() - pos.y(),self.widget.maximumHeight())
        height = int(bar_height / self.widget.maximumHeight() * 127)
      #  print(bar_height)
        if self.dict_rect.get(x):
            self.dict_rect[x].setRect(QRectF(x, self.widget.maximumHeight() - bar_height,
                                      bar_width, bar_height))
            return


        bar = RectangleEvtItem(QRectF(x, self.widget.maximumHeight() - bar_height,
                                      bar_width, bar_height))
        bar.setBrush(QBrush(QColor(0, 150, 255, 200)))
        bar.setPen(QPen(Qt.GlobalColor.black, 1))
        self.addItem(bar)

        # Сохраняем значение
        self.widget.current_values.append((x, height, bar))
        self.dict_rect[x] = bar
class LinkedView(QGraphicsView):
    def __init__(self, main_scene, midi_scene ,parent=None):
        super().__init__(parent)
        self.main_scene = main_scene
        self.midi_scene = midi_scene
        self.setScene(self.midi_scene)
        self.x_scale = 1
        self.y_scale = 1

    def sync_with_main_scene(self):
        if self.main_scene:
            main_rect = self.main_scene.sceneRect()
            v = self.horizontalScrollBar().value()
            self.apply_scaling(self.x_scale, self.height() / self.maximumHeight())
            self.horizontalScrollBar().setValue(v)
            self.midi_scene.setSceneRect(QRectF(main_rect.left(), 0, main_rect.width(), self.maximumHeight()))
    def sync_with_main_scene_y(self):
        if self.main_scene:
            #main_rect = self.main_scene.sceneRect()
            v = self.horizontalScrollBar().value()
            self.apply_scaling(-1, self.y_scale)
            self.horizontalScrollBar().setValue(v)
            #self.midi_scene.setSceneRect(QRectF(main_rect.left(), 0, main_rect.width(), self.maximumHeight()))
    def apply_scaling(self, x, y):
        transform = QTransform()
        if x != -1:
            self.x_scale = x
        if y !=-1:
            self.y_scale = y
        transform.scale(self.x_scale, self.y_scale)
        self.setTransform(transform)

class EditorHeadScene(KeyManageMixin,SnappedScene,LoopObject,SceneTimeMixin):
    def __init__(self,timeline,editor,main_scene, colors = DefaultColorGrid(),parent = None):
        super().__init__(parent)
        self.loop_object = LoopObject.__init__(self)

        self.time_line = timeline
        self.editor = editor
        self.main_scene = main_scene
        self.colors = colors
        self.setBackgroundBrush(self.colors.head_brush)
        self.line_step = 8
        self.max_level = 3
        self.mouse_key_manage = AllEventManager()

        self.loop_draw_bol = True


        self.grid_evts = evts
        self.grid_evts.set_head_scene(self)
        self.grid_evts.all_rects()
        self.set_mouse_binds()
    def set_evts(self,evtts):
        self.grid_evts = evtts

    def set_mouse_binds(self):
        self.mouse_key_manage.add_mouse_bind("Left_all", "click", self.click_head_head)

        self.mouse_key_manage.add_mouse_bind("Left_all", "press", self.loop_draw_start)
        self.mouse_key_manage.add_mouse_bind("Left_all", "move", self.loop_move)
        self.mouse_key_manage.add_mouse_bind("Left_all", "release", self.loop_release)

    def drawBackground(self, painter, rect):
        super().drawBackground(painter, rect)
        a = int(rect.left())
        b = int(rect.right())
        c = int(rect.bottom())
        d = int(rect.top())
        lines = evts.get_grid_colors(a, b, d, c)
        v_lines = lines[1]
        changes = lines[2]
        #painter.drawLine(0, d, 0, c)
        for y in v_lines:
            painter.setPen(y.pen)
            painter.drawLine(y.coord[0][0], c, y.coord[1][0], c - (self.max_level - y.level) * self.line_step)
        for s in changes:
            painter.setPen(s.pen)
            painter.drawLine(s.coord[0][0], c, s.coord[1][0], c - self.max_level * self.line_step)
        if self.loop_draw_bol:
            painter.setBrush(self.colors.loop_brush)
            painter.setPen(QPen(QColor(0, 0, 0,0)))
            painter.drawRect(self.loop_start,c,self.loop_end-self.loop_start,d-c)
        ## print(self.items())
        #print(v_lines)


class HeadSceneView(LinkedView):
    def __init__(self, main_scene, scene, height=None,parent=None):
        super().__init__(main_scene, scene ,parent=None)
        rect = main_scene.sceneRect()
        rect2 = scene.sceneRect()
        if height is None:
            scene.setSceneRect(rect.x(), rect2.y(), rect.width(), rect2.height())
            self.setFixedHeight(rect2.height())
        else:
            scene.setSceneRect(rect.x(), rect2.y(), rect.width(), height)
            self.setFixedHeight(height)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)


class HeadWidget(QWidget):
    def __init__(self,editor,main_scene, timeline, height = None,colors = DefaultColorGrid(),parent = None):
        super().__init__(parent)
        self.timeline = timeline
        self.scene = EditorHeadScene(timeline,editor,main_scene, colors, parent)
        self.view = HeadSceneView(main_scene, self.scene, height)
        self.layout = QGridLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.setContentsMargins(0, 0, 0, 0)
        self.setFixedHeight(self.timeline.height + self.view.height())
        self.setLayout(self.layout)
        self.layout.addWidget(self.timeline,0,0)
        self.layout.addWidget(self.view, 1, 0)
        #self.layout.addWidget(self.view)

class AngleFillerWidget(QWidget):
    def __init__(self, width =None):
        super().__init__()
        if width is not None:
            self.setFixedWidth(width)

class EventFillerWidget(QWidget):
    def __init__(self, event_scene,width =None):
        super().__init__()
        self.event_scene = event_scene
        if width is not None:
            self.setFixedWidth(width)

class MidiEventWidget(LinkedView):
    def __init__(self, main_scene, parent=None):
        midi_scene = TrueEvtGridScene()
        super().__init__(main_scene, midi_scene)
        self.midi_scene = midi_scene
        self.evt_widget = None

        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.midi_scene.add_widget(self)

        self.overlay = None
        self.overlay_offset = 0
        self.setup_overlay()

        self.midi_scene.is_evt()
        self.sync_with_main_scene()
        # Настройки
        self.grid_size = main_scene.v_grid_size if hasattr(main_scene, 'v_grid_size') else 50
        self.max_value = 127  # Максимальное значение MIDI
        self.drawing = False
        self.current_values = []  # Текущие значения событий
        self.grid = None
        # Синхронизация с основной сценой


        self.last_point = None

        self.snapping  = True
        self.midi_data = None

    def set_evt_widget(self, evt):
        self.evt_widget = evt

    def set_midi_data(self, midi_data):
        self.midi_data = midi_data
        self.midi_scene.midi_data = midi_data

    def add_grid(self, grid):
        self.grid = grid



    def mousePressEvent(self, event):
       # self.last_point = event.scenePos()

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):

        # self.last_point = event.pos()
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.drawing = False

        super().mouseReleaseEvent(event)
    def setup_overlay(self):
        # Создаем козырек
        self.overlay = EvtOverlay(self)

        # Позиционируем козырек в правом верхнем углу
        self.position_overlay()

        # Показываем козырек
        self.overlay.show()

    def position_overlay(self):
        # Получаем размеры view
        if self.overlay:
            view_width = self.width()
            overlay_x = view_width - self.overlay.width() - self.overlay_offset
            self.overlay.move(overlay_x, self.overlay_offset)


    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.sync_with_main_scene()
        self.position_overlay()



class MidiEditorDock(QDockWidget):
    """Док-виджет для редактирования MIDI"""

    def __init__(self, main_scene, parent=None):
        super().__init__("MIDI Editor", parent)
        self.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetMovable |
                         QDockWidget.DockWidgetFeature.DockWidgetFloatable)

        # Основной виджет
        main_widget = QWidget()
        layout = QVBoxLayout(main_widget)

        # Панель инструментов сверху
        toolbar = QHBoxLayout()

        # Выпадающий список (пока пустой)
        self.track_selector = QComboBox()
        self.track_selector.addItems(["Track 1", "Track 2", "Track 3"])

        # Кнопка добавления нового трека
        self.add_track_btn = QPushButton("+")
        self.add_track_btn.clicked.connect(self.add_new_track)

        toolbar.addWidget(QLabel("Track:"))
        toolbar.addWidget(self.track_selector)
        toolbar.addWidget(self.add_track_btn)
        toolbar.addStretch()

        # Виджет MIDI событий
        self.midi_widget = MidiEventWidget(main_scene)

        layout.addLayout(toolbar)
        layout.addWidget(self.midi_widget)

        self.setWidget(main_widget)