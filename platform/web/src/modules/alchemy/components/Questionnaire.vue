<template>
  <div>
    <el-progress :percentage="progress" :show-text="false" style="margin-bottom:14px" />
    <div class="card" style="padding:18px">
      <div style="font-size:0.8rem;color:#9a8a6c">第 {{ cur + 1 }} / {{ steps.length }} 步{{ step.multi ? '（可多选）' : '' }}</div>
      <h3 style="color:var(--dan-ink);margin:6px 0 14px">{{ step.title }}</h3>
      <div class="pill-row" style="flex-direction:column;align-items:stretch;gap:0">
        <button v-for="o in step.options" :key="o.id"
                class="assist-opt" :class="{ on: isOn(o.id) }"
                @click="toggle(o.id)">
          <span>{{ o.label }}</span>
          <span v-if="isOn(o.id)" style="color:#fff;font-weight:700">✓</span>
        </button>
      </div>
      <div style="display:flex;justify-content:space-between;margin-top:18px;flex-wrap:wrap;gap:8px">
        <el-button :disabled="cur === 0" @click="cur--">← 上一步</el-button>
        <span>
          <el-button v-if="canSkip" text @click="next">跳过</el-button>
          <el-button type="danger" :disabled="!canNext" @click="next">
            {{ cur < steps.length - 1 ? '下一步 →' : '查看结果' }}
          </el-button>
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  steps: { type: Array, required: true },
  requiredIds: { type: Array, default: () => [] },
})
const emit = defineEmits(['complete'])

const cur = ref(0)
const answers = ref({})

const step = computed(() => props.steps[cur.value])
const progress = computed(() => Math.round((cur.value / props.steps.length) * 100))

function isOn(id) {
  return (answers.value[step.value.id] || []).includes(id)
}
function toggle(id) {
  const arr = answers.value[step.value.id] || []
  if (arr.includes(id)) {
    answers.value[step.value.id] = arr.filter((x) => x !== id)
  } else if (step.value.multi) {
    answers.value[step.value.id] = [...arr, id]
  } else {
    answers.value[step.value.id] = [id]
  }
}
const isRequired = computed(() => props.requiredIds.includes(step.value.id))
const canNext = computed(() => {
  if (isRequired.value) return (answers.value[step.value.id] || []).length > 0
  return true
})
const canSkip = computed(() => !isRequired.value)

function next() {
  if (cur.value < props.steps.length - 1) {
    cur.value++
  } else {
    emit('complete', answers.value)
  }
}
</script>

<style scoped>
.assist-opt {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  text-align: left;
  padding: 11px 14px;
  margin: 5px 0;
  border: 1px solid #d8cba8;
  border-radius: 8px;
  background: #fffdf8;
  cursor: pointer;
  font-size: 0.95rem;
  color: #5c5240;
}
.assist-opt.on {
  background: var(--dan-red);
  border-color: var(--dan-red);
  color: #fff;
}
</style>
