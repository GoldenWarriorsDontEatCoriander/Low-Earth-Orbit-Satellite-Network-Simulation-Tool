from src.simulation.protocolstack.Datapacket import NetworkLayerPacket, LinkLayerFrame
from . import PhysicalLayer, LinkLayer, NetworkLayer
import asyncio

# 将一条消息从[数据包] to [signal]
# async def create_message_to_bits(message, source_ip, target_ip, network_ttl, network_protocol, source_mac, target_mac, type, size, timestamp):
#     data_packet = NetworkLayerPacket(source=source_ip, destination=target_ip, ttl=network_ttl, protocol=network_protocol, data=message, size=size, timestamp=timestamp)
#     data_frame = await link_layer_encapsulation(data_packet, source_mac, target_mac, type)
#     data_signal = await phy_layer_encapsulation(data_frame)
#     return data_signal
async def create_message_to_bits(message, source_ip, target_ip, network_ttl, network_protocol, source_mac, target_mac, type, size, timestamp):
    data_packet = NetworkLayerPacket(source=source_ip, destination=target_ip, ttl=network_ttl, protocol=network_protocol, data=message, size=size, timestamp=timestamp)
    data_frame =  link_layer_encapsulation(data_packet, source_mac, target_mac, type)
    data_signal =  phy_layer_encapsulation(data_frame)
    return data_signal

# 从[signal]获得一条消息
async def get_packet_from_bits(data_signal):
    data_bytes =  phy_layer_decapsulation(data_signal)
    data_packet =  link_layer_decapsulation(data_bytes)
    return data_packet

# 链路层解封 to [网络层处理] to 链路层封装
async def network_layer_processing(data_packet):
    # 获得各项信息
    # 根据if判断协议
        # 各项协议的处理
        # 生成新的数据包或 转发 等等
    # 获得一个数据包
    return data_packet

# [路径损耗后的信号]
async def transmission_loss(amplified_signal, snr, distance, frequency, tx_power_dbm, tx_gain_db, rx_gain_db):
    noisy_data = await PhysicalLayer.add_noise(signal=amplified_signal, snr=snr)
    path_loss_db = await PhysicalLayer.calculate_path_loss(d=distance, f=frequency)
    received_signal = await PhysicalLayer.apply_link_budget(signal=noisy_data, tx_power_dbm=tx_power_dbm, tx_gain_db=tx_gain_db
                                              , rx_gain_db=rx_gain_db, path_loss_db=path_loss_db)
    return received_signal

# 链路层封装 to [物理层封装] to 发送
# async def phy_layer_encapsulation(data_bits):
#     data_bits_encryption =  PhysicalLayer.encryption(data_bits)
#     data_bits_encoding =  PhysicalLayer.channel_encoding(data_bits_encryption)
#     data_bits_scrambling =  PhysicalLayer.scrambling(data_bits_encoding)
#     data_signal =  PhysicalLayer.modulate(data_bits_scrambling)
#     amplified_signal =  PhysicalLayer.amplify_signal(signal=data_signal, gain=2)
#     return amplified_signal
def phy_layer_encapsulation(data_bits):
    data_bits_encryption =  PhysicalLayer.encryption(data_bits)
    data_bits_encoding =  PhysicalLayer.channel_encoding(data_bits_encryption)
    data_bits_scrambling =  PhysicalLayer.scrambling(data_bits_encoding)
    data_signal =  PhysicalLayer.modulate(data_bits_scrambling)
    amplified_signal =  PhysicalLayer.amplify_signal(signal=data_signal, gain=2)
    return amplified_signal

# 发送 to [物理层解封] to 链路层
def phy_layer_decapsulation(data_signal):
    data_bits_demodulate =  PhysicalLayer.demodulate(data_signal)
    data_bits_descrambling =  PhysicalLayer.descrambling(data_bits_demodulate)
    data_bits_decoding =  PhysicalLayer.channel_decoding(data_bits_descrambling)
    data_bits_decryption =  PhysicalLayer.decryption(data_bits_decoding)
    data_bytes =  PhysicalLayer.binary_to_bytes(data_bits_decryption)
    return data_bytes

# 网络层处理 to [链路层封装] to 物理层
# async def link_layer_encapsulation(data_packet, source_mac, target_mac, type):
#     data_frame = await LinkLayer.create_frame(data_packet, source_mac, target_mac, type)
#     data_bits =  LinkLayer.bytes_to_binary(data_frame)
#     return data_bits
def link_layer_encapsulation(data_packet, source_mac, target_mac, type):
    data_frame = LinkLayer.create_frame(data_packet, source_mac, target_mac, type)
    data_bits =  LinkLayer.bytes_to_binary(data_frame)
    return data_bits

# 物理层 to [链路层解封] to 网络层处理
def link_layer_decapsulation(data_bytes):
    data_packet =  LinkLayer.parse_frame(data_bytes)
    return data_packet




