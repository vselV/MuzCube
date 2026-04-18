
from PyQt6.QtCore import   QTimer,  QLineF
from PyQt6.QtGui import      QCursor
from PyQt6.QtWidgets import (QLineEdit, QGraphicsLineItem, QGraphicsSceneWheelEvent, QSplitter)

import sys
from PyQt6.QtCore import    pyqtSignal
from PyQt6.QtWidgets import (QApplication,   QCheckBox,  QSlider )

#from midi_player import MidiPlayer, MidiPlaySync
#from dataClass import ProgramChange, Note, NoteOff, Event, Tempo

from src.MuzCube.Wigets.rGrigPiano3 import VerticalKeyScene, PianoView
from src.MuzCube.Wigets.rGrigEvents import *
from src.MuzCube.UtilClasses.rGrigGrids import *
from src.MuzCube.Wigets.rGrigSyncContainer import AdvancedSeamlessContainer
from src.MuzCube.Lex.tomObj import toMidi
from src.MuzCube.UtilClasses.rGrigDataEvt import *
from src.MuzCube.Wigets.rGrigToolBar import TopTollBar, PlayToolBar
from src.MuzCube.UtilClasses.QtKeyTest import   AllEventManager
from src.MuzCube.Wigets.rGrigSyncGrid import SynchronizedSplitterGrid
from src.MuzCube.UtilClasses.rGrigMixins import SceneTimeMixin, KeyManageMixin
from src.MuzCube.UtilClasses.rGrigNotesChords import RectangleItem

class FixedSizeLineItem(QGraphicsLineItem):
    def __init__(self, line, parent=None):
        super().__init__(line, parent)
     #   self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIgnoresTransformations)

        # Устанавливаем фиксированную толщину и цвет
        pen = QPen(Qt.GlobalColor.red, 2)  # Фиксированная толщина в пикселях
        self.setPen(pen)

    def paint(self, painter, option, widget=None):
        painter.save()

        # Сбрасываем трансформацию
        transform = painter.transform()
        painter.resetTransform()

        # Получаем view
        view = self.scene().views()[0] if self.scene() and self.scene().views() else None
        if view:
            # Преобразуем координаты в экранные (QPoint -> QPointF)
            line = self.line()
            p1 = view.mapFromScene(line.p1())
            p2 = view.mapFromScene(line.p2())

            # Создаем QPointF из QPoint
            p1_f = QPointF(p1)
            p2_f = QPointF(p2)

            # Создаем прямоугольник в экранных координатах
            screen_rect = QLineF(p1_f, p2_f)

            # Рисуем
            painter.setPen(self.pen())
            painter.setBrush(QBrush(QColor(20,20,20,20)))
            painter.drawLine(screen_rect)
        else:
            # Fallback
            super().paint(painter, option, widget)

        painter.setTransform(transform)
        painter.restore()


class InstantClickSlider(QSlider):
    def __init__(self, orientation=Qt.Orientation.Horizontal, parent=None):
        super().__init__(orientation, parent)
        self.setMouseTracking(True)

    def mousePressEvent(self, event):
        # Мгновенное перемещение к точке клика
        if event.button() == Qt.MouseButton.LeftButton:
            self.jump_to_position(event.position())
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        # Перемещение при движении с зажатой кнопкой
        if event.buttons() & Qt.MouseButton.LeftButton:
            self.jump_to_position(event.position())
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def jump_to_position(self, pos):
        """Мгновенно перемещает слайдер к указанной позиции"""
        if self.orientation() == Qt.Orientation.Horizontal:
            # Для горизонтального слайдера
            pos_x = pos.x()
            width = self.width()
            value_range = self.maximum() - self.minimum()

            # Вычисляем новое значение
            new_value = self.minimum() + (pos_x / width) * value_range
            new_value = max(self.minimum(), min(self.maximum(), int(new_value)))

            self.setValue(new_value)
        else:
            # Для вертикального слайдера
            pos_y = pos.y()
            height = self.height()
            value_range = self.maximum() - self.minimum()

            # Инвертируем для вертикального направления
            new_value = self.minimum() + (1 - pos_y / height) * value_range
            new_value = max(self.minimum(), min(self.maximum(), int(new_value)))

            self.setValue(new_value)

