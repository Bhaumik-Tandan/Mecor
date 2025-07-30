"""Monitoring utilities for tracking system performance and bottlenecks."""
import time
import threading
import psutil
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from .logger import get_logger

logger = get_logger(__name__)

@dataclass
class SystemMetrics:
    """System resource metrics at a point in time."""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    memory_available_gb: float
    active_threads: int
    
    @property
    def is_overloaded(self) -> bool:
        """Check if system is overloaded based on conservative thresholds."""
        return self.cpu_percent > 75 or self.memory_percent > 80

@dataclass
class PerformanceTracker:
    """Track performance metrics for operations."""
    operation_name: str
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    thread_id: int = field(default_factory=threading.get_ident)
    success: bool = True
    error_message: Optional[str] = None
    
    @property
    def duration(self) -> float:
        """Get operation duration in seconds."""
        end = self.end_time if self.end_time else time.time()
        return end - self.start_time
    
    def finish(self, success: bool = True, error_message: Optional[str] = None):
        """Mark operation as finished."""
        self.end_time = time.time()
        self.success = success
        self.error_message = error_message

class SafeSystemMonitor:
    """Thread-safe system monitoring with conservative resource checking."""
    
    def __init__(self, check_interval: float = 5.0):
        self.check_interval = check_interval
        self.metrics_history: List[SystemMetrics] = []
        self.performance_trackers: List[PerformanceTracker] = []
        self._lock = threading.Lock()
        self._monitoring = False
        self._monitor_thread: Optional[threading.Thread] = None
        
        logger.info(f"🔍 Initialized SafeSystemMonitor with {check_interval}s interval")
    
    def get_current_metrics(self) -> SystemMetrics:
        """Get current system metrics."""
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_available_gb = memory.available / (1024**3)
            active_threads = threading.active_count()
            
            return SystemMetrics(
                timestamp=datetime.now(),
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
                memory_available_gb=memory_available_gb,
                active_threads=active_threads
            )
        except Exception as e:
            logger.warning(f"Failed to get system metrics: {e}")
            # Return safe defaults if monitoring fails
            return SystemMetrics(
                timestamp=datetime.now(),
                cpu_percent=0.0,
                memory_percent=0.0,
                memory_available_gb=0.0,
                active_threads=threading.active_count()
            )
    
    def is_system_safe(self) -> bool:
        """Check if system is safe to continue operations."""
        metrics = self.get_current_metrics()
        
        if metrics.is_overloaded:
            logger.warning(f"⚠️ System overloaded: CPU {metrics.cpu_percent}%, Memory {metrics.memory_percent}%")
            return False
        
        if metrics.active_threads > 50:  # Conservative thread limit
            logger.warning(f"⚠️ High thread count: {metrics.active_threads}")
            return False
        
        return True
    
    def wait_for_safe_conditions(self, max_wait: float = 30.0) -> bool:
        """Wait for system to be in safe condition for operations."""
        start_wait = time.time()
        
        while time.time() - start_wait < max_wait:
            if self.is_system_safe():
                return True
            
            logger.info("⏳ Waiting for safe system conditions...")
            time.sleep(2.0)
        
        logger.warning(f"⚠️ System did not reach safe conditions within {max_wait}s")
        return False
    
    def start_performance_tracking(self, operation_name: str) -> PerformanceTracker:
        """Start tracking performance for an operation."""
        tracker = PerformanceTracker(operation_name=operation_name)
        
        with self._lock:
            self.performance_trackers.append(tracker)
        
        thread_id = threading.get_ident()
        logger.debug(f"🧵 Thread {thread_id}: Started tracking '{operation_name}'")
        return tracker
    
    def get_performance_summary(self) -> Dict[str, any]:
        """Get summary of performance metrics."""
        with self._lock:
            if not self.performance_trackers:
                return {"message": "No performance data available"}
            
            successful_ops = [t for t in self.performance_trackers if t.success and t.end_time]
            failed_ops = [t for t in self.performance_trackers if not t.success]
            
            if successful_ops:
                durations = [t.duration for t in successful_ops]
                avg_duration = sum(durations) / len(durations)
                max_duration = max(durations)
                min_duration = min(durations)
            else:
                avg_duration = max_duration = min_duration = 0.0
            
            operation_counts = {}
            for tracker in self.performance_trackers:
                op_name = tracker.operation_name
                operation_counts[op_name] = operation_counts.get(op_name, 0) + 1
            
            return {
                "total_operations": len(self.performance_trackers),
                "successful_operations": len(successful_ops),
                "failed_operations": len(failed_ops),
                "average_duration": avg_duration,
                "max_duration": max_duration,
                "min_duration": min_duration,
                "operation_counts": operation_counts,
                "success_rate": len(successful_ops) / len(self.performance_trackers) * 100 if self.performance_trackers else 0
            }
    
    def log_performance_summary(self):
        """Log a summary of performance metrics."""
        summary = self.get_performance_summary()
        
        if "message" in summary:
            logger.info(summary["message"])
            return
        
        logger.info("📊 PERFORMANCE SUMMARY:")
        logger.info(f"   Total Operations: {summary['total_operations']}")
        logger.info(f"   Success Rate: {summary['success_rate']:.1f}%")
        logger.info(f"   Average Duration: {summary['average_duration']:.2f}s")
        logger.info(f"   Duration Range: {summary['min_duration']:.2f}s - {summary['max_duration']:.2f}s")
        
        if summary['operation_counts']:
            logger.info("   Operation Breakdown:")
            for op_name, count in summary['operation_counts'].items():
                logger.info(f"      {op_name}: {count}")
    
    def start_monitoring(self):
        """Start background system monitoring."""
        if self._monitoring:
            logger.warning("Monitoring already started")
            return
        
        self._monitoring = True
        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()
        logger.info("🔍 Started background system monitoring")
    
    def stop_monitoring(self):
        """Stop background system monitoring."""
        self._monitoring = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5.0)
        logger.info("🔍 Stopped background system monitoring")
    
    def _monitor_loop(self):
        """Background monitoring loop."""
        while self._monitoring:
            try:
                metrics = self.get_current_metrics()
                
                with self._lock:
                    self.metrics_history.append(metrics)
                    # Keep only last 100 metrics to prevent memory buildup
                    if len(self.metrics_history) > 100:
                        self.metrics_history = self.metrics_history[-100:]
                
                if metrics.is_overloaded:
                    logger.warning(f"⚠️ System overload detected: CPU {metrics.cpu_percent}%, Memory {metrics.memory_percent}%")
                
                time.sleep(self.check_interval)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(self.check_interval)

