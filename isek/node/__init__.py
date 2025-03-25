from .etcd_registry import EtcdRegistry
from .isek_center_registry import IsekCenterRegistry

__all__ = [
    "EtcdRegistry",
    "IsekCenterRegistry",
    "registries"
]


registries = {
    "etcd": EtcdRegistry,
    "isek_center": IsekCenterRegistry
}
