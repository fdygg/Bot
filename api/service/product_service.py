from typing import Dict, List, Optional
from datetime import datetime, UTC
import logging
from .database_service import DatabaseService

logger = logging.getLogger(__name__)

class ProductService:
    def __init__(self):
        self.db = DatabaseService()
        self.startup_time = datetime.now(UTC)
        logger.info(f"""
        ProductService initialized:
        Time: 2025-05-28 17:16:09
        User: fdygg
        """)

    async def create_product(
        self, 
        code: str,
        name: str,
        price: int,
        description: str = None
    ) -> bool:
        """Create new product"""
        query = """
        INSERT INTO products (
            code, name, price, description,
            created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?)
        """
        now = datetime.now(UTC)
        try:
            await self.db.execute_query(
                query,
                (code, name, price, description, now, now),
                fetch=False
            )
            return True
        except:
            return False

    async def get_product(self, code: str) -> Optional[Dict]:
        """Get product by code"""
        query = """
        SELECT 
            p.*,
            COUNT(CASE WHEN s.status = 'available' THEN 1 END) as stock_available
        FROM products p
        LEFT JOIN stock s ON p.code = s.product_code
        WHERE p.code = ?
        GROUP BY p.code
        """
        result = await self.db.execute_query(query, (code,))
        return result[0] if result else None

    async def get_all_products(self, include_stock: bool = True) -> List[Dict]:
        """Get all products with optional stock count"""
        if include_stock:
            query = """
            SELECT 
                p.*,
                COUNT(CASE WHEN s.status = 'available' THEN 1 END) as stock_available
            FROM products p
            LEFT JOIN stock s ON p.code = s.product_code
            GROUP BY p.code
            ORDER BY p.code
            """
        else:
            query = "SELECT * FROM products ORDER BY code"
        
        return await self.db.execute_query(query)

    async def update_product(
        self,
        code: str,
        name: str = None,
        price: int = None,
        description: str = None
    ) -> bool:
        """Update product details"""
        updates = []
        params = []
        if name is not None:
            updates.append("name = ?")
            params.append(name)
        if price is not None:
            updates.append("price = ?")
            params.append(price)
        if description is not None:
            updates.append("description = ?")
            params.append(description)
        
        if not updates:
            return False

        query = f"""
        UPDATE products 
        SET {', '.join(updates)}
        WHERE code = ?
        """
        params.append(code)
        
        try:
            await self.db.execute_query(query, tuple(params), fetch=False)
            return True
        except:
            return False

    async def delete_product(self, code: str) -> bool:
        """Delete product and its stock"""
        query = "DELETE FROM products WHERE code = ?"
        try:
            await self.db.execute_query(query, (code,), fetch=False)
            return True
        except:
            return False