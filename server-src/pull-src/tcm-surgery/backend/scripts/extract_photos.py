"""从疮疡 PDF 提取彩色照片(300 DPI,颜色检测)

用法: cd backend && python3 -m scripts.extract_photos
依赖: opencv-python-headless
"""
import subprocess
import os
import glob

import cv2
import numpy as np

PDF = os.path.expanduser("~/Desktop/中医书/疮疡图谱_10297907.pdf")
OUT_DIR = "uploads/book/photos"

# 各论彩色照片页(精确来自 pdfimages 的 rgb 页分析,跳过目录/序/附方等黑白文字页)
COLOR_PAGES = (
    [29]
    + list(range(31, 41))   # 31-40
    + list(range(42, 52))   # 42-51
    + list(range(53, 60))   # 53-59
    + [61, 62]
    + list(range(64, 69))   # 64-68
    + list(range(70, 75))   # 70-74
    + list(range(76, 93))   # 76-92(排除黑白 93)
    + list(range(94, 102))  # 94-101(排除黑白 102)
    + list(range(103, 139)) # 103-138
)


def detect(img):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    s = hsv[:, :, 1]
    v = hsv[:, :, 2]
    mask = ((s > 45) & (v > 40) & (v < 248)).astype(np.uint8)
    closed = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((11, 11), np.uint8))
    contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    regions = []
    for c in contours:
        x, y, w, h = cv2.boundingRect(c)
        if w < 200 or h < 200:
            continue
        ar = w / h
        if ar < 0.35 or ar > 2.8:
            continue
        regions.append((x, y, w, h))
    regions.sort(key=lambda r: (r[1], r[0]))
    return regions


def main():
    os.makedirs("/tmp/cy_hires", exist_ok=True)
    os.makedirs(OUT_DIR, exist_ok=True)
    total = 0
    for pg in COLOR_PAGES:
        f = f"/tmp/cy_hires/p-{pg:03d}.jpg"
        if not os.path.exists(f):
            subprocess.run(
                ["pdftoppm", "-f", str(pg), "-l", str(pg), "-jpeg", "-r", "300", PDF, "/tmp/cy_hires/p"],
                check=True, capture_output=True,
            )
        img = cv2.imread(f)
        if img is None:
            continue
        for i, (x, y, w, h) in enumerate(detect(img)):
            m = 10
            x0, y0 = max(0, x - m), max(0, y - m)
            x1, y1 = min(img.shape[1], x + w + m), min(img.shape[0], y + h + m)
            out = f"{OUT_DIR}/p{pg:03d}_{i}.jpg"
            cv2.imwrite(out, img[y0:y1, x0:x1], [cv2.IMWRITE_JPEG_QUALITY, 93])
            total += 1
    print(f"✅ 提取完成: {total} 张照片 -> {OUT_DIR}/")
    print("接下来运行: python3 -m scripts.bind_photos 绑定到病种")


if __name__ == "__main__":
    main()
