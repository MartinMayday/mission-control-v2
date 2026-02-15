import pytest
from unittest.mock import Mock, patch, MagicMock
from mission_control.manager import InstanceManager
from mission_control.models import (
    Config,
    OpenCLAWInstance,
    InstanceType,
    InstanceStatus,
    ProxmoxConfig,
)


@pytest.fixture
def config():
    return Config(
        openclaw_instances=[
            OpenCLAWInstance(
                name="test-vm",
                host="192.168.1.100",
                type=InstanceType.PROXMOX,
                vm_id=100,
            ),
            OpenCLAWInstance(
                name="test-docker",
                host="localhost",
                type=InstanceType.DOCKER,
            ),
        ],
        proxmox=ProxmoxConfig(
            host="proxmox.local",
            token_id="test",
            token_secret="test",
        ),
    )


@pytest.fixture
def manager(config):
    return InstanceManager(config)


class TestInstanceManager:
    def test_get_all_instances(self, manager):
        instances = manager.get_all_instances()
        assert len(instances) == 2
        assert instances[0].name == "test-vm"
        assert instances[1].name == "test-docker"

    def test_get_instance_by_name(self, manager):
        instance = manager.get_instance_by_name("test-vm")
        assert instance is not None
        assert instance.name == "test-vm"

    def test_get_instance_by_name_not_found(self, manager):
        instance = manager.get_instance_by_name("nonexistent")
        assert instance is None

    def test_add_instance(self, manager):
        new_instance = OpenCLAWInstance(
            name="new-instance",
            host="192.168.1.200",
            type=InstanceType.PROXMOX,
        )
        manager.add_instance(new_instance)

        instances = manager.get_all_instances()
        assert len(instances) == 3
        assert instances[-1].name == "new-instance"

    def test_remove_instance(self, manager):
        result = manager.remove_instance("test-vm")
        assert result is True

        instances = manager.get_all_instances()
        assert len(instances) == 1
        assert instances[0].name == "test-docker"

    def test_remove_instance_not_found(self, manager):
        result = manager.remove_instance("nonexistent")
        assert result is False

    @patch("mission_control.manager.HealthChecker.check_instance_health")
    def test_update_instance_status(self, mock_health, manager):
        mock_health.return_value = (True, "1.0.0")

        instance = manager.get_all_instances()[0]
        result = manager.update_instance_status(instance)

        assert result.health_check_passed is True
        assert result.version == "1.0.0"
        assert result.last_health_check is not None

    @patch("mission_control.manager.ProxmoxClient.get_vm_status_enum")
    @patch("mission_control.manager.HealthChecker.check_instance_health")
    def test_update_instance_status_proxmox(self, mock_health, mock_pve_status, manager):
        mock_pve_status.return_value = InstanceStatus.RUNNING
        mock_health.return_value = (True, "1.0.0")

        instance = manager.get_all_instances()[0]
        result = manager.update_instance_status(instance)

        assert result.status == InstanceStatus.RUNNING

    @patch("mission_control.manager.ProxmoxClient.start_vm")
    def test_start_proxmox_instance(self, mock_start, manager):
        mock_start.return_value = True

        result = manager.start_instance("test-vm")

        assert result is True
        mock_start.assert_called_once_with(100)

    @patch("mission_control.manager.SSHClient.start_openclaw")
    def test_start_docker_instance(self, mock_start, manager):
        mock_start.return_value = True

        result = manager.start_instance("test-docker")

        assert result is True

    @patch("mission_control.manager.ProxmoxClient.stop_vm")
    def test_stop_proxmox_instance(self, mock_stop, manager):
        mock_stop.return_value = True

        result = manager.stop_instance("test-vm")

        assert result is True
        mock_stop.assert_called_once_with(100)

    @patch("mission_control.manager.ProxmoxClient.restart_vm")
    def test_restart_proxmox_instance(self, mock_restart, manager):
        mock_restart.return_value = True

        result = manager.restart_instance("test-vm")

        assert result is True
        mock_restart.assert_called_once_with(100)

    @patch("mission_control.manager.SSHClient.get_openclaw_logs")
    def test_get_instance_logs(self, mock_logs, manager):
        mock_logs.return_value = "Log output here"

        result = manager.get_instance_logs("test-docker")

        assert result == "Log output here"

    @patch("mission_control.manager.ProxmoxClient.get_all_vms")
    def test_get_proxmox_vms(self, mock_vms, manager):
        mock_vms.return_value = [
            {"vmid": 100, "name": "vm1", "status": "running", "node": "pve"},
            {"vmid": 101, "name": "vm2", "status": "stopped", "node": "pve"},
        ]

        vms = manager.get_proxmox_vms()

        assert len(vms) == 2
        assert vms[0]["vmid"] == 100

    def test_get_proxmox_vms_not_configured(self, config):
        config.proxmox = None
        manager = InstanceManager(config)

        vms = manager.get_proxmox_vms()

        assert vms == []
