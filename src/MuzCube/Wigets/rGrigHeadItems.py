from copy import copy
from typing import  Any

from PyQt6.QtCore import QRectF,  QPointF
from PyQt6.QtGui import QColor, QBrush, QPen
from PyQt6.QtWidgets import QGraphicsRectItem, QGraphicsItem
from src.MuzCube.UtilClasses.rGrigMixins import MixinRemove


class HeadRect(QGraphicsRectItem,MixinRemove):
    def __init__(self, level = 0, time =0, right = True, block = False,change_grid = None,is_loop= False,loop_left = True, loop_obj = None,size=8,offset=1,height = 45):

        self.change_grid = change_grid
        self.prior = 0
        self.block = block

        self.color = QColor(210,210,210)
        self.pen = QPen(QColor(0,0,0))
        self.pen.setCosmetic(True)
        self.brush = QBrush(self.color)

        self.loop_obj = loop_obj
        self.is_loop = is_loop
        self.loop_left = loop_left

        self.height = height
        self.time = time
        self.level = level
        self.size = size
        self.size_plus = self.size+offset
        self.offset = offset
        self.right = right

        if self.is_loop and self.loop_obj:
            self.right = self.loop_left

        self.back_change_grid()
        self.fix_prior()
        if self.right:
            super().__init__(QRectF(0, 0, self.size, self.size))
        else:
            super().__init__(QRectF(0, 0, self.size, self.size))
        MixinRemove.__init__(self)
        self.set_pos_auto()

        self.setBrush(self.brush)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        self.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIgnoresTransformations)
    def set_block(self,block):
        self.block = block
    def get_q_rect(self):
        if self.right:
            q_rect = QRectF(self.time + self.offset,self.offset + self.level * self.size_plus,self.size,self.size)
        else:
            q_rect = QRectF(self.time - self.size_plus,self.offset + self.level * self.size_plus,self.size,self.size)
        return q_rect

    def set_pos_auto(self):
        if self.right:
            self.setPos(QPointF(self.time,self.offset + self.level * self.size_plus))
        else:
            self.setPos(QPointF(self.time - self.size_plus,self.offset + self.level * self.size_plus))
    def time_from(self,pos):
        if self.right:
            new_time = pos.x() - self.offset
        else:
            new_time = pos.x() - self.offset
            self.setPos(QPointF(self.time - self.size_plus, self.offset + self.level * self.size_plus))
        self.set_time(new_time)

    def set_level(self,level):
        self.level = level
        self.set_pos_auto()

    def auto_rect(self):
        self.set_pos_auto()

    def back_change_grid(self):
        if self.change_grid:
            self.time = self.change_grid.time
            self.color = self.change_grid.get_color()
            self.brush = QBrush(self.color)
            self.right = True

    def fix_prior(self):
        if self.change_grid:
            if self.change_grid.only_y:
                self.prior = 0
            elif self.change_grid.only_x:
                self.prior = 1
            else:
                self.prior = 2
        elif self.is_loop and self.loop_obj:
            self.prior = 3

    def set_change_grid(self,change_grid):
        self.change_grid = change_grid
        self.back_change_grid()
        self.auto_rect()
        self.change_grid.set_head_rect(self)

    def get_time(self):
        if self.right:
            self.time = self.rect().x() + self.pos().x() - self.offset
        else:
            self.time = self.rect().x() + self.pos().x() + self.size_plus
        return self.time

    def set_time(self,time):
        if self.time != time:
            self.time = time
            self.change_grid.set_time(self.time)
        self.set_pos_auto()

    def update_obj(self):
        if self.is_loop and self.loop_obj:
            if self.loop_left:
                self.loop_obj.set_loop_start(self.get_time())
            else:
                self.loop_obj.set_loop_end(self.get_time())
        elif self.change_grid:
            self.change_grid.set_time(self.get_time())

    def mouseMoveEvent(self, event):
        if not self.block:
            super().mouseMoveEvent(event)
            scene = self.scene()

            if self.change_grid:
                x_y = self.change_grid.get_snap(self.pos().x(),self.pos().y(),-1)
                snapped_pos = QPointF(x_y[0],x_y[1])
            else:
                snapped_pos = scene.snap_to_grid(self.pos())
            self.set_time(snapped_pos.x())

    def paint(self, painter, option, widget):
        super().paint(painter, option, widget)

def update_levels(mass):
    for i in range(len(mass)):
            mass[i].set_level(i)
def lock_sort(rect_mass):
    return sorted(rect_mass, key = lambda m: m.prior)

class RectContainer:
    def __init__(self, mass = []):
        self.mass = mass
        self.all_massive = None
        self.back_all_massive()

    def get_all_blocks(self):
        all_massive: list[list[Any]] = []
        if len(self.mass) >= 1:
            element = self.mass[0]
            lock_massive = [element]
            if  len(self.mass) >= 2:
                for i in range(1,len(self.mass)):
                    if self.mass[i].time <= element.time + element.size_plus:
                        lock_massive.append(self.mass[i])
                    else:
                        all_massive.append(copy(lock_massive))
                        lock_massive = [self.mass[i]]
                    element = self.mass[i]
            else:
                all_massive.append(copy(lock_massive))
        return all_massive

    def back_all_massive(self):
        self.all_massive = self.get_all_blocks()

    def append(self, rect: HeadRect):
        self.mass.append(rect)
        self.update_levels()

    def add(self, rect: HeadRect):
        self.mass.append(rect)
        self.sort_all()
        self.update_levels()

    def update_levels(self):
        self.back_all_massive()
        for mass in self.all_massive:
            update_levels(lock_sort(mass))

    def sort_all(self):
        self.mass = sorted(self.mass,key=lambda x: x.time)