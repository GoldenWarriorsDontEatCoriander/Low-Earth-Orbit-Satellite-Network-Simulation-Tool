import numpy as np
import asyncio
from numba import jit

'''
以下是物理层接收到数据后的处理流程
'''
# 1. 解调（Demodulation, DEMOD）：在接收端，将调制后的信号转换回数字信号的过程
def demodulate(data_packet):
    # print(data_packet)
    demodulated_data = np.where(data_packet < 0, 0, 1)
    # await asyncio.sleep(0)  # 模拟解调延时
    return demodulated_data

# @jit(nopython=True)
# def demodulate_optimized(data_packet):
#     # 使用numba进行JIT编译，直接通过比较操作生成0和1的数组
#     return (data_packet >= 0).astype(np.int32)

# 2. 解扰（Descrambling）：解除扰码，恢复信道编码前的数据流。
# 未实现任何功能，仅仅是定义
def descrambling(data_bits):
    # await asyncio.sleep(0)
    return data_bits

# 3. 信道解码（Channel Decoding）：去除信道编码增加的冗余位，纠正由噪声导致的错误。
# 未实现任何功能，仅仅是定义
def channel_decoding(data_bits):
    # await asyncio.sleep(0)
    return data_bits

# 4. 数据解密（Data Decryption）：对加密的数据进行解密，恢复原始的数据内容。
# 未实现任何功能，仅仅是定义
def decryption(data_bits):
    # await asyncio.sleep(0)
    return data_bits

# 转换为链路层数据
def binary_to_bytes(binary_str):
    packed_bytes = np.packbits(binary_str)
    return packed_bytes.tobytes()


'''
以下是物理层准备发送数据的处理流程
'''
# 1. 数据加密（Data Encryption）：为了安全性，原始数据可能在传输前需要加密
# 未实现任何功能，仅仅是定义
def encryption(data_bits):
    # await asyncio.sleep(0)
    return data_bits

# 2. 信道编码（Channel Encoding）：增加冗余位以保护数据不被信道中的噪声和干扰所破坏
# 未实现任何功能，仅仅是定义
def channel_encoding(data_bits):
    # await asyncio.sleep(0)
    return data_bits

# 3. 扰码（Scrambling）：进一步保护数据，防止信号过于规律导致的技术问题
# 未实现任何功能，仅仅是定义
def scrambling(data_bits):
    # await asyncio.sleep(0)
    return data_bits

# 4. 数字调制（Digital Modulation）：将数字信号转换为适合在物理信道上传输的信号的过程。
# 未实现任何功能，仅仅是定义
def modulate(data_bits):
    # print(data_bits)
    """异步执行BPSK调制。"""
    # 假设使用BPSK调制
    modulated_signal = np.where(data_bits == 0, -1, 1)
    # await asyncio.sleep(0)  # 模拟异步操作
    return modulated_signal

# 5. 信号增益
def amplify_signal(signal, gain):
    amplified_signal = signal * gain
    # await asyncio.sleep(0)  # 模拟放大延时
    return amplified_signal

'''以下是数据在环境中传播的损失'''
async def add_noise(signal, snr):
    noise = np.random.normal(0, np.sqrt(10 ** (-snr / 10)), len(signal))
    noisy_signal = signal + noise
    await asyncio.sleep(0)  # 模拟添加噪声延时
    return noisy_signal

async def calculate_path_loss(d, f):
    """ Calculate the free-space path loss. """
    c = 3e8  # Speed of light in meters per second
    fspl_db = 20 * np.log10(d) + 20 * np.log10(f) + 20 * np.log10(4 * np.pi / c)
    return fspl_db

async def apply_link_budget(signal, tx_power_dbm, tx_gain_db, rx_gain_db, path_loss_db):
    """ Apply the link budget which includes the transmit power, gains, and path loss. """
    received_power_dbm = tx_power_dbm + tx_gain_db + rx_gain_db - path_loss_db
    power_ratio = 10 ** ((received_power_dbm - 30) / 10)  # Convert dBm to Watts
    return signal * np.sqrt(power_ratio)  # Adjust signal amplitude based on power
