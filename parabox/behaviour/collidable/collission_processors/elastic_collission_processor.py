from kivy.vector import Vector

from parabox.structures import Collector


class ElasticCollissionProcessor(object):
    """Collission processor for elastic objects"""

    @staticmethod
    def process_collission(first, second):
        """Process collission for two elastic objects

        :param first: first widget to check collission
        :type first: parabox.behaviour.collidable.Collidable
        :param second: second widget to check collission
        :type second: parabox.behaviour.collidable.Collidable
        """
        if first in Collector.get_collection('movable'):
            base, additional = first, second
        else:
            base, additional = second, first
        ElasticCollissionProcessor.clarify_collission_point(base, additional)
        base.velocity, additional.velocity =\
            ElasticCollissionProcessor.get_velocity_after_collission(
                base, additional)

    @staticmethod
    def clarify_collission_point(first, second):
        """Correct collission point of two widgets

        :param first: first collission widget
        :type first: parabox.behaviour.collidable.Collidable
        :param second: second collission widget
        :type second: parabox.behaviour.collidable.Collidable
        """
        temp_velocity = second.get_resistance_vector(first)
        if temp_velocity == Vector(0, 0):
            temp_velocity = Vector(1, 0)
        initial_velocity = Vector(first.velocity)
        first.velocity = temp_velocity
        first.move(first)
        while first.collide_widget(second) and second.collide_widget(first):
            first.move(first)
        first.velocity = -temp_velocity
        first.move(first)
        first.velocity = initial_velocity

    @staticmethod
    def get_velocity_after_collission(first, second):
        """Change velocities vectors after collission

        :param first: first collission widget
        :type first: parabox.behaviour.collidable.Collidable
        :param second: second collission widget
        :type second: parabox.behaviour.collidable.Collidable
        :returns: velocities vectors
        :rtype: set
        """
        collission_vector_x = second.get_resistance_vector(first)
        v1, v2 = first.velocity, second.velocity
        system_speed = Vector(v2)
        v1, v2 = Vector(v1) - system_speed, Vector(v2) - system_speed
        system_rotate_angle = Vector(1, 0).angle(collission_vector_x)
        v1a, v1b = Vector(v1).rotate(system_rotate_angle)
        mass_ratio = 0 if not second.mass else first.mass / second.mass
        u1a_1, u1a_2 = ElasticCollissionProcessor.solve_quadratic_equation(
            a=mass_ratio + 1,
            b=-2 * mass_ratio * v1a,
            c=(mass_ratio - 1) * v1a ** 2)
        u1a = u1a_1 if u1a_1 != v1a else u1a_2
        u1b = v1b
        u2a = mass_ratio * (v1a - u1a)
        u2b = 0
        u1 = Vector(u1a, u1b).rotate(-system_rotate_angle)
        u2 = Vector(u2a, u2b).rotate(-system_rotate_angle)
        u1, u2 = u1 + system_speed, u2 + system_speed
        return u1, u2

    @staticmethod
    def solve_quadratic_equation(a, b, c):
        """Returns roots of quadratic equation

        ax^2 + bx + c = 0

        :return: roots of equation
        :rtype: set
        """
        D = b ** 2 - 4 * a * c
        return (-b + D ** .5) / (2 * a), (-b - D ** .5) / (2 * a)
