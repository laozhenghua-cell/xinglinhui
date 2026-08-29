import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { ElLoading } from 'element-plus'
import {
  ArrowDown, Box, Camera, ChatLineSquare, CircleCheck, Close, Coin,
  DataBoard, Document, DocumentChecked, DocumentCopy, EditPen, Expand,
  FirstAidKit, Fold, FolderOpened, Grape, Grid, Histogram, Lock, Lollipop,
  MagicStick, Memo, Menu, Message, Microphone, Minus, Money,
  OfficeBuilding, Operation, Plus, Pointer, Printer, Reading, Refresh,
  RefreshLeft, Search, Select, Setting, StarFilled, Switch, TrendCharts,
  TrophyBase, User, UserFilled, View, WarnTriangleFilled,
} from '@element-plus/icons-vue'

// 命令式组件/指令样式（按需引入需手动补样式）
import 'element-plus/es/components/message/style/css'
import 'element-plus/es/components/message-box/style/css'
import 'element-plus/es/components/loading/style/css'

import App from './App.vue'
import router from './router'
import './style.css'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)
app.use(ElLoading)

// 仅注册用到的图标（tree-shaking）
const icons = {
  ArrowDown, Box, Camera, ChatLineSquare, CircleCheck, Close, Coin,
  DataBoard, Document, DocumentChecked, DocumentCopy, EditPen, Expand,
  FirstAidKit, Fold, FolderOpened, Grape, Grid, Histogram, Lock, Lollipop,
  MagicStick, Memo, Menu, Message, Microphone, Minus, Money,
  OfficeBuilding, Operation, Plus, Pointer, Printer, Reading, Refresh,
  RefreshLeft, Search, Select, Setting, StarFilled, Switch, TrendCharts,
  TrophyBase, User, UserFilled, View, WarnTriangleFilled,
}
for (const [name, component] of Object.entries(icons)) {
  app.component(name, component)
}

app.mount('#app')
