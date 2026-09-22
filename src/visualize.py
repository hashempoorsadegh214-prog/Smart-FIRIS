"""
visualize.py
ماژول مصورسازی و خروجی کارتوگرافی سامانه Smart-FIRIS
وظیفه: تولید نقشه تصویری باکیفیت از پهنه‌بندی خطر حریق استان فارس
"""

import os
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm
import matplotlib.patches as mpatches
import numpy as np
import rasterio


def plot_hazard_map(classified_raster_path: str, output_image_path: str):
    """
    تولید و ذخیره نقشه نهایی با پالت رنگی ۵ کلاسه استاندارد حریق
    """
    if not os.path.exists(classified_raster_path):
        print(f"خطا: فایل {classified_raster_path} یافت نشد.")
        return

    with rasterio.open(classified_raster_path) as src:
        data = src.read(1)
        nodata = src.nodata

    # پالت رنگی استاندارد آتش‌سوزی
    # 1: خیلی کم (سبز)، 2: کم (زرد)، 3: متوسط (نارنجی)، 4: زیاد (قرمز)، 5: بحرانی (زرشکی)
    colors = [
        "#2ca25f",  # Very Low (سبز)
        "#ffeb3b",  # Low (زرد)
        "#ff9800",  # Moderate (نارنجی)
        "#f44336",  # High (قرمز)
        "#880e4f",  # Extreme (زرشکی)
    ]
    cmap = ListedColormap(colors)
    bounds = [0.5, 1.5, 2.5, 3.5, 4.5, 5.5]
    norm = BoundaryNorm(bounds, cmap.N)

    # تبدیل داده‌های بی‌ارزش به NaN برای نمایش شفاف
    data_masked = np.where(data == 0, np.nan, data)
    if nodata is not None:
        data_masked = np.where(data_masked == nodata, np.nan, data_masked)

    fig, ax = plt.subplots(figsize=(10, 10), dpi=300)
    img = ax.imshow(data_masked, cmap=cmap, norm=norm)

    ax.set_title("Smart-FIRIS: Fars Province Wildfire Hazard Zoning", fontsize=14, fontweight="bold", pad=15)
    ax.axis("off")

    # ساخت راهنمای نقشه (Legend)
    labels = [
        "Very Low (0 - 20)",
        "Low (20 - 40)",
        "Moderate (40 - 60)",
        "High (60 - 80)",
        "Extreme (80 - 100)"
    ]
    patches = [mpatches.Patch(color=colors[i], label=labels[i]) for i in range(len(labels))]
    ax.legend(handles=patches, loc="lower right", frameon=True, facecolor="white", edgecolor="gray", title="Hazard Level")

    plt.tight_layout()
    plt.savefig(output_image_path, bbox_inches="tight", dpi=300)
    plt.close()

    print(f"✅ نقشه تصویری با موفقیت ذخیره شد:\n   -> {output_image_path}")


if __name__ == "__main__":
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    raster_path = os.path.join(base_dir, "outputs", "maps", "fars_wlc_hazard_classified.tif")
    img_out = os.path.join(base_dir, "outputs", "maps", "fars_hazard_map.png")
    plot_hazard_map(raster_path, img_out)
