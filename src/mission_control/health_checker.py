import logging
import requests
from datetime import datetime
from typing import Optional

from .models import OpenCLAWInstance, InstanceStatus

logger = logging.getLogger(__name__)


class HealthChecker:
    def __init__(self, timeout: int = 10):
        self.timeout = timeout

    def check_instance_health(self, instance: OpenCLAWInstance) -> tuple[bool, Optional[str]]:
        url = f"http://{instance.host}:{instance.openclaw_port}/health"
        try:
            response = requests.get(url, timeout=self.timeout)
            if response.status_code == 200:
                try:
                    data = response.json()
                    version = data.get("version", "unknown")
                    return True, version
                except Exception:
                    return True, "unknown"
            else:
                logger.warning(
                    f"Health check failed for {instance.name}: HTTP {response.status_code}"
                )
                return False, None
        except requests.exceptions.Timeout:
            logger.warning(f"Health check timeout for {instance.name}")
            return False, None
        except requests.exceptions.ConnectionError:
            logger.warning(f"Connection failed for {instance.name}")
            return False, None
        except Exception as e:
            logger.error(f"Health check error for {instance.name}: {e}")
            return False, None

    def check_all_instances(self, instances: list[OpenCLAWInstance]) -> list[OpenCLAWInstance]:
        for instance in instances:
            try:
                healthy, version = self.check_instance_health(instance)
                instance.health_check_passed = healthy
                instance.version = version
                instance.last_health_check = datetime.now().isoformat()
                if healthy:
                    instance.status = InstanceStatus.RUNNING
                    instance.error_message = None
                else:
                    instance.status = InstanceStatus.ERROR
                    instance.error_message = "Health check failed"
            except Exception as e:
                instance.status = InstanceStatus.ERROR
                instance.error_message = str(e)
                logger.error(f"Failed to check instance {instance.name}: {e}")

        return instances
