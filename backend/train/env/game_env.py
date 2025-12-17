import numpy as np
import random
from typing import Dict, List


class 京门奕环境:
    def __init__(self):
        self.剧目配置 = {
            '算粮': {
                '角色': {
                    '魏虎': ('净', ['奏折', '令牌'], ['诬告', '威慑']),
                    '薛平贵': ('生', ['马鞭', '宝剑'], ['劈扫', '绕刺']),
                    '王宝钏': ('旦', ['状纸', '水袖'], ['诉冤', '抛掷']),
                    '王允': ('生', ['文墨', '折扇', '玉如意'], ['权谋', '掩面', '威慑']),
                    '苏龙': ('生', ['铁笔', '奏折'], ['直谏', '上书']),
                    '王母': ('旦', ['佛珠', '蒲团'], ['持念', '稳坐']),
                    '金钏银钏': ('旦', ['团扇'], ['半掩'])
                }
            }
        }
        self.角色列表 = list(self.剧目配置['算粮']['角色'].keys())
        self.角色ID表 = {name: i for i, name in enumerate(self.角色列表)}

        self.最大手牌数 = 20
        self.动作数量 = self.最大手牌数

        # === 维度修正 ===
        # 3(全局) + 240(手牌) + 12(场上) + 20(掩码) = 275
        self.状态维度 = 275

        self.reset()

    def reset(self):
        self.当前剧目 = '算粮'
        self.卡牌数据库 = self._生成完整卡牌库(self.当前剧目)

        self.state = {
            'AI血量': 5, '玩家血量': 5,
            'AI护驾牌': 3, '玩家护驾牌': 3,
            'AI手牌': [], '玩家手牌': [],
            '出牌堆': [], '游戏结束': False
        }
        self._检查并补牌('AI', 初始模式=True)
        self._检查并补牌('玩家', 初始模式=True)
        return self._获取观察()

    def step(self, action_idx):
        self._整理手牌('AI')
        hand = self.state['AI手牌']

        # 1. 越界检查
        if action_idx >= len(hand) or action_idx < 0:
            return self._获取观察(), -10, False, {'msg': '索引越界'}

        card_played = hand[action_idx]
        last_card = self.state['出牌堆'][-1] if self.state['出牌堆'] else None

        # 2. 规则判定
        is_legal = self._检查出牌规则(card_played, last_card)
        reward = 0
        done = False

        hand.pop(action_idx)

        if not is_legal:
            # 非法出牌
            reward = -10  # 稍微降低惩罚，别直接扣死
            if self.state['AI护驾牌'] > 0:
                self.state['AI护驾牌'] -= 1
            else:
                self.state['AI血量'] -= 1
        else:
            # 合法出牌
            reward = 5
            self.state['出牌堆'].append(card_played)

            # 连招奖励
            combo_len = self._计算连招长度(self.state['出牌堆'])
            if combo_len == 2:
                reward += 10
            elif combo_len == 3:
                reward += 20
            elif combo_len == 4:
                reward += 50
                self.state['玩家血量'] -= 2

            # 模拟玩家
            if self.state['玩家血量'] > 0:
                self._模拟玩家出牌()

        # 3. 补牌与结束
        self._检查并补牌('AI')
        self._检查并补牌('玩家')

        if self.state['AI血量'] <= 0:
            done = True;
            reward -= 30
        elif self.state['玩家血量'] <= 0:
            done = True;
            reward += 100

        if len(self.state['AI手牌']) == 0:
            self._从库里抽牌(self.state['AI手牌'], '行当')

        return self._获取观察(), reward, done, {}

    def _获取观察(self):
        obs = np.zeros(self.状态维度, dtype=np.float32)

        # 1. 全局 (0-2)
        obs[0] = self.state['AI血量'] / 5.0
        obs[1] = self.state['玩家血量'] / 5.0
        obs[2] = self.state['AI护驾牌'] / 3.0

        type_map = {'行当': 0, '扮相': 1, '砌末': 2, '唱词': 3}

        # 2. 手牌 (3-242)
        for i, card in enumerate(self.state['AI手牌'][:self.最大手牌数]):
            base_idx = 3 + i * 12
            t_val = type_map.get(card['type'], 0)
            obs[base_idx + t_val] = 1.0
            r_id = self.角色ID表.get(card.get('ref_role', ''), 7)
            if r_id < 7: obs[base_idx + 4 + r_id] = 1.0

        # 3. 场上牌 (243-254)
        last_ref = None
        base_last = 3 + self.最大手牌数 * 12
        if self.state['出牌堆']:
            last = self.state['出牌堆'][-1]
            last_ref = last
            t_val = type_map.get(last['type'], 0)
            obs[base_last + t_val] = 1.0
            r_name = last.get('ref_role', '')
            if last['type'] == '扮相': r_name = last['name']
            r_id = self.角色ID表.get(r_name, 7)
            if r_id < 7: obs[base_last + 4 + r_id] = 1.0

        # 4. 掩码 (255-274) - 必须紧跟在最后！
        mask_base = base_last + 12
        for i, card in enumerate(self.state['AI手牌'][:self.最大手牌数]):
            if self._检查出牌规则(card, last_ref):
                obs[mask_base + i] = 1.0
            else:
                obs[mask_base + i] = 0.0

        return obs

    # --- 辅助函数保持不变 ---
    def _检查出牌规则(self, card, last_card):
        if last_card is None: return card['type'] == '行当'
        if last_card['type'] == '行当':
            return card['type'] == '扮相' and self.剧目配置[self.当前剧目]['角色'][card['name']][0] == last_card['name']
        if last_card['type'] == '扮相':
            return card['type'] == '砌末' and card['ref_role'] == last_card['name']
        if last_card['type'] == '砌末':
            return card['type'] == '唱词' and card['ref_role'] == last_card['ref_role']
        if last_card['type'] == '唱词':
            return card['type'] == '行当'
        return False

    def _整理手牌(self, who):
        order = {'行当': 0, '扮相': 1, '砌末': 2, '唱词': 3}
        self.state[f'{who}手牌'].sort(key=lambda x: order.get(x['type'], 99))

    def _计算连招长度(self, stack):
        if not stack: return 0
        last = stack[-1]
        if len(stack) >= 2 and last['type'] == '扮相' and stack[-2]['type'] == '行当': return 2
        if len(stack) >= 3 and last['type'] == '砌末' and stack[-2]['type'] == '扮相': return 3
        if len(stack) >= 4 and last['type'] == '唱词' and stack[-2]['type'] == '砌末': return 4
        return 1

    def _检查并补牌(self, who, 初始模式=False):
        hand = self.state[f'{who}手牌']
        if 初始模式:
            while len([c for c in hand if c['type'] in ['行当', '扮相']]) < 3: self._从库里抽牌(hand, ['行当', '扮相'])
            while len(hand) < 7: self._从库里抽牌(hand, ['砌末', '唱词'])
            return
        for t in ['行当', '扮相', '砌末', '唱词']:
            if len([c for c in hand if c['type'] == t]) < 2:
                self._从库里抽牌(hand, t);
                self._从库里抽牌(hand, t)

    def _从库里抽牌(self, hand_list, target_type):
        if target_type:
            cands = [c for c in self.卡牌数据库 if
                     c['type'] in (target_type if isinstance(target_type, list) else [target_type])]
        else:
            cands = self.卡牌数据库
        if cands:
            c = random.choice(cands).copy()
            c['uid'] = random.random()
            hand_list.append(c)

    def _模拟玩家出牌(self):
        hand = self.state['玩家手牌']
        last = self.state['出牌堆'][-1]
        legal = [i for i, c in enumerate(hand) if self._检查出牌规则(c, last)]
        if legal:
            self.state['出牌堆'].append(hand.pop(random.choice(legal)))
        else:
            self.state['玩家血量'] -= 1
            self.state['出牌堆'] = []

    def _生成完整卡牌库(self, 剧目):
        config = self.剧目配置[剧目]['角色']
        cards = [];
        gid = 0
        for r, (t, its, sks) in config.items():
            for _ in range(3): cards.append({'id': gid, 'type': '行当', 'name': t, 'ref_role': r}); gid += 1
            for _ in range(3): cards.append({'id': gid, 'type': '扮相', 'name': r, 'ref_role': r}); gid += 1
            for i in its: cards.append({'id': gid, 'type': '砌末', 'name': i, 'ref_role': r}); gid += 1
            for s in sks: cards.append({'id': gid, 'type': '唱词', 'name': s, 'ref_role': r}); gid += 1
        return cards


if __name__ == "__main__":
    env = 京门奕环境()
    print("环境修复完成！维度:", env.状态维度)