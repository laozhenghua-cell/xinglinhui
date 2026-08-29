<template>
  <div class="auth-shell">
    <!-- 左侧品牌区 -->
    <div class="brand-panel">
      <div class="brand-inner">
        <div class="brand-logo">
          <img src="/favicon.svg" alt="logo" />
          <span>华夏痔瘘诊疗系统</span>
        </div>

        <div class="brand-hero">
          <h1>传承岐黄 · 精准辨证</h1>
          <p class="brand-tagline">
            基于中医六十年临床经验<br />打造的中医肛肠智能诊疗平台
          </p>
        </div>

        <ul class="brand-features">
          <li>
            <span class="feature-dot"></span>
            <div>
              <strong>四诊合参</strong>
              <p>望闻问切，一键辨证</p>
            </div>
          </li>
          <li>
            <span class="feature-dot"></span>
            <div>
              <strong>辨证论治</strong>
              <p>证型 · 治则 · 方药，精准对应</p>
            </div>
          </li>
          <li>
            <span class="feature-dot"></span>
            <div>
              <strong>内外同治</strong>
              <p>内服 · 外治 · 针刺手术，一应俱全</p>
            </div>
          </li>
        </ul>

        <div class="brand-foot">
          © {{ year }} 华夏痔瘘辅助诊疗系统 · 传承不守旧，创新不离宗
        </div>
      </div>
    </div>

    <!-- 右侧表单区 -->
    <div class="form-panel">
      <div class="form-card">
        <div class="mode-switch">
          <button
            :class="['mode-btn', { active: isLogin }]"
            @click="switchMode(true)"
          >登录</button>
          <button
            :class="['mode-btn', { active: !isLogin }]"
            @click="switchMode(false)"
          >注册</button>
        </div>

        <div class="form-heading">
          <h2>{{ isLogin ? '欢迎回来' : '创建诊所账号' }}</h2>
          <p>{{ isLogin ? '登录以继续您的诊疗工作' : '注册后即可开始使用，30 天免费试用' }}</p>
        </div>

        <!-- 登录表单 -->
        <el-form
          v-if="isLogin"
          ref="formRef"
          :model="form"
          :rules="rules"
          size="large"
          @keyup.enter="handleLogin"
        >
          <el-form-item prop="email">
            <el-input
              v-model="form.email"
              placeholder="邮箱"
              :prefix-icon="Message"
              clearable
            />
          </el-form-item>
          <el-form-item prop="password">
            <el-input
              v-model="form.password"
              type="password"
              placeholder="密码"
              :prefix-icon="Lock"
              show-password
            />
          </el-form-item>
          <el-button
            type="primary"
            size="large"
            class="submit-btn"
            :loading="loading"
            @click="handleLogin"
          >
            登 录
          </el-button>
        </el-form>

        <!-- 注册表单 -->
        <el-form
          v-else
          ref="registerFormRef"
          :model="registerForm"
          :rules="registerRules"
          size="large"
          @keyup.enter="handleRegister"
        >
          <el-form-item prop="name">
            <el-input v-model="registerForm.name" placeholder="医生姓名" :prefix-icon="User" />
          </el-form-item>
          <el-form-item prop="email">
            <el-input v-model="registerForm.email" placeholder="邮箱" :prefix-icon="Message" />
          </el-form-item>
          <el-form-item prop="clinic_name">
            <el-input v-model="registerForm.clinic_name" placeholder="诊所 / 机构名称" :prefix-icon="OfficeBuilding" />
          </el-form-item>
          <el-form-item prop="password">
            <el-input
              v-model="registerForm.password"
              type="password"
              placeholder="密码（至少 6 位）"
              :prefix-icon="Lock"
              show-password
            />
          </el-form-item>
          <el-button
            type="primary"
            size="large"
            class="submit-btn"
            :loading="registerLoading"
            @click="handleRegister"
          >
            注册并开始使用
          </el-button>
        </el-form>

        <p class="form-foot">
          {{ isLogin ? '登录即代表您同意相关服务条款' : '注册即开通 30 天全功能试用' }}
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { Message, Lock, User, OfficeBuilding } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import { register } from '@/api/auth'
import { ElMessage } from 'element-plus'

const router = useRouter()
const authStore = useAuthStore()

const isLogin = ref(true)
const formRef = ref(null)
const registerFormRef = ref(null)
const loading = ref(false)
const registerLoading = ref(false)
const year = new Date().getFullYear()

const form = reactive({ email: '', password: '' })
const registerForm = reactive({ name: '', email: '', password: '', clinic_name: '' })

const rules = {
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' },
  ],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

const registerRules = {
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于 6 位', trigger: 'blur' },
  ],
  clinic_name: [{ required: true, message: '请输入诊所名称', trigger: 'blur' }],
}

function switchMode(login) {
  isLogin.value = login
}

async function handleLogin() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  loading.value = true
  try {
    await authStore.login(form)
    ElMessage.success('登录成功，欢迎回来')
  } catch (e) {
    // 拦截器已处理错误提示
  } finally {
    loading.value = false
  }
}

