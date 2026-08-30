# 杏林汇 · DIY 脉诊仪教程(三级递进)

> 版本 v1 · 2026-08-31
> 目的:从零手搓一台能输出脉搏波形的脉诊仪,最终把"脉率/节律/力度"标签喂给杏林汇六体系辨证(与《硬件接入方案》B 档对齐)。
> 诚实边界:①自制品是**学习与客观化辅助工具,不是医疗器械**,不得用于诊断;②PPG/单点压力设备只能可靠测**脉率、节律、力度**,浮沉滑涩需要多路压力阵列(见 L3),宁缺毋滥。

---

## 〇、原理与信号链(先懂再焊)

任何脉诊仪都是同一条信号链:

```
脉搏(桡动脉搏动)
  → 传感器(光/压力变电信号)
  → 调理电路(放大·滤波·偏置)
  → 单片机 ADC(≥100Hz 采样)
  → 上位机/浏览器(峰值检测→脉率/节律/力度→标签)
```

| 传感原理 | 能测 | 不能测 | 成本 | 难度 |
|---|---|---|---|---|
| **PPG 光电**(MAX30102) | 脉率、节律、相对波形 | 浮沉、力度、滑涩 | ~50 元 | ★ |
| **PVDF 压电薄膜**(单点压力) | + 力度、轻取重取幅度比(浮沉参考) | 寸关尺定位、滑涩 | ~150 元 | ★★ |
| **压力阵列**(3 路以上+程序加压) | 三部九候、浮中沉 | 受限于结构与标定 | 500 元+ | ★★★ |

**采样率**:波形分析 ≥100Hz;要看清重搏波切迹(滑涩参考)≥200Hz。

**安全**:所用元件均为 3.3-5V 低压,无触电风险;加压实验不超过普通血压计袖带压力(约 160mmHg),有血管疾病者勿加压。

---

## 一、L1:PPG 脉搏波形仪(1 天,~50 元)

### 1.1 材料

| 件 | 型号 | 参考价 |
|---|---|---|
| 单片机 | ESP32 DevKitC(带 CH340 串口) | ~25 元 |
| 脉搏血氧模块 | MAX30102 模块(GY-MAX30102) | ~12 元 |
| 线材 | 杜邦线(母对母 4 根)+ 面包板 | ~10 元 |
| 电源 | 手机充电器 + MicroUSB/USB-C 线 | 自备 |

### 1.2 接线(4 根线)

```
ESP32            MAX30102 模块
3V3   ──────────  VIN
GND   ──────────  GND
GPIO21(SDA) ────  SDA
GPIO22(SCL) ────  SCL
```

### 1.3 固件(Arduino IDE)

