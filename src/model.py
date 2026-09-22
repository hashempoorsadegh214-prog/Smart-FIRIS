"""
model.py
هسته محاسباتی مدل ترکیب خطی وزن‌دار (WLC) سامانه Smart-FIRIS
"""

import numpy as np
import rasterio


def compute_wlc_index(
    f_fwi: np.ndarray,
    f_fuel: np.ndarray,
    f_topo: np.ndarray,
    w_fwi: float = 0.45,
    w_fuel: float = 0.35,
    w_topo: float = 0.20
) -> np.ndarray:
    """
    محاسبه امتیاز پیوسته خطر حریق (0 تا 100) بر اساس WLC
    """
    wlc = 100.0 * (
        (w_fwi * f_fwi) +
        (w_fuel * f_fuel) +
        (w_topo * f_topo)
    )
    return wlc.astype(np.float32)


def classify_hazard(wlc_score: np.ndarray) -> np.ndarray:
    """
    طبقه‌بندی امتیاز WLC به ۵ کلاس خطر:
    1: خیلی کم (0-20)
    2: کم (20-40)
    3: متوسط (40-60)
    4: زیاد (60-80)
    5: بحرانی (80-100)
    0: داده نامعتبر (NoData)
    """
    classes = np.zeros_like(wlc_score, dtype=np.uint8)

    valid_mask = ~np.isnan(wlc_score)

    classes[valid_mask & (wlc_score < 20.0)] = 1
    classes[valid_mask & (wlc_score >= 20.0) & (wlc_score < 40.0)] = 2
    classes[valid_mask & (wlc_score >= 40.0) & (wlc_score < 60.0)] = 3
    classes[valid_mask & (wlc_score >= 60.0) & (wlc_score < 80.0)] = 4
    classes[valid_mask & (wlc_score >= 80.0)] = 5

    return classes


def save_raster(output_path: str, data: np.ndarray, profile: dict, is_discrete: bool = False):
    """
    ذخیره رستر خروجی روی دیسک با تنظیمات بهینه فشرده‌سازی
    """
    profile_out = profile.copy()
    if is_discrete:
        profile_out.update(
            dtype=rasterio.uint8,
            nodata=0,
            compress="deflate"
        )
    else:
        profile_out.update(
            dtype=rasterio.float32,
            nodata=np.nan,
            compress="deflate"
        )

    with rasterio.open(output_path, "w", **profile_out) as dst:
        dst.write(data, 1)


if __name__ == "__main__":
    print("ماژول model آماده استفاده است.")
