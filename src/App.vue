<template>
  <div class="game-container">
    <!-- 1. 全局背景图 -->
    <div class="game-bg"></div>

    <!-- === 场景 1: 开始封面 === -->
    <transition name="fade">
      <div v-if="!isGameStarted" class="start-screen">
        <div class="start-content">
          <h1 class="main-title">京门奕</h1>
          <button class="btn-start" @click="handleStartGame">
            <span>开始对决</span>
          </button>
        </div>
      </div>
    </transition>

    <!-- === 场景 2: 游戏主界面 === -->
    <transition name="fade">
      <div v-if="isGameStarted" class="game-interface">

        <!-- 顶部：AI 区域 -->
        <div class="top-hud">
          <div class="player-info ai">
            <div class="avatar-frame">
              <img src="../assets/avatar_ai.png" @error="useDefaultAvatar" alt="AI" />
            </div>
            <div class="info-content">
              <div class="name-tag">AI 对手</div>
              <div class="bars">
                <div class="hp-bar">
                  <span v-for="n in 5" :key="n" class="dot" :class="{ 'active': n <= aiHealth }"></span>
                </div>
                <div class="shield-bar">
                  <span v-for="n in 3" :key="n" class="shield-icon" :class="{ 'active': n <= aiSafeCards }">🛡️</span>
                </div>
              </div>
            </div>
          </div>

          <!-- AI 手牌 (倒扇形) -->
          <div class="ai-hand-container">
            <div class="fan-wrapper ai-fan">
              <div
                v-for="(card, index) in aiCards"
                :key="index"
                class="fan-card ai-card"
                :style="getFanStyle(index, aiCards.length, true)"
              >
                <!-- 牌背图片 -->
                <img src="../assets/card_back.png" class="card-img-back" @error="useDefaultBack" />
              </div>
            </div>
          </div>

          <!-- AI 出牌展示气泡 -->
          <transition name="pop">
            <div v-if="aiMessage" class="ai-bubble">
              {{ aiMessage }}
            </div>
          </transition>
        </div>

        <!-- 中央战场：卡槽区域 (绝对居中) -->
        <div class="battle-field">

          <!-- 4个固定槽位 -->
          <div class="card-slots">
            <!-- 循环渲染4个槽位 -->
            <div
              v-for="(slotName, idx) in ['行当', '扮相', '砌末', '唱词']"
              :key="idx"
              class="slot-group"
            >
              <div class="slot-container">
                <!-- 已填入的卡牌 -->
                <div v-if="tableSlots[idx]" class="slot-card filled">
                  <img :src="getCardImage(tableSlots[idx])" class="card-img-face" @error="useDefaultCard" />
                  <div class="card-text-overlay">{{ tableSlots[idx].name }}</div>
                </div>
                <!-- 空槽位虚线框 -->
                <div v-else class="slot-placeholder" :class="{ 'active': nextNeededType === slotName }">
                  <span class="placeholder-text">{{ slotName }}</span>
                </div>
              </div>
              <!-- 连接线 (除了最后一个) -->
              <div v-if="idx < 3" class="connector" :class="{ 'active': tableSlots[idx] }"></div>
            </div>
          </div>

          <!-- 状态提示文字 -->
          <div class="status-tips">
            <div class="tip-text" :class="{ 'warn': isWarning }">{{ message || currentHint }}</div>
          </div>
        </div>

        <!-- 底部：玩家区域 -->
        <div class="bottom-hud">

          <!-- 左下角：护驾令牌 -->
          <div class="token-area">
            <div class="token-box">
              <div class="token-label">护驾令</div>
              <div class="tokens-row">
                <div v-for="n in 3" :key="n" class="token-item" :class="{ 'lost': n > playerSafeCards }">
                  <img src="../assets/token.png" @error="useDefaultToken" />
                </div>
              </div>
            </div>
          </div>

          <!-- 右下角：玩家信息 -->
          <div class="player-info player">
            <div class="info-content right-align">
              <div class="name-tag">玩家</div>
              <div class="bars">
                <div class="hp-bar">
                  <span v-for="n in 5" :key="n" class="dot player-dot" :class="{ 'active': n <= playerHealth }"></span>
                </div>
              </div>
            </div>
            <div class="avatar-frame">
              <img src="../assets/avatar_player.png" @error="useDefaultAvatar" alt="Player" />
            </div>
          </div>

          <!-- 核心：玩家扇形手牌 -->
          <div class="hand-container">
            <div class="fan-wrapper">
              <div
                v-for="(card, index) in playerCards"
                :key="card.unique_id"
                class="fan-card"
                :class="{
                  'playable': isCardHighlight(card),
                  'selected': selectedCardIndex === index,
                  'disabled': !isCardHighlight(card) || isAiTurn
                }"
                :style="getFanStyle(index, playerCards.length, false)"
                @click="handleCardClick(index)"
              >
                <div class="card-visual">
                  <!-- 卡牌图片 -->
                  <img :src="getCardImage(card)" class="card-img-face" @error="useDefaultCard" />

                  <!-- 兜底文字 (如果没有图片显示这个) -->
                  <div class="card-text-fallback">
                    <div class="c-type">{{ card.type }}</div>
                    <div class="c-name">{{ card.name }}</div>
                  </div>

                  <!-- 遮罩 (不可选时变灰) -->
                  <div class="disabled-mask" v-if="!isCardHighlight(card) || isAiTurn"></div>
                </div>
              </div>
            </div>
          </div>

          <!-- 出牌按钮 (选中牌后出现) -->
          <transition name="fade">
            <div v-if="selectedCardIndex !== -1 && !isAiTurn" class="play-btn-container">
              <button class="btn-play" @click="confirmPlayCard">出牌</button>
            </div>
          </transition>

        </div>

        <!-- 结算弹窗 -->
        <div v-if="gameOver" class="modal-overlay">
          <div class="modal">
            <h2>{{ winner === 'player' ? '🎉 胜利' : '💀 失败' }}</h2>
            <button class="btn-retry" @click="initGame">再来一局</button>
          </div>
        </div>

      </div>
    </transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { GameAI } from './ai/OnnxModel'

