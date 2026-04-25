#!/usr/bin/env bash

XIAOZHI_DIR="${XIAOZHI_DIR:-/home/ciru/xiaozhi-esp32-lightserver}"

case "$1" in
  restart)
    echo "🔄 Restart Xiaozhi server..."
    cd "$XIAOZHI_DIR" || exit 1
    docker compose restart
    ;;
  logs)
    echo "📜 Logs Xiaozhi (Ctrl+C per uscire)"
    cd "$XIAOZHI_DIR" || exit 1
    docker compose logs -f --tail=100
    ;;
  tail)
    LINES="${2:-100}"
    cd "$XIAOZHI_DIR" || exit 1
    docker compose logs --tail="$LINES"
    ;;
  logs-web)
    LINES="${2:-200}"
    cd "$XIAOZHI_DIR" || exit 1
    docker compose logs --tail="$LINES"
    ;;
  rlogs)
    echo "🔄 Restart + logs Xiaozhi..."
    cd "$XIAOZHI_DIR" || exit 1
    docker compose restart
    sleep 1
    docker compose logs -f --tail=100
    ;;
  status)
    cd "$XIAOZHI_DIR" || exit 1
    docker compose ps
    ;;
  *)
    echo "Uso:"
    echo "  xserver restart"
    echo "  xserver logs"
    echo "  xserver tail [n]"
    echo "  xserver logs-web [n]"
    echo "  xserver rlogs"
    echo "  xserver status"
    ;;
esac
