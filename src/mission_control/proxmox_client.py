import logging
from typing import Optional
import proxmoxer
from proxmoxer import ProxmoxAPI
from tenacity import retry, stop_after_attempt, wait_exponential

from .models import ProxmoxConfig, InstanceStatus

logger = logging.getLogger(__name__)


class ProxmoxClient:
    def __init__(self, config: ProxmoxConfig):
        self.config = config
        self._client: Optional[ProxmoxAPI] = None

    def connect(self) -> ProxmoxAPI:
        if self._client is not None:
            return self._client

        try:
            if self.config.token_id and self.config.token_secret:
                self._client = ProxmoxAPI(
                    self.config.host,
                    user=self.config.user,
                    token_id=self.config.token_id,
                    token_secret=self.config.token_secret,
                    verify_ssl=self.config.verify_ssl,
                    timeout=self.config.timeout,
                )
            elif self.config.password:
                self._client = ProxmoxAPI(
                    self.config.host,
                    user=self.config.user,
                    password=self.config.password,
                    verify_ssl=self.config.verify_ssl,
                    timeout=self.config.timeout,
                )
            else:
                raise ValueError("Either token_id/token_secret or password must be provided")

            logger.info(f"Connected to Proxmox at {self.config.host}")
            return self._client

        except Exception as e:
            logger.error(f"Failed to connect to Proxmox: {e}")
            raise

    def disconnect(self):
        self._client = None

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def get_vm_status(self, vmid: int) -> dict:
        client = self.connect()
        try:
            status = client.nodes(client.nodes.get()[0]["node"]).qemu(vmid).status.get()
            return {
                "vmid": vmid,
                "status": status.get("status", "unknown"),
                "uptime": status.get("uptime", 0),
                "cpu": status.get("cpu", 0),
                "memory": status.get("mem", 0),
            }
        except Exception as e:
            logger.error(f"Failed to get VM status for {vmid}: {e}")
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def start_vm(self, vmid: int) -> bool:
        client = self.connect()
        try:
            node = client.nodes.get()[0]["node"]
            client.nodes(node).qemu(vmid).status.post("start")
            logger.info(f"Started VM {vmid}")
            return True
        except Exception as e:
            logger.error(f"Failed to start VM {vmid}: {e}")
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def stop_vm(self, vmid: int) -> bool:
        client = self.connect()
        try:
            node = client.nodes.get()[0]["node"]
            client.nodes(node).qemu(vmid).status.post("stop")
            logger.info(f"Stopped VM {vmid}")
            return True
        except Exception as e:
            logger.error(f"Failed to stop VM {vmid}: {e}")
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def restart_vm(self, vmid: int) -> bool:
        client = self.connect()
        try:
            node = client.nodes.get()[0]["node"]
            client.nodes(node).qemu(vmid).status.post("restart")
            logger.info(f"Restarted VM {vmid}")
            return True
        except Exception as e:
            logger.error(f"Failed to restart VM {vmid}: {e}")
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def get_all_vms(self) -> list[dict]:
        client = self.connect()
        try:
            vms = []
            for node in client.nodes.get():
                node_name = node["node"]
                qemu_vms = client.nodes(node_name).qemu.get()
                for vm in qemu_vms:
                    vms.append(
                        {
                            "vmid": vm["vmid"],
                            "name": vm.get("name", "unknown"),
                            "status": vm.get("status", "unknown"),
                            "node": node_name,
                        }
                    )
            return vms
        except Exception as e:
            logger.error(f"Failed to get all VMs: {e}")
            raise

    def get_vm_status_enum(self, vmid: int) -> InstanceStatus:
        try:
            status = self.get_vm_status(vmid)
            vm_status = status.get("status", "unknown")
            if vm_status == "running":
                return InstanceStatus.RUNNING
            elif vm_status == "stopped":
                return InstanceStatus.STOPPED
            else:
                return InstanceStatus.UNKNOWN
        except Exception:
            return InstanceStatus.ERROR