const brain = new GameAI();

// === 1. 配置数据 ===
const ROLE_CONFIG: any = {
  '魏虎': { type: '净', items: ['奏折', '令牌'], skills: ['诬告', '威慑'] },
  '薛平贵': { type: '生', items: ['马鞭', '宝剑'], skills: ['劈扫', '绕刺'] },
  '王宝钏': { type: '旦', items: ['状纸', '水袖'], skills: ['诉冤', '抛掷'] },
  '王允': { type: '生', items: ['文墨', '折扇', '玉如意'], skills: ['权谋', '掩面', '威慑'] },
  '苏龙': { type: '生', items: ['铁笔', '奏折'], skills: ['直谏', '上书'] },
  '王母': { type: '旦', items: ['佛珠', '蒲团'], skills: ['持念', '稳坐'] },
  '金钏银钏': { type: '旦', items: ['团扇'], skills: ['半掩'] }
};

// === 2. 状态变量 ===
const isGameStarted = ref(false);
const aiHealth = ref(5), playerHealth = ref(5);
const aiSafeCards = ref(3), playerSafeCards = ref(3);
const playerCards = ref<any[]>([]), aiCards = ref<any[]>([]);
const tableSlots = ref<any[]>([null, null, null, null]);

const isAiTurn = ref(false);
const message = ref('');
const isWarning = ref(false);
const aiMessage = ref('');
const gameOver = ref(false);
const winner = ref('');
const selectedCardIndex = ref(-1);

// === 3. 计算属性 & 提示 ===
const nextNeededType = computed(() => {
  if (!tableSlots.value[0]) return '行当';
  if (!tableSlots.value[1]) return '扮相';
  if (!tableSlots.value[2]) return '砌末';
  if (!tableSlots.value[3]) return '唱词';
  return '结算';
});

const currentHint = computed(() => {
  if (isAiTurn.value) return '对方回合...';
  if (nextNeededType.value === '行当') return '请出【行当】牌';
  if (nextNeededType.value === '扮相') return `需出【${tableSlots.value[0].name}】对应的【扮相】`;
  if (nextNeededType.value === '砌末') return `需出【${tableSlots.value[1].name}】的【砌末】`;
  if (nextNeededType.value === '唱词') return `需出【${tableSlots.value[1].name}】的【唱词】`;
  return '';
});

