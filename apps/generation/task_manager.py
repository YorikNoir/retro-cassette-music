"""
Simple background task manager using Python threading.
No external dependencies (Redis/Celery) required.
"""
import logging
import threading
import queue
from typing import Callable, Any, Dict
from datetime import datetime
from django.conf import settings

logger = logging.getLogger(__name__)


class TaskManager:
    """Simple thread-based task manager for background jobs."""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """Singleton pattern to ensure one task manager per process."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the task manager."""
        if self._initialized:
            return
            
        self.task_queue = queue.Queue()
        self.active_tasks: Dict[str, threading.Thread] = {}
        self.max_workers = getattr(settings, 'MAX_CONCURRENT_TASKS', 3)
        self.workers = []
        self.running = False
        self._initialized = True
        
        # Start worker threads
        self.start()
    
    def start(self):
        """Start worker threads."""
        if self.running:
            logger.warning("Task manager already running")
            return
        
        self.running = True
        logger.info(f"Starting task manager with {self.max_workers} workers")
        
        for i in range(self.max_workers):
            worker = threading.Thread(
                target=self._worker,
                name=f"TaskWorker-{i+1}",
                daemon=True
            )
            worker.start()
            self.workers.append(worker)
        
        logger.info(f"Task manager started successfully")
    
    def stop(self):
        """Stop all worker threads."""
        logger.info("Stopping task manager...")
        self.running = False
        
        # Add sentinel values to wake up workers
        for _ in range(self.max_workers):
            self.task_queue.put(None)
        
        # Wait for workers to finish
        for worker in self.workers:
            worker.join(timeout=5)
        
        self.workers.clear()
        logger.info("Task manager stopped")
    
    def _worker(self):
        """Worker thread that processes tasks from the queue."""
        worker_name = threading.current_thread().name
        logger.debug(f"{worker_name} started")
        
        while self.running:
            try:
                # Get task from queue (blocking with timeout)
                task = self.task_queue.get(timeout=1)
                
                if task is None:  # Sentinel value to stop
                    break
                
                task_id, func, args, kwargs = task
                
                logger.info(f"{worker_name} processing task: {task_id}")
                
                try:
                    # Execute the task
                    result = func(*args, **kwargs)
                    logger.info(f"{worker_name} completed task: {task_id}")
                except Exception as e:
                    logger.error(f"{worker_name} task {task_id} failed: {str(e)}")
                    logger.exception(e)
                finally:
                    # Mark task as done
                    self.task_queue.task_done()
                    if task_id in self.active_tasks:
                        del self.active_tasks[task_id]
                        
            except queue.Empty:
                # No tasks available, continue waiting
                continue
            except Exception as e:
                logger.error(f"{worker_name} error: {str(e)}")
                logger.exception(e)
        
        logger.debug(f"{worker_name} stopped")
    
    def submit_task(
        self,
        task_id: str,
        func: Callable,
        *args,
        **kwargs
    ) -> bool:
        """
        Submit a task to be executed in the background.
        
        Args:
            task_id: Unique identifier for the task
            func: The function to execute
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function
        
        Returns:
            bool: True if task was submitted successfully
        """
        if not self.running:
            logger.error("Task manager not running")
            return False
        
        if task_id in self.active_tasks:
            logger.warning(f"Task {task_id} already active")
            return False
        
        try:
            # Add task to queue
            self.task_queue.put((task_id, func, args, kwargs))
            self.active_tasks[task_id] = threading.current_thread()
            
            logger.info(f"Task {task_id} submitted to queue")
            return True
        except Exception as e:
            logger.error(f"Failed to submit task {task_id}: {str(e)}")
            return False
    
    def get_queue_size(self) -> int:
        """Get number of tasks waiting in queue."""
        return self.task_queue.qsize()
    
    def get_active_count(self) -> int:
        """Get number of active tasks."""
        return len(self.active_tasks)
    
    def is_task_active(self, task_id: str) -> bool:
        """Check if a task is currently running."""
        return task_id in self.active_tasks


# Global task manager instance
_task_manager = None


def get_task_manager() -> TaskManager:
    """Get the global task manager instance."""
    global _task_manager
    if _task_manager is None:
        _task_manager = TaskManager()
    return _task_manager


def submit_background_task(task_id: str, func: Callable, *args, **kwargs) -> bool:
    """
    Convenience function to submit a background task.
    
    Args:
        task_id: Unique identifier for the task
        func: The function to execute
        *args: Positional arguments for the function
        **kwargs: Keyword arguments for the function
    
    Returns:
        bool: True if task was submitted successfully
    """
    manager = get_task_manager()
    return manager.submit_task(task_id, func, *args, **kwargs)
