import pygame
import random
from enum import Enum
from collections import namedtuple
from queue import Queue

pygame.init()
font = pygame.font.Font('arial.ttf', 25)

# Enumeración para representar la dirección
class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4

# Estructura para representar un punto en el juego
Point = namedtuple('Point', 'x, y')

# Colores RGB
WHITE = (255, 255, 255)
RED = (200, 0, 0)
BLUE1 = (0, 0, 255)
BLUE2 = (0, 100, 255)
BLACK = (0, 0, 0)

BLOCK_SIZE = 20
# SPEED = 100

class SnakeGameAI:
    def __init__(self, w=640, h=480):
        self.w = w
        self.h = h
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption('Snake')
        self.clock = pygame.time.Clock()
        self.reset()

    def reset(self):
        self.direction = Direction.RIGHT
        self.head = Point(self.w/2, self.h/2)
        self.snake = [self.head,
                      Point(self.head.x-BLOCK_SIZE, self.head.y),
                      Point(self.head.x-(2*BLOCK_SIZE), self.head.y)]
        self.score = 0
        self.food = None
        self._place_food()
        self.frame_iteration = 0

    def _place_food(self):
        x = random.randint(0, (self.w-BLOCK_SIZE)//BLOCK_SIZE)*BLOCK_SIZE
        y = random.randint(0, (self.h-BLOCK_SIZE)//BLOCK_SIZE)*BLOCK_SIZE
        self.food = Point(x, y)
        if self.food in self.snake:
            self._place_food()

    def play_step(self):
        # Recolectar eventos de usuario
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        # Calcular dirección mediante algoritmo greedy
        action = self._greedy_action()
        self._move(action)

        # Verificar colisión
        game_over = False
        if self.is_collision() or self.frame_iteration > 100*len(self.snake):
            game_over = True
            return game_over, self.score

        # Verificar si se come la comida
        if self.head == self.food:
            self.score += 1
            self._place_food()
        else:
            self.snake.pop()

        # Actualizar la interfaz de usuario
        self._update_ui()
        self.clock.tick(300)
        self.frame_iteration += 1

        return game_over, self.score

    def is_collision(self, pt=None):
        if pt is None:
            pt = self.head
        if pt.x >= self.w or pt.x < 0 or pt.y >= self.h or pt.y < 0:
            return True
        if pt in self.snake[1:]:
            return True
        return False

    def _update_ui(self):
        self.display.fill(BLACK)

        for idx, pt in enumerate(self.snake):
            pygame.draw.rect(self.display, BLUE1, pygame.Rect(pt.x, pt.y, BLOCK_SIZE, BLOCK_SIZE))
            pygame.draw.rect(self.display, BLUE2, pygame.Rect(pt.x+4, pt.y+4, 12, 12))

            # Dibujar la cabeza de la serpiente de un color diferente
            if idx == 0:
                pygame.draw.rect(self.display, (0, 150, 255), pygame.Rect(pt.x, pt.y, BLOCK_SIZE, BLOCK_SIZE))

        pygame.draw.rect(self.display, RED, pygame.Rect(self.food.x, self.food.y, BLOCK_SIZE, BLOCK_SIZE))

        text = font.render("Score: " + str(self.score), True, WHITE)
        self.display.blit(text, [0, 0])
        pygame.display.flip()


    def _move(self, action):
        if action == [1, 0, 0]:  # Derecha
            new_direction = Direction.RIGHT
        elif action == [0, 1, 0]:  # Izquierda
            new_direction = Direction.LEFT
        elif action == [0, 0, 1]:  # Abajo
            new_direction = Direction.DOWN
        else:
            new_direction = Direction.UP

        x = self.head.x
        y = self.head.y
        if new_direction == Direction.RIGHT:
            x += BLOCK_SIZE
        elif new_direction == Direction.LEFT:
            x -= BLOCK_SIZE
        elif new_direction == Direction.DOWN:
            y += BLOCK_SIZE
        elif new_direction == Direction.UP:
            y -= BLOCK_SIZE

        self.direction = new_direction
        self.head = Point(x, y)
        self.snake.insert(0, self.head)

    def _greedy_action(self):
        # Paso 1: Calcular la ruta más corta desde la cabeza de la serpiente hasta la comida
        shortest_path = self._find_shortest_path(self.head, self.food)

        # Paso 2: Elegir la dirección basada en la siguiente posición en la ruta más corta
        if shortest_path:
            next_position = shortest_path[1]
            return self._get_action_from_direction(self.head, next_position)
        else:
            # Si no hay ruta, se elige una acción aleatoria
            return self._get_random_action()

    def _find_shortest_path(self, start, end):
        # Algoritmo BFS para encontrar la ruta más corta desde start hasta end

        # Crear una cola para almacenar los nodos a visitar
        queue = Queue()
        queue.put(start)

        # Crear un diccionario para almacenar los padres de cada nodo visitado
        parent = {}
        parent[start] = None

        # Bucle principal del BFS
        while not queue.empty():
            current = queue.get()

            # Verificar si se llegó al nodo objetivo
            if current == end:
                break

            # Obtener los vecinos del nodo actual
            neighbors = self._get_neighbors(current)

            # Recorrer los vecinos del nodo actual
            for neighbor in neighbors:
                if neighbor not in parent:
                    queue.put(neighbor)
                    parent[neighbor] = current

        # Reconstruir la ruta más corta desde start hasta end
        shortest_path = []
        node = end
        while node is not None:
            shortest_path.insert(0, node)
            node = parent[node]

        return shortest_path

    def _get_neighbors(self, point):
        # Obtener los vecinos de un punto en el tablero
        x, y = point
        neighbors = []

        # Verificar vecinos en las cuatro direcciones
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        for dx, dy in directions:
            new_x = x + dx
            new_y = y + dy
            neighbor = Point(new_x, new_y)

            # Verificar si el vecino está dentro del tablero y no es parte de la serpiente
            if 0 <= new_x < self.w and 0 <= new_y < self.h and neighbor not in self.snake:
                neighbors.append(neighbor)

        return neighbors

    def _get_action_from_direction(self, current_point, next_point):
        # Obtener la acción (dirección) para llegar desde current_point a next_point
        x_diff = next_point.x - current_point.x
        y_diff = next_point.y - current_point.y

        if x_diff > 0:
            return [1, 0, 0]  # Derecha
        elif x_diff < 0:
            return [0, 1, 0]  # Izquierda
        elif y_diff > 0:
            return [0, 0, 1]  # Abajo
        else:
            return [0, 0, 0]  # Arriba

    def _get_random_action(self):
        # Obtener una acción aleatoria
        actions = [[1, 0, 0], [0, 1, 0], [0, 0, 1], [0, 0, 0]]
        return random.choice(actions)

game = SnakeGameAI()

while True:
    game_over, score = game.play_step()

    if game_over:
        game.reset()
        game_over = True  # Agregar esta línea para evitar que la serpiente siga moviéndose

