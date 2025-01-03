from dataclasses import dataclass

@dataclass
class NetworkLayerPacket:
    source: str
    destination: str
    ttl: int
    protocol: int

    # 新添加的字段
    size: float
    timestamp: int

    data: str


@dataclass
class LinkLayerFrame:
    destination: str
    source: str
    type: int
    payload: NetworkLayerPacket
    crc: int