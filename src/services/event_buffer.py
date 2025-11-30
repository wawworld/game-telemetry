"""Thread-safe event buffer with asynchronous flushing."""

import asyncio
from collections import deque
from threading import Lock
from typing import Callable, Optional, Any
from utils.logging import get_logger

logger = get_logger(__name__)


class EventBuffer:
    """Thread-safe in-memory buffer for events before persistent storage.
    
    Buffers events and automatically flushes them using async I/O to minimize
    performance impact during high-frequency event periods.
    """
    
    def __init__(
        self,
        flush_callback: Callable[[list], None],
        max_size: int = 1000,
        flush_interval_seconds: float = 1.0,
    ):
        """Initialize event buffer.
        
        Args:
            flush_callback: Function to call when flushing buffered items
            max_size: Maximum buffer size before forced flush
            flush_interval_seconds: Time interval for periodic flushes
        """
        self._buffer = deque()
        self._lock = Lock()
        self._flush_callback = flush_callback
        self._max_size = max_size
        self._flush_interval = flush_interval_seconds
        self._running = False
        self._flush_task: Optional[asyncio.Task] = None
        self._stats = {
            "items_buffered": 0,
            "items_flushed": 0,
            "flush_count": 0,
        }
    
    def add(self, item: Any) -> None:
        """Add an item to the buffer (thread-safe).
        
        Args:
            item: Item to buffer
        """
        with self._lock:
            self._buffer.append(item)
            self._stats["items_buffered"] += 1
            
            # Force flush if buffer is full
            if len(self._buffer) >= self._max_size:
                logger.warning(f"Buffer full ({len(self._buffer)} items), forcing flush")
                asyncio.create_task(self._flush_internal())
    
    async def start(self) -> None:
        """Start periodic flushing."""
        if self._running:
            logger.warning("Buffer already running")
            return
        
        self._running = True
        self._flush_task = asyncio.create_task(self._periodic_flush())
        logger.info(f"Event buffer started (max_size={self._max_size}, interval={self._flush_interval}s)")
    
    async def stop(self) -> None:
        """Stop periodic flushing and flush remaining items."""
        if not self._running:
            return
        
        self._running = False
        
        if self._flush_task:
            self._flush_task.cancel()
            try:
                await self._flush_task
            except asyncio.CancelledError:
                pass
        
        # Final flush
        await self._flush_internal()
        logger.info("Event buffer stopped")
    
    async def _periodic_flush(self) -> None:
        """Periodically flush buffered items."""
        while self._running:
            try:
                await asyncio.sleep(self._flush_interval)
                await self._flush_internal()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error during periodic flush: {e}")
    
    async def _flush_internal(self) -> None:
        """Flush buffered items using the callback."""
        items_to_flush = []
        
        with self._lock:
            if not self._buffer:
                return
            
            items_to_flush = list(self._buffer)
            self._buffer.clear()
        
        if items_to_flush:
            try:
                await asyncio.get_event_loop().run_in_executor(
                    None, self._flush_callback, items_to_flush
                )
                self._stats["items_flushed"] += len(items_to_flush)
                self._stats["flush_count"] += 1
                logger.debug(f"Flushed {len(items_to_flush)} items to storage")
            except Exception as e:
                logger.error(f"Error flushing buffer: {e}")
                # Re-add items to buffer on failure
                with self._lock:
                    self._buffer.extendleft(reversed(items_to_flush))
    
    async def flush(self) -> None:
        """Manually trigger a flush."""
        await self._flush_internal()
    
    def size(self) -> int:
        """Get current buffer size (thread-safe)."""
        with self._lock:
            return len(self._buffer)
    
    def get_stats(self) -> dict:
        """Get buffer statistics."""
        with self._lock:
            return {
                **self._stats,
                "current_size": len(self._buffer),
            }
