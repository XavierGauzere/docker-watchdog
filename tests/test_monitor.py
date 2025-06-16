import pytest
from unittest.mock import MagicMock, patch
from src.monitor import list_containers, get_container_stats

@patch("src.monitor.docker.from_env")
def test_list_containers_basic(mock_from_env):
    # Simule un conteneur Docker minimal
    fake_container = MagicMock()
    fake_container.name = "webapp"
    fake_container.image.tags = ["nginx:alpine"]
    fake_container.status = "exited"

    mock_client = MagicMock()
    mock_client.containers.list.return_value = [fake_container]
    mock_from_env.return_value = mock_client

    list_containers()
    mock_client.containers.list.assert_called_once_with(all=True)

def test_get_container_stats_cpu_and_memory():
    fake_container = MagicMock()
    fake_container.stats.return_value = {
        "memory_stats": {"usage": 104857600},  # 100 Mo
        "cpu_stats": {
            "cpu_usage": {"total_usage": 200000000},
            "system_cpu_usage": 1000000000
        },
        "precpu_stats": {
            "cpu_usage": {"total_usage": 100000000},
            "system_cpu_usage": 900000000
        },
        "networks": {
            "eth0": {"rx_bytes": 4096, "tx_bytes": 2048}
        }
    }

    result = get_container_stats(fake_container)

    assert result["Mémoire (Mo)"] == 100.0
    assert result["Rx (Ko)"] == 4.0
    assert result["Tx (Ko)"] == 2.0
    assert result["CPU (%)"] >= 0

