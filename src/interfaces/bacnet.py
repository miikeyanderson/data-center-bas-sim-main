from __future__ import annotations
import threading, time, asyncio, os
from typing import Callable, Optional
import logging

# Simplified BACnet integration for Phase 2
# This is a minimal implementation focused on getting the foundation working

class BACnetIntegrationError(Exception):
    """BACnet-specific errors that don't stop simulation"""
    pass

class BACnetShim:
    """
    Minimal BACnet/IP shim for Phase 2 implementation.
    
    This is a simplified implementation that provides the interface structure
    for BACnet integration without full protocol implementation.
    Focus is on getting the configuration and integration architecture working.
    """
    
    def __init__(
        self,
        cfg: dict,
        temp_callback: Callable[[], float],
        cmd_setter: Callable[[float, Optional[int]], None],
    ):
        self.cfg = cfg
        self._temp_callback = temp_callback
        self._cmd_setter = cmd_setter
        self._running = False
        self._thread = None
        
        # Priority array for AO (16 slots: 1 highest, 16 lowest)
        self.priority_array = [None] * 16
        
        # Current values
        self.current_temp = 22.0
        self.current_command = 0.0
        
        print(f"✅ BACnet shim initialized - Device {cfg['device']['objectIdentifier']} on port {cfg['network']['port']}")
        
    def start_async(self) -> bool:
        """Start BACnet interface in background thread."""
        try:
            self._running = True
            self._thread = threading.Thread(target=self._run_update_loop, daemon=True)
            self._thread.start()
            print(f"✅ BACnet/IP active - Device {self.cfg['device']['objectIdentifier']} on port {self.cfg['network']['port']}")
            return True
        except Exception as e:
            print(f"⚠️  BACnet startup failed: {e}")
            return False
    
    def _run_update_loop(self):
        """Simple update loop for Phase 2."""
        while self._running:
            try:
                # Update temperature from simulation
                self.current_temp = self._temp_callback()
                
                # For Phase 2, just log that we're running
                # Future phases will implement full BACnet protocol here
                
            except Exception as e:
                print(f"⚠️  BACnet update error: {e}")
                
            time.sleep(1.0)  # Update every second
    
    def set_command(self, cmd_pct: float, priority: int = 16):
        """
        Simulate receiving a BACnet write command.
        
        Args:
            cmd_pct: Command percentage (0-100%)
            priority: BACnet priority level (1-16)
        """
        # Update priority array
        priority_idx = int(priority) - 1
        if 0 <= priority_idx < 16:
            self.priority_array[priority_idx] = cmd_pct
            
            # Calculate effective value (highest priority non-None)
            effective_value = None
            for pv in self.priority_array:
                if pv is not None:
                    effective_value = pv
                    break
            
            if effective_value is None:
                effective_value = 0.0
            
            self.current_command = effective_value
            
            # Notify the simulation
            self._cmd_setter(effective_value, priority)
            
            print(f"🌐 BACnet command received: {cmd_pct:.1f}% (priority {priority}) -> effective: {effective_value:.1f}%")
    
    def get_temperature(self) -> float:
        """Get current temperature value."""
        return self.current_temp
    
    def get_command(self) -> float:
        """Get current effective command value."""
        return self.current_command
    
    def stop(self):
        """Stop BACnet interface."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=1.0)

# Convenience function for simple integration
def start_bacnet(cfg: dict, temp_cb: Callable[[], float], cmd_cb: Callable[[float, Optional[int]], None]) -> Optional[BACnetShim]:
    """
    Start BACnet interface with error handling.
    
    Returns BACnetShim instance if successful, None if failed.
    """
    try:
        shim = BACnetShim(cfg, temp_cb, cmd_cb)
        if shim.start_async():
            return shim
        return None
    except Exception as e:
        print(f"⚠️  BACnet integration failed: {e}")
        return None