class TimelineSlider(QGraphicsView):
    def __init__(self, scene, view, parent=None):
        super().__init__(parent)
        self.pose_in_scene = 0
        self.start_in_scene = 0

        self.max_scroll = 0
        self.scene = scene
        self.view = view
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setContentsMargins(0, 0, 0, 0)
        self.setStyleSheet("border: 0px")

        self.setMouseTracking(True)
        self.dragging = False

        # Создаем ползунок
        self.slider = InstantClickSlider(Qt.Orientation.Horizontal)
        self.height = 15
        self.setFixedHeight(self.height)
        self.slider.setFixedHeight(10)
        self.slider.setStyleSheet("""
    /* Горизонтальный slider */
    QSlider::handle:horizontal {
        background: #d66969;
        width: 20px;
        margin: -8px -10;  /* Это ключевое свойство для центрирования */
    }
    
    /* Вертикальный slider */
    QSlider::handle:vertical {
        background: #9383a8;
        height: 20px;
        margin: 0 -8px;  /* Для вертикального */
        border-radius: 6px;
        border: 1px solid #2980b9;
    }
    
    /* Дополнительные стили для красоты */
    QSlider::groove:horizontal {
        background: #ddd;
        height: 6px;
        border-radius: 3px;
    }
    
    QSlider::sub-page:horizontal {
        background: #8fbaa8;
        border-radius: 10px;
    }
""")
        self.slider.setRange(0, 1000)
        self.slider.valueChanged.connect(self.update_indicator)



        # Линия-указатель
        self.indicator_line = FixedSizeLineItem(QLineF(0,0,0,0))
      #  pen = QPen(Qt.GlobalColor.red)
     #   pen.setWidth(2)  # Всегда 2 пикселя толщиной
        #self.indicator_line.setPen(pen)
       # self.indicator_line.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIgnoresTransformations)
        self.indicator_line.setPen(QPen(Qt.GlobalColor.red, 2))
        self.scene.addItem(self.indicator_line)

        # Добавляем ползунок в layout
        layout = QVBoxLayout(self)
        layout.addWidget(self.slider)
        layout.setContentsMargins(0, 0, 0, 0)

        # Инициализируем линию
        self.update_indicator()

        self.view.viewport_changed.connect(self.viewport_changed)

    def viewport_changed(self):
        """Обновляет слайдер при изменении видимой области"""
        cf = self.view.transform().m11()
        scroll = self.view.verticalScrollBar().width() / cf
        visible_rect = self.view.mapToScene(self.view.viewport().rect()).boundingRect()

        slide = self.slider.maximum() * (self.pose_in_scene-visible_rect.left()) / (scroll+visible_rect.width())

        self.slider.blockSignals(True)
        #print(slide)
        if slide<0:
            self.slider.setValue(0)
        elif  self.slider.maximum() < slide:
            self.slider.setValue(self.slider.maximum())
        else:
            self.slider.setValue(slide)
        self.slider.blockSignals(False)
    def get_x_pose(self):
        cf = self.view.transform().m11()
        scroll = self.view.verticalScrollBar().width() / cf
        visible_rect = self.view.mapToScene(self.view.viewport().rect()).boundingRect()
        self.max_scroll = visible_rect.width() + scroll
        x_pos = visible_rect.left() + (self.max_scroll *
                                       (self.slider.value() / self.slider.maximum()))
        return x_pos
    def set_x(self,x_pos):
        cf = self.view.transform().m11()
        scroll = self.view.verticalScrollBar().width() / cf
        visible_rect = self.view.mapToScene(self.view.viewport().rect()).boundingRect()
        self.max_scroll = visible_rect.width() + scroll
        value = (x_pos - visible_rect.left()) / self.max_scroll * self.slider.maximum()
        self.slider.setValue(value)
        self.update_indicator()
    def update_indicator(self):
        visible_rect = self.view.mapToScene(self.view.viewport().rect()).boundingRect()
        x_pos = self.get_x_pose()

        self.pose_in_scene = x_pos
        self.start_in_scene = visible_rect.left()
        # Обновляем линию через всю высоту сцены (не только видимую)
        scene_rect = self.scene.sceneRect()
        self.indicator_line.setLine(x_pos, scene_rect.top(),
                                    x_pos, scene_rect.bottom())

    def map_to_scene(self, slider_value):
        visible_rect = self.view.mapToScene(self.view.viewport().rect()).boundingRect()
      #  print(self.view.verticalScrollBar())
        # Преобразуем значение ползунка в координаты сцены
        min_x = visible_rect.left()
        max_x = visible_rect.right()
      #  print(min_x,max_x,min_x + (max_x - min_x) * (slider_value / self.slider.maximum()))
        return min_x + (max_x - min_x) * (slider_value / self.slider.maximum())

    def mousePressEvent(self, event):
     #   print(self.view.verticalScrollBar())
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.update_slider_from_mouse(event.pos())

    def mouseMoveEvent(self, event):
        if self.dragging:
            self.update_slider_from_mouse(event.pos())

    def mouseReleaseEvent(self, event):
        self.dragging = False

    def update_slider_from_mouse(self, pos):
        # Преобразуем позицию мыши в значение ползунка
        x = pos.x()
        width = self.width()
        value = int((x / width) * self.slider.maximum())
        self.slider.setValue(value)

class GridLineItem(QGraphicsLineItem):
    def __init__(self, line, is_horizontal, parent=None):
        super().__init__(line, parent)
        self.is_horizontal = is_horizontal
        self.setAcceptHoverEvents(True)
        self.setZValue(-1)  # Линии под другими элементами

        # Настройка внешнего вида
        self.normal_pen = QPen(Qt.GlobalColor.gray, 1, Qt.PenStyle.DotLine)
        self.hover_pen = QPen(Qt.GlobalColor.blue, 2)
        self.setPen(self.normal_pen)

    def hoverEnterEvent(self, event):
        self.setPen(self.hover_pen)
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        self.setPen(self.normal_pen)
        super().hoverLeaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            print(f"Клик по {'горизонтальной' if self.is_horizontal else 'вертикальной'} линии")
            # Здесь можно добавить свою логику обработки клика
        super().mousePressEvent(event)

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        self.slider.setValue(self.slider.value() + delta)

class ScaleSlider(QSlider):
    sliderWheelMoved = pyqtSignal(int)

    def __init__(self, orientation, parent=None):
        super().__init__(orientation, parent)
        self.setRange(10, 400)
        self.setValue(100)
        self.setSingleStep(5)
        self.setPageStep(20)
        self.setTickInterval(50)
        self.setTickPosition(QSlider.TickPosition.TicksBelow)

    def wheelEvent(self, event):
        if isinstance(event,QGraphicsSceneWheelEvent):
            self.sliderWheelMoved.emit(event.delta())
        else:
            self.sliderWheelMoved.emit(event.angleDelta().y())
        event.accept()




