import torch
import os
import sys
import numpy as np

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from env.game_env import 京门奕环境
from agent import DQNAgent


def train():
    env = 京门奕环境()
    agent = DQNAgent(env.状态维度, env.动作数量)

    EPISODES = 2000
    best_reward = -float('inf')
    recent_rewards = []

    print(f"🚀 开始训练 (维度:{env.状态维度})...")

    for episode in range(EPISODES):
        state = env.reset()
        total_reward = 0
        done = False

        # 前 800 局开启'老师傅模式'：强制只选合法动作，让AI体验赢的感觉
        use_heuristic = (episode < 800)

        while not done:
            action = agent.choose_action(state, heuristic=use_heuristic)
            next_state, reward, done, _ = env.step(action)

            agent.store_transition(state, action, reward, next_state, done)
            agent.learn()

            state = next_state
            total_reward += reward

            if len(agent.memory) > 5000 and total_reward < -200: done = True  # 早停

        recent_rewards.append(total_reward)
        if len(recent_rewards) > 50: recent_rewards.pop(0)
        avg = np.mean(recent_rewards)

        if avg > best_reward and episode > 100:
            best_reward = avg
            torch.save(agent.policy_net.state_dict(), "best_model.pth")
            print(f"🌟 新高分: {best_reward:.2f}")

        if episode % 10 == 0:
            agent.update_target_network()

        if (episode + 1) % 100 == 0:
            print(f"📊 回合 {episode + 1}: 平均分 {avg:.2f} | Epsilon {agent.epsilon:.2f}")


if __name__ == "__main__":
    train()