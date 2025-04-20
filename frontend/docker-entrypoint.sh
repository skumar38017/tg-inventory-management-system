#!/bin/bash
# Auto-configure DISPLAY based on OS
if [ -e /tmp/.X11-unix ]; then
  export DISPLAY=${DISPLAY_LINUX:-:0}
else
  export DISPLAY=${DISPLAY:-host.docker.internal:0}
fi

# Verify X11 connection
if ! xhost >& /dev/null; then
  echo "X11 server connection failed! Check your DISPLAY settings."
  echo "Windows/Mac: Ensure XServer (VcXsrv/XQuartz) is running with:"
  echo "  - Disable access control"
  echo "Linux: Run 'xhost +local:docker' first"
  exit 1
fi

exec "$@"