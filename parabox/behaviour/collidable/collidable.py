from kivy.vector import Vector
from numpy import array, zeros

from parabox.base_object import BaseObject
from parabox.structures import Collector


class Collidable(BaseObject):
    """Mixin for classed with collission behaviour"""

    def __init__(self, *args, mass=1, **kwargs):
        """Collidable constructor

        :param mass: mass of object. None for static objects. 1 by default.
        :type mass: float
        """
        super(Collidable, self).__init__(*args, **kwargs)
        self.mass = mass
        self.add_to_collections(["collidable"])
        self.register_event_type('on_collide')
        self.bind(on_update=self.process_collisions)

    def get_resistance_vector(self, widget):
        """Return vector from self to widget

        :param widget: widget to calculate collission
        :type widget: kivy.uix.widget.Widget
        :returns: vector from self to widget
        :rtype: kivy.vector.Vector
        """
        intersection = Collidable.get_intersection(self, widget)
        affection_zone = self._get_affection_zone(intersection)
        result = self._calculate_resistance_vector(affection_zone)
        return result

    def process_collisions(self, instance):
        """Check if self collide another widget.

        Dispatch 'on_collide' event.
        """
        for widget in Collector.get_collection("collidable"):
            if (self is not widget and self.collide_widget(widget) and
                    widget.collide_widget(self)):
                self.dispatch("on_collide", widget)

    def on_collide(self, widget):
        """Event in case of collission self with another widget"""
        pass

    @staticmethod
    def get_intersection(first, second):
        """Returns coords of collission sector between two widgets

        :param first: first widget to check collission
        :type first: parabox.behaviour.collidable.Collidable
        :param second: second widget to check collission
        :type second: parabox.behaviour.collidable.Collidable
        :returns: collission sector's coords or None if no collission
        :rtype: array or None
        """
        if second.size < first.size:
            first, second = second, first
        intersection = array([[0, 0], [0, 0]], dtype=int)
        have_intersection = False
        for x, y in first.get_collide_check_pixels():
            world_x, world_y = first._get_absolute_coords_by_relative(x, y)
            if (second.collide_point(world_x, world_y) and
                    first.collide_point(world_x, world_y)):
                have_intersection = True
                if intersection[0, 0] == 0 or intersection[0, 0] > world_x:
                    intersection[0, 0] = world_x
                if intersection[1, 0] == 0 or intersection[1, 0] < world_x:
                    intersection[1, 0] = world_x
                if intersection[0, 1] == 0 or intersection[0, 1] > world_y:
                    intersection[0, 1] = world_y
                if intersection[1, 1] == 0 or intersection[1, 1] < world_y:
                    intersection[1, 1] = world_y
        return intersection if have_intersection else None

    def _get_affection_zone(self, intersection, expand=5):
        """Get matrix of collission sector

        :param intersection: collission coords
        :type intersection: array
        :param expand: expanding of collission sector, 5 by default
        :type expand: int
        :returns: bitmap of collission sector
        :rtype: numpy.ones
        """
        intersection_size = (
            intersection[1, 0] - intersection[0, 0] + 1,
            intersection[1, 1] - intersection[0, 1] + 1)
        affection_zone = zeros([
            intersection_size[0] + expand * 2,
            intersection_size[1] + expand * 2],
            dtype=bool)
        for x in range(intersection[0, 0] - expand,
                       intersection[1, 0] + expand + 1):
            for y in range(intersection[0, 1] - expand,
                           intersection[1, 1] + expand + 1):
                if self.collide_point(x, y):
                    local_x = x - intersection[0, 0] + expand
                    local_y = y - intersection[0, 1] + expand
                    affection_zone[local_x, local_y] = True
        return affection_zone

    def _calculate_resistance_vector(self, affection_zone):
        """Calculate vector from self to widget

        :param affection_zone: bitmap of collission sector
        :type affection_zone: numpy.ones
        :returns: vector from self to widget
        :rtype: kivy.vector.Vector
        """
        resistance_vector = Vector(0, 0)
        for x in range(affection_zone.shape[0]):
            for y in range(affection_zone.shape[1]):
                if not affection_zone[x, y]:
                    resistance_vector += Vector(
                        x - (affection_zone.shape[0] - 1) / 2,
                        y - (affection_zone.shape[1] - 1) / 2).normalize()
        return resistance_vector.normalize()

    def get_collide_check_pixels(self):
        """Get points to use for checking collission

        :returns: points for check collission
        :rtype: array of sets
        """
        check_pixels = []
        for x in range(self.size[0] + 1):
            if x == 0 or x == self.size[0]:
                y_values_to_check = range(self.size[1] + 1)
            else:
                y_values_to_check = (0, self.size[1])
            for y in y_values_to_check:
                check_pixels.append((x, y))
        return check_pixels
