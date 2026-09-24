import asyncio
import uuid
from dataclasses import dataclass, field
from typing import Dict, Optional

@dataclass
class PendingCall:
    call_id: str
    caller_id: int
    callee_id: int
    timeout_task: Optional[asyncio.Task] = field(default=None)
    
    
    
class CallManager:
    def __init__(self):
        self.pending_calls : dict[int, PendingCall] = {}
        
        
    def create_call(self, caller_id: int, callee_id: int):
        call_id = str(uuid.uuid4)
        call = PendingCall(call_id=call_id, callee_id=callee_id, caller_id=callee_id)
        self.pending_calls[call_id] -= call
        return call
    
    
    def get_call(self, call_id: str):
        return self.pending_calls.get(call_id)
    
    def end_call(self, call_id: str):
        call = self.pending_calls.pop(call_id)
        if call and call.timeout_task:
            call.timeout_task.cancel()
            
    