1. 装 [Arduino IDE](https://www.arduino.cc/en/software),开发板管理器装 **esp32**(by Espressif);
2. 库管理器装 **SparkFun MAX3010x Pulse and Proximity Sensor Library**;
3. 烧录下面代码(100Hz 红光波形,Serial 输出 CSV):

```cpp
// L1 脉搏波采集:ESP32 + MAX30102,100Hz,串口 CSV 输出
#include <Wire.h>
#include "MAX30105.h"
#include "heartRate.h"

MAX30105 sensor;
const uint32_t PERIOD_US = 10000UL;  // 100Hz

void setup() {
  Serial.begin(115200);
  Wire.begin(21, 22);
  if (!sensor.begin(Wire, I2C_SPEED_FAST)) {
    Serial.println("ERR:MAX30102_NOT_FOUND");
    while (1) delay(100);
  }
  // setup(亮度0x1F, 均值4, 只开红光, 采样率400, 脉宽411us, ADC 4096)
  // 400/4 = 有效 100Hz
  sensor.setup(0x1F, 4, 2, 400, 411, 4096);
}

void loop() {
  uint32_t t = micros();
  int32_t ir = sensor.getIR();
  Serial.print(millis());
  Serial.print(',');
  Serial.println(ir);
  while (micros() - t < PERIOD_US) {}
}
```

4. 手指轻按模块玻璃窗(别按死),打开**串口绘图器**(工具→串口绘图器,115200),看到规律的脉搏波形即成功。可参考开源实现 [HeartRateSPO2(ESP32/Arduino/Pico 多平台)](https://gitee.com/rainseasion/heart-rate-spo2)与 [MAX30102 开源主题](https://github.com/topics/max30102)。

### 1.4 上位机分析(Python:波形→脉率/节律→标签)

```python
# 需: pip install pyserial numpy scipy
import time
import numpy as np
from scipy.signal import find_peaks
import serial

ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)  # 端口按实际
ts, ir = [], []
t0 = time.time()
while time.time() - t0 < 30:              # 采 30 秒
    line = ser.readline().decode().strip()
    if not line or ',' not in line:
        continue
    ms, v = line.split(',')
    ts.append(int(ms) / 1000.0)
    ir.append(int(v))

x = np.array(ir, dtype=float)
x -= np.median(x)                          # 去直流漂移
pk, _ = find_peaks(x, distance=int(0.4 * 100), height=np.percentile(x, 80))
rr = np.diff(np.array(ts)[pk])             # 峰间期(秒)
bpm = 60.0 / np.mean(rr)
rr_var = np.std(rr) / np.mean(rr)          # 节律变异系数
tag = "脉数" if bpm > 90 else "脉迟" if bpm < 60 else "脉缓"
rhythm = "节律不齐(结代提示,建议进一步检查)" if rr_var > 0.15 else "节律齐"
print(f"脉率 {bpm:.1f} 次/分 | {tag} | {rhythm}")
# 输出的"脉数/脉迟/脉缓"直接就是杏林汇六体系引擎的词表标签
```

### 1.5 验收

- 波形稳定可见、峰值清晰;
- 与人工数脉搏对比,**误差 <5 次/分**(安静状态下);
- 输出标签与杏林汇辨证页手动点选一致。

---

## 二、L2:单点压力脉诊仪(1-2 周,~150 元)

**目标**:测出"力度"与"轻取/重取幅度比",接近中医候脉的浮沉参考。

### 2.1 材料

| 件 | 型号 | 参考价 |
|---|---|---|
| 压电薄膜 | PVDF 传感器 LDT0-028K(带配重) | ~10 元 |
| 运放 | MCP6002(轨到轨双运放) | ~1 元 |
| 电阻电容 | 10MΩ / 100kΩ / 1MΩ、0.1μF、1μF、1.5V 分压电阻 | ~5 元 |
| 加压装置 | 旧血压计袖带(带气泵与放气阀) | ~20 元 |
| 其他 | 洞洞板、LDO(AMS1117-3.3)、导线、3D 打印腕带壳(可选) | ~50 元 |

### 2.2 电路要点(电荷放大器)

```
PVDF ──┬── C1 0.1μF ──┬── MCP6002 ──┬── R2/C2 带通(0.1~40Hz) ──┐
       │              │    (电荷放大)│                           │
       R1 10MΩ        Rf 100MΩ      └── 偏置 1.65V(分压)        ▼
       │              └──────────────┘                     ESP32 ADC(GPIO34)
      GND
```

要点:
- PVDF 输出是电荷,须用**极高输入阻抗**(R1≥10MΩ)的运放做电荷放大,否则波形失真;
- 信号**偏置到 ADC 量程中点**(3.3V 系统偏到 1.65V);
- **带通 0.1-40Hz**:去掉呼吸/体动低频与 50Hz 工频干扰;
- ESP32 用 **ADC1 通道(GPIO32-39)**,`analogSetPinAttenuation(pin, ADC_11db)` 后 `analogRead` 约 500Hz;更稳可用定时器中断采样;
- 传感器贴桡动脉搏动点(腕横纹上约 2 指),外套袖带气囊,**程序控制加压:轻取(约 40mmHg)→ 重取(约 100mmHg)两档**;
- 轻取幅度/重取幅度 >1.2 → "脉浮"倾向;<0.8 → "脉沉"倾向(仅作参考,写入结果时注明"单点压力参考值")。

### 2.3 验收

- 加压两档波形幅度比可复现(同人同档重复 3 次差异 <15%);
- 用力按紧时波形幅值明显增大——证明测到的是压力而非光电容积。

---

## 三、L3:三部九候压力阵列(1-3 月,500 元+,选做)

- 3 路 PVDF/柔性压力传感器按**寸、关、尺**间距(约 10mm)排列 + 独立三通道放大;
- 加压用气泵+电磁阀程序控制(或步进电机丝杆),实现**浮、中、沉**三档自动加压;
- 三通道 ≥200Hz 同步采样(ESP32-S3 三路 ADC 或外接 AD7606);
- 参照 2025 年学术前沿《基于六阵列传感器的全自动脉搏采集系统》(六阵列商用化方向)——做到这一步工程量接近商用脉诊仪,**建议到此直接购买带 SDK 的成品**(见《硬件接入方案》B 档,如 @qihuangai/pulse-device 类),DIY 用于理解原理即可。

---

## 四、与杏林汇对接(下一步)

1. **当前(立即可用)**:L1 输出的"脉数/脉迟/脉缓/节律不齐"标签,直接在六体系辨证页"望闻切"步骤手动点选,或并入 `form.pulse` 后辨证;
2. **B 档实施时**:ESP32 加 BLE 串口服务(Nordic UART Service,`6E400001-B5A3-F393-E0A9-E50E24DCCA9E`,TX 用 Notify),浏览器 Chrome/Edge 用 Web Bluetooth 订阅波形 → 前端 PulseDevice.vue → 波形特征提取服务 → 标签自动入引擎;
3. **数据契约**(预定义,DIY 固件按此输出即可无缝接):

```json
{"device_id": "xinglin-diy-l1", "kind": "pulse_wave", "sample_rate": 100,
 "channel": "ir", "unit": "adc", "samples": [12345, 12401, "..."]}
```

---

## 五、常见坑(踩过的都写这)

1. **运动伪影**:手指/腕部要静止,PPG 对环境光敏感——手指要完全盖住窗口遮光;
2. **50Hz 工频**:波形上叠正弦干扰 → 加带通滤波、传感器线用屏蔽线;
3. **PVDF 静电与高阻**:手焊前先摸地放电,电路板清洗助焊剂,否则基线漂移;
4. **MAX30102 找不到**:检查 3.3V 供电(5V 会烧)、SDA/SCL 是否接反、I2C 扫描确认地址 0x57;
5. **串口丢数**:115200 下 100Hz CSV 足够;若丢,用二进制打包(4 字节/样本)或降采样;
6. **别追求"把脉"级精度**:客观化是趋势,但单点 DIY 设备的中医解释力有限——**报告里如实标注设备能力边界**,这本身就是杏林汇的原则。
