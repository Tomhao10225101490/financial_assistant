"""Multi-source market data adapters for MarketRadar terminal."""

from sources.briefing import BriefingService
from sources.registry import SourceRegistry

__all__ = ["BriefingService", "SourceRegistry"]
