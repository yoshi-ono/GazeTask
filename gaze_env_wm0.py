import numpy as np
import gym
import threading
from gaze_task import GazeTask, F_RATE
from observation_window import ObservationWindow

class GazeEnvWM0(gym.Env):
    def __init__(self, visualize = True):
        self.obswin = ObservationWindow()
        self.thread = threading.Thread(target=self.obswin.start)
        self.thread.start()

        self.task = GazeTask(visualize)

        self.action_space = gym.spaces.Discrete(10)
        ##self.observation_space = gym.spaces.Box(low=np.int32([0, 0]),high=np.int32([9, 2]))
        self.observation_space = gym.spaces.Box(low=0, high=1, shape=(10,), dtype=np.int32)
        self.reward_range = (-100,100)

        self.act_to_pos = { 0: (0, 0),
                            1: (110, 110), 2: (330, 110), 3: (550, 110),
                            4: (110, 330), 5: (550, 330),
                            6: (110, 550), 7: (330, 550), 8: (550, 550),
                            9: (330, 330) }

    def reset(self):
        self.task.reset()

        self.observation = np.int32([0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        self.wm = 0
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
            self.observation[index] = 0

        # 注視点表示
        self.observation[9] = obs_s

        # 手掛かり刺激表示
        if (obs_t > 0):
            self.observation[obs_t] = 1

            if (self.wm == 0):
                self.wm = obs_t
        
        # WM
        if (obs_s == 0 and self.wm > 0):
            self.observation[self.wm] = 1

        # 報酬
        reward = 0
        if (status == "on_center"):
            reward = 1
        elif (status == "ready" or status == "reaction"):
            reward = -1
        elif (done):
            if (status == "clear"):
                reward = 100
            elif (status == "time_over"):
                reward = -100
            elif (status == "look_away"):
                if (score > 0):
                    reward = 50
                else:
                    reward = -1

        # 観察画面更新
        self.obswin.set_pos_color(act)
        self.obswin.label_status["text"] = status
        self.obswin.value.set(reward)
        for i in range(10):
            self.obswin.pos_strvar[i].set(self.observation[i])

        return self.observation,np.float32(reward),done,{}

    def close(self):
        self.task.exit()

        self.swin.quit()
        self.thread.join()
