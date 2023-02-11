from tensorforce import Agent
from tensorforce.environments import OpenAIGym
from gaze_env_wm0 import GazeEnvWM0 as GazeEnv

def main():
    environment = OpenAIGym.create(environment=GazeEnv, max_episode_timesteps=500, visualize=True)
    #environment = wrappers.Monitor(environment, 'tmp', force=True)

    agent = Agent.create(agent='configs/ppo.json', environment=environment)
    #agent = Agent.create(agent='tensorforce', environment=environment)

    # Train for 100 episodes
    for episode in range(100):

        # Episode using act and observe
        states = environment.reset()
        terminal = False
        sum_rewards = 0.0
        num_updates = 0
        while not terminal:
            actions = agent.act(states=states)
            states, terminal, reward = environment.execute(actions=actions)
            num_updates += agent.observe(terminal=terminal, reward=reward)
            sum_rewards += reward
        print('Train Episode {}: return={} updates={}'.format(episode, sum_rewards, num_updates))

    # Evaluate for 100 episodes
    total_rewards = 0.0
    environment.visualize = True
    for evaluate in range(100):
        states = environment.reset()
        internals = agent.initial_internals()
        terminal = False
        sum_rewards = 0.0
        while not terminal:
            actions, internals = agent.act(
                states=states, internals=internals, independent=True, deterministic=True
            )
            states, terminal, reward = environment.execute(actions=actions)
            sum_rewards += reward
        print('Evaluate Episode {}: return={}'.format(evaluate, sum_rewards))
        total_rewards += sum_rewards

    print('Mean evaluation return:', total_rewards / 100.0)

    # Close agent and environment
    agent.close()
    environment.close()


if __name__ == '__main__':
    main()
