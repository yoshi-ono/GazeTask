import pygame
import math
import numpy as np
import gym
from tensorflow.keras.models import Sequential,load_model
from tensorflow.keras.layers import Dense,Flatten
from tensorflow.keras.optimizers import Adam
from rl.memory import SequentialMemory
from rl.policy import BoltzmannQPolicy
from rl.agents.dqn import DQNAgent
import gaze_task

class GazeEnv(gym.Env):
    def __init__(self):
        self.task = gaze_task.GazeTask()

        self.action_space = gym.spaces.Discrete(10)
        self.observation_space = gym.spaces.Box(low=np.int32([0, 0]),high=np.int32([9, 2]))
        self.reward_range = (-1,10)

        self.act_to_pos = { 0: (0, 0),
                            1: (110, 110), 2: (330, 110), 3: (550, 110),
                            4: (110, 330), 5: (550, 330),
                            6: (110, 550), 7: (330, 550), 8: (550, 550),
                            9: (330, 330) }

    def reset(self):
        self.task.reset()

        self.observation = np.int32([0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        return self.observation

    def render(self, mode):
        self.task.draw()

    def step(self, act):
        [obs_s, obs_t, reward, done] = self.task.motion(self.act_to_pos[act])

        for index in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]:
            self.observation[index] = 0

        # 注視点表示
        self.observation[9] = obs_s

        # 手掛かり刺激表示
        if (obs_t > 0):
            self.observation[obs_t] = 2

        return self.observation,np.float32(reward),done,{}

    def close(self):
        self.task.exit()

env = GazeEnv()
env.reset()

reinforcement_learning = False

if (reinforcement_learning):
    model = Sequential([Flatten(input_shape=(1, 10)),
                        Dense(16,activation='relu'),
                        Dense(16,activation='relu'),
                        Dense(16,activation='relu'),
                        Dense(10,activation='linear')])
else:
    model = load_model('game_20220816')                                                     #保存したモデルを呼び出す時に使用する

memory = SequentialMemory(limit=50000, window_length=1)
policy = BoltzmannQPolicy()
dqn = DQNAgent(model=model,nb_actions=10,gamma=0.99,memory=memory,nb_steps_warmup=100,target_model_update=1e-2,policy=policy)
dqn.compile(Adam(lr=1e-3), metrics=['mae'])

if (reinforcement_learning):
    dqn.fit(env,nb_steps=100000,visualize=True,verbose=1)                           #visualize=Falseにすれば、画面描写をしなくなる
    dqn.model.save('game',overwrite=True)

dqn.test(env,nb_episodes=10,visualize=True)
