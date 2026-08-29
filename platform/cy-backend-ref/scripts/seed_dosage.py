"""剂量换算与组成规范化(幂等,在方剂 seed 之后运行)

1. 马培之《外科传薪集》古制(两/钱/分)→ 现代克数,存入 dosage
2. 无定量方(各等分/枚个条/单味)标注"原书未载剂量/各药等分"
3. 张觉人方 composition 已含克数的拷贝到 dosage
4. 组成字段 空格分隔符 → 顿号
用法: cd backend && python3 -m scripts.seed_dosage
"""
import asyncio
import re

from sqlalchemy import select

from app.database import SessionLocal, init_db
from app.models import Formula

CN = {'一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9}
UNIT = {'两': 30, '钱': 3, '分': 0.3}


def cn_num(s: str) -> int:
    if not s:
        return 1
    if '百' in s:
        a, b = s.split('百', 1)
        return (cn_num(a) if a else 1) * 100 + (cn_num(b) if b else 0)
    if '十' in s:
        a, b = s.split('十', 1)
        return (cn_num(a) if a else 1) * 10 + (cn_num(b) if b else 0)
    return CN.get(s, 1)


def amount_to_g(a: str):
    s = a
    suffix = s.endswith('半')
    if suffix:
        s = s[:-1]
    units = []
    m = re.match(r'^([一二三四五六七八九十百]*)(两|钱|分)', s)
    while m:
        units.append((cn_num(m.group(1)) if m.group(1) else 1, m.group(2)))
        s = s[m.end():]
        m = re.match(r'^([一二三四五六七八九十百]*)(两|钱|分)', s)
    if not units:
        return None
    total = sum(n * UNIT[u] for n, u in units)
    if suffix:
        total += 0.5 * UNIT[units[-1][1]]
    return round(total, 2)


def convert_comp(comp: str) -> str:
    out = []
    for m in re.finditer(r'([^\s（）]+)（([^）]*)）', comp or ''):
        herb = m.group(1).strip('、')
        inner = m.group(2).strip()
        dm = re.search(r'[一二三四五六七八九十百两钱分半]+', inner)
        if dm:
            g = amount_to_g(dm.group(0))
            if g is not None:
                if '各' in inner:
                    out.append(f"{herb}{g:g}g(各)")
                else:
                    out.append(f"{herb}{g:g}g")
                continue
        out.append(f"{herb}（{inner}）")
    return '、'.join(out)


async def seed() -> None:
    await init_db()
    async with SessionLocal() as db:
        formulas = list((await db.execute(select(Formula))).scalars().all())
        converted = marked = normalized = 0
        for f in formulas:
            # 1~2. 剂量(在空格分隔的原始组成上换算)
            if not f.dosage:
                if f.source == '《外科传薪集》':
                    d = convert_comp(f.composition or '')
                    if d:
                        f.dosage = d
                        converted += 1
                    elif '等分' in (f.composition or ''):
                        f.dosage = '各药等分'
                        marked += 1
                    else:
                        # 无定量方(单味药/膏药熬法):直接显示组成
                        f.dosage = (f.composition or '').strip() or '原书未载剂量'
                        marked += 1
                elif f.source == '《红蓼山馆医集》':
                    if 'g' in (f.composition or ''):
                        f.dosage = f.composition
                        converted += 1
                    else:
                        # 丹药/马钱子方无克数:组成 + 服法(如"制马钱子(九制)。每服2~3分")
                        parts = [x for x in [(f.composition or '').strip(), (f.usage or '').strip()] if x]
                        f.dosage = '。'.join(parts) + '。' if parts else '原书未载剂量'
                        marked += 1
            # 3. 组成 空格 → 顿号(最后做)
            if f.composition and ' ' in f.composition:
                f.composition = f.composition.replace('） ', '）、').replace(' ', '、')
                normalized += 1
            if f.dosage and ' ' in f.dosage:
                f.dosage = f.dosage.replace('） ', '）、').replace(' ', '、')
        await db.commit()
    print(f"✅ 剂量换算完成: 换算 {converted} 首 / 标注 {marked} 首 / 组成规范化 {normalized} 首")


if __name__ == "__main__":
    asyncio.run(seed())
