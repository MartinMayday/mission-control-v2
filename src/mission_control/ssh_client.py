import logging
from typing import Optional
import paramiko

from .models import OpenCLAWInstance

logger = logging.getLogger(__name__)


class SSHClient:
    def __init__(self, instance: OpenCLAWInstance):
        self.instance = instance
        self._client: Optional[paramiko.SSHClient] = None

    def connect(self) -> paramiko.SSHClient:
        if self._client is not None:
            return self._client

        try:
            self._client = paramiko.SSHClient()
            self._client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            self._client.connect(
                hostname=self.instance.host,
                port=self.instance.port,
                username=self.instance.user,
                timeout=10,
            )

            logger.info(f"Connected to {self.instance.name} via SSH")
            return self._client

        except Exception as e:
            logger.error(f"Failed to connect to {self.instance.name}: {e}")
            raise

    def disconnect(self):
        if self._client:
            self._client.close()
            self._client = None

    def execute_command(self, command: str) -> tuple[str, str, int]:
        client = self.connect()
        try:
            stdin, stdout, stderr = client.exec_command(command)
            exit_code = stdout.channel.recv_exit_status()
            stdout_data = stdout.read().decode("utf-8")
            stderr_data = stderr.read().decode("utf-8")
            return stdout_data, stderr_data, exit_code
        except Exception as e:
            logger.error(f"Failed to execute command on {self.instance.name}: {e}")
            raise

    def check_openclaw_status(self) -> bool:
        try:
            stdout, stderr, code = self.execute_command(
                "docker ps --filter name=openclaw --format '{{.Status}}'"
            )
            return "Up" in stdout
        except Exception as e:
            logger.error(f"Failed to check OpenCLAW status on {self.instance.name}: {e}")
            return False

    def start_openclaw(self) -> bool:
        try:
            self.execute_command("cd ~/openclaw-docker && docker-compose up -d")
            return True
        except Exception as e:
            logger.error(f"Failed to start OpenCLAW on {self.instance.name}: {e}")
            return False

    def stop_openclaw(self) -> bool:
        try:
            self.execute_command("cd ~/openclaw-docker && docker-compose stop")
            return True
        except Exception as e:
            logger.error(f"Failed to stop OpenCLAW on {self.instance.name}: {e}")
            return False

    def restart_openclaw(self) -> bool:
        try:
            self.execute_command("cd ~/openclaw-docker && docker-compose restart")
            return True
        except Exception as e:
            logger.error(f"Failed to restart OpenCLAW on {self.instance.name}: {e}")
            return False

    def get_openclaw_logs(self, lines: int = 50) -> str:
        try:
            stdout, _, _ = self.execute_command(f"docker-compose logs --tail={lines} openclaw")
            return stdout
        except Exception as e:
            logger.error(f"Failed to get logs from {self.instance.name}: {e}")
            return f"Error: {e}"

    def get_openclaw_version(self) -> Optional[str]:
        try:
            stdout, _, code = self.execute_command(
                "docker exec openclaw openclaw --version 2>/dev/null || echo 'unknown'"
            )
            if code == 0:
                return stdout.strip()
            return None
        except Exception:
            return None
