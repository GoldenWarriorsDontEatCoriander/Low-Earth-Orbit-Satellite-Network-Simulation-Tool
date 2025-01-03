import string
import secrets
import random
import numpy as np

# 随机生成IP地址
def generate_random_ipv4():
    return f"{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}"

# 随机生成MAC地址
def generate_random_mac():
    return ':'.join(f"{random.randint(0, 255):02x}" for _ in range(6))

# 随机生成一个安全的会话ID
def generate_random_session_id():
    session_id = secrets.token_hex(16)  # 生成一个32字符的十六进制字符串
    return session_id

# 随机生成用户名密码
def generate_random_credentials(username_length=8, password_length=12):
    characters = string.ascii_letters + string.digits  # 包括字母和数字
    random_username = ''.join(secrets.choice(characters) for _ in range(username_length))
    random_password = ''.join(secrets.choice(characters) for _ in range(password_length))
    return random_username, random_password

def generate_random_user_position(population_array):
    # 将数组元素转换为概率
    probabilities = population_array / population_array.sum()

    # 随机选择一个块，numpy.random.choice可以按照给定的概率分布进行选择
    flat_index = np.random.choice(population_array.size, p=probabilities.flatten())

    # 将一维索引转换为二维索引
    lat_index, lon_index = np.unravel_index(flat_index, population_array.shape)
    # 在选定的1度*1度块内随机选择一个更具体的点
    # numpy.random.uniform(low, high)生成一个介于low和high之间的随机数
    latitude = lat_index + np.random.uniform(0, 1) - 90
    latitude = 90 - lat_index + np.random.uniform(0, 1)
    # 确保用户在卫星的覆盖范围内工作
    if latitude > 70:
        latitude = latitude - 20
    elif latitude < -70:
        latitude = latitude + 20
    longitude = lon_index + np.random.uniform(0, 1) - 180
    return latitude, longitude

