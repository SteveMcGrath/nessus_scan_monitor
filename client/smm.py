#!/usr/bin/env python
import os
from commands import getoutput as run

found = False
for line in run('ps aux').split('\n'):
  if line.find('python /opt/scan_monitor/scan_monitor') > -1:
    found = True

if not found:
  run('/opt/scan_monitor/scan_monitor')