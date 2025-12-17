import * as ort from 'onnxruntime-web';

// 类型映射
const TYPE_MAP: Record<string, number> = {
    '行当': 0,
    '扮相': 1,
    '砌末': 2,
    '唱词': 3
};

// 角色ID映射 (必须和 game_env.py 一致)
const ROLE_MAP: Record<string, number> = {
    '魏虎': 0, '薛平贵': 1, '王宝钏': 2, '王允': 3,
    '苏龙': 4, '王母': 5, '金钏银钏': 6
};

export class GameAI {
    private session: ort.InferenceSession | null = null;
    // === 关键修改：维度升级为 280 ===
    private stateDim = 280;
    // === 关键修改：手牌上限 20 ===
    private maxHandSize = 20;

    async init() {
        try {
            ort.env.wasm.wasmPaths = "https://cdn.jsdelivr.net/npm/onnxruntime-web/dist/";
            this.session = await ort.InferenceSession.create('./jingmenyi.onnx');
            console.log("✅ AI 模型加载成功 (Dimension: 280)");
            return true;
        } catch (e) {
            console.error("❌ AI 模型加载失败:", e);
            return false;
        }
    }

    async predict(
        aiHealth: number,
        playerHealth: number,
        aiSafeCards: number,
        aiHand: any[],
        playedCards: any[]
    ): Promise<number> {
        if (!this.session) {
            return Math.floor(Math.random() * aiHand.length);
        }

        try {
            const inputData = new Float32Array(this.stateDim).fill(0);

            // 1. 全局信息
            inputData[0] = aiHealth / 5.0;
            inputData[1] = playerHealth / 5.0;
            inputData[2] = aiSafeCards / 3.0;

            // 2. 编码手牌 (循环 20 次)
            for (let i = 0; i < Math.min(aiHand.length, this.maxHandSize); i++) {
                const card = aiHand[i];
                const baseIdx = 3 + i * 12; // 3, 15, 27...

                // 类型
                const typeVal = TYPE_MAP[card.type] ?? -1;
                if (typeVal >= 0) inputData[baseIdx + typeVal] = 1.0;

                // 角色
                // 行当牌可能没有 ref_role 或者是通用的，需要防御性编程
                const roleName = card.ref_role || card.name;
                const roleId = ROLE_MAP[roleName] ?? 7;
                if (roleId < 7) inputData[baseIdx + 4 + roleId] = 1.0;
            }

            // 3. 编码上一张出牌
            if (playedCards.length > 0) {
                const last = playedCards[playedCards.length - 1];
                const baseIdx = 3 + this.maxHandSize * 12; // 3 + 240 = 243

                const typeVal = TYPE_MAP[last.type] ?? -1;
                if (typeVal >= 0) inputData[baseIdx + typeVal] = 1.0;

                const roleName = last.ref_role || last.name;
                const roleId = ROLE_MAP[roleName] ?? 7;
                if (roleId < 7) inputData[baseIdx + 4 + roleId] = 1.0;
            }

            // 4. Action Mask (20位)
            // 简单全开，允许AI尝试所有手牌位置
            const maskBase = 3 + this.maxHandSize * 12 + 12; // 243 + 12 = 255
            for(let i=0; i<this.maxHandSize; i++) {
                inputData[maskBase + i] = 1.0;
            }

            // 推理
            const tensor = new ort.Tensor('float32', inputData, [1, this.stateDim]);
            const results = await this.session.run({ input: tensor });
            const output = results.output.data as Float32Array;

            // Argmax
            let maxScore = -Infinity;
            let bestAction = 0;
            // 只在实际手牌范围内寻找最大值
            for (let i = 0; i < aiHand.length; i++) {
                if (output[i] > maxScore) {
                    maxScore = output[i];
                    bestAction = i;
                }
            }

            console.log(`🤖 AI 决策: 索引 ${bestAction}/${aiHand.length}, 得分 ${maxScore}`);
            return bestAction;

        } catch (e) {
            console.error("AI 推理出错:", e);
            return 0;
        }
    }
}