# Global monitor instance with conservative settings
system_monitor = SafeSystemMonitor(check_interval=10.0)  # Check every 10 seconds

class SafeOperationContext:
    """Context manager for safe operation execution with monitoring."""
    
    def __init__(self, operation_name: str, wait_for_safe: bool = True):
        self.operation_name = operation_name
        self.wait_for_safe = wait_for_safe
        self.tracker: Optional[PerformanceTracker] = None
    
    def __enter__(self):
        if self.wait_for_safe:
            if not system_monitor.wait_for_safe_conditions():
                logger.warning(f"⚠️ Starting '{self.operation_name}' despite unsafe conditions")
        
        self.tracker = system_monitor.start_performance_tracking(self.operation_name)
        return self.tracker
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.tracker:
            success = exc_type is None
            error_message = str(exc_val) if exc_val else None
            self.tracker.finish(success=success, error_message=error_message)
            
            if not success:
                logger.error(f"❌ Operation '{self.operation_name}' failed: {error_message}")
            else:
                logger.debug(f"✅ Operation '{self.operation_name}' completed in {self.tracker.duration:.2f}s")

def safe_operation(operation_name: str, wait_for_safe: bool = True):
    """Decorator for safe operation execution with monitoring."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            with SafeOperationContext(operation_name, wait_for_safe):
                return func(*args, **kwargs)
        return wrapper
    return decorator 