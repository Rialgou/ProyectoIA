from pygame import display, time, draw, QUIT, init, KEYDOWN, K_a, K_s, K_d, K_w
from random import randint
import pygame
from numpy import sqrt
import matplotlib.pyplot as plt
init()

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
max_score = []
episode = 0

cols = 25
rows = 25

width = 600
height = 600
wr = width/cols
hr = height/rows
direction = 1


class Spot:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.f = 0
        self.g = 0
        self.h = 0
        self.neighbors = []
        self.camefrom = []
        self.obstrucle = False

    def show(self, color): # crea las celdas
        draw.rect(screen, color, [self.x*hr+2, self.y*wr+2, hr-4, wr-4])

    def add_neighbors(self): # añade a los cercanos al head a lista neighbors
        if self.x > 0:
            self.neighbors.append(grid[self.x - 1][self.y])
        if self.y > 0:
            self.neighbors.append(grid[self.x][self.y - 1])
        if self.x < rows - 1:
            self.neighbors.append(grid[self.x + 1][self.y])
        if self.y < cols - 1:
            self.neighbors.append(grid[self.x][self.y + 1])


def getpath(food1, snake1): # obtener camino a comida
    food1.camefrom = []
    for s in snake1:
        s.camefrom = []
    openset = [snake1[-1]]
    closedset = []
    dir_array1 = []
    while 1:
        if not openset:
            break
        current1 = openset.pop()
        closedset.append(current1)
        for neighbor in current1.neighbors:
            if neighbor not in closedset and not neighbor.obstrucle and neighbor not in snake1:
                neighbor.camefrom = current1
                openset.append(neighbor)
        if current1 == food1:
            break
    while current1.camefrom:
        if current1.x == current1.camefrom.x and current1.y < current1.camefrom.y:
            dir_array1.append(2)
        elif current1.x == current1.camefrom.x and current1.y > current1.camefrom.y:
            dir_array1.append(0)
        elif current1.x < current1.camefrom.x and current1.y == current1.camefrom.y:
            dir_array1.append(3)
        elif current1.x > current1.camefrom.x and current1.y == current1.camefrom.y:
            dir_array1.append(1)
        current1 = current1.camefrom
    return dir_array1


def run_game():
    score = 0
    global grid, screen
    screen = display.set_mode([width, height])
    display.set_caption("Snake Game")
    clock = time.Clock()

    grid = [[Spot(i, j) for j in range(cols)] for i in range(rows)]

    for i in range(rows):
        for j in range(cols):
            grid[i][j].add_neighbors()

    snake = [grid[round(rows/2)][round(cols/2)]]
    food = grid[randint(0, rows-1)][randint(0, cols-1)]
    current = snake[-1]
    dir_array = getpath(food, snake)
    food_array = [food]

    done = False
    while not done:
        clock.tick(10000000)
        screen.fill(BLACK)
        if(len(dir_array) == 0):
            max_score.append(score) 
            break
        direction = dir_array.pop(-1)
        if direction == 0:    # down
            snake.append(grid[current.x][current.y + 1])
        elif direction == 1:  # right
            snake.append(grid[current.x + 1][current.y])
        elif direction == 2:  # up
            snake.append(grid[current.x][current.y - 1])
        elif direction == 3:  # left
            snake.append(grid[current.x - 1][current.y])
        current = snake[-1]

        if current.x == food.x and current.y == food.y:
            score = score + 1
            while 1:
                food = grid[randint(0, rows - 1)][randint(0, cols - 1)]
                if not (food.obstrucle or food in snake):
                    break
            food_array.append(food)
            dir_array = getpath(food, snake)
        else:
                if(len(snake)> 1):
                    snake.pop(0)

        for spot in snake:
            spot.show(BLUE)
        for i in range(rows):
            for j in range(cols):
                if grid[i][j].obstrucle:
                    grid[i][j].show(RED)

        food.show(RED)
        snake[-1].show(BLUE)
        display.flip()
        for event in pygame.event.get():
            if event.type == QUIT:
                done = True
                quit()
            elif event.type == KEYDOWN:
                if event.key == K_w and not direction == 0:
                    direction = 2
                elif event.key == K_a and not direction == 1:
                    direction = 3
                elif event.key == K_s and not direction == 2:
                    direction = 0
                elif event.key == K_d and not direction == 3:
                    direction = 1

for _ in range(10):  # Ejecutar el juego 100 veces
    print("Episodio: ", episode+1)
    run_game()
    score = 0
    episode = episode + 1

min = min(max_score)
max = max(max_score)
print("Puntajes:", max_score)
mean_score = (sum(max_score)/len(max_score))
print("Media: ", mean_score)
print("Menor: ", min)
print("Mayor: ", max)
plt.plot(range(1, len(max_score) + 1), max_score)
plt.plot(mean_score)
plt.xlabel("Juego")
plt.ylabel("Puntaje")
plt.title("Puntajes obtenidos en cada juego")
plt.show()
