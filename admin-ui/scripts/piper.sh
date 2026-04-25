#!/usr/bin/env bash

SERVICE="${PIPER_SERVICE_NAME:-piper-api}"

case "$1" in
  restart)
    echo "🔄 Restart Piper..."
    sudo systemctl restart $SERVICE
    ;;
  logs)
    echo "📜 Logs Piper (Ctrl+C per uscire)"
    journalctl -u $SERVICE -f
    ;;
  tail)
    LINES="${2:-100}"
    journalctl -u $SERVICE -n "$LINES" --no-pager
    ;;
  logs-web)
    LINES="${2:-200}"
    journalctl -u $SERVICE -n "$LINES" --no-pager
    ;;
  rlogs)
    echo "🔄 Restart + logs Piper..."
    sudo systemctl restart $SERVICE
    sleep 1
    journalctl -u $SERVICE -f
    ;;
  status)
    sudo systemctl status $SERVICE
    ;;
  *)
    echo "Uso:"
    echo "  piper restart"
    echo "  piper logs"
    echo "  piper tail [n]"
    echo "  piper logs-web [n]"
    echo "  piper rlogs"
    echo "  piper status"
    ;;
esac
