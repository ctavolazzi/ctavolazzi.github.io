"""
Simplified Configuration for PixelLab Gallery Generation

Always uses LIVE mode - no mock/fixture system needed for gallery generation.
"""

import os


class MockConfig:
    """Simplified config that always returns LIVE mode."""
    
    def __init__(self, global_mode: str = "LIVE"):
        self._global_mode = global_mode
    
    @property
    def global_mode(self) -> str:
        return self._global_mode
    
    @global_mode.setter
    def global_mode(self, value: str):
        self._global_mode = value
    
    def get_mode(self, component: str) -> str:
        return self._global_mode
    
    def is_live(self, component: str) -> bool:
        return self._global_mode == "LIVE"
    
    def is_mock(self, component: str) -> bool:
        return self._global_mode == "MOCK"


# Always use LIVE mode for gallery generation
api_config = MockConfig(global_mode="LIVE")
