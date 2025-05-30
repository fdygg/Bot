from api.service.database_service import DatabaseService
from api.service.user_service import UserService
from api.service.auth_service import AuthService
from datetime import datetime, timedelta

class RateLimitService:
    def __init__(self):
        self.db = DatabaseService()
        self.user_service = UserService()
        self.auth_service = AuthService()
        
        # Default rate limits
        self.default_limit = 100  # requests
        self.default_window = 3600  # 1 hour in seconds
        
    def check_rate_limit(self, request):
        """Check if request exceeds rate limit"""
        user_id = self.auth_service.get_user_id(request)
        endpoint = request.path
        
        # Get user's role and custom limits
        user = self.user_service.get_user(user_id)
        limit = self.get_user_limit(user)
        
        # Check cache for existing count
        cache_key = f"ratelimit:{user_id}:{endpoint}"
        current_count = self.db.cache.get(cache_key) or 0
        
        if current_count >= limit:
            return False
            
        # Increment counter
        self.db.cache.incr(cache_key)
        if current_count == 0:
            self.db.cache.expire(cache_key, self.default_window)
            
        return True
        
    def get_user_limit(self, user):
        """Get rate limit based on user role"""
        role_limits = {
            'admin': 1000,
            'premium': 500,
            'basic': 100
        }
        return role_limits.get(user.role, self.default_limit)

    def reset_limits(self, user_id):
        """Reset rate limits for user"""
        pattern = f"ratelimit:{user_id}:*"
        self.db.cache.delete_pattern(pattern)