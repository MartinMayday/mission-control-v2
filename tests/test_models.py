import pytest
from unittest.mock import Mock, patch, MagicMock
from mission_control.models import (
    OpenCLAWInstance,
    InstanceType,
    InstanceStatus,
    ProxmoxConfig,
    Config,
)
from mission_control.health_checker import HealthChecker


class TestOpenCLAWInstance:
    def test_from_dict(self):
        data = {
            "name": "test-instance",
            "host": "192.168.1.100",
            "port": 22,
            "user": "root",
            "type": "proxmox",
            "vm_id": 100,
            "openclaw_port": 8080,
            "description": "Test instance",
        }
        instance = OpenCLAWInstance.from_dict(data)

        assert instance.name == "test-instance"
        assert instance.host == "192.168.1.100"
        assert instance.type == InstanceType.PROXMOX
        assert instance.vm_id == 100
        assert instance.openclaw_port == 8080

    def test_to_dict(self):
        instance = OpenCLAWInstance(
            name="test-instance",
            host="192.168.1.100",
            type=InstanceType.PROXMOX,
            status=InstanceStatus.RUNNING,
            health_check_passed=True,
            version="1.0.0",
        )

        data = instance.to_dict()

        assert data["name"] == "test-instance"
        assert data["host"] == "192.168.1.100"
        assert data["type"] == "proxmox"
        assert data["status"] == "running"
        assert data["health_check_passed"] is True
        assert data["version"] == "1.0.0"


class TestProxmoxConfig:
    def test_from_dict_with_token(self):
        data = {
            "host": "proxmox.local",
            "port": 8006,
            "user": "root@pam",
            "token_id": "test-token-id",
            "token_secret": "test-token-secret",
            "verify_ssl": False,
        }
        config = ProxmoxConfig.from_dict(data)

        assert config.host == "proxmox.local"
        assert config.token_id == "test-token-id"
        assert config.token_secret == "test-token-secret"

    def test_from_dict_with_password(self):
        data = {
            "host": "proxmox.local",
            "user": "root@pam",
            "password": "test-password",
        }
        config = ProxmoxConfig.from_dict(data)

        assert config.host == "proxmox.local"
        assert config.password == "test-password"


class TestHealthChecker:
    @pytest.fixture
    def health_checker(self):
        return HealthChecker(timeout=5)

    @pytest.fixture
    def running_instance(self):
        return OpenCLAWInstance(
            name="test-instance",
            host="localhost",
            openclaw_port=8080,
        )

    def test_check_instance_health_success(self, health_checker, running_instance):
        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"version": "1.0.0"}
            mock_get.return_value = mock_response

            healthy, version = health_checker.check_instance_health(running_instance)

            assert healthy is True
            assert version == "1.0.0"

    def test_check_instance_health_connection_error(self, health_checker, running_instance):
        with patch("requests.get") as mock_get:
            mock_get.side_effect = Exception("Connection refused")

            healthy, version = health_checker.check_instance_health(running_instance)

            assert healthy is False
            assert version is None

    def test_check_all_instances(self, health_checker):
        instances = [
            OpenCLAWInstance(name="instance-1", host="localhost", openclaw_port=8080),
            OpenCLAWInstance(name="instance-2", host="localhost", openclaw_port=8081),
        ]

        with patch.object(health_checker, "check_instance_health") as mock_check:
            mock_check.side_effect = [
                (True, "1.0.0"),
                (False, None),
            ]

            result = health_checker.check_all_instances(instances)

            assert result[0].health_check_passed is True
            assert result[0].version == "1.0.0"
            assert result[1].health_check_passed is False