def copy_rect_item(item : RectangleItem):
    new_item = RectangleItem(item.rect())
    new_item.setPos(item.pos())
    if item.text_item is not None:
        new_item.set_text(item.get_text())
    return new_item

class InfiniteScene(ForRootScene,SceneTimeMixin):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSceneRect(-10000, -10000, 20000, 20000)

        self.root_view = None
        self.midi_data = None
        self.time_line = None

        self.rect_massive = []

        self.midi_player = None
        self.active_notes = []

        self.h_grid_enabled = True
        self.v_grid_enabled = True
        self.h_grid_size = 50  # Шаг вертикальной сетки (высота)
        self.v_grid_size = 50  # Шаг горизонтальной сетки (ширина)
        self.off_set = True
        self.h_start_set = 0
        self.v_start_set = 0

        self.drawing = False
        self.right_button_pressed = False

        self.start_point = QPointF()
        self.current_rect = None
        self.rect_height = 50

       # self.setBackgroundBrush(QBrush(QColor(240, 240, 240)))

        self.interpr = None
        self.move = False

        self.left_btn = False

        self.draw_loop = False
        self.dr_loop = True

        self.loop_rez = 0
        self.first_cl = False

        self.editor = None

        self.mouse_key_manage = AllEventManager()
        self.set_key_binds()
        self.set_mouse_binds()

        self.item_at = None
        self.rect_offsets = None
        self.rect_sizes = None

        self.scroll_transform_x = None
        self.scroll_transform_y = None

        self.rubberBandRect = QRectF()
        self.selecting = False
        self.startPoint = QPointF()

        self.first_move = False

    def drawBackground(self, painter, rect):
        super().drawBackground(painter, rect)
        a = int(rect.left())
        b = int(rect.right())
        c = int(rect.bottom())
        d = int(rect.top())
        if self.editor.head_scene.loop_legal() and self.editor.head_scene.loop_draw_bol:
            painter.setBrush(self.colors.loop_brush)
            painter.setPen(QPen(QColor(0, 0, 0, 0)))
            painter.drawRect(self.editor.head_scene.loop_start, c, self.editor.head_scene.loop_end - self.editor.head_scene.loop_start, d - c)
        if self.editor is not None:
            self.editor.key_scene.set_key_data(self.grid_evts.get_by_time(rect.x()).get_keys())
    def set_root_view(self,v):
        self.views
    def set_scroll_x(self,scroll_x):
        self.scroll_transform_x = scroll_x
    def set_scroll_y(self,scroll_y):
        self.scroll_transform_y =  scroll_y




    def set_editor(self,editor):
        self.editor = editor


    def set_time_line(self,timeline):
        self.time_line = timeline
    def set_midi_data(self,midi_data):
        self.midi_data = midi_data
    def add_interpr(self,interPr):
        self.interpr = interPr

    def add_midi_player(self,midi_player):
        self.midi_player = midi_player

    def set_key_binds(self):
        self.mouse_key_manage.add_key_bind("Q", self.add_text,False)
        self.mouse_key_manage.add_key_bind("Delete", self.delete_selected,False)
        self.mouse_key_manage.add_key_bind("G",self.add_grid_change)
        ####
        #self.mouse_key_manage.add_key_bind("S", self.editor.save_as)

    ##################################
 #   def line_equal(self):
    def delete_selected(self):
        for s in self.selectedItems():
            if isinstance(s,RectangleItem):
                s.fade_out_and_remove()
    def add_text(self):
        selected = self.selectedItems()
        ## print(selected)
        for s in selected:
            ## print(s,s.isSelected())
            if isinstance(s, RectangleItem):
                ## print(s.isSelected())
                s.add_text_item()
                #return
    def add_grid_change(self):
        time = self.time_line.get_x_pose()
        time = self.snap_to_grid(QPointF(time, 0))
        self.grid_evts.dialog_add(time.x())
    ##############################
    def keyPressEvent(self, event):
        self.mouse_key_manage.KeyPress(event)
        if self.mouse_key_manage.sup():
            super().keyPressEvent(event)
    def keyReleaseEvent(self, event):
        self.mouse_key_manage.KeyRelease(event)
        super().keyReleaseEvent(event)



    def _create_clickable_grid(self, rect):
        # Удаляем старые линии
        for line in self.grid_lines:
            self.removeItem(line)
        self.grid_lines.clear()

        # Вертикальные линии
        if self.v_grid_enabled:
            left = int(rect.left()) - (int(rect.left()) % self.v_grid_size)
            right = int(rect.right())
            for x in range(left, right, self.v_grid_size):
                line = GridLineItem(QLineF(x, rect.top(), x, rect.bottom()), False)
                self.addItem(line)
                self.grid_lines.append(line)

        # Горизонтальные линии
        if self.h_grid_enabled:
            top = int(rect.top()) - (int(rect.top()) % self.h_grid_size)
            bottom = int(rect.bottom())
            for y in range(top, bottom, self.h_grid_size):
                line = GridLineItem(QLineF(rect.left(), y, rect.right(), y), True)
                self.addItem(line)
                self.grid_lines.append(line)



    def play_rect(self,rect):
        if self.midi_data:
            if type(rect) == RectangleItem:
                nt = calc_note_rect(sum_rect(rect))
            else:
                nt = calc_note_rect(rect)
            self.midi_data.current_track.player.play_note(nt)
    def off_rect(self,rect):
        if self.midi_data:
            if type(rect) == RectangleItem:
                nt = calc_note_off_rect(sum_rect(rect))
            else:
                nt = calc_note_off_rect(rect)
            self.midi_data.current_track.player.play_note_off(nt)

    def addItem(self, rect):
        super().addItem(rect)
        if self.midi_data is not None:
            if isinstance(rect,RectangleItem):
                self.midi_data.append_rect(rect)
    def removeItem(self,rect):
        super().removeItem(rect)
        if self.midi_data is not None:
            if isinstance(rect,RectangleItem):
                self.midi_data.remove_rect(rect)
    def set_mouse_binds(self):
        self.mouse_key_manage.add_mouse_bind("Left_draw","press",self.start_drawing)
        self.mouse_key_manage.add_mouse_bind("Left_draw", "move", self.move_draw_rect)
        self.mouse_key_manage.add_mouse_bind("Left_draw", "release", self.release_draw)

        self.mouse_key_manage.add_mouse_bind("Left_draw", "click", self.click_head)

        self.mouse_key_manage.add_mouse_bind("Right_delete", "press", self.start_delete, False)
        self.mouse_key_manage.add_mouse_bind("Right_delete", "move", self.start_delete)

        self.mouse_key_manage.add_mouse_bind("Right_select", "press", self.start_select, False)
        self.mouse_key_manage.add_mouse_bind("Right_select", "move", self.move_select,False)
        self.mouse_key_manage.add_mouse_bind("Right_select", "release", self.release_select,False)


    ####################################
    def lock_text(self):
        for item in self.items():
            if isinstance(item,RectangleItem):
                item.text_no_interact()
    def start_drawing(self,event):
        if not self.rectAt(event.scenePos(), QTransform()):
            self.drawing = True
            self.start_point = self.snap_to_grid(event.scenePos(),time=event.scenePos().x()) if (
                    self.v_grid_enabled or self.h_grid_enabled) else event.scenePos()
            self.current_rect = RectangleItem(QRectF(
                0,
                0,
                0,
                self.rect_height
            ))
            self.current_rect.setPos(self.start_point)
            #self.one_item_select(self.current_rect)
            self.current_rect.setSelected(True)
            self.rect_massive.append(self.current_rect)
            self.play_rect(self.current_rect)
    def move_draw_rect(self,event):
        if self.current_rect is not None:
            if self.first_cl:
                self.addItem(self.current_rect)
            end_point = self.snap_to_grid(event.scenePos(), time=self.start_point.x()) if (
                    self.v_grid_enabled or self.h_grid_enabled) else event.scenePos()
            bol = end_point.y() != self.current_rect.pos().y()
            if bol:
                self.off_rect(self.current_rect)
            if end_point.x() < self.start_point.x():
                self.current_rect.setRect(
                    0,
                    0,
                    self.start_point.x() - end_point.x(),
                    self.rect_height
                )
                self.current_rect.setPos(end_point)
            else:
                self.current_rect.setRect(
                    0,
                    0,
                    end_point.x() - self.start_point.x(),
                    self.rect_height
                )
                self.current_rect.setPos(QPointF(self.start_point.x(), end_point.y()))
            if bol:
                self.play_rect(self.current_rect)
            if self.views():
                self.views()[0].viewport().update()
    def release_draw(self,event):
        if self.current_rect is not None:
            self.drawing = False
            if abs(self.current_rect.rect().width()) < 5 and self.current_rect in self.items():
                self.removeItem(self.current_rect)
            self.off_rect(self.current_rect)
            self.current_rect = None

    def start_delete(self,event):
        self.delete_under_cursor(event.scenePos())
    def start_select(self,event):
        self.startPoint = event.scenePos()
        self.selecting = True
        self.rubberBandRect = QRectF(self.startPoint, self.startPoint)
        event.accept()
    def move_select(self, event):
        endPoint = event.scenePos()
        self.rubberBandRect = QRectF(self.startPoint, endPoint)
        self.update()
        event.accept()
    def release_select(self,event):
        self.selectItemsInRubberBand()
        self.selecting = False
        self.rubberBandRect = QRectF()
        self.update()
        event.accept()
    def one_item_select(self,item_base):
        for item in self.items():
            item.setSelected(False)
        item_base.setSelected(True)
        self.update()
    def selectItemsInRubberBand(self):
        for item in self.items():
            if isinstance(item, RectangleItem):
                #print(item.rect(),self.rubberBandRect)
                if self.rubberBandRect.intersects(sum_rect_out(item)):
                    item.setSelected(True)
                else:
                    item.setSelected(False)
    def move_fix_press(self,event):
        self.item_at = self.rectAt(event.scenePos(), QTransform())
        self.rect_offsets = {}
        selected = self.selectedItems()
        for item in selected:
            if isinstance(item, RectangleItem):
                self.rect_offsets[item] = item.pos() - self.item_at.pos()
        self.rect_offsets[self.item_at] = QPointF(0,0)
    def move_fix(self,event):
        selected = self.selectedItems()
        for item in selected:
            if isinstance(item, RectangleItem):
                item.setPos(self.rect_offsets[item]+self.item_at.pos())
    def move_fix_release(self,event):
        self.rect_offsets = None
        self.item_at = None
    def move_fix_copy(self):
        for item in self.rect_offsets.keys():
            if isinstance(item,RectangleItem):
                new_item = copy_rect_item(item)
                new_item.setSelected(False)
                self.addItem(new_item)
    def resize_back(self,rect : RectangleItem):
        self.rect_sizes = {}
        for item in self.selectedItems():
            if isinstance(item,RectangleItem):
                self.rect_sizes[item] = item.rect()

    def resize_all(self,event,rect : RectangleItem):
        pos = event.pos()
        for item in self.selectedItems():
            if isinstance(item,RectangleItem) and item != rect:
                item.resize_press()
                ## print(self.rect_sizes)
                if rect.is_resizing_right:
                    new_pos = QPointF(pos.x() - self.rect_sizes[rect].width() +self.rect_sizes[item].width(),pos.y())
                else:
                    new_pos = pos
               # new_pos =  QPointF(pos.x() - rect.rect().width() + item.rect().width(),pos.y())
                item.resize(new_pos,rect.is_resizing_left,rect.is_resizing_right)
                item.resize_out()
    def resize_close(self):
        self.rect_sizes = None
    ################################
    def rectAt(self, pos, transform=QTransform()):
        items = self.items(pos, Qt.ItemSelectionMode.IntersectsItemShape,
                           Qt.SortOrder.DescendingOrder, transform)
        for item in items:
            if isinstance(item, QGraphicsRectItem):
                return item
        return None

    def mousePressEvent(self, event):
        self.lock_text()
        self.first_cl = True
        self.left_btn = True
        sup = True
        if self.on_head(event):
            if event.button() != Qt.MouseButton.RightButton:
                self.draw_loop = True
                point = self.snap_to_grid(event.scenePos()) if (
                        self.v_grid_enabled or self.h_grid_enabled) else event.scenePos()
                self.loop_rez = point.x()
            else:
                sup = self.mouse_key_manage.auto_def('press', event)
        else:
            sup = self.mouse_key_manage.auto_def('press', event)
        if sup:
            ## print(sup)
            if event.button() == Qt.MouseButton.LeftButton and self.rectAt(event.scenePos(), QTransform()):
                self.first_move = True
                self.move_fix_press(event)
            super().mousePressEvent(event)
        #if self.current_rect:
            #self.current_rect.setSelected(True)
    ##########
    def wheelEvent(self, event):
        if self.scroll_transform_x is not None:
            ## print(self.mouse_key_manage.ctrl())
            if not self.mouse_key_manage.ctrl():
                self.scroll_transform_x.wheelEvent(event)
            elif self.scroll_transform_y is not None:
                self.scroll_transform_y.wheelEvent(event)


    def mouseMoveEvent(self, event):
        if self.left_btn:
            self.move = True
        if self.draw_loop:
            self.mouse_key_manage.ghost_move()
            self.loop_start = self.loop_rez
            point = self.snap_to_grid(event.scenePos()) if (
                    self.v_grid_enabled or self.h_grid_enabled) else event.scenePos()
            self.loop_end = point.x()
            self.update()
        else:
            sup = self.mouse_key_manage.auto_def("move",event)
            if sup:
                if self.first_move and self.mouse_key_manage.ctrl():
                    self.move_fix_copy()
                    self.first_move = False
                super().mouseMoveEvent(event)
                if self.rect_offsets:
                    self.move_fix(event)
        self.first_cl = False

    def mouseReleaseEvent(self, event):
        self.first_move = False
        if self.draw_loop:
            self.update()
            self.draw_loop = False
        self.move = False
        self.left_btn = False
        self.first_cl = False
        self.mouse_key_manage.auto_def("release", event)
        if self.rect_offsets:
            self.move_fix_release(event)
        super().mouseReleaseEvent(event)


    def delete_under_cursor(self, pos):
        """Удаляет все прямоугольники под курсором"""
        items = self.items(pos)
        for item in items:
            if isinstance(item, RectangleItem):
                item.fade_out_and_remove()
                # self.removeItem(item)
        if items:
            self.update()
    """def set_time(self,x):
        if self.time_line is not None:
            self.time_line.set_x(x)"""
    def drawForeground(self, painter, rect):
        super().drawForeground(painter, rect)
        if self.selecting and not self.rubberBandRect.isNull():
            pen = QPen(Qt.GlobalColor.red, 1, Qt.PenStyle.DashLine)
            pen.setCosmetic(True)
            painter.setPen(pen)
            painter.setBrush(QBrush(QColor(255, 0, 0, 50)))
            painter.drawRect(self.rubberBandRect)
