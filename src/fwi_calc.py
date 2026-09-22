"""
fwi_calc.py
ماژول پردازش شاخص هواشناسی حریق (FWI) سامانه Smart-FIRIS
وظیفه: تطبیق داده‌های اقلیمی بر شبکه ۶۰ متری و نرمال‌سازی شاخص F_FWI
"""

import numpy as np
import rasterio
from rasterio.enums import Resampling


def normalize_fwi(fwi_array: np.ndarray, max_fwi_threshold: float = 50.0) -> np.ndarray:
    """
    نرمال‌سازی FWI بین 0 و 1
    بر اساس استانداردهای آتش‌سوزی، FWI بالای ۵۰ به عنوان شرایط بسیار بحرانی (Extreme) در نظر گرفته می‌شود.
    """
    norm = np.clip(fwi_array / max_fwi_threshold, 0.0, 1.0)
    return norm


def resample_fwi_to_reference(fwi_coarse_path: str, reference_raster_path: str) -> tuple[np.ndarray, dict]:
    """
    درونیابی داده‌های درشت‌مقیاس FWI به شبکه دقیق ۶۰ متری رستر مرجع با استفاده از روش Bilinear
    جهت ایجاد گرادیان پیوسته و جلوگیری از ایجاد لبه‌های بلوکی کاذب
    """
    with rasterio.open(reference_raster_path) as ref:
        ref_shape = (ref.height, ref.width)
        ref_profile = ref.profile.copy()

    with rasterio.open(fwi_coarse_path) as src_fwi:
        # درونیابی نرم Bilinear به ابعاد دقیق رستر مرجع
        fwi_resampled = src_fwi.read(
            1,
            عاد دقیق رستر مرجع
        fwi_resampled = src_fwi.read(
            1,
            out_shape=ref_shape,
            resampling=Resampling.bilinear
        ).astype(np.float32)

    # نرمال‌سازی به بازه 0 تا 1
    f_fwi = normalize_fwi(fwi_resampled)

    ref_profile.update(dtype=rasterio.float32, nodata=np.nan)

    return f_fwi, ref_profile


if __name__ == "__main__":
    print("ماژول fwi_calc آماده استفاده است.")
