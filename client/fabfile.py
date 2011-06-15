from fabric.api     import *
from fabric.contrib import files

def update():
  # First we need to kill off any running copies of scan_monitor
  sudo('skill python /opt/scan_monitor/scan_monitor')
  
  # If this is the first installation, then we need to create the directory
  # and then run the cron function to add the cron entry for the scan_monitor
  # manager (smm).
  if not files.exists('/opt/scan_monitor'):
    sudo('mkdir /opt/scan_monitor')
    cron()
    
  # Now we need to stage all thge files onto the remote scanner.
  put('scan_monitor.py', '/tmp/scan_monitor.py')
  put('smm.py', '/tmp/smm.py')
  put('config.ini', '/tmp/sm_config.py')
  
  # Then we move everything into place.
  sudo('mv /tmp/sm_config.ini /top/scan_monitor/config.ini')
  sudo('mv /tmp/smm.py /opt/scan_monitor/smm.py')
  sudo('mv /tmp/scan_monitor.py /opt/scan_monitor/scan_monitor')
  
  # Lastly we start the scan_monitor service back up.
  sudo('/opt/scan_monitor/scan_monitor')

def cron():
  files.append('* * * * * root /opt/scan_monitor/smm.py', '/etc/crontab')

def get_logs():
  get('/var/log/scan_monitor.log', 'info.log')
  get('/var/log/scan_monitor.err', 'error.log')