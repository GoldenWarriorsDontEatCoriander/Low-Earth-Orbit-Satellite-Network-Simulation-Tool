import numpy as np
import time
from numba import jit

@jit(nopython=True)
def get_distance_3D(position_3D_1, position_3D_2):
    return np.linalg.norm(position_3D_1 - position_3D_2)

def get_current_timestamp_ms():
    # 获取当前时间的时间戳（秒）
    timestamp_sec = time.time()
    # 转换为毫秒
    timestamp_ms = int(timestamp_sec * 1000)
    return timestamp_ms

def position_3D_to_2D(position_3D):
    # 地球半径（单位：米）
    earth_radius = 6378137.0
    # 解构 x, y, z
    x, y, z = position_3D
    # 计算地心距离
    r = np.sqrt(x ** 2 + y ** 2 + z ** 2)
    # 计算经度
    longitude = np.arctan2(y, x)
    # 计算纬度
    latitude = np.arcsin(z / r)
    # 计算高度
    height = r - earth_radius
    # 将经度和纬度从弧度转换为度
    longitude_deg = np.degrees(longitude)
    latitude_deg = np.degrees(latitude)
    # 创建包含纬度、经度、高度的数组
    geodetic_coords = np.array([latitude_deg, longitude_deg, height])
    return geodetic_coords

# h是相对于地球表面的高度，而不是地球原点
def position_2D_to_3D(lat, lon, h=0):
    # 地球半径（公里）
    R = 6371.0
    # 将经纬度从度转换为弧度
    lat = np.radians(lat)
    lon = np.radians(lon)
    # XYZ坐标
    x = (R + h) * np.cos(lat) * np.cos(lon)
    y = (R + h) * np.cos(lat) * np.sin(lon)
    z = (R + h) * np.sin(lat)
    return np.array([x, y, z])

# def get_distance_3D(position_3D_1, position_3D_2):
#     return np.linalg.norm(position_3D_1 - position_3D_2)