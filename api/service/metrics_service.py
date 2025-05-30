from api.service.logs_service import LogsService
from api.service.database_service import DatabaseService
from datetime import datetime
import psutil
import time

class MetricsService:
    def __init__(self):
        self.logger = LogsService()
        self.db = DatabaseService()
        
    def collect_metrics(self, request, response):
        """Collect metrics from request and response"""
        metrics = {
            'timestamp': datetime.utcnow(),
            'endpoint': request.path,
            'method': request.method,
            'response_time': self.calculate_response_time(request),
            'status_code': response.status_code,
            'cpu_usage': psutil.cpu_percent(),
            'memory_usage': psutil.virtual_memory().percent
        }
        
        # Store metrics in cache
        self.db.cache.set(
            f"metrics:{request.id}",
            metrics,
            expire=3600 # 1 hour
        )
        
        # Log if response time exceeds threshold
        if metrics['response_time'] > 1.0: # 1 second
            self.logger.warning(
                f"Slow response detected: {metrics['response_time']}s for {request.path}"
            )
            
    def calculate_response_time(self, request):
        """Calculate response time in seconds"""
        start_time = getattr(request, '_start_time', time.time())
        return time.time() - start_time

    def export_metrics(self):
        """Export metrics to monitoring system"""
        try:
            metrics = self.db.cache.get_all("metrics:*")
            # Here you would integrate with your monitoring system
            # Example: Prometheus, Grafana, etc.
            return metrics
        except Exception as e:
            self.logger.error(f"Failed to export metrics: {str(e)}")
            return None