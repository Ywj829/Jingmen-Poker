import torch
import torch.optim as optim
import torch.nn as nn
import numpy as np
import random
from model import DQN


class DQNAgent:
    def __init__(self, state_dim, action_dim):
        self.action_dim = action_dim
        self.policy_net = DQN(state_dim, action_dim)
        self.target_net = DQN(state_dim, action_dim)
        self.target_net.load_state_dict(self.policy_net.state_dict())

        self.optimizer = optim.Adam(self.policy_net.parameters(), lr=0.001)
        self.loss_func = nn.MSELoss()

        self.memory = []
        self.memory_capacity = 20000

        # 探索参数
        self.epsilon = 1.0
        self.epsilon_min = 0.05
        self.epsilon_decay = 0.999

    def choose_action(self, state, heuristic=False):
        """
        heuristic=True: 开启'老师傅模式'，强制在合法动作里选
        """
        # 提取掩码 (最后20位)
        mask = state[-self.action_dim:]
        legal_actions = [i for i, m in enumerate(mask) if m == 1.0]

        # 如果没有合法动作，只能随便选(然后被罚)
        if not legal_actions:
            return random.randrange(self.action_dim)

        # 1. 探索阶段 (Random)
        if np.random.rand() <= self.epsilon:
            if heuristic:
                # 老师傅带路：只在合法里随机，保证拿正分
                return random.choice(legal_actions)
            else:
                # 瞎蒙：可能选到非法的
                return random.randrange(self.action_dim)

        # 2. 推理阶段 (Model)
        with torch.no_grad():
            state_tensor = torch.FloatTensor(state).unsqueeze(0)
            q_values = self.policy_net(state_tensor).squeeze()

            # Masking: 把非法动作Q值设为负无穷
            for i in range(self.action_dim):
                if mask[i] == 0:
                    q_values[i] = -float('inf')

            return torch.argmax(q_values).item()

    # (store_transition, learn, update_target_network 保持不变)
    def store_transition(self, s, a, r, ns, d):
        if len(self.memory) >= self.memory_capacity: self.memory.pop(0)
        self.memory.append((s, a, r, ns, d))

    def learn(self, batch_size=64):
        if len(self.memory) < batch_size: return
        batch = random.sample(self.memory, batch_size)
        s, a, r, ns, d = zip(*batch)
        s = torch.FloatTensor(np.array(s))
        a = torch.LongTensor(a).unsqueeze(1)
        r = torch.FloatTensor(r).unsqueeze(1)
        ns = torch.FloatTensor(np.array(ns))
        d = torch.FloatTensor(d).unsqueeze(1)

        q_eval = self.policy_net(s).gather(1, a)
        with torch.no_grad():
            q_next = self.target_net(ns).max(1)[0].unsqueeze(1)
            q_target = r + (0.95 * q_next * (1 - d))

        loss = self.loss_func(q_eval, q_target)
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

        if self.epsilon > self.epsilon_min: self.epsilon *= self.epsilon_decay

    def update_target_network(self):
        self.target_net.load_state_dict(self.policy_net.state_dict())