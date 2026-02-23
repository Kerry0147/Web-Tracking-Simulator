import asyncio
from typing import Dict, List, Optional

class StreamManager:
    def __init__(self):
        # Maps session_id -> list of asyncio.Queue (one per SSE connection/tab)
        self.active_connections: Dict[str, List[asyncio.Queue]] = {}

    async def connect(self, session_id: str) -> asyncio.Queue:
        """Create a queue for a new SSE connection and append it to the session's list."""
        queue = asyncio.Queue()
        if session_id not in self.active_connections:
            self.active_connections[session_id] = []
        self.active_connections[session_id].append(queue)
        print(f"🔌 SSE Connected: {session_id} (tabs: {len(self.active_connections[session_id])})")
        return queue

    def disconnect(self, session_id: str, queue: asyncio.Queue):
        """Remove only the specific queue that disconnected, not the entire session."""
        if session_id in self.active_connections:
            try:
                self.active_connections[session_id].remove(queue)
            except ValueError:
                pass
            # Clean up empty list
            if not self.active_connections[session_id]:
                del self.active_connections[session_id]
            print(f"🔌 SSE Disconnected: {session_id}")

    async def broadcast_to_session(self, session_id: str, message: dict):
        """Push a message to ALL active queues for a session."""
        if session_id in self.active_connections:
            for queue in self.active_connections[session_id]:
                await queue.put(message)

# Global Instance
stream_manager = StreamManager()
