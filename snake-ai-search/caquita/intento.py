import pygame
import random
from queue import Queue
from enum import Enum
from collections import namedtuple
import numpy as np
import copy
import math

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
SPEED = 100

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
        self.clock.tick(SPEED)
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

        for pt in self.snake:
            pygame.draw.rect(self.display, BLUE1, pygame.Rect(pt.x, pt.y, BLOCK_SIZE, BLOCK_SIZE))
            pygame.draw.rect(self.display, BLUE2, pygame.Rect(pt.x+4, pt.y+4, 12, 12))

        pygame.draw.rect(self.display, RED, pygame.Rect(self.food.x, self.food.y, BLOCK_SIZE, BLOCK_SIZE))

        text = font.render("Score: " + str(self.score), True, WHITE)
        self.display.blit(text, [0, 0])
        pygame.display.flip()

    def _move(self, action):
        clock_wise = [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP]
        idx = clock_wise.index(self.direction)
        if np.array_equal(action, [1, 0, 0]) and self.direction != Direction.LEFT:
            self.direction = Direction.RIGHT
        elif np.array_equal(action, [0, 1, 0]) and self.direction != Direction.UP:
            self.direction = Direction.DOWN
        elif np.array_equal(action, [0, 0, 1]) and self.direction != Direction.RIGHT:
            self.direction = Direction.LEFT
        elif np.array_equal(action, [0, 0, 0]) and self.direction != Direction.DOWN:
            self.direction = Direction.UP

        x = self.head.x
        y = self.head.y
        if self.direction == Direction.RIGHT:
            x += BLOCK_SIZE
        elif self.direction == Direction.LEFT:
            x -= BLOCK_SIZE
        elif self.direction == Direction.DOWN:
            y += BLOCK_SIZE
        elif self.direction == Direction.UP:
            y -= BLOCK_SIZE

        self.head = Point(x, y)

        # Insertar nueva cabeza al principio de la serpiente
        self.snake.insert(0, self.head)

    def _greedy_action(self):
        food_x, food_y = self.food
        head_x, head_y = self.head

        print("PASO 1")
        # Paso 1: Calcular la ruta más corta desde la cabeza de la serpiente hasta la comida
        shortest_path = self._find_shortest_path(self.head, self.food)
        print("FIN PASO 1")

        if shortest_path is not None:
            print("DENTRO DEL IF, SHORTEST_PATH IS NOT NONE")
            # Paso 2: Mover una serpiente virtual S2 a lo largo de la ruta más corta para comer la comida
            virtual_snake = copy.deepcopy(self.snake)
            virtual_snake_head = virtual_snake[0]

            for point in shortest_path:
                x_diff = point.x - virtual_snake_head.x
                y_diff = point.y - virtual_snake_head.y

                if x_diff > 0:
                    action = [1, 0, 0]  # Derecha
                elif x_diff < 0:
                    action = [0, 1, 0]  # Izquierda
                elif y_diff > 0:
                    action = [0, 0, 1]  # Abajo
                else:
                    action = [0, 0, 0]  # Arriba

                virtual_snake_head = Point(virtual_snake_head.x + action[0] * BLOCK_SIZE,
                                            virtual_snake_head.y + action[1] * BLOCK_SIZE)

                virtual_snake.insert(0, virtual_snake_head)
                virtual_snake.pop()
            print("SERPIENTE VIRTUAL SE COMIO LA COMIDA")
            # Paso 3: Calcular la ruta más larga desde la cabeza hasta la cola de S2
            longest_path_S2 = self._find_longest_path(virtual_snake[0], virtual_snake[-1])

            if longest_path_S2 and len(longest_path_S2) > 1:
                print("EXISTE UN CAMINO SEGURO, LA ORIGINAL TOMARA EL CAMINO CORTO")
                return self._get_action_from_direction(shortest_path[0], self.head)
        
        print("NOOO EXISTE UN CAMINO SEGURO,")
        # Paso 4: Calcular la ruta más larga desde la cabeza hasta la cola de S1
        longest_path_S1 = self._find_longest_path(self.head, self.snake[-1])

        if longest_path_S1 and len(longest_path_S1) > 0:
            print("DADO QUE NO EXISTE UN CAMINO SEGURO, SE TOMA EL PRIMER MOVIMIENTO DE LA SERPIENTE ORIGINAL HACIA SU COLA ")
            return self._get_action_from_direction(longest_path_S1[0], self.head)


        print("DADO QUE NO EXISTE UN CAMINO SEGURO X 2 LA SERPIENTE SE ALEJA DE LA COMIDA")
        # Paso 5: Elegir la dirección que haga que S1 esté más lejos de la comida
        farthest_direction = self._get_farthest_direction()

        return self._get_action_from_direction(self._get_next_position(farthest_direction), self.head)

   
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


    def _find_longest_path(self, start, end):
        # Algoritmo DFS iterativo para encontrar la ruta más larga desde start hasta end

        # Crear una pila para almacenar los nodos a visitar
        stack = [(start, [start])]
        visited = set()

        # Variables para almacenar la ruta más larga encontrada
        longest_path = []
        max_length = -1

        while stack:
            current, path = stack.pop()

            if current == end:
                if len(path) > max_length:
                    longest_path = path
                    max_length = len(path)
            elif current not in visited:
                visited.add(current)
                neighbors = self._get_neighbors(current)

                for neighbor in neighbors:
                    stack.append((neighbor, path + [neighbor]))

        return longest_path



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


    def _get_action_from_direction(self, next_point, current_point):
        # Obtener la acción (dirección) para llegar desde current_point a next_point

        if next_point.x > current_point.x:
            return [1, 0, 0]  # Derecha
        elif next_point.x < current_point.x:
            return [0, 1, 0]  # Izquierda
        elif next_point.y > current_point.y:
            return [0, 0, 1]  # Abajo
        else:
            return [0, 0, 0]  # Arriba


    def _get_farthest_direction(self):
        # Obtener la dirección que hace que S1 esté más lejos de la comida

        farthest_distance = -1
        farthest_direction = None

        for direction in Direction:
            next_x, next_y = self._get_next_position(direction)
            distance = self._calculate_distance(next_x, next_y, self.food.x, self.food.y)

            if distance > farthest_distance:
                farthest_distance = distance
                farthest_direction = direction

        return farthest_direction


    def _get_next_position(self, direction):
        x = self.head.x
        y = self.head.y

        if direction == Direction.RIGHT:
            x += BLOCK_SIZE
        elif direction == Direction.LEFT:
            x -= BLOCK_SIZE
        elif direction == Direction.DOWN:
            y += BLOCK_SIZE
        elif direction == Direction.UP:
            y -= BLOCK_SIZE

        return Point(x, y)


    def _calculate_distance(self, x1, y1, x2, y2):
        # Calcular la distancia entre dos puntos (x1, y1) y (x2, y2)

        return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)


game = SnakeGameAI()

while True:
    game_over, score = game.play_step()

    if game_over:
        game.reset()
        game_over = True  # Agregar esta línea para evitar que la serpiente siga moviéndose
