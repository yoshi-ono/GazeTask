import numpy as np
#from tensorforce.environments import PyGameLearningEnvironment
from tensorforce.environments import Environment
from tensorforce.agents import Agent
from tensorforce.execution import Runner
import gaze_task


class GazeEnvironment(Environment):

    def __init__(self):
        super().__init__()

        self.task = gaze_task.GazeTask(True)

    def states(self):
        return dict(type='int', shape=(10,))

    def actions(self):
        return dict(type='int', num_values=10)

    # Optional: should only be defined if environment has a natural fixed
    # maximum episode length; otherwise specify maximum number of training
    # timesteps via Environment.create(..., max_episode_timesteps=???)
    def max_episode_timesteps(self):
        return super().max_episode_timesteps()

    # Optional additional steps to close environment
    def close(self):
        self.task.exit()
        super().close()

    def reset(self):
        self.task.reset()

        state = np.int32([0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        return state

    def execute(self, actions):
        next_state = np.random.random(size=(8,))
        terminal = False  # Always False if no "natural" terminal state
        reward = np.random.random()

        [obs_s, obs_t, reward, done] = self.task.motion(self.act_to_pos[actions])

        state = np.int32([0, 0, 0, 0, 0, 0, 0, 0, 0, 0])

        # 注視点表示
        state[9] = obs_s

        # 手掛かり刺激表示
        if (obs_t > 0):
            state[obs_t] = 2

        return state, done, reward


environment = Environment.create(
    environment=GazeEnvironment, max_episode_timesteps=100
)

agent = Agent.create(
    agent='tensorforce', environment=environment, update=64,
    optimizer=dict(optimizer='adam', learning_rate=1e-3),
    objective='policy_gradient', reward_estimation=dict(horizon=20)
)

runner = Runner(
    agent=agent,
    environment=environment,
    max_episode_timesteps=500
)

runner.run(num_episodes=200)

runner.run(num_episodes=100, evaluation=True)

runner.close()