#!/bin/bash
# OpenCLAW Staging Setup Script
# Run this ON the Proxmox server (hl-pve01) as root

set -e

echo "=== OpenCLAW Staging Clone Setup ==="
echo ""

# Configuration
SOURCE_VM_NAME="openclaw-hl01"
TARGET_VM_NAME="openclaw-staging"
SOURCE_VMID=""  # Will be auto-detected
TARGET_VMID=103  # Choose an available VMID
STORAGE="local-lvm"  # Adjust if needed

# Find source VMID
echo "[1/5] Finding source VM..."
SOURCE_VMID=$(qm list | grep "$SOURCE_VM_NAME" | awk '{print $1}')
if [ -z "$SOURCE_VMID" ]; then
    echo "ERROR: Could not find VM '$SOURCE_VM_NAME'"
    echo "Available VMs:"
    qm list
    exit 1
fi
echo "Found $SOURCE_VM_NAME at VMID: $SOURCE_VMID"

# Check target VMID is available
echo "[2/5] Checking target VMID..."
if qm list | grep -q "^$TARGET_VMID "; then
    echo "ERROR: VMID $TARGET_VMID is already in use"
    qm list
    exit 1
fi
echo "Target VMID $TARGET_VMID is available"

# Clone the VM
echo "[3/5] Cloning VM (this may take a few minutes)..."
qm clone $SOURCE_VMID $TARGET_VM_ID \
    --name $TARGET_VM_NAME \
    --storage $STORAGE \
    --full  # Full clone (independent)

# Update VM settings for staging
echo "[4/5] Configuring staging VM..."
# Set to start on boot
qm set $TARGET_VMID --onboot 1

# Update network to get new IP (clone gets same MAC = same IP)
# Option 1: Restart network in the VM
# Option 2: Set static MAC and IP

echo "Cloned VM $TARGET_VM_NAME to VMID: $TARGET_VMID"

# Start the VM
echo "[5/5] Starting staging VM..."
qm start $TARGET_VMID

echo ""
echo "=== Clone Complete ==="
echo "VMID: $TARGET_VMID"
echo "Name: $TARGET_VM_NAME"
echo ""
echo "Next steps:"
echo "1. Log into the new VM: qm terminal $TARGET_VMID"
echo "2. Change hostname: hostnamectl set-hostname openclaw-staging"
echo "3. Get new IP: ip addr show"
echo "4. Update config.yaml with new IP and VMID"
