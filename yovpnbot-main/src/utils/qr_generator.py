#!/usr/bin/env python3
"""
Утилиты для генерации QR-кодов
"""

import qrcode
from io import BytesIO
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class QRGenerator:
    """Генератор QR-кодов"""
    
    def __init__(self):
        self.qr_available = self._check_qr_availability()
    
    def _check_qr_availability(self) -> bool:
        """Проверка доступности библиотеки qrcode"""
        try:
            import qrcode
            return True
        except ImportError:
            logger.warning("Библиотека qrcode недоступна")
            return False
    
    def generate_qr_code(self, data: str, size: int = 10, border: int = 4) -> Optional[BytesIO]:
        """Генерация QR-кода"""
        if not self.qr_available:
            logger.warning("QR-код не может быть сгенерирован: библиотека недоступна")
            return None
        
        try:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=size,
                border=border,
            )
            qr.add_data(data)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            
            bio = BytesIO()
            img.save(bio, format='PNG')
            bio.seek(0)
            
            return bio
        except Exception as e:
            logger.error(f"Ошибка генерации QR-кода: {e}")
            return None
    
    def generate_referral_qr(self, referral_link: str) -> Optional[BytesIO]:
        """Генерация QR-кода для реферальной ссылки"""
        return self.generate_qr_code(referral_link)
    
    def generate_vless_qr(self, vless_link: str) -> Optional[BytesIO]:
        """Генерация QR-кода для VLESS ссылки"""
        return self.generate_qr_code(vless_link)

# Глобальный экземпляр генератора
qr_generator = QRGenerator()