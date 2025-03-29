#!/usr/bin/env python
"""
Simple script to run the Eat-and-Run Telegram bot.
"""

import asyncio

from app.main import main

if __name__ == "__main__":
    asyncio.run(main())
