import random
import numpy as np
from game import SnakeGameAI, Direction, Point
from helper import plot

# learning rate 
LR = 0.1

class Agent:

    def __init__(self):
        self.episodes = 10000
        self.n_games = 0
        self.epsilon = 0.98 # randomness
        self.epsilon_discount = 0.97
        #0.97 early
        #0.997 late
        self.gamma = 1.0 # discount rate
        self.table = np.zeros((2,2,2,2,2,2,2,2,2,2,2,3))
        #self.table = np.random.rand(2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 3) * 0.01

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

    def get_action(self, state):
        #self.epsilon = 40 - self.n_games
        final_move = [0,0,0]
        index = 0
        # exploration
        if random.random() < self.epsilon:
            #print("tome exploración")
            index = random.randint(0,2)
            final_move[index] = 1
            
        # exploitation
        else:
           # print("tome explotación")
            index = np.argmax(self.table[state])

            #print("argumento recibido: ", index)
            #print("valor",max(self.table[state]))
            #print(self.table[state][index])
            #print(self.table[state])
            #print("1 ",self.table[state][0] )
            #print("2 ",self.table[state][1] )
            #print("3 ",self.table[state][2] )

            final_move[index] = 1

        return final_move,index

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
        final_move,idx = agent.get_action(state_old)
       
        # recibimos información del paso
        reward, done, score = game.play_step(final_move)
    
        # obtenemos la información del nuevo ciclo
        state_new = agent.get_state(game)
    
        

        # Bellman Equation Update
        # accedemos al indice de la acción utilizada
       # print("valor antiguo qtable", agent.table[state_old][idx])
        agent.table[state_old][idx] = (1 - LR)\
                    * agent.table[state_old][idx] + LR\
                    * (reward + agent.gamma * max(agent.table[state_new])) 
        #print("valor nuevo qtable", agent.table[state_old][idx])
       # print("demas valores", agent.table[state_old])

        #print(" ")

        #agent.table[state_old][idx] += LR * (reward + (agent.gamma * max(agent.table[state_new])) - agent.table[state_old][idx]) 
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