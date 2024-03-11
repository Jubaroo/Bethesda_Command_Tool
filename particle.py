import math
import random

import pygame


class Particle:
    def __init__(self, x, y, radius, color, screen_width, screen_height):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.angle = random.uniform(0, 2 * math.pi)
        self.velocity = random.uniform(1, 4)
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.trail_length = random.randint(10, 20)
        self.history = []

    def move(self):
        self.history.append((self.x, self.y))
        if len(self.history) > self.trail_length:
            self.history.pop(0)

        self.x += math.cos(self.angle) * self.velocity
        self.y += math.sin(self.angle) * self.velocity

        # Bounce off the edges
        if self.x < 0 or self.x > self.screen_width:
            self.angle = math.pi - self.angle
        if self.y < 0 or self.y > self.screen_height:
            self.angle = -self.angle

    def draw(self, screen):
        # Drawing the trail
        for i, point in enumerate(self.history):
            alpha = int(255 * i / len(self.history))
            radius = int(self.radius * i / len(self.history))
            trail_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(trail_surface, (*self.color, alpha), (radius, radius), radius)
            screen.blit(trail_surface, (point[0] - radius, point[1] - radius))

        # Drawing the particle
        glow_surface = pygame.Surface((self.radius * 4, self.radius * 4), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, self.color, (self.radius * 2, self.radius * 2), self.radius)
        screen.blit(glow_surface, (self.x - self.radius * 2, self.y - self.radius * 2))