async function handleRegister() {
  const valid = await registerFormRef.value.validate().catch(() => false)
  if (!valid) return
  registerLoading.value = true
  try {
    const res = await register(registerForm)
    // 后端注册即返回 token，自动登录
    authStore.setAuth(res.access_token, res.user)
    ElMessage.success('注册成功，已自动登录')
    router.push('/dashboard')
  } catch (e) {
    // 拦截器已处理错误提示
  } finally {
    registerLoading.value = false
  }
}
</script>

<style scoped>
.auth-shell {
  display: flex;
  min-height: 100vh;
  background: #f4f1ea;
  font-family: 'PingFang SC', 'Microsoft YaHei', 'Helvetica Neue', sans-serif;
}

/* ============ 左侧品牌区 ============ */
.brand-panel {
  flex: 1 1 46%;
  position: relative;
  background:
    radial-gradient(1200px 600px at -10% -10%, rgba(201, 168, 106, 0.18), transparent 60%),
    radial-gradient(900px 500px at 110% 110%, rgba(38, 90, 72, 0.35), transparent 55%),
    linear-gradient(160deg, #12352a 0%, #0d2820 55%, #081c16 100%);
  color: #efe9dc;
  display: flex;
  align-items: center;
  overflow: hidden;
}

.brand-panel::after {
  content: '';
  position: absolute;
  inset: 0;
  background-image: repeating-linear-gradient(
    45deg,
    rgba(255, 255, 255, 0.015) 0,
    rgba(255, 255, 255, 0.015) 1px,
    transparent 1px,
    transparent 8px
  );
  pointer-events: none;
}

.brand-inner {
  position: relative;
  z-index: 1;
  width: 100%;
  max-width: 460px;
  margin-left: clamp(32px, 8vw, 120px);
  padding: 48px 24px;
}

.brand-logo {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 72px;
}
.brand-logo img {
  width: 44px;
  height: 44px;
}
.brand-logo span {
  font-size: 20px;
  font-weight: 600;
  letter-spacing: 2px;
  color: #efe9dc;
}

.brand-hero h1 {
  font-size: clamp(28px, 3vw, 40px);
  font-weight: 700;
  letter-spacing: 3px;
  margin: 0 0 20px;
  color: #f5efe2;
}
.brand-tagline {
  font-size: 16px;
  line-height: 1.9;
  color: rgba(239, 233, 220, 0.72);
  margin: 0 0 56px;
}

.brand-features {
  list-style: none;
  padding: 0;
  margin: 0 0 72px;
}
.brand-features li {
  display: flex;
  gap: 16px;
  margin-bottom: 28px;
}
.feature-dot {
  flex: none;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #c9a86a;
  margin-top: 7px;
  box-shadow: 0 0 0 4px rgba(201, 168, 106, 0.18);
}
.brand-features strong {
  display: block;
  font-size: 15px;
  color: #f5efe2;
  letter-spacing: 1px;
  margin-bottom: 4px;
}
.brand-features p {
  margin: 0;
  font-size: 13px;
  color: rgba(239, 233, 220, 0.6);
}

.brand-foot {
  font-size: 12px;
  color: rgba(239, 233, 220, 0.4);
  letter-spacing: 1px;
}

/* ============ 右侧表单区 ============ */
.form-panel {
  flex: 1 1 54%;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 32px;
}

.form-card {
  width: 100%;
  max-width: 400px;
}

.mode-switch {
  display: flex;
  background: #eae5da;
  border-radius: 12px;
  padding: 5px;
  margin-bottom: 40px;
}
.mode-btn {
  flex: 1;
  padding: 10px 0;
  border: none;
  background: transparent;
  border-radius: 9px;
  font-size: 15px;
  color: #7a7468;
  cursor: pointer;
  transition: all 0.25s;
  letter-spacing: 2px;
}
.mode-btn.active {
  background: #fff;
  color: #12352a;
  font-weight: 600;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.form-heading {
  margin-bottom: 32px;
}
.form-heading h2 {
  font-size: 26px;
  font-weight: 700;
  color: #1c2b26;
  margin: 0 0 8px;
}
.form-heading p {
  font-size: 14px;
  color: #9a9387;
  margin: 0;
}

:deep(.el-input__wrapper) {
  background: #fff;
  border-radius: 10px;
  box-shadow: 0 0 0 1px #e3ded2 inset;
  padding: 4px 14px;
  transition: box-shadow 0.25s;
}
:deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px #c9a86a inset;
}
:deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 2px #12352a inset;
}

.submit-btn {
  width: 100%;
  height: 48px;
  border-radius: 10px;
  font-size: 16px;
  letter-spacing: 6px;
  background: #12352a;
  border-color: #12352a;
  margin-top: 8px;
  transition: all 0.25s;
}
.submit-btn:hover {
  background: #1b4a3a;
  border-color: #1b4a3a;
  box-shadow: 0 8px 20px rgba(18, 53, 42, 0.25);
}

.form-foot {
  text-align: center;
  font-size: 12px;
  color: #b0a99c;
  margin-top: 32px;
}

/* ============ 响应式 ============ */
@media (max-width: 900px) {
  .brand-panel {
    display: none;
  }
  .form-panel {
    flex: 1 1 100%;
  }
}
</style>