// === 4. 资源加载辅助 ===
function getCardImage(card: any) {
  // 对应文件: public/assets/行当_生.png
  return `../assets/卡牌合集/${card.type}_${card.name}.png`;
}
// 兜底图片处理 (如果没图，也不要裂开)
function useDefaultCard(e: Event) { (e.target as HTMLImageElement).style.opacity = '0'; }
function useDefaultAvatar(e: Event) { (e.target as HTMLImageElement).src = 'https://placehold.co/100x100?text=Avatar'; }
function useDefaultBack(e: Event) { (e.target as HTMLImageElement).src = 'https://placehold.co/100x150?text=Card'; }
function useDefaultToken(e: Event) { (e.target as HTMLImageElement).src = 'https://placehold.co/50x50?text=令'; }

// === 5. 游戏逻辑 ===
function generateFullDeck() {
  const deck = [];
  let id = 0;
  for (const [role, data] of Object.entries(ROLE_CONFIG)) {
    for (let i=0; i<3; i++) deck.push({ id: id++, type: '行当', name: data.type, ref_role: role });
    for (let i=0; i<3; i++) deck.push({ id: id++, type: '扮相', name: role, ref_role: role });
    for (let i=0; i<4; i++) {
        const item = data.items[i % data.items.length];
        deck.push({ id: id++, type: '砌末', name: item, ref_role: role });
    }
    for (let i=0; i<4; i++) {
        const skill = data.skills[i % data.skills.length];
        deck.push({ id: id++, type: '唱词', name: skill, ref_role: role });
    }
  }
  return deck;
}
const FULL_DECK = generateFullDeck();

function drawCard(targetType?: string) {
  let pool = targetType ? FULL_DECK.filter(c => c.type === targetType) : FULL_DECK;
  const t = pool[Math.floor(Math.random() * pool.length)];
  return { ...t, unique_id: Math.random().toString(36).substr(2, 9) };
}

function handleStartGame() { isGameStarted.value = true; initGame(); }

function initGame() {
  aiHealth.value = 5; playerHealth.value = 5;
  aiSafeCards.value = 3; playerSafeCards.value = 3;
  playerCards.value = []; aiCards.value = [];
  tableSlots.value = [null, null, null, null];
  isAiTurn.value = false; gameOver.value = false; selectedCardIndex.value = -1;

  const deal = (hand: any[]) => {
    for(let i=0; i<3; i++) hand.push(drawCard('行当'));
    for(let i=0; i<3; i++) hand.push(drawCard('扮相'));
    for(let i=0; i<4; i++) hand.push(drawCard('砌末'));
    for(let i=0; i<4; i++) hand.push(drawCard('唱词'));
    sortHand(hand);
  };
  deal(playerCards.value);
  deal(aiCards.value);
}

function sortHand(hand: any[]) {
  const order = ['行当', '扮相', '砌末', '唱词'];
  hand.sort((a,b) => order.indexOf(a.type) - order.indexOf(b.type));
}

function replenish(hand: any[]) {
  ['行当', '扮相', '砌末', '唱词'].forEach(t => {
    if (hand.filter(c => c.type === t).length < 2) {
      hand.push(drawCard(t));
      hand.push(drawCard(t));
    }
  });
  sortHand(hand);
}

// === 6. 交互逻辑 (改进) ===

// 判断是否高亮 (只判断类型，不判断具体对错，让玩家自己选)
function isCardHighlight(card: any): boolean {
  return card.type === nextNeededType.value;
}

// 点击卡牌：选中并弹出
function handleCardClick(index: number) {
  if (isAiTurn.value) return;
  const card = playerCards.value[index];

  if (!isCardHighlight(card)) {
    // 如果点了灰色的牌，提示一下
    showWarn(`当前阶段需出【${nextNeededType.value}】牌`);
    return;
  }

  // 选中逻辑
  if (selectedCardIndex.value === index) {
    // 如果已经选中，再点一次不做操作，等待点击"出牌"按钮
    // 或者设计成双击出牌
  } else {
    selectedCardIndex.value = index;
  }
}

