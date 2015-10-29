from kivy.vector import Vector
from numpy import array, zeros

from warlocks_war.objects.collector import Collector
from warlocks_war.objects.world_object import WorldObject


class Collidable(WorldObject):
    def __init__(self, *args, **kwargs):
        super(Collidable, self).__init__(*args, **kwargs)
        self.add_to_collections(["collidable"])
        self.bind(on_update=self.process_collisions)

    def get_resistance_vector(self, widget):
        intersection = self._get_intersection(widget)
        affection_zone = self._get_affection_zone(intersection)
        return self._calculate_resistance_vector(affection_zone)

    def process_collisions(self, instance):
        for widget in Collector.get_collection("collidable"):
           if self is not widget and self.collide_widget(widget):
               resistance = widget.get_resistance_vector(self)
               collide_velocity = Vector(self.velocity) - Vector(widget.velocity)
               resistance_vector_factor = -2 * (collide_velocity[0] * resistance[0] + collide_velocity[1] * resistance[1])
               self.velocity_x = collide_velocity[0] + resistance_vector_factor * resistance[0]
               self.velocity_y = collide_velocity[1] + resistance_vector_factor * resistance[1]

    def _get_intersection(self, widget):
        intersection = array([[0, 0], [0, 0]], dtype=int)
        have_intersection = False
        for x in range(self.size[0] + 1):
            for y in range(self.size[1] + 1):
                world_x, world_y = self._get_absolute_coords_by_relative(x, y)
                if widget.collide_point(world_x, world_y) and self.collide_point(world_x, world_y):
                    have_intersection = True
                    if intersection[0, 0] == 0:
                        intersection[0, 0] = world_x
                    intersection[1, 0] = world_x
                    if intersection[0, 1] == 0 or intersection[0, 1] > world_y:
                        intersection[0, 1] = world_y
                    if intersection[1, 1] == 0 or intersection[1, 1] < world_y:
                        intersection[1, 1] = world_y
        return intersection if have_intersection else None

    def _get_affection_zone(self, intersection, expand=1):
        intersection_size = (
            intersection[1, 0] - intersection[0, 0] + 1,
            intersection[1, 1] - intersection[0, 1] + 1)
        affection_zone = zeros([
                intersection_size[0] + expand * 2,
                intersection_size[1] + expand * 2,],
            dtype=bool)
        for x in range(intersection[0, 0] - expand, intersection[1, 0] + expand + 1):
            for y in range(intersection[0, 1] - expand, intersection[1, 1] + expand + 1):
                if self.collide_point(x, y):
                    local_x = x - intersection[0, 0] + expand
                    local_y = y - intersection[0, 1] + expand
                    affection_zone[local_x, local_y] = True
        return affection_zone

    def _calculate_resistance_vector(self, affection_zone):
        resistance_vector = Vector(0, 0)
        for x in range(affection_zone.shape[0]):
            for y in range(affection_zone.shape[1]):
                if not affection_zone[x, y]:
                    resistance_vector += Vector(
                        x - (affection_zone.shape[0] - 1) / 2,
                        y - (affection_zone.shape[1] - 1) / 2).normalize()
        return resistance_vector.normalize()

