"""
terrain.py
ماژول تحلیل توپوگرافی سامانه Smart-FIRIS
وظیفه: خواندن لایه‌های شیب و جهت شیب، نرمال‌سازی و تولید شاخص توپوگرافی (F_Topo)
"""

import numpy as np
import rasterio


def normalize_slope(slope_deg: np.ndarray) -> np.ndarray:
    """
    نرمال‌سازی شیب بین 0 تا 1
    شیب‌های تندتر پتانسیل حریق بالاتری دارند.
    محدوده موثر: 0 تا 45 درجه (شیب‌های بالای 45 درجه ماکزیمم 1 در نظر گرفته می‌شوند)
    """
    norm = np.clip(slope_deg / 45.0, 0.0, 1.0)
    return norm


def normalize_aspect(aspect_deg: np.ndarray) -> np.ndarray:
    """
    نرمال‌سازی جهت شیب بین 0 تا 1
    دامنه‌های جنوبی و جنوب‌غربی بیشترین تابش آفتاب و خشکی را دارند:
    - جنوب (180 درجه) و جنوب‌غرب: خطر ماکزیمم (نزدیک 1)
    - شمال (0 و 360 درجه): خطر مینیمم (نزدیک 0)
    - مناطق مسطح (aspect == -1): مقدار خنثی 0.2
    """
    norm = np.zeros_like(aspect_deg, dtype=np.float32)

    flat_mask = aspect_deg < 0
    valid_mask = ~flat_mask

    # استفاده از تابع کسینوس برای امتیازدهی (زاویه 180 درجه بیشترین مقدار 1 را می‌گیرد)
    # rad = (aspect - 180) * pi / 180 -> cos(0) = 1 (برای جنوب)
    rad = np.radians(aspect_deg[valid_mask] - 180.0)
    norm[valid_mask] = (np.cos(rad) + 1.0) / 2.0

    # زمین‌های صاف (بدون جهت)
    norm[flat_mask] = 0.2

    return norm


def compute_topography_hazard(
    slope_path: str,
    aspect_path: str,
    slope_weight: float = 0.7,
    aspect_weight: float = 0.3
) -> tuple[np.ndarray, dict]:
    """
    ترکیب شیب و جهت شیب برای تولید شاخص نهایی F_Topo
    وزن استاندارد: 70% شیب و 30% جهت شیب
    """
    with rasterio.open(slope_path) as src_slope:
        slope = src_slope.read(1).astype(np.float32)
        profile = src_slope.profile.copy()
        nodata = src_slope.nodata

    with rasterio.open(aspect_path) as src_aspect:
        aspect = src_aspect.read(1).astype(np.float32)

    # ایجاد ماسک داده‌های نامعتبر (NoData)
    if nodata is not None:
        mask = (slope == nodata) | np.isnan(slope)
    else:
        mask = np.isnan(slope)

    # نرمال‌سازی
    slope_norm = normalize_slope(slope)
    aspect_norm = normalize_aspect(aspect)

    # ترکیب خطی
    f_topo = (slope_weight * slope_norm) + (aspect_weight * aspect_norm)
    f_topo[mask] = np.nan

    # بروزرسانی پروفایل متادیتا برای خروجی float32
    profile.update(dtype=rasterio.float32, nodata=np.nan)

    return f_topo, profile


if __name__ == "__main__":
    print("ماژول terrain آماده استفاده است.")
