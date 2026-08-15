"""Compatibility entry point for the coordinated unpublished Week 0 builder.

Day 2 is no longer a separate Canvas mutation path. Keeping this filename as a
thin wrapper prevents old runbook commands from bypassing the current five-day
preflight, storage locks, mapped-Minor guard, and exact module reconciliation.
The Canvas token is still read only by ``build_wk0.main`` through stdin.
"""

import asyncio

from build_wk0 import main


if __name__ == "__main__":
    asyncio.run(main())
