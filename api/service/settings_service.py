from typing import Any, Dict, List, Optional
from datetime import datetime, UTC
import logging
from .database_service import DatabaseService
from ..models.settings import Setting, SettingCategory, FeatureFlag

logger = logging.getLogger(__name__)

class SettingsService:
    def __init__(self):
        self.db = DatabaseService()
        self.startup_time = datetime.now(UTC)
        logger.info(f"""
        SettingsService initialized:
        Time: 2025-05-29 17:11:23
        User: fdygg
        """)

    async def get_setting(
        self,
        category: SettingCategory,
        key: str
    ) -> Optional[Setting]:
        """Get setting value"""
        query = """
        SELECT * FROM settings 
        WHERE category = ? AND key = ?
        """
        
        result = await self.db.execute_query(query, (category.value, key))
        if not result:
            return None
            
        setting = result[0]
        return Setting(
            id=setting["id"],
            category=SettingCategory(setting["category"]),
            key=setting["key"],
            value=setting["value"],
            description=setting["description"],
            is_public=setting["is_public"],
            created_by=setting["created_by"],
            created_at=setting["created_at"],
            updated_by=setting["updated_by"],
            updated_at=setting["updated_at"],
            metadata=eval(setting["metadata"]) if setting["metadata"] else {}
        )

    async def set_setting(
        self,
        category: SettingCategory,
        key: str,
        value: Any,
        description: Optional[str] = None,
        is_public: bool = False,
        metadata: Optional[Dict] = None
    ) -> Optional[Setting]:
        """Create or update setting"""
        try:
            existing = await self.get_setting(category, key)
            
            if existing:
                # Update
                query = """
                UPDATE settings 
                SET 
                    value = ?,
                    description = ?,
                    is_public = ?,
                    metadata = ?,
                    updated_by = ?,
                    updated_at = ?
                WHERE category = ? AND key = ?
                """
                
                await self.db.execute_query(
                    query,
                    (
                        str(value),
                        description,
                        is_public,
                        str(metadata or {}),
                        "fdygg",
                        datetime.now(UTC),
                        category.value,
                        key
                    ),
                    fetch=False
                )
            else:
                # Create
                query = """
                INSERT INTO settings (
                    category, key, value, description,
                    is_public, created_by, created_at, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """
                
                await self.db.execute_query(
                    query,
                    (
                        category.value,
                        key,
                        str(value),
                        description,
                        is_public,
                        "fdygg",
                        datetime.now(UTC),
                        str(metadata or {})
                    ),
                    fetch=False
                )
                
            return await self.get_setting(category, key)
            
        except Exception as e:
            logger.error(f"Error setting setting: {str(e)}")
            return None

    async def delete_setting(
        self,
        category: SettingCategory,
        key: str
    ) -> bool:
        """Delete setting"""
        try:
            query = "DELETE FROM settings WHERE category = ? AND key = ?"
            await self.db.execute_query(query, (category.value, key), fetch=False)
            return True
        except Exception as e:
            logger.error(f"Error deleting setting: {str(e)}")
            return False

    async def get_feature_flag(self, name: str) -> Optional[FeatureFlag]:
        """Get feature flag"""
        query = "SELECT * FROM feature_flags WHERE name = ?"
        result = await self.db.execute_query(query, (name,))
        
        if not result:
            return None
            
        flag = result[0]
        return FeatureFlag(
            id=flag["id"],
            name=flag["name"],
            description=flag["description"],
            enabled=flag["enabled"],
            conditions=eval(flag["conditions"]) if flag["conditions"] else {},
            created_by=flag["created_by"],
            created_at=flag["created_at"],
            updated_by=flag["updated_by"],
            updated_at=flag["updated_at"]
        )

    async def set_feature_flag(
        self,
        name: str,
        enabled: bool,
        description: Optional[str] = None,
        conditions: Optional[Dict] = None
    ) -> Optional[FeatureFlag]:
        """Create or update feature flag"""
        try:
            existing = await self.get_feature_flag(name)
            
            if existing:
                # Update
                query = """
                UPDATE feature_flags 
                SET 
                    enabled = ?,
                    description = ?,
                    conditions = ?,
                    updated_by = ?,
                    updated_at = ?
                WHERE name = ?
                """
                
                await self.db.execute_query(
                    query,
                    (
                        enabled,
                        description,
                        str(conditions or {}),
                        "fdygg",
                        datetime.now(UTC),
                        name
                    ),
                    fetch=False
                )
            else:
                # Create
                query = """
                INSERT INTO feature_flags (
                    name, description, enabled,
                    conditions, created_by, created_at
                ) VALUES (?, ?, ?, ?, ?, ?)
                """
                
                await self.db.execute_query(
                    query,
                    (
                        name,
                        description,
                        enabled,
                        str(conditions or {}),
                        "fdygg",
                        datetime.now(UTC)
                    ),
                    fetch=False
                )
                
            return await self.get_feature_flag(name)
            
        except Exception as e:
            logger.error(f"Error setting feature flag: {str(e)}")
            return None

    async def check_feature_flag(
        self,
        name: str,
        context: Optional[Dict] = None
    ) -> bool:
        """Check if feature is enabled"""
        try:
            flag = await self.get_feature_flag(name)
            if not flag or not flag.enabled:
                return False
                
            # Check conditions if any
            if flag.conditions and context:
                # Role based
                if "user_roles" in flag.conditions:
                    user_role = context.get("user_role")
                    if user_role and user_role not in flag.conditions["user_roles"]:
                        return False
                        
                # Percentage rollout
                if "percentage" in flag.conditions:
                    user_id = context.get("user_id")
                    if user_id:
                        import hashlib
                        hash_input = f"{name}:{user_id}"
                        hash_value = int(hashlib.md5(hash_input.encode()).hexdigest(), 16)
                        percentage = hash_value % 100
                        if percentage >= flag.conditions["percentage"]:
                            return False
                            
            return True
            
        except Exception as e:
            logger.error(f"Error checking feature flag: {str(e)}")
            return False