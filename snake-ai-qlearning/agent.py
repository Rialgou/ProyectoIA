import random
import numpy as np
from game import SnakeGameAI, Direction, Point
from helper import plot

# learning rate 
LR = 0.01

class Agent:

    def __init__(self):
        self.n_games = 0
        self.epsilon = 1.0 # randomness
        self.epsilon_discount = 0.9992
        self.gamma = 0.95 # discount rate
        self.table = np.zeros((2,2,2,2,2,2,2,2,2,2,2,3))

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
            (dir_r and game.is_collision(point_r)) or 
            (dir_l and game.is_collision(point_l)) or 
            (dir_u and game.is_collision(point_u)) or 
            (dir_d and game.is_collision(point_d)),

            # Danger right
            (dir_u and game.is_collision(point_r)) or 
            (dir_d and game.is_collision(point_l)) or 
            (dir_l and game.is_collision(point_u)) or 
            (dir_r and game.is_collision(point_d)),

            # Danger left
            (dir_d and game.is_collision(point_r)) or 
            (dir_u and game.is_collision(point_l)) or 
            (dir_r and game.is_collision(point_u)) or 
            (dir_l and game.is_collision(point_d)),
            
            # Move direction
            dir_l,
            dir_r,
            dir_u,
            dir_d,
            
            # Food location 
            game.food.x < game.head.x,  # food left
            game.food.x > game.head.x,  # food right
            game.food.y < game.head.y,  # food up
            game.food.y > game.head.y  # food down
            ]

        return tuple(map(int,state))


        self.trainer.train_step(state, action, reward, next_state, done)

    def get_action(self, state):
        #self.epsilon = 40 - self.n_games
        final_move = [0,0,0]
        # exploration
        if random.random() < self.epsilon:
            move = random.randint(0,2)
            final_move[move] = 1
        #if random.randint(0, 200) < self.epsilon:
         #   move = random.randint(0, 2)
          #  final_move[move] = 1
        # exploitation
        else:
            move = np.argmax(self.table[state])
            final_move[move] = 1
        self.epsilon = max(self.epsilon * self.epsilon_discount, 0.001)
        return final_move


def train():
    plot_scores = []
    plot_mean_scores = []
    total_score = 0
    record = 0
    agent = Agent()
    game = SnakeGameAI()
    while True:
        # get old state
        state_old = agent.get_state(game)
        #print(state_old)
        # get move
        final_move = agent.get_action(state_old)
        
        # perform move and get new state
        reward, done, score = game.play_step(final_move)
        state_new = agent.get_state(game)

        # Bellman Equation Update
        agent.table[state_old][final_move] = (1 - LR) * agent.table[state_old][final_move] + LR * (reward + agent.gamma * max(agent.table[state_new]))
        if done:
            # train long memory, plot result
            game.reset()
            agent.n_games += 1

            if score > record:
                record = score

            print('Game', agent.n_games, 'Score', score, 'Record:', record)

            plot_scores.append(score)
            total_score += score
            mean_score = total_score / agent.n_games
            plot_mean_scores.append(mean_score)
            plot(plot_scores, plot_mean_scores)


if __name__ == '__main__':
    train()