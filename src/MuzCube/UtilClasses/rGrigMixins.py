from PyQt6.QtCore import QPropertyAnimation
from PyQt6.QtGui import QTransform
from PyQt6.QtWidgets import QGraphicsOpacityEffect


class TimerPlayMixin:
   # def init(self,timer):

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
class LoopObject:
    def __init__(self):
        self.draw_loop = False
        self.loop_rez = 0

        self.loop = True
        self.loop_start = 0
        self.loop_end = 0

    def loop_legal(self):
        return self.loop and self.loop_start != self.loop_end

    def loop_fix(self):
        if self.loop_end < self.loop_start:
            a = self.loop_end
            self.loop_end = self.loop_start
            self.loop_start = a

    def set_loop_bol(self, value):
        self.loop = value

    def set_loop(self,start,end):
        self.loop_start = start
        self.loop_end = end
    def set_loop_start(self,start):
        self.loop_start = start
        self.update()
    def set_loop_end(self,end):
        self.loop_end = end
        self.update()

    def loop_draw_start(self, event):
        self.draw_loop = True
        point = self.snap_to_grid(event.scenePos())
        self.loop_rez = point.x()

    def loop_move(self, event):
        self.loop_start = self.loop_rez
        point = self.snap_to_grid(event.scenePos())
        self.loop_end = point.x()
        self.update()
        self.main_scene.update()

    def loop_release(self, event):
        self.draw_loop = False
        self.update()
        self.main_scene.update()

class MixinRemove:
    def __init__(self):
        self.removing = False
        self._opacity = 1.0
    def _final_remove(self):
        """Финальное удаление элемента после анимации"""
        if self.scene():
            self.scene().removeItem(self)
        self.removing = False

    def opacity(self, value):
        self._opacity = max(0.0, min(1.0, value))
        if self.text_item:
            self.text_item.setOpacity(self._opacity)
        self.update()

    def fade_out_and_remove(self):
        # Создаем эффект прозрачности
        if not self.removing:
            effect = QGraphicsOpacityEffect()
            self.setGraphicsEffect(effect)

            # Анимация прозрачности
            self.animation = QPropertyAnimation(effect, b"opacity")
            self.animation.setDuration(300)
            self.animation.setStartValue(1.0)
            self.animation.setEndValue(0.0)
            self.animation.finished.connect(self._final_remove)
            self.animation.start()
        self.removing = True

class SceneTimeMixin:
    def set_time(self, x):
        if self.time_line is not None:
            self.time_line.set_x(x)
    def click_head(self,event):
        if not self.rectAt(event.scenePos(), QTransform()):
            self.click_for_head(event)
    def click_for_head(self, event):
        point = self.snap_to_grid(event.scenePos(), time=self.start_point.x()) if (
                self.v_grid_enabled or self.h_grid_enabled) else event.scenePos()
        if self.editor is not None:
            self.editor.line_x = point.x()
            self.editor.line_start = self.editor.line_x
        self.set_time(point.x())

    def click_head_head(self, event):
        point = self.snap_to_grid(event.scenePos())
        if self.editor is not None:
            self.editor.line_x = point.x()
            self.editor.line_start = self.editor.line_x
        self.set_time(point.x())


class KeyManageMixin:
    def mousePressEvent(self, event):
        sup = self.mouse_key_manage.auto_def('press', event)
        if sup:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        sup = self.mouse_key_manage.auto_def('move', event)
        if sup:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        sup = self.mouse_key_manage.auto_def('release', event)
        if sup:
            super().mouseReleaseEvent(event)

    def keyPressEvent(self, event):
        self.mouse_key_manage.KeyPress(event)
        if self.mouse_key_manage.sup():
            super().keyPressEvent(event)

    def keyReleaseEvent(self, event):
        self.mouse_key_manage.KeyRelease(event)
        super().keyReleaseEvent(event)

class DeleteMixin:
    def test(self):
        print("Mixin2")
class SelectMixin:
    def test(self):
        d=0
