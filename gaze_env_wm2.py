import numpy as np
import gym
import threading
from gaze_task import GazeTask, F_RATE
from observation_window import ObservationWindow

class GazeEnvWM2(gym.Env):
    def __init__(self, visualize = True):
        self.obswin = ObservationWindow()
        self.thread = threading.Thread(target=self.obswin.start)
        self.thread.start()

        self.task = GazeTask(visualize)

        self.action_space = gym.spaces.Discrete(10)
        self.observation_space = gym.spaces.Box(low=0, high=2, shape=(10, 2), dtype=np.int32)
        self.reward_range = (-100,100)

        self.act_to_pos = { 0: (0, 0),
                            1: (110, 110), 2: (330, 110), 3: (550, 110),
                            4: (110, 330), 5: (550, 330),
                            6: (110, 550), 7: (330, 550), 8: (550, 550),
                            9: (330, 330) }

    def reset(self):
        self.task.reset()

        self.observation = np.zeros((10, 2), dtype=np.int32)
        return self.observation

    def render(self):
        self.task.draw()
        self.task.event_clear()

    def step(self, act):
        """
        Retuens:
            observation 座標の位置と状態
                座標の位置
                    (0)
                    ┏━━━┳━━━┳━━━┓
                    ┃ 1 ┃ 2 ┃ 3 ┃
                    ┣━━━╋━━━╋━━━┫
                    ┃ 4 ┃(9)┃ 5 ┃
                    ┣━━━╋━━━╋━━━┫
                    ┃ 6 ┃ 7 ┃ 8 ┃
                    ┗━━━┻━━━┻━━━┛
                座標の状態
                    0:表示なし
                    1:注視点表示
                    2:手掛かり刺激表示
        """
        [obs_s, obs_t, score, done, status] = self.task.motion(self.act_to_pos[act])

        for index in range(10):
            self.observation[index][0] = 0

        # 注視点表示
        self.observation[9][0] = obs_s
        if (self.observation[9][1] < obs_s):
            self.observation[9][1] = obs_s

        # 手掛かり刺激表示
        if (obs_t > 0):
            self.observation[obs_t][0] = 2
            if (self.observation[obs_t][1] < 2):
                self.observation[obs_t][1] = 2

        # 報酬
        reward = 0
        if (status == "playing"):
            reward = 1
        elif (done):
            if (status == "clear"):
                reward = score
            elif (status == "time_over"):
                reward = -5 * F_RATE
            elif (status == "look_away"):
                if (score > 0):
                    reward = score
                else:
                    reward = -1

        # 観察画面更新
        self.obswin.set_pos_color(act)
        self.obswin.value.set(reward)
        for i in range(10):
            self.obswin.pos_strvar[i].set(self.observation[i][0])
            self.obswin.wm_strvar[i].set(self.observation[i][1])

        return self.observation,np.float32(reward),done,{}

    def close(self):
        self.task.exit()

        self.swin.quit()
        self.thread.join()
