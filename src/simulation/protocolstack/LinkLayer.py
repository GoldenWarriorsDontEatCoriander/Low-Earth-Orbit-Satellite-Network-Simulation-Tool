import struct
from dataclasses import dataclass
import zlib  # 使用zlib库计算CRC
import numpy as np
from src.simulation.protocolstack.Datapacket import NetworkLayerPacket, LinkLayerFrame

'''
以下是接收数据包后 数据链路层处理的逻辑  即 【数据链路层阶段】 to 物理层 
'''
# async def link_to_phy_layer_processing(data_packet):
#     # print(data_packet)
#     data_frame = await create_frame(data_packet)
#     data_bits = await bytes_to_binary(data_frame)
#     return data_bits

def create_frame(data_packet, source_mac, target_mac, type):
    # print(data_packet)
    data_frame = LinkLayerFrame(source=source_mac, destination=target_mac, type=type, payload=data_packet, crc=0)
    # 编码网络层数据包
    # print(data_packet.size)
    payload_data = struct.pack('>16s16sHHfQ',
                               data_packet.source.encode(),
                               data_packet.destination.encode(),
                               data_packet.ttl,
                               data_packet.protocol,
                               data_packet.size,
                               data_packet.timestamp) + data_packet.data.encode()
    # 计算CRC
    data_frame.crc = zlib.crc32(payload_data)
    # 构造链路层帧
    header = struct.pack('>16s16sH', data_frame.destination.encode(), data_frame.source.encode(), data_frame.type)
    footer = struct.pack('>I', data_frame.crc)
    # print(header)
    return header + payload_data + footer


from numba import jit


@jit(nopython=True)
def bytes_to_binary(data):
    data_length = len(data)
    num_bits = data_length * 8
    binary_array = np.zeros(num_bits, dtype=np.uint8)

    for i in range(data_length):
        byte = data[i]
        for j in range(8):
            binary_array[i * 8 + (7 - j)] = (byte >> j) & 1

    return binary_array


# # 最后一步  将字节码转换为二进制
# async def bytes_to_binary(data):
#     # 将字节数据转换为一个大整数
#     num = int.from_bytes(data, 'big')
#     # 计算数据长度需要的二进制位数
#     num_bits = len(data) * 8
#     # 使用NumPy直接生成二进制表示的数组
#     binary_str = np.binary_repr(num, width=num_bits)
#     # 将字符串转换为NumPy数组，每个字符转为一个整数
#     binary_array = np.array(list(binary_str), dtype=int)
#     return binary_array


# # 最后一步  将字节码转换为二进制
# async def bytes_to_binary(data):
#     print('input ', data)
#     # 计算数据长度
#     data_length = len(data)
#     # 创建合适的struct格式字符串（这里使用data_length个字节的字符串）
#     fmt = f'{data_length}s'
#     # 打包数据
#     packed_data = struct.pack(fmt, data)
#     # 将打包的数据转换为一个大整数
#     num = int.from_bytes(packed_data, 'big')
#     # 将整数转换为二进制字符串，去掉前缀'0b'，并确保长度为8的倍数
#     binary_str = bin(num)[2:].zfill(data_length * 8)
#     # arr = np.array(list(binary_str), dtype=np.uint8) - ord('0')
#     binary_str = np.array(list(binary_str), dtype=int)
#     print('output', binary_str)
#     return binary_str

# 传输到网络层
def parse_frame(data_frame):
    # 解析帧头
    header = struct.unpack('>16s16sH', data_frame[:34])
    destination = header[0].decode().strip('\x00')
    source = header[1].decode().strip('\x00')
    frame_type = header[2]

    # 解析帧尾CRC
    footer = struct.unpack('>I', data_frame[-4:])
    crc_received = footer[0]

    # 解析负载
    payload_data = data_frame[34:-4]
    crc_calculated = zlib.crc32(payload_data)

    if crc_received == crc_calculated:
        # 解析网络层数据包
        network_header = struct.unpack('>16s16sHHfQ', payload_data[:48])
        payload = NetworkLayerPacket(source=network_header[0].decode().strip('\x00'),
                                     destination=network_header[1].decode().strip('\x00'),
                                     ttl=network_header[2],
                                     protocol=network_header[3],
                                     size=network_header[4],# 解析新的 size 字段
                                     timestamp=network_header[5],  # 解析 timestamp
                                     data=payload_data[48:])
        return payload
    else:
        raise ValueError("CRC check failed")