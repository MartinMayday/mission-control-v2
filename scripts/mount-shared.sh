#!/bin/bash
# Mount shared folder between local and VM
# Usage: ./mount-shared.sh [mount|unmount]

ACTION=${1:-mount}
LOCAL_DIR="$HOME/.openclaw-mgmt/shared"
VM_HOST="nosrc@192.168.100.202"
VM_DIR="/home/nosrc/shared"

case $ACTION in
  mount)
    echo "Mounting shared folder..."
    mkdir -p "$LOCAL_DIR"
    # Use sshfs if available, otherwise warn
    if command -v sshfs &> /dev/null; then
      sshfs "$VM_HOST:$VM_DIR" "$LOCAL_DIR" -o reconnect,ServerAliveInterval=15,ServerAliveCountMax=3
      echo "Mounted: $LOCAL_DIR"
    else
      echo "sshfs not installed. Install with: brew install sshfs"
      echo "Or use scp/rsync for file sharing:"
      echo "  To VM:  scp -i ~/.ssh/id_ed25519_coder file nosrc@192.168.100.202:$VM_DIR"
      echo "  From VM: scp -i ~/.ssh/id_ed25519_coder nosrc@192.168.100.202:$VM_DIR/file ."
    fi
    ;;
  unmount)
    echo "Unmounting shared folder..."
    if command -v fusermount &> /dev/null; then
      fusermount -u "$LOCAL_DIR"
    elif command -v umount &> /dev/null; then
      umount "$LOCAL_DIR"
    fi
    echo "Unmounted"
    ;;
  *)
    echo "Usage: $0 [mount|unmount]"
    ;;
esac
