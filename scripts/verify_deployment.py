#!/usr/bin/env python3
import subprocess, sys
raise SystemExit(subprocess.call([sys.executable,'scripts/deploy.py','--verify']))
