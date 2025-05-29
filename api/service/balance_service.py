from typing import Dict, Optional
from datetime import datetime, UTC
import logging
from .database_service import DatabaseService

logger = logging.getLogger(__name__)

class BalanceService:
    def __init__(self):
        self.db = DatabaseService()
        self.startup_time = datetime.now(UTC)
        logger.info(f"""
        BalanceService initialized:
        Time: 2025-05-28 17:13:34
        User: fdygg
        """)

    async def get_balance(self, user_id: str, platform: str = "discord") -> Optional[Dict]:
        """Get user balance"""
        query = """
        SELECT 
            balance_wl,
            balance_dl,
            balance_bgl,
            balance_rupiah
        FROM users 
        WHERE growid = ?
        """
        result = await self.db.execute_query(query, (user_id,))
        return result[0] if result else None

    async def update_balance(self, user_id: str, currency: str, amount: float, platform: str = "discord") -> bool:
        """Update user balance"""
        query = f"""
        UPDATE users 
        SET 
            balance_{currency} = balance_{currency} + ?,
            updated_at = ?,
            updated_by = ?
        WHERE growid = ?
        """
        try:
            await self.db.execute_query(
                query, 
                (amount, datetime.now(UTC), platform, user_id),
                fetch=False
            )
            return True
        except:
            return False

    async def get_conversion_rates(self) -> Dict[str, float]:
        """Get current conversion rates"""
        query = """
        SELECT currency, rate 
        FROM conversion_rates 
        WHERE is_active = 1
        """
        result = await self.db.execute_query(query)
        return {row['currency']: row['rate'] for row in result}