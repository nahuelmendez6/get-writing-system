#!/usr/bin/env python3
"""Convenience script to execute the Get Idiomas Writing Assessment Benchmark."""

import os
import sys

# Ensure ai_service is on the python search path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
AI_SERVICE_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if AI_SERVICE_DIR not in sys.path:
    sys.path.insert(0, AI_SERVICE_DIR)

from app.benchmark.cli import main  # noqa: E402

if __name__ == "__main__":
    main()
