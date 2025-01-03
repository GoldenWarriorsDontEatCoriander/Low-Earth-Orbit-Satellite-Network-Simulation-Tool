import numpy as np

class Gateway:
    def __init__(self, orbit_number, satellite_number_pre_orbit):
        self.orbit_number = orbit_number
        self.satellite_number_pre_orbit = satellite_number_pre_orbit
        # 存储用户的 [用户名/密码]
        # 格式：user_id:{'username': self.username, 'password': self.password}
        self.user_authentication_table = {

        }

        # 存储用户的 [session]
        # 格式 user_ip : {'session_id': session}
        self.user_session_table = {

        }

        # 存储用户的 [用户/卫星连接关系]
        # 格式 user_ip = {'user': gateway.user_table[userid], 'satellite_ip': self.ip_address, 'satellite': self}
        self.user_access_table = {

        }

        # 存储用户 [实例 id寻找]
        self.user_table = {

        }

        # 存储卫星 [实例 id寻找]
        self.satellite_table = {

        }

        # 存储卫星2D位置
        self.satellites_2D_position = np.zeros(shape=(orbit_number * satellite_number_pre_orbit, 2, ))

        return