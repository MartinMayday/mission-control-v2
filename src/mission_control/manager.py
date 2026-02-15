import logging
from typing import Optional
from datetime import datetime

from .models import Config, OpenCLAWInstance, InstanceStatus, InstanceType
from .proxmox_client import ProxmoxClient
from .health_checker import HealthChecker
from .ssh_client import SSHClient

logger = logging.getLogger(__name__)


class InstanceManager:
    def __init__(self, config: Config):
        self.config = config
        self.proxmox_client: Optional[ProxmoxClient] = None
        self.health_checker = HealthChecker()

        if config.proxmox:
            self.proxmox_client = ProxmoxClient(config.proxmox)

    def get_all_instances(self) -> list[OpenCLAWInstance]:
        return self.config.openclaw_instances

    def get_instance_by_name(self, name: str) -> Optional[OpenCLAWInstance]:
        for instance in self.config.openclaw_instances:
            if instance.name == name:
                return instance
        return None

    def update_instance_status(self, instance: OpenCLAWInstance) -> OpenCLAWInstance:
        if instance.type == InstanceType.PROXMOX and instance.vm_id and self.proxmox_client:
            try:
                instance.status = self.proxmox_client.get_vm_status_enum(instance.vm_id)
            except Exception as e:
                instance.status = InstanceStatus.ERROR
                instance.error_message = str(e)
                logger.error(f"Failed to update status for {instance.name}: {e}")

        healthy, version = self.health_checker.check_instance_health(instance)
        instance.health_check_passed = healthy
        instance.version = version
        instance.last_health_check = datetime.now().isoformat()

        return instance

    def update_all_instance_statuses(self) -> list[OpenCLAWInstance]:
        for instance in self.config.openclaw_instances:
            self.update_instance_status(instance)
        return self.config.openclaw_instances

    def start_instance(self, name: str) -> bool:
        instance = self.get_instance_by_name(name)
        if not instance:
            logger.error(f"Instance {name} not found")
            return False

        if instance.type == InstanceType.PROXMOX and instance.vm_id and self.proxmox_client:
            try:
                return self.proxmox_client.start_vm(instance.vm_id)
            except Exception as e:
                logger.error(f"Failed to start VM for {name}: {e}")
                return False

        elif instance.type == InstanceType.DOCKER or instance.type == InstanceType.LOCAL:
            ssh = SSHClient(instance)
            try:
                return ssh.start_openclaw()
            finally:
                ssh.disconnect()

        return False

    def stop_instance(self, name: str) -> bool:
        instance = self.get_instance_by_name(name)
        if not instance:
            logger.error(f"Instance {name} not found")
            return False

        if instance.type == InstanceType.PROXMOX and instance.vm_id and self.proxmox_client:
            try:
                return self.proxmox_client.stop_vm(instance.vm_id)
            except Exception as e:
                logger.error(f"Failed to stop VM for {name}: {e}")
                return False

        elif instance.type == InstanceType.DOCKER or instance.type == InstanceType.LOCAL:
            ssh = SSHClient(instance)
            try:
                return ssh.stop_openclaw()
            finally:
                ssh.disconnect()

        return False

    def restart_instance(self, name: str) -> bool:
        instance = self.get_instance_by_name(name)
        if not instance:
            logger.error(f"Instance {name} not found")
            return False

        if instance.type == InstanceType.PROXMOX and instance.vm_id and self.proxmox_client:
            try:
                return self.proxmox_client.restart_vm(instance.vm_id)
            except Exception as e:
                logger.error(f"Failed to restart VM for {name}: {e}")
                return False

        elif instance.type == InstanceType.DOCKER or instance.type == InstanceType.LOCAL:
            ssh = SSHClient(instance)
            try:
                return ssh.restart_openclaw()
            finally:
                ssh.disconnect()

        return False

    def get_instance_logs(self, name: str, lines: int = 50) -> Optional[str]:
        instance = self.get_instance_by_name(name)
        if not instance:
            logger.error(f"Instance {name} not found")
            return None

        ssh = SSHClient(instance)
        try:
            return ssh.get_openclaw_logs(lines)
        finally:
            ssh.disconnect()

    def get_proxmox_vms(self) -> list[dict]:
        if not self.proxmox_client:
            return []
        return self.proxmox_client.get_all_vms()

    def add_instance(self, instance: OpenCLAWInstance):
        self.config.openclaw_instances.append(instance)
        logger.info(f"Added instance: {instance.name}")

    def remove_instance(self, name: str) -> bool:
        instance = self.get_instance_by_name(name)
        if instance:
            self.config.openclaw_instances.remove(instance)
            logger.info(f"Removed instance: {name}")
            return True
        return False
