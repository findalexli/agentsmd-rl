#!/bin/bash
cd /tests && python3 -m pytest test_outputs.py -v --tb=short 2>&1
