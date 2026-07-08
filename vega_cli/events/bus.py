from typing import Callable, Dict, List, Any
from vega_cli.types.event import Event

class EventBus:
    """
    A lightweight, synchronous event bus allowing different parts of Vega
    to publish and subscribe to agent lifecycle events.
    """
    def __init__(self):
        self._listeners: Dict[str, List[Callable[[Event], Any]]] = {}

    def subscribe(self, event_type: str, listener: Callable[[Event], Any]):
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        self._listeners[event_type].append(listener)

    def publish(self, event_type: str, data: Dict[str, Any]):
        event = Event(type=event_type, data=data)
        for listener in self._listeners.get(event_type, []):
            try:
                listener(event)
            except Exception:
                # Silently catch listener errors to avoid disrupting core agent execution loop
                pass

# Global singleton event bus
event_bus = EventBus()
