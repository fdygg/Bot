from typing import Dict, List, Optional
from datetime import datetime, UTC
import logging
from .database_service import DatabaseService

logger = logging.getLogger(__name__)

class TransactionService:
    def __init__(self):
        self.db = DatabaseService()
        self.startup_time = datetime.now(UTC)
        logger.info(f"""
        TransactionService initialized:
        Time: 2025-05-28 17:13:34
        User: fdygg
        """)

    async def create_transaction(
        self,
        user_id: str,
        type: str,
        currency: str,
        amount: float,
        platform: str = "discord"
    ) -> bool:
        """Create new transaction"""
        query = """
        INSERT INTO transactions (
            growid, platform, type, currency, 
            amount, details, created_by
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        details = f"{type} {amount} {currency} via {platform}"
        try:
            await self.db.execute_query(
                query,
                (user_id, platform, type, currency, amount, details, platform),
                fetch=False
            )
            return True
        except:
            return False

    async def get_user_transactions(
        self,
        user_id: str,
        platform: str = "discord",
        limit: int = 10
    ) -> List[Dict]:
        """Get user transaction history"""
        query = """
        SELECT *
        FROM transactions
        WHERE growid = ? AND platform = ?
        ORDER BY created_at DESC
        LIMIT ?
        """
        return await self.db.execute_query(query, (user_id, platform, limit))