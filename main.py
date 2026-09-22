"""
main.py
نقطه ورود اصلی اجرای سامانه Smart-FIRIS
مدیریت گردش کار: خواندن لایه‌ها -> محاسبه شاخص‌ها -> ارزیابی WLC -> ذخیره نقشه‌های خروجی
"""

import os
import sys
import numpy as np
import rasterio

# اضافه کردن پوشه src به مسیرهای اجرایی
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "src")))

from terrain import compute_topography_hazard
from model import compute_wlc_index, classify_hazard, save_raster


def load_fuel_layer(fuel_path: str) -> tuple[np.ndarray, dict]:
    """
    خواندن و نرمال‌سازی لایه بار سوخت (بین 0 تا 1)
    """
    with rasterio.open(fuel_path) as src:
        fuel = src.read(1).astype(np.float32)
        profile = src.profile.copy()
        nodata = src.nodata

    if nodata is not None:
        fuel[fuel == nodata] = np.nan

    # اگر مقادیر سوخت بین 0 تا 100 باشند به 0 تا 1 تبدیل می‌شوند
    max_val = np.nanmax(fuel)
    if max_val > 1.0:
        f_fuel = fuel / 100.0
    else:
        f_fuel = fuel

    f_fuel = np.clip(f_fuel, 0.0, 1.0)
    return f_fuel, profile


def run_pipeline():
    print("=" * 55)
    print("🌲🔥 آغاز فرآیند ارزیابی و مدل‌سازی حریق (Smart-FIRIS)")
    print("=" * 55)

    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, "data", "processed")
    output_dir = os.path.join(base_dir, "outputs", "maps")
    os.makedirs(output_dir, exist_ok=True)

    fuel_path = os.path.join(data_dir, "fars_fire_fuel_hazard_60m.tif")
    slope_path = os.path.join(data_dir, "fars_slope_60m.tif")
    aspect_path = os.path.join(data_dir, "fars_aspect_60m_light.tif")

    # ۱. پردازش لایه بار سوخت
    print("[1/4] در حال خواندن لایه بار سوخت گیاهی...")
    f_fuel, profile = load_fuel_layer(fuel_path)

    # ۲. پردازش لایه توپوگرافی
    print("[2/4] در حال محاسبه شاخص توپوگرافی (F_Topo)...")
    f_topo, _ = compute_topography_hazard(slope_path, aspect_path)

    # ۳. داده FWI (در نسخه آزمایشی لایه پایه مقیاس‌بندی شده به کار می‌رود)
    print("[3/4] در حال پردازش داده‌های اقلیمی (F_FWI)...")
    # فرض سناریوی پایه FWI متوسط/زیاد در غیاب داده برخط
    f_fwi = np.full_like(f_fuel, fill_value=0.55, dtype=np.float32)

    # ۴. محاسبه مدل ترکیبی WLC
    print("[4/4] اجرای فرمول ترکیب خطی وزن‌دار (WLC)...")
    wlc_continuous = compute_wlc_index(f_fwi, f_fuel, f_topo)
    wlc_classes = classify_hazard(wlc_continuous)

    # ذخیره نقشه‌ها
    out_cont_path = os.path.join(output_dir, "fars_wlc_hazard_continuous.tif")
    out_class_path = os.path.join(output_dir, "fars_wlc_hazard_classified.tif")

    print(f" -> ذخیره نقشه پیوسته خطر: {out_cont_path}")
    save_raster(out_cont_path, wlc_continuous, profile, is_discrete=False)

    print(f" -> ذخیره نقشه طبقه‌بندی‌شده خطر (۵ کلاسه): {out_class_path}")
    save_raster(out_class_path, wlc_classes, profile, is_discrete=True)

    print("=" * 55)
    print("✅ پردازش با موفقیت کامل شد.")
    print("=" * 55)


if __name__ == "__main__":
    run_pipeline()
