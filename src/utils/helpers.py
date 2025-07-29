"""Helper utilities for the search agent application."""
import json
import time
import csv
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable, TypeVar
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import wraps
from ..utils.logger import get_logger
logger = get_logger(__name__)
T = TypeVar('T')
R = TypeVar('R')
def retry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    backoff_factor: float = 2.0
) -> Callable:
    """
    Decorator to retry function calls with exponential backoff.
    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay between retries in seconds
        max_delay: Maximum delay between retries in seconds  
        backoff_factor: Multiplier for delay on each retry
    Returns:
        Decorated function with retry logic
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            delay = base_delay
            last_exception = None
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt == max_retries:
                        logger.error(f"Function {func.__name__} failed after {max_retries} retries: {e}")
                        raise e
                    logger.warning(f"Attempt {attempt + 1} failed for {func.__name__}: {e}. Retrying in {delay:.1f}s")
                    time.sleep(delay)
                    delay = min(delay * backoff_factor, max_delay)
            raise last_exception
        return wrapper
    return decorator
def execute_parallel_tasks(
    tasks: List[Callable[[], T]],
    max_workers: int = 5,
    timeout: Optional[float] = None
) -> List[T]:
    """
    Execute multiple tasks in parallel using ThreadPoolExecutor.
    Args:
        tasks: List of callable tasks to execute
        max_workers: Maximum number of worker threads
        timeout: Optional timeout for all tasks in seconds
    Returns:
        List of results from all tasks
    """
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_task = {executor.submit(task): i for i, task in enumerate(tasks)}
        for future in as_completed(future_to_task, timeout=timeout):
            task_index = future_to_task[future]
            try:
                result = future.result()
                results.append((task_index, result))
                logger.debug(f"Task {task_index} completed successfully")
            except Exception as e:
                logger.error(f"Task {task_index} failed: {e}")
                results.append((task_index, None))
    results.sort(key=lambda x: x[0])
    return [result for _, result in results]
def load_json_file(file_path: str) -> Dict[str, Any]:
    """
    Load and parse a JSON file.
    Args:
        file_path: Path to the JSON file
    Returns:
        Parsed JSON data as dictionary
    Raises:
        FileNotFoundError: If file doesn't exist
        json.JSONDecodeError: If file contains invalid JSON
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"JSON file not found: {file_path}")
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in file {file_path}: {e}")
        raise
def save_json_file(data: Dict[str, Any], file_path: str, indent: int = 2) -> None:
    """
    Save data to a JSON file.
    Args:
        data: Data to save
        file_path: Path to save the file
        indent: JSON indentation level
    """
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)
    logger.debug(f"Saved JSON data to {file_path}")
def save_results_to_csv(
    results: List[Dict[str, Any]], 
    file_path: str,
    fieldnames: Optional[List[str]] = None
) -> None:
    """
    Save evaluation results to a CSV file.
    Args:
        results: List of result dictionaries
        file_path: Path to save the CSV file
        fieldnames: Optional list of field names for CSV header
    """
    if not results:
        logger.warning("No results to save to CSV")
        return
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if fieldnames is None:
        fieldnames = list(results[0].keys())
    with open(path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    logger.info(f"Saved {len(results)} results to CSV: {file_path}")
def normalize_job_category(category: str) -> str:
    """
    Normalize job category name to a standard format.
    Args:
        category: Raw category name
    Returns:
        Normalized category name
    """
    return category.replace("_", " ").replace(".yml", "").strip().lower()
def calculate_weighted_score(
    scores: Dict[str, float], 
    weights: Dict[str, float]
) -> float:
    """
    Calculate weighted average score from multiple components.
    Args:
        scores: Dictionary of score components
        weights: Dictionary of weights for each component
    Returns:
        Weighted average score
    """
    total_weight = 0.0
    weighted_sum = 0.0
    for component, score in scores.items():
        weight = weights.get(component, 0.0)
        weighted_sum += score * weight
        total_weight += weight
    return weighted_sum / total_weight if total_weight > 0 else 0.0
def format_performance_metrics(results: Dict[str, Any]) -> str:
    """
    Format performance metrics for display.
    Args:
        results: Dictionary containing performance metrics
    Returns:
        Formatted string representation
    """
    if not results:
        return "No results available"
    lines = [
        "🏆 PERFORMANCE METRICS",
        "=" * 50
    ]
    for category, score in results.items():
        if isinstance(score, (int, float)):
            emoji = "🥇" if score > 70 else "🥈" if score > 50 else "🥉" if score > 30 else "📈" if score > 10 else "⚠️"
            lines.append(f"{emoji} {category:<30}: {score:>8.2f}")
    return "\n".join(lines)
def chunk_list(lst: List[T], chunk_size: int) -> List[List[T]]:
    """
    Split a list into chunks of specified size.
    Args:
        lst: List to chunk
        chunk_size: Size of each chunk
    Returns:
        List of chunks
    """
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]
class PerformanceTimer:
    """Context manager for measuring execution time."""
    def __init__(self, operation_name: str):
        self.operation_name = operation_name
        self.start_time = None
        self.end_time = None
    def __enter__(self):
        self.start_time = time.time()
        logger.debug(f"Starting operation: {self.operation_name}")
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
        duration = self.end_time - self.start_time
        logger.info(f"Operation '{self.operation_name}' completed in {duration:.2f} seconds")
        if exc_type is not None:
            logger.error(f"Operation '{self.operation_name}' failed with {exc_type.__name__}: {exc_val}")
    @property
    def duration(self) -> Optional[float]:
        """Get the duration of the operation."""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return None 