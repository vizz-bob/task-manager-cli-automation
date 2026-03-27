#!/usr/bin/env bash
# ============================================================
# docker_run.sh — Helper to build, run, and manage the
# Task Manager Docker container
#
# Usage:
#   ./docker_run.sh build    — Build the Docker image
#   ./docker_run.sh start    — Start the container
#   ./docker_run.sh shell    — Open a bash shell inside it
#   ./docker_run.sh stop     — Stop the container
#   ./docker_run.sh clean    — Stop + remove container + image
# ============================================================
set -euo pipefail

IMAGE_NAME="taskmanager"
CONTAINER_NAME="taskmanager"

case "${1:-help}" in

  build)
    echo "Building Docker image: $IMAGE_NAME ..."
    docker build -t "$IMAGE_NAME" .
    echo "Done. Image built: $IMAGE_NAME"
    ;;

  start)
    echo "Starting container: $CONTAINER_NAME ..."
    docker compose up -d
    echo ""
    echo "Container is running. Open a shell with:"
    echo "  ./docker_run.sh shell"
    ;;

  shell)
    echo "Opening bash shell inside $CONTAINER_NAME ..."
    docker exec -it "$CONTAINER_NAME" bash
    ;;

  stop)
    echo "Stopping container: $CONTAINER_NAME ..."
    docker compose down
    echo "Container stopped."
    ;;

  clean)
    echo "Stopping and removing container + image ..."
    docker compose down --rmi local --volumes --remove-orphans 2>/dev/null || true
    docker rmi "$IMAGE_NAME" 2>/dev/null || true
    echo "Cleanup complete. Your Mac is clean."
    ;;

  logs)
    docker logs -f "$CONTAINER_NAME"
    ;;

  *)
    echo ""
    echo "Usage: ./docker_run.sh [command]"
    echo ""
    echo "Commands:"
    echo "  build   — Build the Docker image"
    echo "  start   — Start the container (detached)"
    echo "  shell   — Open bash shell inside container"
    echo "  stop    — Stop the container"
    echo "  clean   — Remove container + image entirely"
    echo "  logs    — Follow container logs"
    echo ""
    ;;
esac
