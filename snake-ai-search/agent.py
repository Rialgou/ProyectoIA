import random
import heapq
import numpy as np
from game import SnakeGameAI, Direction, Point, BLOCK_SIZE
from helper import plot

# learning rate 
LR = 0.1

class Agent:

    def __init__(self):
        #episodes a 1 si quieren un juego normal, si quieren ir viendo las variaciones 
        #setean más

        self.episodes = 10000
        self.n_games = 0
        #self.epsilon = 0.98 # randomness
        #self.epsilon_discount = 0.97
        #0.97 early
        #0.997 late
        #self.gamma = 1.0 # discount rate
        #self.table = np.zeros((2,2,2,2,2,2,2,2,2,2,2,3))
        #self.table = np.random.rand(2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 3) * 0.01
    
    #queda igual
    def get_state(self, game):
        head = game.snake[0]
        point_l = Point(head.x - 20, head.y)
        point_r = Point(head.x + 20, head.y)
        point_u = Point(head.x, head.y - 20)
        point_d = Point(head.x, head.y + 20)
        
        dir_l = game.direction == Direction.LEFT
        dir_r = game.direction == Direction.RIGHT
        dir_u = game.direction == Direction.UP
        dir_d = game.direction == Direction.DOWN

        state = [
            # Danger straight
            int((dir_r and game.is_collision(point_r))) or 
            int((dir_l and game.is_collision(point_l))) or 
            int((dir_u and game.is_collision(point_u))) or 
            int((dir_d and game.is_collision(point_d))),

            # Danger right
            int((dir_u and game.is_collision(point_r))) or 
            int((dir_d and game.is_collision(point_l))) or 
            int((dir_l and game.is_collision(point_u))) or 
            int((dir_r and game.is_collision(point_d))),

            # Danger left
            int((dir_d and game.is_collision(point_r))) or 
            int((dir_u and game.is_collision(point_l))) or 
            int((dir_r and game.is_collision(point_u))) or 
            int((dir_l and game.is_collision(point_d))),
            
            # Move direction
            int(dir_l),
            int(dir_r),
            int(dir_u),
            int(dir_d),
            
            # Food location 
            int(game.food.x < game.head.x),  # food left
            int(game.food.x > game.head.x),  # food right
            int(game.food.y < game.head.y),  # food up
            int(game.food.y > game.head.y)  # food down
            ]

        return tuple(state)

    #aqui deberia ir la logica de la búsqueda según yo 
    #al final se eligira la acción en base a las condiciones dadas
    #aunque para el tema del greedy quizas estaria mejor editar un poco el flujo
    #tener dos instancias del juego para poder hacer ese recorrido a la fruta antes de elegir la acción real
    def greedy_search(self, state, game):
        #chatGPTEADO XD
        # Step 1: Compute the shortest path P1 from S1's head to the food
        path_to_food = game.shortest_path_to_food()

        if path_to_food:
            # Step 2: Move a virtual snake S2 to eat the food along path P1
            s_copy = game.snake.copy()
            s_copy.move_path(path_to_food)

            # Step 3: Compute the longest path P2 from S2's head to its tail
            path_to_tail = s_copy.longest_path_to_tail()

            if path_to_tail:
                # Step 4: Compute the longest path P3 from S1's head to its tail
                path_to_tail_original = game.longest_path_to_tail()

                if path_to_tail_original:
                    # Let D be the first direction in path P3
                    direction = path_to_tail_original[0]
                else:
                    # Go to step 5: Let D be the direction that makes S1 the farthest from the food
                    head = game.snake.head()
                    max_dist = -1
                    direction = game.snake.direc

                    for adj in head.all_adj():
                        if game.map.is_safe(adj):
                            dist = Point.manhattan_dist(adj, game.map.food)
                            if dist > max_dist:
                                max_dist = dist
                                direction = head.direc_to(adj)
            else:
                # Go to step 4: Let D be the first direction in path P1
                direction = path_to_food[0]
        else:
            # Go to step 5: Let D be the direction that makes S1 the farthest from the food
            head = game.snake.head()
            max_dist = -1
            direction = game.snake.direc

            for adj in head.all_adj():
                if game.map.is_safe(adj):
                    dist = Point.manhattan_dist(adj, game.map.food)
                    if dist > max_dist:
                        max_dist = dist
                        direction = head.direc_to(adj)

        return direction
       #REVISAR
    
    def heuristic(self, p1, p2):
        return abs(p1.x - p2.x) + abs(p1.y - p2.y)
         #REVISAR

    def a_star_search(self, game, start, goal):
        # Crea un diccionario para almacenar los costos de movimiento g(x) desde el inicio hasta cada posición.
        g = {}
        # Crea una cola de prioridad para almacenar los nodos a explorar.
        open_list = []
        # Crea un diccionario para almacenar los nodos padres.
        parents = {}

        # Inicializa los costos g(x) del inicio como 0.
        g[start] = 0
        # Calcula la distancia heurística h(x) desde el inicio hasta el objetivo.
        h = self.heuristic(Point(*start), Point(*goal))
        # Calcula el valor de f(x) para el inicio.
        f = g[start] + h
        # Agrega el inicio a la cola de prioridad con prioridad f(x).
        heapq.heappush(open_list, (f, start))

        # Mientras la cola de prioridad no esté vacía.
        while open_list:
            # Obtiene el nodo actual de la cola de prioridad.
            current = heapq.heappop(open_list)[1]

            # Si se alcanza el objetivo, reconstruye la ruta y la devuelve.
            if current == goal:
                path = []
                while current in parents:
                    path.append(current)
                    current = parents[current]
                return path[::-1]  # Invierte la ruta encontrada.

            # Genera los vecinos del nodo actual.
            for direction in [Direction.RIGHT, Direction.LEFT, Direction.UP, Direction.DOWN]:
                if direction == Direction.RIGHT:
                    neighbor = (current[0] + BLOCK_SIZE, current[1])
                elif direction == Direction.LEFT:
                    neighbor = (current[0] - BLOCK_SIZE, current[1])
                elif direction == Direction.UP:
                    neighbor = (current[0], current[1] - BLOCK_SIZE)
                elif direction == Direction.DOWN:
                    neighbor = (current[0], current[1] + BLOCK_SIZE)

                # Calcula el nuevo costo g(x) del vecino.
                new_g = g[current] + 1

                # Si el vecino ya fue visitado con un costo menor, ignóralo.
                if neighbor in g and new_g >= g[neighbor]:
                    continue

                # Almacena el nuevo costo g(x) y el nodo padre del vecino.
                g[neighbor] = new_g
                parents[neighbor] = current

                # Calcula la distancia heurística h(x) desde el vecino hasta el objetivo.
                h = self.heuristic(Point(*neighbor), Point(*goal))
                # Calcula el valor de f(x) para el vecino.
                f = new_g + h

                # Agrega el vecino a la cola de prioridad con prioridad f(x).
                heapq.heappush(open_list, (f, neighbor))

        # Si no se encuentra ninguna ruta, retorna None.
        return None
      
    def get_action(self, state, game):
        final_move = [0, 0, 0]
        path_to_food = self.shortest_path_to_food(game)
        if path_to_food:
            direction = path_to_food[0]
        else:
            direction = random.choice([Direction.RIGHT, Direction.LEFT, Direction.UP, Direction.DOWN])
        final_move[direction.value] = 1

        return final_move, direction

        #REVISAR
    def shortest_path_to_food(self, game):
        start = (game.head.x, game.head.y)
        goal = (game.food.x, game.food.y)
        path = self.a_star_search(game, start, goal)
        if path:
            return [game.head.direc_to(Point(*pos)) for pos in path]
        return None
    
        #REVISAR
    def longest_path_to_tail(self, game):
        start = (game.head.x, game.head.y)
        goal = (game.snake[-1].x, game.snake[-1].y)
        path = self.a_star_search(game, start, goal)
        if path:
            return [game.head.direc_to(Point(*pos)) for pos in path]
        return None
    
    
