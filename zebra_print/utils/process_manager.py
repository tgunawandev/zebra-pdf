"""
Process management utilities.
Provides utilities for managing background processes.
"""

import os
import signal
import time
from typing import Optional

class ProcessManager:
    """Utilities for managing background processes."""
    
    @staticmethod
    def is_process_running(pid: int) -> bool:
        """Check if a process is running."""
        try:
            os.kill(pid, 0)
            return True
        except (OSError, ProcessLookupError):
            return False
    
    @staticmethod
    def read_pid_file(pid_file: str) -> Optional[int]:
        """Read PID from file safely."""
        if not os.path.exists(pid_file):
            return None
        
        try:
            with open(pid_file, 'r') as f:
                return int(f.read().strip())
        except (ValueError, IOError):
            return None
    
    @staticmethod
    def write_pid_file(pid_file: str, pid: int) -> bool:
        """Write PID to file safely."""
        try:
            with open(pid_file, 'w') as f:
                f.write(str(pid))
            return True
        except IOError:
            return False
    
    @staticmethod
    def cleanup_stale_pid_file(pid_file: str) -> bool:
        """Remove stale PID files."""
        pid = ProcessManager.read_pid_file(pid_file)
        if pid and not ProcessManager.is_process_running(pid):
            try:
                os.remove(pid_file)
                return True
            except OSError:
                pass
        return False
    
    @staticmethod
    def terminate_process_group(pid: int, timeout: int = 5) -> bool:
        """Terminate a process group gracefully."""
        try:
            # Send SIGTERM to the process group
            os.killpg(os.getpgid(pid), signal.SIGTERM)
            
            # Wait for graceful termination
            for _ in range(timeout):
                if not ProcessManager.is_process_running(pid):
                    return True
                time.sleep(1)
            
            # Force kill if still running
            os.killpg(os.getpgid(pid), signal.SIGKILL)
            return True
            
        except (OSError, ProcessLookupError):
            return True  # Already dead