"""把提取的彩色照片按「图号 → 病种」绑定(图号对应关系来自全书 OCR 通读)

用法: cd backend && python3 -m scripts.bind_photos
"""
import asyncio
import glob
import re

from app.database import SessionLocal, init_db
from app.models import Disease, Image
from sqlalchemy import select

# 图号 → 病名(各论,图1~图227)
# 格式: (起始图号, 结束图号, 病名)  含头尾
FIGURE_RANGES = [
    # 第一章 疔疮
    (1, 1, "印堂疔"), (2, 2, "眼角疔"), (3, 3, "鼻根疔"), (4, 4, "鼻疔"),
    (5, 5, "鼻翼疔"), (6, 6, "人中疔"), (7, 7, "迎香疔"), (8, 9, "额疔"),
    (10, 12, "虎须疔"), (13, 15, "唇疔"), (16, 16, "地仓疔"), (17, 17, "颊疔"),
    (18, 18, "领疔"), (19, 20, "沿爪疔"), (21, 23, "蛇头疔"), (24, 26, "蛇腹疔"),
    (27, 27, "蛇节疔"), (28, 29, "手丫疔"), (30, 30, "托盘疔"), (31, 31, "红丝疔"),
    (32, 34, "疔疮走黄"),
    # 第二章 疖
    (35, 36, "热疖"), (37, 38, "多发性疖"), (39, 40, "蝼蛄疖"), (41, 42, "坐板疖"),
    # 第三章 痈
    (43, 48, "颈痈"), (49, 49, "结喉痈"), (50, 50, "耳根痈"), (51, 52, "腋痈"),
    (53, 56, "腹壁痈"), (57, 58, "脐痈"), (59, 59, "胯腹痈"), (60, 60, "腰痈"),
    (61, 62, "臀痈"), (63, 63, "肛痈"), (64, 64, "子痈"), (65, 65, "臂痈"),
    (66, 67, "肘痈"), (68, 68, "腕痈"), (69, 69, "手背痈"), (70, 71, "大腿痈"),
    (72, 72, "小腿痈"), (73, 73, "足背痈"),
    # 第四章 有头疽
    (74, 87, "脑疽"), (88, 88, "脑顶疽"), (89, 94, "额疽"), (95, 95, "缺盆疽"),
    (96, 107, "发背疽"), (108, 109, "髂腰疽"), (110, 110, "肾俞发"), (111, 111, "莲子发"),
    (112, 115, "腹壁疽"), (116, 118, "腋疽"), (119, 119, "上臂疽"), (120, 120, "前臂疽"),
    (121, 121, "腕疽"), (122, 122, "股内疽"), (123, 123, "股后疽"), (124, 124, "膝疽"),
    # 第五章 无头疽
    (125, 128, "附骨疽"), (129, 130, "胁肋疽"), (131, 132, "足踝疽"), (133, 134, "足跟疽"),
    # 第六章 瘰疬
    (135, 142, "瘰疬"),
    # 第七章 乳痈
    (143, 150, "乳痈"), (151, 152, "乳头破碎"), (153, 154, "乳岩"),
    # 第八章 臁疮
    (155, 167, "臁疮"),
    # 第九章 丹毒
    (168, 170, "丹毒"),
    # 第十章 褥疮
    (171, 173, "褥疮"),
    # 第十一章 冻疮
    (174, 178, "冻疮"),
    # 第十二章 周围血管病
    (179, 197, "脱疽"), (198, 200, "糖尿病坏疽"), (201, 205, "闭塞性动脉硬化坏疽"),
    (206, 207, "坏死性皮肤血管炎"), (208, 210, "恶脉"), (211, 212, "股白肿"),
    # 第十三章 疮疡杂病
    (213, 213, "发颐"), (214, 215, "缠腰毒"), (216, 219, "皮肤坏疽"),
    (220, 221, "串珠疖"), (222, 222, "蛇串疮"), (223, 224, "漆疮"),
    (225, 226, "阴肿"), (227, 227, "子痫"),
]

# 展开为 图号 → 病名
FIG_TO_DISEASE = {}
for start, end, name in FIGURE_RANGES:
    for n in range(start, end + 1):
        FIG_TO_DISEASE[n] = name


def photo_order(filename: str) -> tuple:
    """p029_0.jpg -> (29, 0)"""
    import os
    m = re.match(r'p(\d+)_(\d+)', os.path.basename(filename))
    return (int(m.group(1)), int(m.group(2)))


async def bind() -> None:
    await init_db()
    photos = sorted(glob.glob('uploads/book/photos/p*.jpg'), key=photo_order)

    async with SessionLocal() as db:
        # 病名 → disease_id
        diseases = (await db.execute(select(Disease))).scalars().all()
        name_to_id = {d.name: d.id for d in diseases}

        # 删除旧的 book 照片绑定(保留 6 张图版 category 绑定)
        await db.execute(Image.__table__.delete().where(
            Image.image_type == "book", Image.category.is_(None)
        ))

        bound = 0
        unbound = []
        for i, path in enumerate(photos):
            fig_no = i + 1  # 第 i 张照片对应图号 i+1
            disease_name = FIG_TO_DISEASE.get(fig_no)
            fname = path.split('/')[-1]
            if disease_name and disease_name in name_to_id:
                db.add(Image(
                    disease_id=name_to_id[disease_name],
                    image_type="book",
                    path=f"/{path}",
                    caption=f"图{fig_no} {disease_name}",
                ))
                bound += 1
            else:
                unbound.append((fig_no, fname))

        await db.commit()

    print(f"✅ 绑定完成: {bound}/{len(photos)} 张照片已绑定到病种")
    if unbound:
        print(f"未绑定 {len(unbound)} 张(图号超出227或病名未匹配):")
        for fig_no, fname in unbound[:20]:
            print(f"  图{fig_no} {fname}")


if __name__ == "__main__":
    asyncio.run(bind())
