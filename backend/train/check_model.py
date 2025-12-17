import torch
import numpy as np
import sys
import os

# 确保能找到 env 包
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from env.game_env import 京门奕环境
from model import DQN


def check_connection():
    print("=== 开始系统自检 ===")

    # 1. 初始化环境
    try:
        env = 京门奕环境()
        # === 修正点: 使用 reset() ===
        state = env.reset()
        print("✅ 游戏环境初始化成功")
        print(f"   初始状态维度: {state.shape}")
        print(f"   环境定义的维度: {env.状态维度}")
    except Exception as e:
        print(f"❌ 环境初始化失败: {e}")
        import traceback
        traceback.print_exc()
        return

    # 2. 初始化 AI 模型
    try:
        # 动态获取维度
        state_dim = env.状态维度
        action_dim = env.动作数量

        ai_brain = DQN(input_dim=state_dim, output_dim=action_dim)
        print(f"✅ AI 模型初始化成功 (输入:{state_dim}, 输出:{action_dim})")
    except Exception as e:
        print(f"❌ 模型初始化失败: {e}")
        return

    # 3. 尝试一次“思考”过程
    try:
        # 转为 Tensor 并增加 batch 维度
        state_tensor = torch.FloatTensor(state).unsqueeze(0)

        # 模型预测
        q_values = ai_brain(state_tensor)

        print("✅ 模型推理成功")
        print(f"   输出 Q 值形状: {q_values.shape}")

        best_action = torch.argmax(q_values).item()
        print(f"   AI 认为最好的动作 ID: {best_action}")

    except Exception as e:
        print(f"❌ 推理过程失败: {e}")
        return

    print("\n=== 自检完成：代码已修复，可以开始训练！ ===")


if __name__ == "__main__":
    check_connection()