// 确认出牌
function confirmPlayCard() {
  if (selectedCardIndex.value === -1) return;

  const card = { ...playerCards.value[selectedCardIndex.value] };

  // 规则校验
  if (checkRule(card)) {
    // 合法
    const slotIdx = tableSlots.value.findIndex(s => s === null);
    if (slotIdx !== -1) {
      tableSlots.value[slotIdx] = card;
      playerCards.value.splice(selectedCardIndex.value, 1);
      replenish(playerCards.value);
      selectedCardIndex.value = -1;

      // 检查连招
      if (slotIdx === 3) {
        finishRound();
      } else {
        isAiTurn.value = true;
        setTimeout(aiPlay, 1000);
      }
    }
  } else {
    // 违规
    applyPenalty(false);
    playerCards.value.splice(selectedCardIndex.value, 1);
    replenish(playerCards.value);
    selectedCardIndex.value = -1;

    if (!gameOver.value) {
      isAiTurn.value = true;
      setTimeout(aiPlay, 1000);
    }
  }
}

// 规则裁判
function checkRule(card: any): boolean {
  if (card.type !== nextNeededType.value) return false;

  if (nextNeededType.value === '扮相') {
    const target = tableSlots.value[0];
    const config = ROLE_CONFIG[card.name];
    return config && config.type === target.name;
  }

  if (nextNeededType.value === '砌末' || nextNeededType.value === '唱词') {
    const target = tableSlots.value[1]; // 扮相
    return card.ref_role === target.name;
  }
  return true;
}

function applyPenalty(isAi: boolean) {
  const who = isAi ? 'AI' : '你';
  let hasShield = isAi ? aiSafeCards.value > 0 : playerSafeCards.value > 0;

  if (hasShield) {
    if (isAi) aiSafeCards.value--; else playerSafeCards.value--;
    showWarn(`${who}出牌错误，扣除护驾牌！`);
  } else {
    if (isAi) aiHealth.value--; else playerHealth.value--;
    showWarn(`${who}出牌错误，扣除血量！`);
    setTimeout(() => resetTable(), 1500);
  }
  checkGameOver();
}

function finishRound() {
  aiSafeCards.value = 3; playerSafeCards.value = 3;
  showMessage("✨ 连招完成！");
  setTimeout(() => resetTable(), 1500);
}

function resetTable() {
  tableSlots.value = [null, null, null, null];
  isAiTurn.value = false; // 玩家先手
}

function checkGameOver() {
  if (aiHealth.value <= 0) { gameOver.value = true; winner.value = 'player'; }
  if (playerHealth.value <= 0) { gameOver.value = true; winner.value = 'ai'; }
}

// === 7. AI ===
async function aiPlay() {
  const history = tableSlots.value.filter(c => c !== null);
  let actionIdx = await brain.predict(
    aiHealth.value, playerHealth.value, aiSafeCards.value,
    aiCards.value, history
  );

  if (actionIdx >= aiCards.value.length) actionIdx = 0;
  const cardToPlay = aiCards.value[actionIdx];

  // AI 行为展示
  if (!checkRule(cardToPlay)) {
    aiMessage.value = `违规: ${cardToPlay.name}`;
    setTimeout(() => aiMessage.value = '', 2000);
    applyPenalty(true);
    aiCards.value.splice(actionIdx, 1);
    replenish(aiCards.value);
    // 违规后轮到玩家
    if (!gameOver.value) isAiTurn.value = false;
    return;
  }

  // 合法出牌
  const slotIdx = tableSlots.value.findIndex(s => s === null);
  if (slotIdx !== -1) {
    tableSlots.value[slotIdx] = cardToPlay;
    aiCards.value.splice(actionIdx, 1);
    replenish(aiCards.value);

    if (slotIdx === 3) {
      finishRound();
    } else {
      isAiTurn.value = false;
    }
  }
}

// === 8. UI 辅助 ===
function showMessage(msg: string) { message.value = msg; isWarning.value = false; setTimeout(() => message.value = '', 3000); }
function showWarn(msg: string) { message.value = msg; isWarning.value = true; setTimeout(() => message.value = '', 3000); }

// 扇形算法
function getFanStyle(index: number, total: number, isOpponent: boolean) {
  if (total === 0) return {};
  const step = 4; // 角度
  const mid = (total - 1) / 2;
  const offset = index - mid;
  const rotate = offset * step;

  // 调大间距，让牌不那么挤
  const xSpacing = 40;
  const xOffset = offset * xSpacing;

  // 弧度
  let yOffset = Math.abs(offset) * 10;
  if (isOpponent) yOffset = Math.abs(offset) * 6; // AI弧度小一点

  return {
    transform: `translateX(${xOffset}px) translateY(${yOffset}px) rotate(${rotate}deg)`,
    zIndex: index + 10, // 基础 z-index
    transformOrigin: isOpponent ? 'top center' : 'bottom center'
  };
}

