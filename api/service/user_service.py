from typing import Dict, Optional
from datetime import datetime, UTC
import logging
from .database_service import DatabaseService

logger = logging.getLogger(__name__)

class UserService:
    def __init__(self):
        self.db = DatabaseService()
        self.startup_time = datetime.now(UTC)
        logger.info(f"""
        UserService initialized:
        Time: 2025-05-28 17:13:34
        User: fdygg
        """)

    async def get_user(self, user_id: str, platform: str = "discord") -> Optional[Dict]:
        """Get user details"""
        if platform == "discord":
            query = """
            SELECT u.*, ug.discord_id
            FROM users u
            JOIN user_growid ug ON u.growid = ug.growid
            WHERE ug.discord_id = ?
            """
        else:
            query = """
            SELECT *
            FROM users
            WHERE website_username = ?
            """
        result = await self.db.execute_query(query, (user_id,))
        return result[0] if result else None

    async def create_web_account(self, discord_id: str, username: str, password: str) -> bool:
        """Create/Update web account untuk user Discord"""
        query = """
        UPDATE users 
        SET 
            website_username = ?,
            website_password = ?,
            is_web_active = 1,
            updated_at = ?,
            updated_by = 'web'
        WHERE growid IN (
            SELECT growid 
            FROM user_growid 
            WHERE discord_id = ?
        )
        """
        try:
            await self.db.execute_query(
                query,
                (username, password, datetime.now(UTC), discord_id),
                fetch=False
            )
            return True
        except:
            return False