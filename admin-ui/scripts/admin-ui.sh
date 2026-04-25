#!/usr/bin/env bash

SERVICE="xiaozhi-admin-ui"

case "$1" in
  restart)
    echo "🔄 Restart $SERVICE..."
    sudo systemctl restart $SERVICE
    ;;
  status)
    sudo systemctl status $SERVICE
    ;;
  logs)
    echo "📜 Logs $SERVICE (Ctrl+C per uscire)"
    journalctl -u $SERVICE -f
    ;;
  rlogs)
    echo "🔄 Restart + logs $SERVICE..."
    sudo systemctl restart $SERVICE
    sleep 1
    journalctl -u $SERVICE -f
    ;;
  *)
    echo "Uso:"
    echo "  ./admin-ui.sh restart   → restart servizio"
    echo "  ./admin-ui.sh status    → stato servizio"
    echo "  ./admin-ui.sh logs      → log live"
    echo "  ./admin-ui.sh rlogs     → restart + log live"
    ;;
esac