onMounted(async () => {
  await brain.init();
});
</script>

<style scoped>
/* 全局设定 */
.game-container {
  width: 100vw; height: 100vh; overflow: hidden;
  background-color: #000;
  font-family: "Microsoft YaHei", sans-serif;
  user-select: none;
}

/* 背景图: 替换 url(...) */
.game-bg {
  position: absolute; width: 100%; height: 100%;
  background: url('../assets/界面UI/对决UI.jpg') no-repeat center center;
  background-size: cover;
  opacity: 0.6; /* 稍微暗一点 */
}

/* 1. 开始封面 */
.start-screen {
  position: absolute; z-index: 100; width: 100%; height: 100%;
  background: rgba(0,0,0,0.8); display: flex; justify-content: center; align-items: center;
}
.main-title {
  font-size: 80px; color: #ffd700; font-family: "KaiTi"; letter-spacing: 10px;
  text-shadow: 0 0 20px #c0392b; margin-bottom: 40px;
}
.btn-start {
  padding: 15px 60px; font-size: 24px; border: 2px solid #ffd700;
  background: #c0392b; color: #fff; border-radius: 50px; cursor: pointer;
  transition: 0.3s;
}
.btn-start:hover { transform: scale(1.1); background: #e74c3c; }

/* 2. 主界面 */
.game-interface { position: relative; width: 100%; height: 100%; }

/* AI 区域 (顶部) */
.top-hud {
  position: absolute; top: 0; width: 100%; height: 200px;
  display: flex; justify-content: center; pointer-events: none;
}
.player-info {
  position: absolute; top: 20px; z-index: 20;
  display: flex; align-items: center; gap: 10px;
  background: rgba(0,0,0,0.6); padding: 5px 20px; border-radius: 30px; border: 1px solid #666;
}
.player-info.ai { left: 40px; }
.player-info.player { right: 40px; bottom: 40px; top: auto; pointer-events: auto; }

.avatar-frame img { width: 50px; height: 50px; border-radius: 50%; border: 2px solid #ffd700; }
.info-content { color: #fff; }
.name-tag { font-size: 14px; font-weight: bold; margin-bottom: 2px; }
.bars { display: flex; flex-direction: column; gap: 4px; }
.dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; background: #333; margin-right: 2px; border: 1px solid #666; }
.dot.active { background: #ff4757; border-color: #ff4757; box-shadow: 0 0 5px #ff4757; }
.shield-icon { font-size: 12px; opacity: 0.2; }
.shield-icon.active { opacity: 1; text-shadow: 0 0 5px gold; }

/* AI 手牌 */
.ai-hand-container { position: absolute; top: -30px; left: 50%; transform: translateX(-50%); }
.fan-wrapper.ai-fan { height: 100px; }
.fan-card.ai-card {
  width: 90px; height: 140px; border-radius: 8px;
  background: #c0392b; border: 2px solid #fff;
  transform-origin: top center; box-shadow: 0 5px 15px rgba(0,0,0,0.5);
}
.card-img-back { width: 100%; height: 100%; object-fit: cover; border-radius: 6px; }
.ai-bubble {
  position: absolute; top: 120px; left: 50%; transform: translateX(-50%);
  background: #fff; color: #000; padding: 5px 15px; border-radius: 20px; font-weight: bold;
}

/* 3. 中央战场 (卡槽) */
.battle-field {
  position: absolute; top: 50%; left: 50%; transform: translate(-50%, -60%);
  display: flex; flex-direction: column; align-items: center; pointer-events: none;
}
.card-slots { display: flex; align-items: center; }
.slot-group { display: flex; align-items: center; }
.slot-container {
  width: 110px; height: 160px;
  display: flex; justify-content: center; align-items: center;
}
.slot-placeholder {
  width: 100px; height: 150px; border: 2px dashed rgba(255,255,255,0.3);
  border-radius: 8px; display: flex; justify-content: center; align-items: center;
  color: rgba(255,255,255,0.5); font-size: 16px; transition: 0.3s;
}
.slot-placeholder.active {
  border-color: #ffd700; background: rgba(255, 215, 0, 0.1);
  color: #ffd700; transform: scale(1.05); box-shadow: 0 0 20px rgba(255,215,0,0.2);
}
.slot-card { width: 100px; height: 150px; position: relative; animation: dropIn 0.3s ease-out; }
.card-img-face { width: 100%; height: 100%; border-radius: 8px; object-fit: cover; border: 2px solid #ddd; }
.card-text-overlay {
  position: absolute; bottom: 0; width: 100%; background: rgba(0,0,0,0.6);
  color: #fff; font-size: 14px; text-align: center; padding: 2px 0;
  border-bottom-left-radius: 6px; border-bottom-right-radius: 6px;
}
.connector {
  width: 30px; height: 3px; background: rgba(255,255,255,0.2); margin: 0 5px;
}
.connector.active { background: #ffd700; box-shadow: 0 0 10px #ffd700; }

.status-tips { margin-top: 20px; height: 30px; }
.tip-text { font-size: 18px; color: #ffd700; text-shadow: 0 2px 4px rgba(0,0,0,0.5); }
.tip-text.warn { color: #ff4757; }

/* 4. 底部 HUD */
.bottom-hud {
  position: absolute; bottom: 0; width: 100%; height: 300px;
  pointer-events: none; /* 让鼠标穿透空白处 */
}

/* 护驾令牌 */
.token-area {
  position: absolute; left: 40px; bottom: 40px; pointer-events: auto;
}
.token-box {
  background: rgba(0,0,0,0.6); padding: 10px; border-radius: 10px; border: 1px solid #555;
}
.token-label { font-size: 12px; color: #aaa; margin-bottom: 5px; text-align: center; }
.tokens-row { display: flex; gap: 5px; }
.token-item img { width: 30px; height: 40px; }
.token-item.lost { opacity: 0.3; filter: grayscale(1); }

/* 玩家手牌 (大尺寸扇形) */
.hand-container {
  position: absolute; bottom: -60px; left: 50%; transform: translateX(-50%);
  width: 100%; display: flex; justify-content: center;
  z-index: 50;
}
.fan-wrapper {
  position: relative; height: 250px; display: flex; justify-content: center;
  pointer-events: auto;
}
.fan-card {
  position: absolute; bottom: 0;
  width: 130px; height: 190px; /* 大尺寸 */
  transform-origin: bottom center;
  transition: transform 0.2s, bottom 0.2s;
  cursor: pointer;
}
/* 卡牌视觉 */
.card-visual {
  width: 100%; height: 100%; background: #fff;
  border-radius: 10px; position: relative; overflow: hidden;
  box-shadow: -5px 0 15px rgba(0,0,0,0.5); border: 1px solid #aaa;
}
.card-text-fallback {
  width: 100%; height: 100%; display: flex; flex-direction: column;
  justify-content: center; align-items: center; color: #333;
}
.c-type { font-size: 12px; color: #888; margin-bottom: 10px; }
.c-name { font-size: 24px; font-weight: bold; font-family: "KaiTi"; }

/* 状态样式 */
.fan-card.playable .card-visual { border: 2px solid #ffd700; box-shadow: 0 0 15px rgba(255,215,0,0.4); }
/* 悬停微动 */
.fan-card.playable:hover { bottom: 20px !important; z-index: 100 !important; }
/* 选中状态 (明显弹出) */
.fan-card.selected { bottom: 60px !important; z-index: 200 !important; transform: scale(1.1) !important; }
.disabled-mask { position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.65); }

/* 出牌按钮 */
.play-btn-container {
  position: absolute; bottom: 260px; left: 50%; transform: translateX(-50%);
  pointer-events: auto; z-index: 300;
}
.btn-play {
  padding: 10px 40px; font-size: 18px; border-radius: 30px; border: none;
  background: #2ecc71; color: #fff; font-weight: bold; cursor: pointer;
  box-shadow: 0 5px 15px rgba(46,204,113,0.4);
}
.btn-play:hover { transform: scale(1.05); }

/* 动画与弹窗 */
.modal-overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.9); z-index: 999; display: flex; justify-content: center; align-items: center; }
.modal { background: #fff; padding: 40px; border-radius: 10px; text-align: center; color: #000; }
.btn-retry { padding: 10px 30px; background: #3498db; color: #fff; border: none; cursor: pointer; margin-top: 20px; }
@keyframes dropIn { from { opacity: 0; transform: scale(1.5); } to { opacity: 1; transform: scale(1); } }
.fade-enter-active, .fade-leave-active { transition: opacity 0.5s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>