from PyQt6.QtCore import QTimer, Qt, QPointF
from PyQt6.QtWidgets import QGraphicsItem, QGraphicsTextItem, QGraphicsOpacityEffect

from src.MuzCube.Scripts.rGrigDataMethods import calc_note_full_rect
from src.MuzCube.Wigets.rGrigEvents import ResizeRect
from src.MuzCube.UtilClasses.rGrigGrids import Scale

class RectangleItem(ResizeRect):
    def __init__(self, rect, parent=None):
        super().__init__(rect, parent)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        self.setAcceptHoverEvents(True)

        self.vel = 100
        self.chan = 0
        self.duration = 0
        self.last_pose =QPointF(rect.x(),rect.y())




        # Настройки для изменения размера
        self.resize_area_def = 5
        self.resize_area_width = 5  # Ширина невидимой области для изменения размера
        self.is_resizing_left = False
        self.is_resizing_right = False
        self.initial_rect = None

        # Эффект прозрачности для анимации
        self.opacity_effect = QGraphicsOpacityEffect()
        self.opacity_effect.setOpacity(1.0)
        self.setGraphicsEffect(self.opacity_effect)

        # Таймер для удаления после анимации
        self.fade_timer = QTimer()
        self.fade_timer.setSingleShot(True)
        self.fade_timer.timeout.connect(self._final_remove)

        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsFocusable)

        self.text_scale = 1.3
        self.text_offset = 0

        self.evt = self.pos()

        self.first_cl = False
    def get_note_on_off(self):
        return calc_note_full_rect(self.rect(),velocity=self.vel,channel=self.chan)

    def add_text_item(self):
        # Удаляем предыдущий текст, если есть
        if self.text_item is None:
            # Создаем новый текстовый элемент
            self.text_item = QGraphicsTextItem("", self)
            self.text_item.setDefaultTextColor(Qt.GlobalColor.black)
            self.text_item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIgnoresTransformations)
            self.text_item.keyPressEvent = self.text_key_press_event
            # Центрируем текст внутри прямоугольника
            self.update_text_and_bord()
            self.text_item.setScale(self.text_scale)
        # Даем фокус текстовому элементу для редактирования
        self.text_item.setTextInteractionFlags(Qt.TextInteractionFlag.TextEditorInteraction)
        self.text_item.setFocus()
        # Подключаем сигнал изменения текста (опционально)
    def set_text(self,text):
        if self.text_item is None:
            self.text_item = QGraphicsTextItem(text, self)
            self.text_item.setDefaultTextColor(Qt.GlobalColor.black)
            self.text_item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIgnoresTransformations)
            self.text_item.keyPressEvent = self.text_key_press_event
            self.update_text_position()
            self.text_item.setScale(self.text_scale)
        else:
            self.text_item.setPlainText(text)
    def get_text(self):
        if self.text_item is not None:
            return self.text_item.toPlainText()
        return ""
    def text_no_interact(self):
        if self.text_item is not None:
            self.clearFocus()
            if self.scene():
                self.scene().clearFocus()
            self.text_item.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
    def update_area(self):
        self.resize_area_width = self.resize_area_def / self.transforms.m11()
    def update_text_and_bord(self):
        self.update_area()
        if self.text_item is not None:
            rect = self.rect()
            off = self.transforms.m22()
            text_rect = self.text_item.boundingRect()
            self.text_offset = (rect.height() * off - text_rect.height() * self.text_scale) / 2 / off
            self.text_item.setPos(rect.x() + self.resize_area_width, rect.y() + self.text_offset)
    def keyPressEvente(self, event):
        if event.key() == Qt.Key.Key_Tab and self.isSelected():
            self.add_text_item()
            event.accept()
        """elif event.key() == Qt.Key.Key_Delete and self.isSelected():
            self.fade_out_and_remove()
            event.accept()"""

    def text_key_press_event(self, event):
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            # Завершаем редактирование
            self.clearFocus()
            if self.scene():
                self.scene().clearFocus()
            self.text_item.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        else:
            # Стандартная обработка для других клавиш
            QGraphicsTextItem.keyPressEvent(self.text_item, event)

    def set_note_text(self):
        #########################
       # k=-0
        scene = self.scene()
        if scene.interpr:
            scene.interpr()

    def hoverMoveEvent(self, event):
        ## print(self.resize_area_width)
        rect = self.rect()
        if (event.pos().x() < rect.left() + self.resize_area_width or
                event.pos().x() > rect.right() - self.resize_area_width):
            self.setCursor(Qt.CursorShape.SizeHorCursor)
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)
        super().hoverMoveEvent(event)
    def mousePressEvent(self, event):
        self.first_cl = True
        if event.button() == Qt.MouseButton.RightButton:
            self.fade_out_and_remove()
            return

        rect = self.rect()
        # Проверяем, нажали ли на области изменения размера
        if event.pos().x() < rect.left() + self.resize_area_width:
            if self.isSelected():
                self.scene().resize_back(self)
            self.is_resizing_left = True
            self.initial_rect = rect
        elif event.pos().x() > rect.right() - self.resize_area_width:
            if self.isSelected():
                self.scene().resize_back(self)
            self.is_resizing_right = True
            self.initial_rect = rect
        else:
            self.evt = event.pos()
            self.scene().play_rect(self)
            self.last_pose = self.pos()
            super().mousePressEvent(event)
    def resize_press(self):
        self.initial_rect = self.rect()
    def resize(self,pos,left,right):
        x = self.pos().x()
        new_pos = pos
        # new_pos = self.pos()
        scene = self.scene()
        if scene and (scene.v_grid_enabled or scene.h_grid_enabled):
            new_pos = scene.snap_to_grid(new_pos + self.pos())

        rect = self.rect()
        if left:
            if x - new_pos.x() + rect.width() > 5:  # Минимальная ширина
                self.setRect(0, 0, x - new_pos.x() + rect.width(), rect.height())
                out_pos = QPointF(new_pos.x(),self.pos().y())
                self.setPos(out_pos)
            if self.text_item:
                self.text_item.setPos(rect.x() + self.resize_area_width, rect.y() + self.text_offset)
        elif right:
            # Растягиваем вправо
            new_right = new_pos.x()
            new_width = new_right - self.initial_rect.left()
            if new_width > 5:  # Минимальная ширина
                self.setRect(0, 0, new_pos.x() - self.pos().x(), rect.height())
    def resize_out(self):
        self.initial_rect = None
    def mouseMoveEvent(self, event):
        if self.is_resizing_left or self.is_resizing_right:
            # Изменяем размер прямоугольника
            self.resize(event.pos(),self.is_resizing_left,self.is_resizing_right)
            if self.isSelected():
                self.scene().resize_all(event,self)
        else:
            super().mouseMoveEvent(event)
            scene = self.scene()
            snapped_pos = event.pos()
            if scene and (scene.v_grid_enabled or scene.h_grid_enabled):
                snapped_pos = scene.snap_to_grid(self.pos(),time=self.pos().x()+self.evt.x())
                self.setPos(snapped_pos)
            if self.last_pose.y() != snapped_pos.y():
                scene.off_rect(self.last_pose + self.rect().bottomLeft())
                scene.play_rect(self)
            self.last_pose = snapped_pos



        if self.scene() and self.scene().views():
            self.scene().views()[0].viewport().update()
        self.first_cl = False
    def mouseReleaseEvent(self, event):
        if self.isSelected() and (self.is_resizing_left or self.is_resizing_right):
            self.scene().resize_close()
        self.is_resizing_left = False
        self.is_resizing_right = False
        self.first_cl = False
        self.initial_rect = None
        self.scene().off_rect(self.last_pose + self.rect().bottomLeft())

        super().mouseReleaseEvent(event)

    def update_text_position(self):
        if self.text_item is not None:
            view = self.scene().views()[0] if self.scene() and self.scene().views() else None
            if not view:
                return
            transform = view.transform()
            scale_y = transform.m22()
            rect = self.rect()
            rect_height = rect.height()
            text_rect = self.text_item.boundingRect()
            text_height = text_rect.height()
            center_y = (rect_height * scale_y - text_height * self.text_scale) / 2 / scale_y
            self.text_item.setPos(0, center_y)
    def check_focus(self):
        if self.text_item is not None:
            if not self.text_item.hasFocus():
                self.text_no_interact()
    def paint(self, painter, option, widget):
        self.update_text_position()
        self.update_area()
        super().paint(painter, option, widget)
#class ArpegNotes():

class ChordNotes():
    def __init__(self):
        self.interpr = None
        self.scale = None
        self.name = 'name'
        self.text = 'text'
        self.notes = []
    def from_text(self, name, interpr, text = None):
        self.name = name
        self.interpr = interpr
        self.scale = Scale(interpr,name,str=text)

