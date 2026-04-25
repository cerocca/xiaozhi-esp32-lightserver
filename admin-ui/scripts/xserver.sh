#!/usr/bin/env bash

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
MONOREPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
LEGACY_SIBLING_ROOT="$SCRIPT_DIR/../../xiaozhi-esp32-lightserver"

if [ -f "$MONOREPO_ROOT/docker-compose.yml" ]; then
  DEFAULT_XIAOZHI_DIR="$MONOREPO_ROOT"
elif [ -f "$LEGACY_SIBLING_ROOT/docker-compose.yml" ]; then
  DEFAULT_XIAOZHI_DIR="$(cd "$LEGACY_SIBLING_ROOT" && pwd)"
else
  DEFAULT_XIAOZHI_DIR="$MONOREPO_ROOT"
fi

XIAOZHI_DIR="${XIAOZHI_DIR:-$DEFAULT_XIAOZHI_DIR}"

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
