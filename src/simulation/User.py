import asyncio
import random
import numpy as np
from src.unils.Calculation import position_2D_to_3D, get_distance_3D, get_current_timestamp_ms
from src.unils.RandomGenerator import generate_random_ipv4, generate_random_mac, generate_random_user_position, generate_random_credentials
from src.simulation.protocolstack import Stack
from src.unils import Regular


class User:
    def __init__(self, user_id, population_array, user_to_satellite_gain, user_receiver_sensitivity, user_snr, user_data_rate, gateway, globalVariables):
        # 用户身份
        self.id = user_id
        self.ip_address = generate_random_ipv4()
        self.mac_address = generate_random_mac()
        self.username, self.password = generate_random_credentials(username_length=8, password_length=16)
        gateway.user_authentication_table[str(self.id)] = {'username': self.username, 'password': self.password}
        gateway.user_table[str(self.id)] = self

        # 坐标
        latitude, longitude = generate_random_user_position(population_array=population_array)
        self.position_2D_GCS = np.array([latitude, longitude, 0])  # 地理坐标系 纬度/经度/高度
        self.position_3D_ECI = position_2D_to_3D(lat=latitude, lon=longitude, h=0)   # 地心惯性坐标系
        self.globalVariables = globalVariables
        globalVariables.globle_user_position_3D_ECI.append({'user_id': self.id, 'x': self.position_3D_ECI[0], 'y': self.position_3D_ECI[1], 'z': self.position_3D_ECI[2]})

        # 物理参数 用于接入过程
        self.user_to_satellite_gain = user_to_satellite_gain
        self.user_receiver_sensitivity = user_receiver_sensitivity
        self.user_snr = user_snr
        self.user_data_rate = user_data_rate

        # 接入卫星
        self.session = None  # 接入卫星后会得到一个会话
        self.access_satellite = None  # 真正接入的卫星
        self.candidate_access_satellite = None  # 候选的接入卫星，即用户连接后等待接入认证和切换时的卫星


        # 缓冲区
        self.receiver_buffer = asyncio.Queue()
        self.max_buffer_size = 1024 * 1024 * 1024  # MB
        self.phy_current_get_buffer_size = 0
        return

    async def start_user_behavior_async(self, gateway, global_variables, satellites):
        # 同时启动所有行为
        await asyncio.gather(
            self.start_user_send_behavior_async(gateway=gateway, global_variables=global_variables),
            self.start_user_receive_behavior_async(),
            self.start_user_access_and_switch_satellite_behavior_async(satellites=satellites, gateway=gateway)
        )

    async def start_user_send_behavior_async(self, gateway, global_variables):
        while True:
            if self.access_satellite and self.access_satellite == self.candidate_access_satellite:
                # 用户发送数据的逻辑
                network_protocol = 0x0064
                target_user = random.choice(list(gateway.user_table.values()))
                target_ip = target_user.ip_address
                if self.ip_address == target_ip:
                    continue
                data_size = random.uniform(1, self.user_data_rate)
                # data = np.random.bytes(data_size * 1024)
                message = f'This is a normal data packet, from user {self.ip_address}, sent to user {target_ip}. [has_routing_path:{0}], [r_p:{None}]'
                send_to_satellite = self.access_satellite
                wait_time = data_size / self.user_data_rate

                self.globalVariables.count_total_packet_number = self.globalVariables.count_total_packet_number + 1
            # 如果当前已经接入一个卫星，且候选卫星与接入卫星不同，则执行切换卫星的逻辑
            elif self.access_satellite and self.candidate_access_satellite and self.access_satellite != self.candidate_access_satellite:
                # 切换的逻辑
                network_protocol = 0x0002
                message = f'User [userid:{self.id}] want to switch from [original_satellite:{self.access_satellite.id}] to [new_satellite:{self.candidate_access_satellite.id}], my_session [session:{self.session}]'
                send_to_satellite = self.candidate_access_satellite
                target_ip = send_to_satellite.ip_address
                wait_time = 5
                data_size = 0.1
            # 选择一个视野的候选卫星
            elif self.candidate_access_satellite and self.access_satellite == None:
                network_protocol = 0x0001
                message = f'User [userid:{self.id}] want to access to Satellite {self.candidate_access_satellite.id}, my username is [username:{self.username}], my_password is [password:{self.password}]'
                send_to_satellite = self.candidate_access_satellite
                target_ip = send_to_satellite.ip_address
                wait_time = 5
                data_size = 0.1
            else:
                # 用户正在搜索合适的卫星接入
                # print('Users are searching for suitable access satellites !!')
                await asyncio.sleep(3)
                continue
            data_signal = await Stack.create_message_to_bits(message=message, source_ip=self.ip_address, target_ip=target_ip
                                               , network_ttl=64, network_protocol=network_protocol, source_mac=self.mac_address
                                               , target_mac=send_to_satellite.mac_address, type=0x0032, size=data_size
                                                             , timestamp=get_current_timestamp_ms())

            delay = data_size * 8 / send_to_satellite.bandwith + get_distance_3D(self.position_3D_ECI, send_to_satellite.position_3D_ECI) * 1e3 / 3e8
            if send_to_satellite:
                # await send_to_satellite.phy_get_buffer.put(data_signal)
                # 判断接收方的缓冲区容量大小
                if send_to_satellite.phy_current_get_buffer_size < send_to_satellite.max_buffer_size:
                    await send_to_satellite.phy_get_buffer.put((data_signal, data_size, delay, send_to_satellite.phy_get_buffer.qsize()))
                    send_to_satellite.phy_current_get_buffer_size = send_to_satellite.phy_current_get_buffer_size + data_size
                else:
                    global_variables.count_total_loss_packet_number = global_variables.count_total_loss_packet_number + 1
                    # print(f'User {self.id} cant sent to satellite {send_to_satellite.id}, its buffer current {send_to_satellite.phy_current_get_buffer_size}')
            await asyncio.sleep(wait_time)




    async def start_user_receive_behavior_async(self):
        while True:
            data_signal, data_size, delay, queue_length = await self.receiver_buffer.get()
            data_packet = await Stack.get_packet_from_bits(data_signal)
            if data_packet.destination != self.ip_address:
                self.receiver_buffer.task_done()
                continue
            # 处理普通数据包的逻辑
            if data_packet.protocol == 0x0064:
                if data_packet.destination == self.ip_address:
                    self.globalVariables.count_total_arrive_packet_number = self.globalVariables.count_total_arrive_packet_number + 1
                    self.globalVariables.count_total_packet_delay = self.globalVariables.count_total_packet_delay + delay
                    self.globalVariables.count_total_arrive_packet_size = self.globalVariables.count_total_arrive_packet_size + data_size
                    # self.globalVariables.count_total_packet_delay = self.globalVariables.count_total_packet_delay + get_current_timestamp_ms() - data_packet.timestamp

                    # print(f'user {self.id} received data: {data_packet.data}. ')
                    pass
                else:
                    print(f'user {self.id} wrong packet receive. ')
            # 接入认证的逻辑
            elif data_packet.protocol == 0x0001:
                access_state = int(Regular.get_attribute_from_message(PATTERN=Regular.ACCESS_STATE_PATTERN, message=data_packet.data))
                if access_state:
                    self.access_satellite = self.candidate_access_satellite
                    self.session = Regular.get_attribute_from_message(PATTERN=Regular.SESSION_PATTERN, message=data_packet.data)
                    # print(f'{self.ip_address}, User {self.id} access successful, allocate session {self.session}. {data_packet.data}')
                else:
                    # print(f'User {self.id} access failed. {data_packet.data}')
                    pass
            # 切换认证的逻辑
            elif data_packet.protocol == 0x0002:
                switch_state = int(Regular.get_attribute_from_message(PATTERN=Regular.SWITCH_STATE_PATTERN, message=data_packet.data))
                if switch_state:
                    self.access_satellite = self.candidate_access_satellite
                    # print(f'{self.ip_address}, User {self.id} switch to satellite {self.candidate_access_satellite.id} successful. {data_packet.data}')
                else:
                    # print(f'User {self.id} switch to satellite {self.candidate_access_satellite.id} failed. {data_packet.data}')
                    pass
            self.receiver_buffer.task_done()
            # 处理数据的逻辑

            # 根据协议解析message




    # 开启用户接入和切换的行为
    async def start_user_access_and_switch_satellite_behavior_async(self,  satellites, gateway):
        while True:
            # 判断视野内是否存在卫星
            satellites_in_LOS = self.get_satellites_in_LOS(satellites, gateway)
            if len(satellites_in_LOS) == 0:
                # print(f'No Satellite in sight of User {self.id}')
                if self.ip_address in gateway.user_access_table:
                    del gateway.user_access_table[self.ip_address]
                    self.access_satellite = None
                    self.candidate_access_satellite = None
                await asyncio.sleep(5)
                continue
            candidate_access_satellite = self.get_satellite_with_strongest_signal(satellites_in_LOS)
            # 判断视野内的卫星是否有足够的信号
            if candidate_access_satellite == None:
                # print(f'No Satellite have strong signal to access with User {self.id}')
                if self.ip_address in gateway.user_access_table:
                    del gateway.user_access_table[self.ip_address]
                    self.access_satellite = None
                    self.candidate_access_satellite = None
                await asyncio.sleep(5)
                continue
            self.candidate_access_satellite = candidate_access_satellite
            await asyncio.sleep(5)

    # 获得视距内的卫星
    def get_satellites_in_LOS(self, satellites, gateway):
        cover_radius = satellites[0].cover_radius
        # sat_positions_np = np.radians(np.array([sat.position_2D_GCS[0:2] for sat in satellites]))
        sat_positions_np = np.radians(gateway.satellites_2D_position)
        user_position_np = np.radians(self.position_2D_GCS[0:2])
        # print(self.position_2D_GCS[0:2])
        R = 6371.0
        lat_diff = sat_positions_np[:, 0] - user_position_np[0]
        lon_diff = sat_positions_np[:, 1] - user_position_np[1]
        a = np.sin(lat_diff / 2) ** 2 + np.cos(user_position_np[0]) * np.cos(sat_positions_np[:, 0]) * np.sin(
            lon_diff / 2) ** 2
        c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
        distance = R * c
        visible_indices = np.where(distance < cover_radius)[0]
        # return [sat for i, sat in enumerate(satellites) if distance[i] < sat.cover_radius]
        return [satellites[i] for i in visible_indices]



    # 获得信号足够的卫星
    def get_satellite_with_strongest_signal(self, satellites_in_Los):
        best_satellite = None
        strong_signal = -1000
        for satellite in satellites_in_Los:
            user_satellite_distance = get_distance_3D(self.position_3D_ECI, satellite.position_3D_ECI)  # 单位km
            user_satellite_distance = user_satellite_distance * 1000  # 单位m
            speed_of_light = 3 * 10 ** 8  # 光速 m/s
            FSPL = 20 * np.log10(user_satellite_distance) + 20 * np.log10(satellite.satellite_to_ground_frequency) + 20 * np.log10(
                (4 * np.pi) / speed_of_light)
            # 计算接收点的信号强度 Pr
            L_s = 0  # dB, 系统损耗
            P_r = satellite.satellite_to_ground_power + satellite.satellite_to_ground_gain + self.user_to_satellite_gain - FSPL - L_s
            if P_r > strong_signal and P_r > self.user_receiver_sensitivity:
                strong_signal = P_r
                best_satellite = satellite
        return best_satellite