def train():
    plot_scores = []
    plot_mean_scores = []
    total_score = 0
    record = 0
    agent = Agent()
    game = SnakeGameAI()
    file = open('Learning.txt', 'a')
    while agent.n_games < agent.episodes:
        # get old state
        state_old = agent.get_state(game)
        #print("tabla antigua: ",agent.table[state_old])
        
        # obtenemos el movimiento y su indice
        final_move,idx = agent.get_action(state_old, game)
       
        # recibimos información del paso
        reward, done, score = game.play_step(final_move)
    
        # obtenemos la información del nuevo ciclo
        state_new = agent.get_state(game)
        final_move, idx = agent.get_action(state_new, game)
    
        

        # Bellman Equation Update
        # accedemos al indice de la acción utilizada
       # print("valor antiguo qtable", agent.table[state_old][idx])
        agent.table[state_old][idx] = (1 - LR)\
                    * agent.table[state_old][idx] + LR\
                    * (reward + agent.gamma * max(agent.table[state_new])) 
        #print("valor nuevo qtable", agent.table[state_old][idx])
       # print("demas valores", agent.table[state_old])

        #print(" ")

        #agent.table[state_old][final_move[idx]] += LR * (reward + (agent.gamma * max(agent.table[state_new])) - agent.table[state_old][final_move[idx]]) 
        if done:
            # train long memory, plot result
            game.reset()
            agent.epsilon = max(agent.epsilon * agent.epsilon_discount, 0.01)
            print(agent.epsilon)
            agent.n_games += 1

            if score > record:
                record = score

            print('Game', agent.n_games, 'Score', score, 'Record:', record)
            file.write('Game {} Score {} Record: {}\n'.format(agent.n_games, score, record))
            plot_scores.append(score)
            total_score += score
            mean_score = total_score / agent.n_games
            plot_mean_scores.append(mean_score)
            plot(plot_scores, plot_mean_scores)
    file.close()
        


if __name__ == '__main__':
    train()