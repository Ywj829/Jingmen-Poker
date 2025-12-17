import torch
import os
import sys

# 确保能找到 env 包
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from model import DQN
from env.game_env import 京门奕环境


def export():
    # 1. 动态获取最新环境参数
    env = 京门奕环境()
    state_dim = env.状态维度  # 应该是 280
    action_dim = env.动作数量  # 应该是 20

    print(f"⚙️ 环境参数: 输入维度={state_dim}, 输出动作数={action_dim}")

    # 2. 加载模型结构
    model = DQN(state_dim, action_dim)

    # 3. 加载训练好的参数
    model_path = "best_model.pth"
    if not os.path.exists(model_path):
        print(f"❌ 错误：找不到文件 {model_path}")
        return

    model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))
    model.eval()

    # 4. 虚拟输入 (维度必须是 280)
    dummy_input = torch.randn(1, state_dim, requires_grad=True)

    # 5. 导出路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(current_dir))
    output_path = os.path.join(project_root, "fronted", "public", "jingmenyi.onnx")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    torch.onnx.export(
        model,
        dummy_input,
        output_path,
        export_params=True,
        opset_version=11,
        do_constant_folding=True,
        input_names=['input'],
        output_names=['output'],
        dynamic_axes={'input': {0: 'batch_size'}, 'output': {0: 'batch_size'}}
    )

    print(f"🎉 模型已更新并导出到: {output_path}")


if __name__ == "__main__":
    export()