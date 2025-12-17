<!-- src/components/GameArea.vue -->
<template>
  <div class="game-area" :class="{'active': isActive}">
    <div class="area-header">
      <h2 class="area-title">{{ title }}</h2>
      <div class="health-bar">
        <span class="health-label">血量: </span>
        <div class="health-points">
          <span 
            v-for="i in 5" 
            :key="i" 
            class="health-point"
            :class="{ 'active': i <= health }"
          >
            ❤️
          </span>
        </div>
      </div>
    </div>
    
    <div class="area-content">
      <!-- 当前出牌区域 -->
      <div class="current-card" v-if="currentCard">
        <div class="card current">
          <div class="card-header">{{ currentCard.type }}</div>
          <div class="card-body">{{ currentCard.name }}</div>
          <div class="card-desc">{{ currentCard.desc }}</div>
        </div>
      </div>
      <div class="current-card empty" v-else>
        <div class="empty-text">暂未出牌</div>
      </div>
      
      <!-- 手牌区域 -->
      <div class="hand-cards">
        <div 
          v-for="(card, index) in cards" 
          :key="card.id || index"
          class="hand-card"
          :class="{ 'selected': playerType === 'player' && selectedIndex === index }"
          @click="playerType === 'player' && $emit('card-click', index)"
        >
          <div v-if="card.back" class="card-back">🃏</div>
          <div v-else class="card">
            <div class="card-header">{{ card.type }}</div>
            <div class="card-body">{{ card.name }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { defineProps, defineEmits, ref } from 'vue'

interface Card {
  id?: string | number
  type?: string
  name?: string
  desc?: string
  back?: boolean
}

interface Props {
  title: string
  playerType: 'player' | 'ai'
  health: number
  cards: Card[]
  currentCard?: Card | null
  isActive: boolean
}

const props = defineProps<Props>()
const emit = defineEmits<{
  'card-click': [index: number]
}>()

const selectedIndex = ref(-1)

// 当玩家点击卡片时触发
const handleCardClick = (index: number) => {
  if (props.playerType === 'player') {
    selectedIndex.value = index
    emit('card-click', index)
  }
}
</script>

<style scoped>
.game-area {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 15px;
  padding: 20px;
  border: 2px solid transparent;
  transition: all 0.3s ease;
  min-height: 250px;
}

.game-area.active {
  border-color: #4CAF50;
  box-shadow: 0 0 20px rgba(76, 175, 80, 0.3);
}

.area-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.area-title {
  margin: 0;
  font-size: 1.5rem;
  color: #FFD700;
}

.health-bar {
  display: flex;
  align-items: center;
  gap: 10px;
}

.health-label {
  font-size: 0.9rem;
  opacity: 0.8;
}

.health-points {
  display: flex;
  gap: 5px;
}

.health-point {
  font-size: 1.2rem;
  opacity: 0.3;
  transition: all 0.3s ease;
}

.health-point.active {
  opacity: 1;
  transform: scale(1.2);
  filter: drop-shadow(0 0 3px rgba(255, 0, 0, 0.5));
}

.area-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.current-card {
  display: flex;
  justify-content: center;
}

.card {
  background: linear-gradient(135deg, #667eea, #764ba2);
  border-radius: 10px;
  padding: 15px;
  min-width: 150px;
  text-align: center;
  color: white;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
  border: 2px solid rgba(255, 255, 255, 0.2);
}

.card.current {
  background: linear-gradient(135deg, #4CAF50, #2E7D32);
  transform: scale(1.05);
}

.card-header {
  font-size: 0.9rem;
  opacity: 0.9;
  margin-bottom: 5px;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.card-body {
  font-size: 1.3rem;
  font-weight: bold;
  margin: 10px 0;
}

.card-desc {
  font-size: 0.8rem;
  opacity: 0.8;
  margin-top: 5px;
}

.current-card.empty {
  height: 100px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.empty-text {
  color: rgba(255, 255, 255, 0.5);
  font-style: italic;
}

.hand-cards {
  display: flex;
  justify-content: center;
  gap: 15px;
  flex-wrap: wrap;
}

.hand-card {
  cursor: pointer;
  transition: all 0.3s ease;
}

.hand-card:hover {
  transform: translateY(-5px);
}

.hand-card.selected {
  transform: translateY(-10px);
  filter: drop-shadow(0 5px 15px rgba(255, 255, 255, 0.3));
}

.card-back {
  width: 80px;
  height: 120px;
  background: linear-gradient(45deg, #ff6b6b, #ff8e53);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  color: white;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  border: 2px solid rgba(255, 255, 255, 0.3);
}
</style>