#class WithHeadInfiniteScene()
class WithHeadInfiniteScene(InfiniteScene):
    def __init__(self,parent = None):
        super().__init__(parent = parent)
        #передавать раодителя чтобы оставить подписи 1 вид будет иметь

# ... (остальные классы InfiniteView и RectangleEditor остаются без изменений)
class InfiniteView(QGraphicsView):
    viewport_changed = pyqtSignal()
    def __init__(self, scene, parent=None):
        super().__init__(scene, parent)
        self.scroll_transform = None
        self.colors = scene.colors
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        self.setDragMode(QGraphicsView.DragMode.NoDrag)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setInteractive(True)
        self.scale(1.5, 1.5)

        self.x_scale = 1.0
        self.y_scale = 1.0
        self.head_h = 24
        self.head_draw = True
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)
    def set_scroll(self,bar):
        self.scroll_transform = bar
    def apply_scaling(self):
        transform = QTransform()
        transform.scale(self.x_scale, self.y_scale)
        self.setTransform(transform)

    def scrollContentsBy(self, dx, dy):
        super().scrollContentsBy(dx, dy)
        self.viewport_changed.emit()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.viewport_changed.emit()

    def set_visible_scene_start(self, x, y):
        """Устанавливает начало видимой области сцены"""
        # Способ 1: через setSceneRect
        visible_rect = self.viewport().rect()
        self.setSceneRect(QRectF(x, y, visible_rect.width(), visible_rect.height()))
        if self.verticalScrollBar().isVisible():
            self.verticalScrollBar().setValue(int(y))
        if self.horizontalScrollBar().isVisible():
            self.horizontalScrollBar().setValue(int(x))

    def move_centre(self, x):
        screen_rect = self.viewport().rect()
        screen_top_left = screen_rect.topLeft()
        screen_bottom_right = screen_rect.bottomRight()
        scene_top_left = self.mapToScene(screen_top_left)
        scene_bottom_right = self.mapToScene(screen_bottom_right)

        visible_rect = self.mapToScene(self.viewport().rect()).boundingRect()

        center = (scene_top_left.x() + scene_bottom_right.x())/2
        new_center = (x + center) / 2
        self.centerOn(QPointF(new_center, visible_rect.y() + visible_rect.height() / 2))

    def move_centre_2(self):
        x = self.mapToScene(QCursor.pos()).x()
        visible_rect = self.viewport().rect()
        center = visible_rect.center().x()
        new_center = (x + center) / 2
        ## print(center,new_center)
        self.setSceneRect(QRectF(new_center - visible_rect.width() / 2, visible_rect.y(), visible_rect.width(),
                                 visible_rect.height()))
        if self.horizontalScrollBar().isVisible():
            self.horizontalScrollBar().setValue(int(new_center))
        #self.set
    def drawForegroundd(self, painter, rect):
        screen_rect = self.viewport().rect()
        screen_top_left = screen_rect.topLeft()
        screen_bottom_right = screen_rect.bottomRight()
        scene_top_left = self.mapToScene(screen_top_left)
        scene_bottom_right = self.mapToScene(screen_bottom_right)

        if self.head_draw:
            painter.setBrush(self.colors.head_brush)
            painter.setPen(self.colors.head_pen)
            painter.drawRect(QRectF(rect.x(), rect.y(), screen_bottom_right.x(), self.head_h))
        super().drawForeground(painter, rect)

        '''       if self.loop and self.loop_start != self.loop_end:
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
            painter.drawText(QPointF(point1.x(), point1.y() + self.loop_down), ":")
            painter.drawText(QPointF(point2.x(), point2.y() + self.loop_down), ":")'''
    """def wheelEvent(self, event):
        if self.scroll_transform_x is not None:
            if not self.mouse_key_manage.ctrl():
                self.scroll_transform_x.wheelEvent(event)
            elif self.scroll_transform_y is not None:
                self.scroll_transform_y.wheelEvent(event)"""

