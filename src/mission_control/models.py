from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
import yaml


class InstanceType(Enum):
    PROXMOX = "proxmox"
    DOCKER = "docker"
    ORBSTACK = "orbstack"
    LOCAL = "local"


class InstanceStatus(Enum):
    UNKNOWN = "unknown"
    RUNNING = "running"
    STOPPED = "stopped"
    ERROR = "error"
    STARTING = "starting"
    STOPPING = "stopping"


@dataclass
class OpenCLAWInstance:
    name: str
    host: str
    port: int = 22
    user: str = "root"
    type: InstanceType = InstanceType.PROXMOX
    vm_id: Optional[int] = None
    openclaw_port: int = 8080
    description: str = ""
    status: InstanceStatus = InstanceStatus.UNKNOWN
    last_health_check: Optional[str] = None
    health_check_passed: bool = False
    version: Optional[str] = None
    error_message: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> "OpenCLAWInstance":
        instance_type = InstanceType(data.get("type", "proxmox"))
        return cls(
            name=data["name"],
            host=data["host"],
            port=data.get("port", 22),
            user=data.get("user", "root"),
            type=instance_type,
            vm_id=data.get("vm_id"),
            openclaw_port=data.get("openclaw_port", 8080),
            description=data.get("description", ""),
        )

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "host": self.host,
            "port": self.port,
            "user": self.user,
            "type": self.type.value,
            "vm_id": self.vm_id,
            "openclaw_port": self.openclaw_port,
            "description": self.description,
            "status": self.status.value,
            "last_health_check": self.last_health_check,
            "health_check_passed": self.health_check_passed,
            "version": self.version,
            "error_message": self.error_message,
        }


@dataclass
class ProxmoxConfig:
    host: str
    port: int = 8006
    user: str = "root@pam"
    token_id: Optional[str] = None
    token_secret: Optional[str] = None
    password: Optional[str] = None
    verify_ssl: bool = False
    timeout: int = 30

    @classmethod
    def from_dict(cls, data: dict) -> "ProxmoxConfig":
        return cls(
            host=data.get("host", "proxmox.local"),
            port=data.get("port", 8006),
            user=data.get("user", "root@pam"),
            token_id=data.get("token_id"),
            token_secret=data.get("token_secret"),
            password=data.get("password"),
            verify_ssl=data.get("verify_ssl", False),
            timeout=data.get("timeout", 30),
        )


@dataclass
class OrbStackConfig:
    enabled: bool = False
    socket_path: str = "/var/run/docker.sock"

    @classmethod
    def from_dict(cls, data: dict) -> "OrbStackConfig":
        return cls(
            enabled=data.get("enabled", False),
            socket_path=data.get("socket_path", "/var/run/docker.sock"),
        )


@dataclass
class Config:
    openclaw_instances: list[OpenCLAWInstance] = field(default_factory=list)
    proxmox: Optional[ProxmoxConfig] = None
    orbstack: Optional[OrbStackConfig] = None

    @classmethod
    def from_yaml(cls, path: str) -> "Config":
        with open(path, "r") as f:
            data = yaml.safe_load(f)

        instances = [OpenCLAWInstance.from_dict(i) for i in data.get("openclaw_instances", [])]
        proxmox_data = data.get("proxmox")
        orbstack_data = data.get("orbstack")

        return cls(
            openclaw_instances=instances,
            proxmox=ProxmoxConfig.from_dict(proxmox_data) if proxmox_data else None,
            orbstack=OrbStackConfig.from_dict(orbstack_data) if orbstack_data else None,
        )
