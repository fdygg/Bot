from typing import Dict, List, Optional
from datetime import datetime, UTC
import logging
from .database_service import DatabaseService

logger = logging.getLogger(__name__)

class StockService:
    def __init__(self):
        self.db = DatabaseService()
        self.startup_time = datetime.now(UTC)
        logger.info(f"""
        StockService initialized:
        Time: 2025-05-28 17:16:09
        User: fdygg
        """)

    async def add_stock(
        self,
        product_code: str,
        content: str,
        added_by: str
    ) -> bool:
        """Add new stock item"""
        query = """
        INSERT INTO stock (
            product_code, content, added_by,
            added_at, updated_at
        ) VALUES (?, ?, ?, ?, ?)
        """
        now = datetime.now(UTC)
        try:
            await self.db.execute_query(
                query,
                (product_code, content, added_by, now, now),
                fetch=False
            )
            return True
        except:
            return False

    async def get_available_stock(
        self,
        product_code: str,
        limit: int = 10
    ) -> List[Dict]:
        """Get available stock for a product"""
        query = """
        SELECT *
        FROM stock
        WHERE product_code = ? AND status = 'available'
        ORDER BY added_at
        LIMIT ?
        """
        return await self.db.execute_query(query, (product_code, limit))

    async def update_stock_status(
        self,
        stock_id: int,
        status: str,
        buyer_id: str = None,
        seller_id: str = None
    ) -> bool:
        """Update stock status (available/sold/deleted)"""
        query = """
        UPDATE stock 
        SET 
            status = ?,
            buyer_id = ?,
            seller_id = ?,
            updated_at = ?
        WHERE id = ?
        """
        try:
            await self.db.execute_query(
                query,
                (status, buyer_id, seller_id, datetime.now(UTC), stock_id),
                fetch=False
            )
            return True
        except:
            return False

    async def get_stock_by_id(self, stock_id: int) -> Optional[Dict]:
        """Get stock item by ID"""
        query = """
        SELECT s.*, p.name as product_name, p.price
        FROM stock s
        JOIN products p ON s.product_code = p.code
        WHERE s.id = ?
        """
        result = await self.db.execute_query(query, (stock_id,))
        return result[0] if result else None

    async def get_stock_history(
        self,
        product_code: str = None,
        status: str = None,
        limit: int = 50
    ) -> List[Dict]:
        """Get stock history with filters"""
        conditions = []
        params = []
        
        if product_code:
            conditions.append("s.product_code = ?")
            params.append(product_code)
        if status:
            conditions.append("s.status = ?")
            params.append(status)

        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        query = f"""
        SELECT 
            s.*,
            p.name as product_name,
            p.price
        FROM stock s
        JOIN products p ON s.product_code = p.code
        WHERE {where_clause}
        ORDER BY s.added_at DESC
        LIMIT ?
        """
        params.append(limit)
        
        return await self.db.execute_query(query, tuple(params))

    async def bulk_add_stock(
        self,
        product_code: str,
        contents: List[str],
        added_by: str
    ) -> tuple[bool, int]:
        """Add multiple stock items at once"""
        success_count = 0
        now = datetime.now(UTC)
        
        query = """
        INSERT INTO stock (
            product_code, content, added_by,
            added_at, updated_at
        ) VALUES (?, ?, ?, ?, ?)
        """
        
        for content in contents:
            try:
                await self.db.execute_query(
                    query,
                    (product_code, content, added_by, now, now),
                    fetch=False
                )
                success_count += 1
            except:
                continue
                
        return success_count == len(contents), success_count