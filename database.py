import sqlite3
import logging
import time
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)

def get_connection(max_retries: int = 3, timeout: int = 5) -> sqlite3.Connection:
    """Get SQLite database connection with retry mechanism"""
    for attempt in range(max_retries):
        try:
            conn = sqlite3.connect('shop.db', timeout=timeout)
            conn.row_factory = sqlite3.Row
            
            # Enable foreign keys and set pragmas
            cursor = conn.cursor()
            cursor.execute("PRAGMA foreign_keys = ON")
            cursor.execute("PRAGMA journal_mode = WAL")
            cursor.execute("PRAGMA busy_timeout = 5000")
            
            return conn
        except sqlite3.Error as e:
            if attempt == max_retries - 1:
                logger.error(f"Failed to connect to database after {max_retries} attempts: {e}")
                raise
            logger.warning(f"Database connection attempt {attempt + 1} failed, retrying... Error: {e}")
            time.sleep(0.1 * (attempt + 1))

def setup_database():
    """Initialize database tables"""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Modify users table - add web-related columns
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                growid TEXT PRIMARY KEY,
                balance_wl INTEGER DEFAULT 0,
                balance_dl INTEGER DEFAULT 0,
                balance_bgl INTEGER DEFAULT 0,
                balance_rupiah INTEGER DEFAULT 0,
                website_username TEXT UNIQUE,
                website_password TEXT,
                is_web_active INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_by TEXT DEFAULT 'system',
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_by TEXT DEFAULT 'system'
            )
        """)

        # User Discord mapping table - unchanged
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_growid (
                discord_id TEXT PRIMARY KEY,
                growid TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (growid) REFERENCES users(growid) ON DELETE CASCADE
            )
        """)

        # Products table - unchanged
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                code TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                price INTEGER NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Stock table - unchanged
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS stock (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_code TEXT NOT NULL,
                content TEXT NOT NULL UNIQUE,
                status TEXT DEFAULT 'available' CHECK (status IN ('available', 'sold', 'deleted')),
                added_by TEXT NOT NULL,
                buyer_id TEXT,
                seller_id TEXT,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (product_code) REFERENCES products(code) ON DELETE CASCADE
            )
        """)

        # Modify transactions table - add platform and currency columns
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                growid TEXT NOT NULL,
                platform TEXT DEFAULT 'discord' CHECK (platform IN ('discord', 'web')),
                type TEXT NOT NULL,
                currency TEXT NOT NULL,
                amount INTEGER NOT NULL,
                details TEXT NOT NULL,
                old_balance TEXT,
                new_balance TEXT,
                items_count INTEGER DEFAULT 0,
                total_price INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_by TEXT DEFAULT 'system',
                FOREIGN KEY (growid) REFERENCES users(growid) ON DELETE CASCADE
            )
        """)

        # Add conversion_rates table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversion_rates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                currency TEXT NOT NULL CHECK (currency IN ('wl', 'dl', 'bgl')),
                rate INTEGER NOT NULL,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_by TEXT DEFAULT 'system',
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_by TEXT DEFAULT 'system'
            )
        """)

        # World info table - unchanged
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS world_info (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                world TEXT NOT NULL,
                owner TEXT NOT NULL,
                bot TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Bot settings table - unchanged
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bot_settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Blacklist table - unchanged
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS blacklist (
                growid TEXT PRIMARY KEY,
                added_by TEXT NOT NULL,
                reason TEXT,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (growid) REFERENCES users(growid) ON DELETE CASCADE
            )
        """)

        # Admin logs table - add platform field
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS admin_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                admin_id TEXT NOT NULL,
                platform TEXT DEFAULT 'discord' CHECK (platform IN ('discord', 'web')),
                action TEXT NOT NULL,
                target TEXT,
                details TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Role permissions table - unchanged
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS role_permissions (
                role_id TEXT PRIMARY KEY,
                permissions TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # User activity table - add platform field
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_activity (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                discord_id TEXT NOT NULL,
                platform TEXT DEFAULT 'discord' CHECK (platform IN ('discord', 'web')),
                activity_type TEXT NOT NULL,
                details TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (discord_id) REFERENCES user_growid(discord_id)
            )
        """)

        # Cache table - unchanged
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cache_table (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                expires_at TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Add/Update triggers for timestamp management
        triggers = [
            # Users table trigger
            """
            CREATE TRIGGER IF NOT EXISTS update_users_timestamp 
            AFTER UPDATE ON users
            BEGIN
                UPDATE users 
                SET 
                    updated_at = CURRENT_TIMESTAMP,
                    updated_by = 'system'
                WHERE growid = NEW.growid;
            END;
            """,
            # Products table trigger
            """
            CREATE TRIGGER IF NOT EXISTS update_products_timestamp 
            AFTER UPDATE ON products
            BEGIN
                UPDATE products 
                SET updated_at = CURRENT_TIMESTAMP
                WHERE code = NEW.code;
            END;
            """,
            # Stock table trigger
            """
            CREATE TRIGGER IF NOT EXISTS update_stock_timestamp 
            AFTER UPDATE ON stock
            BEGIN
                UPDATE stock 
                SET updated_at = CURRENT_TIMESTAMP
                WHERE id = NEW.id;
            END;
            """,
            # Bot settings trigger
            """
            CREATE TRIGGER IF NOT EXISTS update_bot_settings_timestamp 
            AFTER UPDATE ON bot_settings
            BEGIN
                UPDATE bot_settings 
                SET updated_at = CURRENT_TIMESTAMP
                WHERE key = NEW.key;
            END;
            """,
            # Conversion rates trigger
            """
            CREATE TRIGGER IF NOT EXISTS update_conversion_rates_timestamp 
            AFTER UPDATE ON conversion_rates
            BEGIN
                UPDATE conversion_rates 
                SET 
                    updated_at = CURRENT_TIMESTAMP,
                    updated_by = 'system'
                WHERE id = NEW.id;
            END;
            """,
            # Role permissions trigger
            """
            CREATE TRIGGER IF NOT EXISTS update_role_permissions_timestamp 
            AFTER UPDATE ON role_permissions
            BEGIN
                UPDATE role_permissions 
                SET updated_at = CURRENT_TIMESTAMP
                WHERE role_id = NEW.role_id;
            END;
            """
        ]

        for trigger in triggers:
            cursor.execute(trigger)

        # Create/Update indexes
        indexes = [
            ("idx_user_growid_discord", "user_growid(discord_id)"),
            ("idx_user_growid_growid", "user_growid(growid)"),
            ("idx_users_website_username", "users(website_username)"),
            ("idx_stock_product_code", "stock(product_code)"),
            ("idx_stock_status", "stock(status)"),
            ("idx_transactions_growid", "transactions(growid)"),
            ("idx_transactions_platform", "transactions(platform)"),
            ("idx_transactions_created", "transactions(created_at)"),
            ("idx_blacklist_growid", "blacklist(growid)"),
            ("idx_admin_logs_admin", "admin_logs(admin_id)"),
            ("idx_admin_logs_platform", "admin_logs(platform)"),
            ("idx_admin_logs_created", "admin_logs(created_at)"),
            ("idx_user_activity_discord", "user_activity(discord_id)"),
            ("idx_user_activity_platform", "user_activity(platform)"),
            ("idx_conversion_rates_currency", "conversion_rates(currency)"),
            ("idx_conversion_rates_active", "conversion_rates(is_active)")
        ]

        for idx_name, idx_cols in indexes:
            cursor.execute(f"CREATE INDEX IF NOT EXISTS {idx_name} ON {idx_cols}")

        # Insert default data
        cursor.execute("""
            INSERT OR IGNORE INTO world_info (id, world, owner, bot)
            VALUES (1, 'YOURWORLD', 'OWNER', 'BOT')
        """)

        cursor.execute("""
            INSERT OR IGNORE INTO role_permissions (role_id, permissions)
            VALUES ('admin', 'all')
        """)

        # Insert default conversion rates if not exists
        default_rates = [
            ('wl', 3000),   # 1 WL = 3000 rupiah
            ('dl', 300000), # 1 DL = 300000 rupiah
            ('bgl', 30000000) # 1 BGL = 30000000 rupiah
        ]
        
        for currency, rate in default_rates:
            cursor.execute("""
                INSERT OR IGNORE INTO conversion_rates 
                (currency, rate, created_by) 
                VALUES (?, ?, 'system')
            """, (currency, rate))

        conn.commit()
        logger.info("""
        Database setup completed successfully
        Time: 2025-05-28 17:07:17
        User: fdygg
        """)

    except sqlite3.Error as e:
        logger.error(f"Database setup error: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()

# Rest of the code (verify_database and main) remains unchanged

def verify_database():
    """Verify database integrity and tables existence"""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Check all tables exist
        tables = [
            'users', 'user_growid', 'products', 'stock', 
            'transactions', 'world_info', 'bot_settings', 'blacklist',
            'admin_logs', 'role_permissions', 'user_activity', 'cache_table'
        ]

        missing_tables = []
        for table in tables:
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
            if not cursor.fetchone():
                missing_tables.append(table)

        if missing_tables:
            logger.error(f"Missing tables: {', '.join(missing_tables)}")
            raise sqlite3.Error(f"Database verification failed: missing tables")

        # Check database integrity
        cursor.execute("PRAGMA integrity_check")
        if cursor.fetchone()['integrity_check'] != 'ok':
            raise sqlite3.Error("Database integrity check failed")

        # Clean expired cache entries
        cursor.execute("DELETE FROM cache_table WHERE expires_at < CURRENT_TIMESTAMP")
        conn.commit()

        logger.info("Database verification completed successfully")
        return True

    except sqlite3.Error as e:
        logger.error(f"Database verification error: {e}")
        return False
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('database.log')
        ]
    )
    
    try:
        setup_database()
        if not verify_database():
            logger.error("Database verification failed. Attempting to recreate database...")
            # Backup existing database if it exists
            import shutil
            from pathlib import Path
            if Path('shop.db').exists():
                backup_path = f"shop.db.backup_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
                shutil.copy2('shop.db', backup_path)
                logger.info(f"Created database backup: {backup_path}")
            
            # Recreate database
            Path('shop.db').unlink(missing_ok=True)
            setup_database()
            if verify_database():
                logger.info("Database successfully recreated")
            else:
                logger.error("Failed to recreate database")
        else:
            logger.info("Database initialization complete")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}", exc_info=True)