class SceneCopile(QWidget):
    def __init__(self,scene_spliter,piano_spliter):
        self.container = AdvancedSeamlessContainer()
class SborScenes(QWidget):
    def __init__(self, scene=None,parent=None):
        super().__init__(parent)
        self.setContentsMargins(0,0,0,0)
        self.layout = QHBoxLayout()
        self.main_grid_layout = QGridLayout()
        if scene is not None:
            self.scene = scene
        else:
            self.scene = InfiniteScene()
        self.view = InfiniteView(self.scene)
        self.view.setFrameShape(QFrame.Shape.NoFrame)

        self.timeline = TimelineSlider(self.scene, self.view)
        self.scene.set_time_line(self.timeline)

        self.key_scene = VerticalKeyScene()
        self.key_view = PianoView(self.scene, self.key_scene)
        self.head_height = 55

        self.head_widget = HeadWidget(self, self.scene, self.timeline, self.head_height)
        self.head_scene = self.head_widget.scene
        ## print(self.head_scene.sceneRect())
        self.head_view = self.head_widget.view

        self.angle_widget = AngleFillerWidget(self.key_view.width())

        self.left_container = QWidget()
        self.piano_grid_layout = QGridLayout(self.left_container)
        self.left_container.setContentsMargins(0, 0, 0, 0)
        self.left_container.setFixedWidth(self.key_view.width())
        self.piano_grid_layout.setContentsMargins(0, 0, 0, 0)
        self.piano_grid_layout.setSpacing(0)


        self.splitter = QSplitter(Qt.Orientation.Vertical)
        self.splitter.setHandleWidth(5)
        self.splitter.addWidget(self.view)

        self.container = AdvancedSeamlessContainer()


        self.container.add_to_grid(self.angle_widget, 0, 0)
        self.container.add_to_grid(self.head_widget, 0, 1)

        self.piano_grid_layout.addWidget(self.key_view, 0, 0)

        self.container.add_to_grid(self.left_container, 1, 0)
        self.container.add_to_grid(self.splitter, 1, 1)
        self.sync_grider = SynchronizedSplitterGrid(self.splitter, self.piano_grid_layout)

        self.layout.addWidget(self.container)
        self.setLayout(self.layout)


