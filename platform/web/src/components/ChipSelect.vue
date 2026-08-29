<template>
  <div class="field-item chip-field">
    <label v-if="label">{{ label }}</label>
    <div class="chip-group">
      <span
        v-for="(opt, idx) in options"
        :key="idx"
        class="chip"
        :class="{ active: modelValue === optionValue(opt) }"
        @click="toggle(opt)"
      >
        {{ optionLabel(opt) }}
      </span>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  label: { type: String, default: '' },
  modelValue: { type: [String, Number, Boolean], default: null },
  // 支持字符串数组 或 {label, value} 对象数组
  options: { type: Array, default: () => [] },
  // 取消选中时回写的值（字符串字段默认 ''，布尔字段可传 null）
  emptyValue: { type: [String, Number, Boolean], default: '' },
})

const emit = defineEmits(['update:modelValue'])

function optionValue(opt) {
  return opt && typeof opt === 'object' && 'value' in opt ? opt.value : opt
}

function optionLabel(opt) {
  return opt && typeof opt === 'object' && 'label' in opt ? opt.label : opt
}

function toggle(opt) {
  const val = optionValue(opt)
  emit('update:modelValue', props.modelValue === val ? props.emptyValue : val)
}
</script>

<style scoped>
.chip-field {
  margin-bottom: 12px;
}
.chip-field > label {
  display: block;
  font-size: 13px;
  color: #5B6B7A;
  margin-bottom: 6px;
}
.chip-group {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.chip {
  display: inline-flex;
  align-items: center;
  padding: 4px 12px;
  border: 1px solid #D5DCE3;
  border-radius: 16px;
  font-size: 13px;
  color: #333;
  background: #fff;
  cursor: pointer;
  user-select: none;
  transition: all 0.15s;
  line-height: 1.4;
}
.chip:hover {
  border-color: #3C5A78;
  color: #3C5A78;
}
.chip.active {
  background: #3C5A78;
  border-color: #3C5A78;
  color: #fff;
  font-weight: 500;
}
</style>
