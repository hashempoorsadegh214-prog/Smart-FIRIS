"""
Smart-FIRIS: Web Exporter
صادرکننده لایه نقشه خطر حریق برای وب‌جی‌آی‌اس (Leaflet)
"""

import os
import json
import numpy as np
import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling
from PIL import Image

def get_color_map():
    """جدول رنگی ۵ کلاسه استاندارد حریق (RGBA)"""
    return {
        0: (0, 0, 0, 0),         # پس‌زمینه بدون داده: کاملاً شفاف
        1: (38, 115, 0, 210),    # بسیار کم: سبز
        2: (168, 168, 0, 210),   # کم: زرد-سبز
        3: (255, 170, 0, 210),   # متوسط: زرد
        4: (230, 76, 0, 220),    # زیاد: نارنجی
        5: (115, 0, 0, 235)      # بسیار زیاد: قرمز تیره
    }

def export_for_web():
    # مسیرهای ورودی و خروجی
    input_path = "outputs/fwi_hazard_5class.tif"
    fallback_path = "data/processed/fars_fire_fuel_hazard_60m.tif"
    
    # بررسی وجود فایل
    if os.path.exists(input_path):
        raster_path = input_path
    elif os.path.exists(fallback_path):
        raster_path = fallback_path
        print(f"[توجه] خروجی نهایی مدل یافت نشد؛ از فایل پایه استفاده می‌شود: {fallback_path}")
    else:
        print("[خطا] هیچ رستر ورودی پیدا نشد.")
        return

    output_dir = "web/data"
    os.makedirs(output_dir, exist_ok=True)
    output_image = os.path.join(output_dir, "hazard_overlay.png")
    bounds_file = os.path.join(output_dir, "bounds.json")

    print(f"[1/3] در حال خواندن رستر: {raster_path} ...")
    with rasterio.open(raster_path) as src:
        # اگر مختصات WGS84 نباشد تبدیل می‌کند
        dst_crs = "EPSG:4326"
        transform, width, height = calculate_default_transform(
            src.crs, dst_crs, src.width, src.height, *src.bounds
        )
        
        data = np.zeros((height, width), dtype=np.uint8)
        reproject(
            source=rasterio.band(src, 1),
            destination=data,
            src_transform=src.transform,
            src_crs=src.crs,
            dst_transform=transform,
            dst_crs=dst_crs,
            resampling=Resampling.nearest
        )
        
        # محاسبه مرزهای جغرافیایی برای Leaflet [[جنوب, غرب], [شمال, شرق]]
        west = transform[2]
        north = transform[5]
        east = west + width * transform[0]
        south = north + height * transform[4]
        leaflet_bounds = [[float(south), float(west)], [float(north), float(east)]]

    print("[2/3] اعمال کلاس‌بندی ۵ گانه و رنگ‌آمیزی نقشه ...")
    # طبقه‌بندی مقادیر در صورت پیوسته بودن (0 تا 5)
    if data.max() > 5:
        valid_mask = data > 0
        classified = np.zeros_like(data, dtype=np.uint8)
        if np.any(valid_mask):
            percentiles = np.percentile(data[valid_mask], [20, 40, 60, 80])
            classified[valid_mask] = np.digitize(data[valid_mask], percentiles) + 1
    else:
        classified = data

    # ساخت تصویر RGBA
    cmap = get_color_map()
    rgba_img = np.zeros((classified.shape[0], classified.shape[1], 4), dtype=np.uint8)
    for class_val, color in cmap.items():
        rgba_img[classified == class_val] = color

    # ذخیره تصویر خروجی
    img = Image.fromarray(rgba_img, "RGBA")
    img.save(output_image, "PNG", optimize=True)

    # ذخیره فایل مختصات
    with open(bounds_file, "w", encoding="utf-8") as f:
        json.dump({"bounds": leaflet_bounds}, f, indent=2)

    print(f"[3/3] خروجی‌ها با موفقیت ایجاد شدند:")
    print(f"  - تصویر وب: {output_image}")
    print(f"  - مختصات رفرنس: {bounds_file}")
    print(f"  - محدوده استان: {leaflet_bounds}")

if __name__ == "__main__":
    export_for_web()
