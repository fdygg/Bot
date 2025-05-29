from typing import Dict, Optional
from datetime import datetime, UTC
import logging
import hashlib
import secrets
import jwt
from .database_service import DatabaseService
from .user_service import UserService

logger = logging.getLogger(__name__)

class AuthService:
    def __init__(self):
        self.db = DatabaseService()
        self.user_service = UserService()
        self.startup_time = datetime.now(UTC)
        self.SECRET_KEY = "your-secret-key-here"  # Ganti dengan environment variable
        logger.info(f"""
        AuthService initialized:
        Time: 2025-05-29 06:59:37
        User: fdygg
        """)

    def _hash_password(self, password: str) -> str:
        """Hash password menggunakan SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()

    def _generate_token(self, user_data: Dict) -> str:
        """Generate JWT token untuk web authentication"""
        payload = {
            'user_id': user_data['growid'],
            'username': user_data['website_username'],
            'exp': datetime.now(UTC).timestamp() + (24 * 60 * 60)  # 24 jam expiry
        }
        return jwt.encode(payload, self.SECRET_KEY, algorithm='HS256')

    async def register_web_user(
        self,
        discord_id: str,
        username: str,
        password: str
    ) -> tuple[bool, str]:
        """Register user baru untuk web interface"""
        try:
            # Check if username already exists
            existing_user = await self.user_service.get_user(username, platform="web")
            if existing_user:
                return False, "Username already taken"

            # Hash password
            hashed_password = self._hash_password(password)

            # Create web account
            success = await self.user_service.create_web_account(
                discord_id=discord_id,
                username=username,
                password=hashed_password
            )

            if success:
                return True, "Web account created successfully"
            return False, "Failed to create web account"

        except Exception as e:
            logger.error(f"Registration error: {str(e)}")
            return False, "Registration failed"

    async def login_web_user(
        self,
        username: str,
        password: str
    ) -> tuple[bool, str, Optional[str]]:
        """Login untuk web interface"""
        try:
            # Get user
            user = await self.user_service.get_user(username, platform="web")
            if not user:
                return False, "Invalid username", None

            # Verify password
            if user['website_password'] != self._hash_password(password):
                return False, "Invalid password", None

            # Check if web account is active
            if not user['is_web_active']:
                return False, "Web account is not active", None

            # Generate token
            token = self._generate_token(user)
            return True, "Login successful", token

        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            return False, "Login failed", None

    async def verify_token(self, token: str) -> tuple[bool, Optional[Dict]]:
        """Verify JWT token dan return user data"""
        try:
            # Decode token
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=['HS256'])
            
            # Check expiration
            if payload['exp'] < datetime.now(UTC).timestamp():
                return False, None

            # Get user data
            user = await self.user_service.get_user(
                payload['username'],
                platform="web"
            )
            if not user:
                return False, None

            return True, user

        except jwt.InvalidTokenError:
            return False, None
        except Exception as e:
            logger.error(f"Token verification error: {str(e)}")
            return False, None

    async def check_permission(
        self,
        user_id: str,
        permission: str,
        platform: str = "discord"
    ) -> bool:
        """Check if user has specific permission"""
        query = """
        SELECT permissions
        FROM role_permissions
        WHERE role_id IN (
            SELECT role_id 
            FROM user_roles 
            WHERE user_id = ? AND platform = ?
        )
        """
        try:
            results = await self.db.execute_query(query, (user_id, platform))
            
            for result in results:
                perms = result['permissions'].split(',')
                if 'all' in perms or permission in perms:
                    return True
            
            return False

        except Exception as e:
            logger.error(f"Permission check error: {str(e)}")
            return False

    async def change_password(
        self,
        username: str,
        old_password: str,
        new_password: str
    ) -> tuple[bool, str]:
        """Change user password"""
        try:
            # Verify current password
            success, msg, _ = await self.login_web_user(username, old_password)
            if not success:
                return False, "Current password is incorrect"

            # Hash new password
            new_hash = self._hash_password(new_password)

            # Update password
            query = """
            UPDATE users 
            SET 
                website_password = ?,
                updated_at = ?,
                updated_by = 'web'
            WHERE website_username = ?
            """
            await self.db.execute_query(
                query,
                (new_hash, datetime.now(UTC), username),
                fetch=False
            )
            return True, "Password changed successfully"

        except Exception as e:
            logger.error(f"Password change error: {str(e)}")
            return False, "Failed to change password"