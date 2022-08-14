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

        self.action_space = gym.spaces.Box(low=np.int32([0, 0, 0]),high=np.int32([3, 3, 3]))
        self.observation_space = gym.spaces.Box(low=np.int32([0, 0, 0]),high=np.int32([3, 3, 3]))
        self.reward_range = (-1,1)

        self.act_to_pos = { 0: (0, 0),
                            1: (110, 110), 2: (330, 110), 3: (550, 110),
                            4: (110, 330), 5: (550, 330),
                            6: (110, 550), 7: (330, 550), 8: (550, 550),
                            9: (330, 330) }

    def reset(self):
        self.task.reset()

        self.observation = np.int32([0, 0, 0, 0, 0, 0, 0, 0, 0])
        return self.observation

    def render(self, mode):
        self.task.draw()

    def step(self, act):
        self.task.motion(self.act_to_pos[act])

        self.observation[2] += np.float32(act*2-1)/20
        self.observation[0] += math.sin(self.observation[2])*6
        self.observation[1] -= math.cos(self.observation[2])*6
        if self.observation[0] >= 400 or self.observation[1] <= 0 or self.observation[1] >= 300 or self.observation[2] <= 0 or self.observation[2] >= math.pi:
            return self.observation,np.float32(-1),True,{}                      #失敗（画面外に出た、船が真上か真下を向いた）、reward=-1
        if (self.observation[0]-300)**2+(self.observation[1]-150)**2 <= 400:
            return self.observation,np.float32(1),True,{}                       #成功（船が地球に到着した、地球の半径20)、reward=1
        return self.observation,np.float32(0),False,{}                          #まだ飛行中、reward=0

    def close(self):
        self.task.exit()

env = GazeEnv()
env.reset()

model = Sequential([Flatten(input_shape=(1,9)),
                    Dense(16,activation='relu'),
                    Dense(16,activation='relu'),
                    Dense(16,activation='relu'),
                    Dense(9,activation='linear')])
#model = load_model('game')                                                     #保存したモデルを呼び出す時に使用する

memory = SequentialMemory(limit=50000, window_length=1)
policy = BoltzmannQPolicy()
dqn = DQNAgent(model=model,nb_actions=9,gamma=0.99,memory=memory,nb_steps_warmup=100,target_model_update=1e-2,policy=policy)
dqn.compile(Adam(lr=1e-3), metrics=['mae'])
dqn.fit(env,nb_steps=100000,visualize=True,verbose=1)                           #visualize=Falseにすれば、画面描写をしなくなる
dqn.model.save('game',overwrite=True)
dqn.test(env,nb_episodes=10,visualize=True)
