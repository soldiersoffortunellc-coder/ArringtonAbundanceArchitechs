"""
csuite — the C-Suite AI Agent System for the White-Label AI Revenue Operating System.

This package models a set of task-oriented, C-suite-level AI agents that plan,
score, provision, and monitor a GoHighLevel (GHL) based Revenue Operating System.

Everything in this package is dry-run by default. No agent here ever calls a
live GHL API, sends a real message, or moves real money unless a caller
explicitly constructs a GHLAdapter with dry_run=False AND live_authorized=True.
"""

__version__ = "0.1.0"