class WithLayWidget(QWidget):
    def __init__(self,layout):
        super().__init__()
        self.setLayout(layout)
class RectangleEditor(QWidget, KeyManageMixin):
    def __init__(self, scene=None,parent=None):
        super().__init__(parent)
        KeyManageMixin.__init__(self)

        self.mouse_key_manage = AllEventManager()
        self.name="name"
        self.set_key_binds()


        self.container = AdvancedSeamlessContainer()

        self.midi_player = None
        self.midi_data = None

        self.midi_editors = []

        self.setWindowTitle("MidiMuzCube")
        self.resize(800, 800)

        if scene == None:
            self.scene = InfiniteScene()
        else:
            self.scene = scene


        self.sbor = SborScenes(self.scene)

        self.scene.set_editor(self)

        self.view = self.sbor.view

        self.timeline = self.sbor.timeline

        self.key_scene = self.sbor.key_scene
        self.key_view = self.sbor.key_view

        self.head_widget = self.sbor.head_widget
        self.head_scene = self.sbor.head_scene
        self.head_view = self.sbor.head_view

        self.angle_widget = self.sbor.angle_widget
        self.sync_splitter = self.sbor.sync_grider

        self.init_ui()
    def set_key_binds(self):
        self.mouse_key_manage.add_key_bind("S", self.save)
    def init_ui(self):


        self.x_scale_slider = ScaleSlider(Qt.Orientation.Horizontal)
        self.x_scale_slider.setMinimumWidth(200)
        self.x_scale_slider.valueChanged.connect(self.update_x_scale)
        self.x_scale_slider.sliderWheelMoved.connect(self.handle_slider_wheel)

       # self.view.set_scroll(self.x_scale_slider)
        self.scene.set_scroll_x(self.x_scale_slider)


        self.y_scale_slider = ScaleSlider(Qt.Orientation.Vertical)
        self.y_scale_slider.setMinimumHeight(200)

        self.y_scale_slider.valueChanged.connect(self.update_y_scale)
        self.y_scale_slider.sliderWheelMoved.connect(self.handle_slider_wheel)

        self.scene.set_scroll_y(self.y_scale_slider)

        x_label = QLabel("Масштаб X:")
        y_label = QLabel("Масштаб Y:")
        y_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.h_grid_check = QCheckBox("Горизонтальная сетка")
        self.h_grid_check.setChecked(True)
        self.h_grid_check.stateChanged.connect(self.toggle_h_grid)

        self.h_grid_step = QLineEdit("30")
        self.h_grid_step.setFixedWidth(40)
        self.h_grid_step.editingFinished.connect(self.update_grid_steps)

        self.v_grid_check = QCheckBox("Вертикальная сетка")
        self.v_grid_check.setChecked(True)
        self.v_grid_check.stateChanged.connect(self.toggle_v_grid)

        self.v_grid_step = QLineEdit("50")
        self.v_grid_step.setFixedWidth(40)
        self.v_grid_step.editingFinished.connect(self.update_grid_steps)

        self.toolbar = QHBoxLayout()
       # self.toolbar.addWidget(x_label)


        y_slider_container = QWidget()
        y_slider_layout = QVBoxLayout(y_slider_container)
        y_slider_layout.addWidget(y_label)
        y_slider_layout.addWidget(self.y_scale_slider)
        y_slider_layout.addStretch()

        main_layout = QHBoxLayout()

        left_container = QWidget()
        left_layout = QVBoxLayout(left_container)

        ################################
        self.splitter = self.sbor.splitter


        # Контейнер для MIDI редакторов
        self.midi_container = QWidget()
        self.midi_layout = QVBoxLayout(self.midi_container)
        self.midi_layout.setContentsMargins(0, 0, 0, 0)
        self.midi_layout.setSpacing(2)

        # Кнопка добавления MIDI редактора
        self.add_midi_btn = QPushButton("Add MIDI Track")
        self.add_midi_btn.clicked.connect(self.add_midi_editor)

        left_layout.addLayout(self.toolbar)
        left_layout.addWidget(self.sbor)
        left_layout.addWidget(self.add_midi_btn)
        left_layout.addWidget(self.midi_container)


        # Добавляем первый MIDI редактор
        self.add_midi_editor()

        # Синхронизация скроллинга
        self.view.horizontalScrollBar().valueChanged.connect(self.sync_midi_scrolling)
        self.view.verticalScrollBar().valueChanged.connect(self.sync_midi_scrolling_y)
        ##############################
        self.play_toolbar = PlayToolBar(self)
        self.top_tool_bar = TopTollBar(self,30)


        self.toolbar.addWidget(self.play_toolbar)
        self.toolbar.addWidget(self.top_tool_bar)
        self.toolbar.addStretch()
        self.toolbar.addWidget(self.x_scale_slider)

        main_layout.addWidget(left_container)
        main_layout.addWidget(y_slider_container)


        self.setLayout(main_layout)
        self.update_x_scale(100)
        self.update_y_scale(100)

        self.timeline.update_indicator()

        self.interpr = None

        self.timer = QTimer()
        self.timer_len = 30
        self.timer.timeout.connect(self.move_line)

        self.is_playing = False
        self.tempo = 120
        self.line_x = self.timeline.get_x_pose()
        self.line_start = self.line_x
        self.speed = calc_speed(self.tempo) * 0.001 * self.timer_len

        self.active_loop = False

        #self.update()
    def save(self):
        self.save_as(self.name)
    def save_as(self,filename):
        self.scene.grid_evts.save_as(filename)
        self.midi_data.save_as(filename)

    def toggle_animation(self):
        if not self.is_playing:
            self.line_x = self.timeline.get_x_pose()
            self.start_animation()
        else:
            self.line_x = self.line_start
            self.start_animation()
        self.line_start = self.line_x

    def start_animation(self):
        self.is_playing = True
        self.timer.start(self.timer_len)
    def stop_animation(self):
        self.is_playing = False
        self.timer.stop()
    def stop_ret(self):
        self.is_playing = False
        self.timer.stop()
        self.timeline.set_x(self.line_start)
    def move_line(self):
        self.line_x += self.speed
        if self.active_loop and self.scene.loop_legal():
            if self.line_start < self.scene.loop_end and self.line_x > self.scene.loop_end:
                self.line_x = self.scene.loop_start + self.line_x - self.scene.loop_end
        else:
            self.line_x += self.speed
        self.timeline.set_x(self.line_x)
    def play_midi(self):
        self.midi_data.play_auto_full_all(calc_ppq(self.timeline.get_x_pose()))

    def stop_midi(self):
        self.midi_data.stop_auto_full_all()


    def set_midi_data(self, data):
        self.midi_data = data
        self.scene.midi_data = data
    def add_interpr(self,interPr):
        self.interpr = interPr
        self.scene.add_interpr(interPr)
        self.scene.grid_evts.set_interpr(interPr)

    def add_midi_player(self,midi_player):
        self.midi_player = midi_player
        self.scene.add_midi_player(midi_player)

    def update_x_scale(self, value):
        scale = value / 100.0
        self.view.x_scale = scale
        self.view.apply_scaling()
        x_pos = self.timeline.get_x_pose()
        self.view.move_centre(x_pos)

        self.scene.grid_evts.set_size_factor(scale)
        self.head_view.apply_scaling(scale,-1)
        self.head_view.sync_with_main_scene()
        self.sync_midi_scrolling()
        for editor in self.midi_editors:
         #   editor.resizeEvent(event)
            editor.apply_scaling(scale,-1)
            editor.sync_with_main_scene()
            self.sync_midi_scrolling()

    def update_y_scale(self, value):
        scale = value / 100.0
        self.view.y_scale = scale
        self.view.apply_scaling()
        self.key_view.apply_scaling(-1,scale)
        self.sync_midi_scrolling_y()

    def handle_slider_wheel(self, delta):
        slider = self.sender()
        if delta > 0:
            slider.setValue(slider.value() + slider.singleStep())
        else:
            slider.setValue(slider.value() - slider.singleStep())

    def toggle_h_grid(self, state):
        self.scene.h_grid_enabled = state == Qt.CheckState.Checked.value
        self.scene.update()

    def toggle_v_grid(self, state):
        self.scene.v_grid_enabled = state == Qt.CheckState.Checked.value
        self.scene.update()

    def update_grid_steps(self):
        try:
            h_step = int(self.h_grid_step.text())
            if h_step > 0:
                self.scene.h_grid_size = h_step
               # self.scene.rect_height = h_step  # Обновляем высоту новых прямоугольников
        except ValueError:
            pass

        try:
            v_step = int(self.v_grid_step.text())
            if v_step > 0:
                self.scene.v_grid_size = v_step
        except ValueError:
            pass

    def add_midi_editor(self):
        """Добавляет новый MIDI редактор"""
        midi_editor = MidiEventWidget(self.scene)
        self.midi_editors.append(midi_editor)

        #self.splitter.addWidget(midi_editor)
        evt_widget = EventFillerWidget(midi_editor,self.key_view.width())
        midi_editor.set_evt_widget(evt_widget)
        self.sync_splitter.add_sync_widget(evt_widget,midi_editor)

        midi_editor.setMaximumHeight(200)
        midi_editor.setMinimumHeight(20)
        midi_editor.set_midi_data(self.midi_data)

    def sync_midi_scrolling(self):
        """Синхронизирует прокрутку всех MIDI редакторов с основной сценой"""
        h_scroll = self.view.horizontalScrollBar().value()

        self.head_view.horizontalScrollBar().setValue(h_scroll)
        for editor in self.midi_editors:
            editor.horizontalScrollBar().setValue(h_scroll)
            #editor.verticalScrollBar().setValue(v_scroll)

    def sync_midi_scrolling_y(self):
        v_scroll = self.view.verticalScrollBar().value()
        #print( self.view.verticalScrollBar().maximum())
        self.key_view.verticalScrollBar().setValue(v_scroll)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        #self.scene.grid_evts.set_size_factor(self.scene.transform().m11)
        # При изменении размера обновляем синхронизацию
        for editor in self.midi_editors:
         #   editor.resizeEvent(event)
            editor.sync_with_main_scene()
           # editor.apply_scaling(self.y_scale_slider.value() / 100.0,1)
        #self.key_view.sync_with_main_scene()

    def get_all_rect_items(self):
        """Возвращает все QGraphicsRectItem на сцене"""
        rect_items = []
        for item in self.scene.items():
            if isinstance(item, RectangleItem):
                rect_items.append(item)
        return rect_items


if __name__ == "__main__":

    #player = MidiPlayer(port_name = "Microsoft GS Wavetable Synth 0")
    app = QApplication(sys.argv)
    #editor = RectangleEditor()
    editor = RectangleEditor()
  #  editor.add_midi_player(midi_play)
    player = MidiPlaySync()
    #player = MidiPlayer('loopMIDI Port 1 5')
    editor.set_midi_data(AllNotesEvtData(player))
    #midi_play = MidiPlayer(port_name="Microsoft GS Wavetable Synth 1")
    editor.add_interpr(toMidi())
    editor.show()
    sys.exit(app.exec())