import asyncio
import numpy as np
from src.unils.RandomGenerator import generate_random_ipv4, generate_random_mac, generate_random_session_id
from src.unils.Calculation import position_3D_to_2D, get_current_timestamp_ms, get_distance_3D
from src.simulation.protocolstack import Stack
from src.unils import Regular
from src.simulation.protocolstack import NetworkLayer
import re


class Satellite:
    def __init__(self, id, orbit_id, satellite_id, height, satellite_cone_angle, satellite_to_ground_power
                 , satellite_to_ground_gain, satellite_to_ground_frequency, satellite_to_satellite_transmit_power
                 , satellite_to_satellite_transmit_gain, satellite_to_satellite_receive_gain, satellite_buffer_size, gateway):
        # 卫星编号
        self.id = id
        self.orbit_id = orbit_id
        self.satellite_id = satellite_id
        gateway.satellite_table[self.id] = self

        # 与覆盖有关的参数
        self.height = height
        self.satellite_cone_angle = satellite_cone_angle  # 覆盖圆锥的角度
        self.cone_half_angle = np.radians(self.satellite_cone_angle/2)   # 覆盖圆锥的角度的一半
        self.cover_radius = np.tan(self.cone_half_angle) * self.height

        # 与轨道动力学有关
        self.M_init = -1
        self.R3_Omega = np.zeros(shape=(3, 3))
        self.R1_i = np.zeros(shape=(3, 3))
        self.R3_omega = np.zeros(shape=(3, 3))
        self.position_2D_GCS = np.zeros(shape=(1, 3))  # 地理坐标系 纬度/经度/高度
        self.position_3D_ECI = np.zeros(shape=(1, 3))  # 地心惯性坐标系 x/y/z

        # 物理参数
        self.satellite_to_ground_power = satellite_to_ground_power
        self.satellite_to_ground_gain = satellite_to_ground_gain
        self.satellite_to_ground_frequency = satellite_to_ground_frequency
        self.satellite_to_satellite_transmit_power = satellite_to_satellite_transmit_power
        self.satellite_to_satellite_transmit_gain = satellite_to_satellite_transmit_gain
        self.satellite_to_satellite_receive_gain = satellite_to_satellite_receive_gain
        self.bandwith = 1 * 1024 * 1024 * 8# 1Gbps


        # 网络参数
        self.ip_address = generate_random_ipv4()
        self.mac_address = generate_random_mac()
        self.satellite_buffer_size = satellite_buffer_size

        # 缓冲区
        self.max_buffer_size = 1024 * 20  # MB
        # 物理层缓冲区
        self.phy_get_buffer = asyncio.Queue()  # 物理层 卫星从其他地方接收数据的队列
        self.phy_current_get_buffer_size = 0
        self.phy_wait_buffer = asyncio.Queue()  # 物理层 链路层发送到物理层的队列
        self.phy_send_orbit_plus_buffer = asyncio.Queue()  # 物理层 轨道编号+1的等待发送队列
        self.phy_send_orbit_minus_buffer = asyncio.Queue()  # 物理层 轨道编号-1的等待发送队列
        self.phy_send_satellite_plus_buffer = asyncio.Queue()  # 物理层 卫星编号+1的等待发送队列
        self.phy_send_satellite_minus_buffer = asyncio.Queue()  # 物理层 卫星编号-1的等待发送队列
        self.phy_downlink_buffer = asyncio.Queue()  # 向用户传输数据的等待队列

        # 链路层缓冲区
        self.link_get_buffer = asyncio.Queue()  # 链路层 卫星从物理层接收数据的队列
        self.link_wait_buffer = asyncio.Queue()  # 链路层 卫星从网络层接收的数据队列

        # 网络层缓冲区
        self.network_get_buffer = asyncio.Queue()  # 网络层 卫星从链路层接收数据的队列

        # 邻居表和用户表
        self.neighbor_table = {}  # ip: satellite
        self.mac_table = {}
        self.user_table = {}
        self.routing_table = {}
        self.state = True  # 自身的存活状态
        return



    def init_position_parameters(self, orbit_number, satellite_number_pre_orbit, semi_major_axis, eccentricity, orbit_inclination, orbit_omega):
        Omega = np.radians(self.orbit_id * (360 / orbit_number))  # 计算升交点赤经
        delta_f = self.orbit_id * (2 * np.pi / (orbit_number * satellite_number_pre_orbit))  # 计算相位偏差
        self.M_init = np.radians(self.satellite_id * (360 / satellite_number_pre_orbit)) + delta_f  # 计算平近点角
        nu = self.M_init  # 由于固定偏心率为0，轨道为圆形，真近点角等于平近点角
        r = semi_major_axis * (1 - eccentricity ** 2) / (1 + eccentricity * np.cos(nu))
        self.R3_Omega = np.array([[np.cos(Omega), -np.sin(Omega), 0],
                                  [np.sin(Omega), np.cos(Omega), 0],
                                  [0, 0, 1]])
        self.R1_i = np.array([[1, 0, 0],
                              [0, np.cos(orbit_inclination), -np.sin(orbit_inclination)],
                              [0, np.sin(orbit_inclination), np.cos(orbit_inclination)]])
        self.R3_omega = np.array([[np.cos(orbit_omega), -np.sin(orbit_omega), 0],
                                  [np.sin(orbit_omega), np.cos(orbit_omega), 0],
                                  [0, 0, 1]])
        # 初始化地心惯性坐标系 3D坐标
        x_prime = r * np.cos(nu)
        y_prime = r * np.sin(nu)
        position_vector_orbital_plane = np.array([[x_prime], [y_prime], [0]])
        self.position_3D_ECI = (self.R3_Omega @ self.R1_i @ self.R3_omega @ position_vector_orbital_plane).T[0]
        self.position_2D_GCS = position_3D_to_2D(self.position_3D_ECI)
        return

    def init_neighbor(self, satellites, orbit_number, satellite_number):
        neighbor_orbit_plus = satellites[
            ((self.orbit_id + 1) % orbit_number) * satellite_number + self.satellite_id]
        neighbor_orbit_minus = satellites[
            ((self.orbit_id - 1) % orbit_number) * satellite_number + self.satellite_id]
        neighbor_satellite_plus = satellites[
            self.orbit_id * satellite_number + ((self.satellite_id + 1) % satellite_number)]
        neighbor_satellite_minus = satellites[
            self.orbit_id * satellite_number + ((self.satellite_id - 1) % satellite_number)]
        # 存储邻居卫星，state存活状态，时间戳用于记录时间
        self.neighbor_table[neighbor_orbit_plus.ip_address] = {'satellite': neighbor_orbit_plus, 'state': True, 'timestamp':0, 'propagation_delay': 3000}
        self.neighbor_table[neighbor_orbit_minus.ip_address] = {'satellite': neighbor_orbit_minus, 'state': True, 'timestamp':0, 'propagation_delay': 3000}
        self.neighbor_table[neighbor_satellite_plus.ip_address] = {'satellite': neighbor_satellite_plus, 'state': True, 'timestamp':0, 'propagation_delay': 3000}
        self.neighbor_table[neighbor_satellite_minus.ip_address] = {'satellite': neighbor_satellite_minus, 'state': True, 'timestamp':0, 'propagation_delay': 3000}

        # print(self.neighbor_table)
        return


    async def start_satellite_behavior_async(self, semi_major_axis, eccentricity, orbit_period_seconds, earth_period_hours
                                    , timer, global_variables, gateway):
        # 同时启动所有行为
        await asyncio.gather(
            self.update_position_async(semi_major_axis, eccentricity, orbit_period_seconds, earth_period_hours
                                    , timer, global_variables, gateway),
            self.start_satellite_send_survival_information(timer),
            self.start_satellite_receive_behavior_async(gateway, global_variables)
        )




    async def update_position_async(self, semi_major_axis, eccentricity, orbit_period_seconds, earth_period_hours
                                    , timer, global_variables, gateway):
        while True:
            M = self.M_init + (2 * np.pi / orbit_period_seconds) * timer.now_time_seconds
            M = M % (2 * np.pi)
            nu = M
            r = semi_major_axis * (1 - eccentricity ** 2) / (1 + eccentricity * np.cos(nu))
            x_prime = r * np.cos(nu)
            y_prime = r * np.sin(nu)
            position_vector_orbital_plane = np.array([[x_prime], [y_prime], [0]])
            self.position_3D_ECI = (self.R3_Omega @ self.R1_i @ self.R3_omega @ position_vector_orbital_plane).T[0]
            # 3D坐标系是惯性的所以不需要考虑地球自转，而2D需要考虑地球自转
            theta = earth_period_hours * timer.now_time_seconds / 3600
            _position_3D = np.array([
                [self.position_3D_ECI[0] * np.cos(theta) + self.position_3D_ECI[1] * np.sin(theta)]
                , [-self.position_3D_ECI[0] * np.sin(theta) + self.position_3D_ECI[1] * np.cos(theta)]
                , [self.position_3D_ECI[2]]])
            self.position_2D_GCS = position_3D_to_2D(_position_3D)
            global_variables.globle_satellite_position_2D_GCS[self.id] ={'id': self.id
                ,'lat': self.position_2D_GCS[1], 'lon': self.position_2D_GCS[0], 'height': self.height
                , 'orbit_id': self.orbit_id, 'satellite_id': self.satellite_id}
            global_variables.globle_satellite_position_3D_ECI[self.id] = {'id': self.id
                    , 'x': self.position_3D_ECI[0], 'y': self.position_3D_ECI[1],'z': self.position_3D_ECI[2]
                    , 'orbit_id': self.orbit_id, 'satellite_id': self.satellite_id}
            # print(global_variables.globle_satellite_position_3D_ECI)
            # print(self.position_2D_GCS)
            gateway.satellites_2D_position[self.id] = self.position_2D_GCS[0:2].T
            # print(gateway.satellites_2D_position)
            # 计算与相邻卫星的距离
            for neighbor in self.neighbor_table.values():
                neighbor['propagation_delay'] = get_distance_3D(position_3D_1=self.position_3D_ECI, position_3D_2=neighbor['satellite'].position_3D_ECI) / 299792 # 光速

            await asyncio.sleep(1)

    # 卫星会固定向周围的四个卫星发送存活信息
    async def start_satellite_send_survival_information(self, timer):
        while True:
            # 更新一下路由表，清空
            self.routing_table.clear()

            # 检查缓冲区容量
            if self.phy_current_get_buffer_size < - 0.1:
                print('Satellite ', self.id, ' buffer size massive error ! current buffer size = ', self.phy_current_get_buffer_size
                      , '. I have set current buffer size = 0!')
                self.phy_current_get_buffer_size = 0
            elif self.phy_current_get_buffer_size > self.max_buffer_size:
                print('Satellite ', self.id, ' buffer over flow!', self.phy_current_get_buffer_size)
                self.state = False
                await asyncio.sleep(30)
                self.state = True

            if self.state:
                # 检测邻居的存活状态
                for neighbor in self.neighbor_table.values():
                    if timer.now_time_seconds - neighbor['timestamp'] > 20:
                        neighbor['state'] = False
                # 发送自己的存活状态
                for neighbor in self.neighbor_table.values():
                    data_size = 0.1
                    neighbor_satellite = neighbor['satellite']
                    message = f'I am Satellite [satelliteid:{self.id}], my ip is [satelliteip:{self.ip_address}], my survival state is [state:{True}]'
                    network_protocol = 0x0008
                    data_signal = await Stack.create_message_to_bits(message=message, source_ip=self.ip_address
                                                               , target_ip=neighbor_satellite.ip_address, network_ttl=2
                                                               , network_protocol=network_protocol, source_mac=self.mac_address
                                                               , target_mac=neighbor_satellite.mac_address, type=0x0032, size=0.1, timestamp=get_current_timestamp_ms())
                    # print(data_signal)
                    # await neighbor_satellite.phy_get_buffer.put(data_signal)
                    delay = 0
                    await neighbor_satellite.phy_get_buffer.put((data_signal, data_size, delay, neighbor_satellite.phy_get_buffer.qsize()))
                    neighbor_satellite.phy_current_get_buffer_size = neighbor_satellite.phy_current_get_buffer_size + data_size
            else:
                print(f'I am Satellite [satelliteid:{self.id}], my ip is [satelliteip:{self.ip_address}], I died :(')
            await asyncio.sleep(10)




    async def start_satellite_receive_behavior_async(self, gateway, global_variables):
        while True:
            if self.state is not True:
                print(f'Satellite {self.id} packet loss because i deid. I lost {self.phy_get_buffer.qsize()} packet  :(')
                global_variables.count_total_loss_packet_number = global_variables.count_total_loss_packet_number + self.phy_get_buffer.qsize()
                self.phy_get_buffer = asyncio.Queue()
                self.phy_current_get_buffer_size = 0
                await asyncio.sleep(5)
                continue

            data_signal, data_size, delay, queue_length = await self.phy_get_buffer.get()
            self.phy_current_get_buffer_size = self.phy_current_get_buffer_size - data_size
            data_packet = await Stack.get_packet_from_bits(data_signal)

            return_dict = await self.protocol_process(data_packet=data_packet, gateway=gateway, global_variables=global_variables)
            if return_dict['can_i_forward']:
                message = return_dict['information']['message']
                source_ip = return_dict['information']['source_ip']
                target_ip = return_dict['information']['target_ip']
                network_ttl = return_dict['information']['network_ttl']
                network_protocol = return_dict['information']['network_protocol']
                target_mac = return_dict['information']['target_mac']
                data_packet_size = return_dict['information']['data_packet_size']
                current_time = return_dict['information']['current_time']
                target_buffer = return_dict['information']['target_buffer']
                target_entity = return_dict['information']['target_entity']
            else:
                continue
            data_signal = await Stack.create_message_to_bits(message=message, source_ip=source_ip
                                                             , target_ip=target_ip, network_ttl=network_ttl, network_protocol=network_protocol
                                                             , source_mac=self.mac_address, target_mac=target_mac, type=0x0032, size=data_packet_size, timestamp=current_time)
            # 传播时延
            # await target_buffer.put(data_signal)
            # [传输时延 第一部分]   [传播时延  第二部分]  [处理时延1ms]  [排队时延=处理时延*前面的数据包数量]
            delay = delay + data_size * 1024 * 8 / self.bandwith * 1e3 + get_distance_3D(self.position_3D_ECI, target_entity.position_3D_ECI) * 1e3 * 1e3 / 3e8 + 0.5 + 0.5 * queue_length
            if target_entity.phy_current_get_buffer_size < target_entity.max_buffer_size:
                await target_buffer.put((data_signal, data_packet_size, delay, target_buffer.qsize()))
                target_entity.phy_current_get_buffer_size = target_entity.phy_current_get_buffer_size + data_size
            else:
                global_variables.count_total_loss_packet_number = global_variables.count_total_loss_packet_number + 1
                # print(f'Satellite {self.id} cant sent to satellite {target_entity.id}, its buffer current {target_entity.phy_current_get_buffer_size}')
            self.phy_get_buffer.task_done()


    # async def start_satellite_receive_behavior_async(self, gateway, global_variables):
    #     while True:
    #         if not self.state:
    #             lost_packets = self.phy_get_buffer.qsize()
    #             print(f'Satellite {self.id} packet loss because it died. I lost {lost_packets} packets :(')
    #             global_variables.count_total_loss_packet_number += lost_packets
    #             self.phy_get_buffer = asyncio.Queue()
    #             self.phy_current_get_buffer_size = 0
    #             await asyncio.sleep(5)
    #             continue
    #
    #         data_signal, data_size, delay, queue_length = await self.phy_get_buffer.get()
    #         self.phy_current_get_buffer_size -= data_size
    #         data_packet = await Stack.get_packet_from_bits(data_signal)
    #
    #         return_dict = await self.protocol_process(data_packet=data_packet, gateway=gateway,
    #                                                   global_variables=global_variables)
    #         if not return_dict.get('can_i_forward', False):
    #             continue
    #
    #         await self.process_and_forward_packet(return_dict, delay, queue_length, data_size, global_variables)
    #
    #         self.phy_get_buffer.task_done()
    #
    # async def process_and_forward_packet(self, return_dict, delay, queue_length, data_size, global_variables):
    #     info = return_dict['information']
    #     new_data_signal = await Stack.create_message_to_bits(
    #         message=info['message'],
    #         source_ip=info['source_ip'],
    #         target_ip=info['target_ip'],
    #         network_ttl=info['network_ttl'],
    #         network_protocol=info['network_protocol'],
    #         source_mac=self.mac_address,
    #         target_mac=info['target_mac'],
    #         type=0x0032,
    #         size=info['data_packet_size'],
    #         timestamp=info['current_time']
    #     )
    #
    #     delay = self.calculate_total_delay(delay, data_size, queue_length, info['target_entity'])
    #     target_entity = info['target_entity']
    #     target_buffer = info['target_buffer']
    #     data_packet_size = info['data_packet_size']
    #
    #     if target_entity.phy_current_get_buffer_size < target_entity.max_buffer_size:
    #         await target_buffer.put((new_data_signal, data_packet_size, delay, target_buffer.qsize()))
    #         target_entity.phy_current_get_buffer_size += data_size
    #     else:
    #         global_variables.count_total_loss_packet_number += 1
    #
    # def calculate_total_delay(self, initial_delay, data_size, queue_length, target_entity):
    #     transmission_delay = data_size * 1024 * 8 / self.bandwith * 1e3
    #     propagation_delay = get_distance_3D(self.position_3D_ECI, target_entity.position_3D_ECI) * 1e3 * 1e3 / 3e8
    #     process_delay = 0.5  # Fixed processing delay
    #     queuing_delay = 0.5 * queue_length  # Queuing delay
    #
    #     return initial_delay + transmission_delay + propagation_delay + process_delay + queuing_delay






    # 协议处理 应该放到协议栈函数中
    async def protocol_process(self, data_packet, gateway, global_variables):
        if data_packet.protocol == 0x0064:
            return_dict = await self.protocol_0x0064(data_packet=data_packet, gateway=gateway, global_variables=global_variables)
            return return_dict
        # 接入认证的处理逻辑
        elif data_packet.protocol == 0x0001:
            message, source_ip, target_ip, network_ttl, network_protocol, target_mac, data_packet_size, current_time \
                , target_buffer, target_entity = await self.protocol_0x0001(data_packet=data_packet, gateway=gateway)
        # 切换认证的处理逻辑
        elif data_packet.protocol == 0x0002:
            message, source_ip, target_ip, network_ttl, network_protocol, target_mac, data_packet_size, current_time \
                , target_buffer, target_entity = await self.protocol_0x0002(data_packet=data_packet, gateway=gateway)
        # 更新邻居卫星状态的数据包
        elif data_packet.protocol == 0x0008:
            await self.protocol_0x0008(data_packet=data_packet)
            return {'can_i_forward': False,'information': None}
        else:
            print('Unknown protocol: ', data_packet)
            return {'can_i_forward': False,'information': None}
        return {'can_i_forward': True, 'information':{'message':message, 'source_ip':source_ip, 'target_ip':target_ip, 'network_ttl': 64, 'network_protocol':network_protocol
            , 'target_mac':'aa', 'data_packet_size': data_packet.size, 'current_time': get_current_timestamp_ms()
            , 'target_buffer': target_buffer, 'target_entity':target_entity}}


    # 接入认证的处理逻辑 协议0x0001
    async def protocol_0x0001(self, data_packet, gateway):
        network_protocol = 0x0001
        user_ip = data_packet.source
        source_ip = self.ip_address
        target_ip = user_ip
        userid = Regular.get_attribute_from_message(PATTERN=Regular.USERID_PATTERN, message=data_packet.data)
        username = Regular.get_attribute_from_message(PATTERN=Regular.USERNAME_PATTERN, message=data_packet.data)
        password = Regular.get_attribute_from_message(PATTERN=Regular.PASSWORD_PATTERN, message=data_packet.data)
        target_buffer = gateway.user_table[userid].receiver_buffer
        target_entity = gateway.user_table[userid]
        if userid in gateway.user_authentication_table:
            if gateway.user_authentication_table[userid]['username'] == username and \
                    gateway.user_authentication_table[userid]['password'] == password:
                session = generate_random_session_id()
                gateway.user_session_table[user_ip] = {'session_id': session}
                gateway.user_access_table[user_ip] = {'user': gateway.user_table[userid],
                                                      'satellite_ip': self.ip_address, 'satellite': self}
                message = f'Congratulations! Access [access_state:{1}], Satellite [satelliteid:{self.id}] access is allowed, allocates session [session:{session}] to {user_ip}, userid {userid}.'
                # print(message)
            else:
                message = f'Wrong username and password! Access [access_state:{0}], Satellite [satelliteid:{self.id}] access is not allowed, no [session:{None}].'
        else:
            message = f'Unregistered illegal users! Access [access_state:{0}], Satellite [satelliteid:{self.id}] access is not allowed, no [session:{None}]. '
        return message, source_ip, target_ip, 64, network_protocol, 'aa', data_packet.size, get_current_timestamp_ms(), target_buffer, target_entity

    # 切换认证的处理逻辑 协议0x0002
    async def protocol_0x0002(self, data_packet, gateway):
        network_protocol = 0x0002
        user_ip = data_packet.source
        source_ip = self.ip_address
        target_ip = user_ip
        userid = Regular.get_attribute_from_message(PATTERN=Regular.USERID_PATTERN, message=data_packet.data)
        session = Regular.get_attribute_from_message(PATTERN=Regular.SESSION_PATTERN, message=data_packet.data)
        target_buffer = gateway.user_table[userid].receiver_buffer
        target_entity = gateway.user_table[userid]
        # print(f'from message: {session}, from gateway: {gateway.user_session_table[user_ip]["session_id"]}')
        if user_ip in gateway.user_session_table and gateway.user_session_table[user_ip]['session_id'] == session:
            message = f'Congratulations! Switch [switch_state:{1}], Satellite [satelliteid:{self.id}] switch is allowed.'
            gateway.user_access_table[user_ip] = {'user': gateway.user_table[userid], 'satellite_ip': self.ip_address,
                                                  'satellite': self}
        else:
            message = f'Unauthorized illegal user cannot switch [switch_state:{0}], Satellite [satelliteid:{self.id}] switch is not allowed.'
        return message, source_ip, target_ip, 64, network_protocol, 'aa', data_packet.size, get_current_timestamp_ms(), target_buffer, target_entity

    # 更新邻居卫星状态的数据包 协议0x0008
    async def protocol_0x0008(self, data_packet):
        neighbor_ip = data_packet.source
        survival_state = Regular.get_attribute_from_message(PATTERN=Regular.STATE_PATH_PATTERN,
                                                            message=data_packet.data)
        if neighbor_ip in self.neighbor_table and survival_state == 'True':
            self.neighbor_table[neighbor_ip]['state'] = True

        elif neighbor_ip not in self.neighbor_table:
            print('You are not in my neighbor table')
        else:
            print('you are died :(')
        return


    async def protocol_0x0064(self, data_packet, gateway, global_variables):
        return_dict = {'can_i_forward': False, 'information': None}
        network_protocol = 0x0064
        source_ip = data_packet.source
        target_ip = data_packet.destination

        has_routing_path = int(Regular.get_attribute_from_message(PATTERN=Regular.HAS_ROUTING_PATH_PATTERN,
                                                              message=data_packet.data))
        # 如果有路由路径 直接查找数据包中存储的路由路径即可
        if has_routing_path:
            routing_ip_path = Regular.get_routing_path_from_message(message=data_packet.data.decode())
        # 如果没有路由路径 那么需要计算一条路由路径
        else:
            # 判断用户是否在接入表里
            if data_packet.destination in gateway.user_access_table:
                # 如果用户在接入表里则找到其接入的卫星
                access_satellite_ip = gateway.user_access_table[data_packet.destination]['satellite'].ip_address
                # 判断目标卫星是否在路由表里
                if access_satellite_ip in self.routing_table:
                    # 目标卫星在接入表里，查表直接找到路径
                    path = self.routing_table[access_satellite_ip]
                else:
                    # 目标卫星不在接入表，计算路由路径
                    path = await NetworkLayer.find_path(M=gateway.orbit_number, N=gateway.satellite_number_pre_orbit
                                                        , src=self.id,
                                                        dst=gateway.user_access_table[data_packet.destination][
                                                            'satellite'].id)
                    # 将路径存入路由表
                    self.routing_table[access_satellite_ip] = path
                routing_ip_path = [gateway.satellite_table[satellite_id].ip_address for satellite_id in path]

            else:
                # 如果用户不在接入表里 则无法转发 [丢包]
                # print('packet losss because user not access any satellite')
                global_variables.count_total_loss_packet_number = global_variables.count_total_loss_packet_number + 1
                return return_dict
        # 现在都获得一条routing ip path了
        del routing_ip_path[0]
        # 判断 routing_ip_path 是否包含任何元素
        # 如果routing_ip_path长度大于0 则表明数据包需要转发
        if len(routing_ip_path) != 0:
            routing_ip_path_str = ', '.join(routing_ip_path).encode()
            data_packet.data = data_packet.data.replace(b'has_routing_path:0', b'has_routing_path:1')
            data_packet.data = re.sub(rb'\[r_p:[^\]]+\]', b'[r_p:' + routing_ip_path_str + b']',
                                      data_packet.data)
            target_entity = self.neighbor_table[routing_ip_path[0]]['satellite']
            target_buffer = target_entity.phy_get_buffer
            message = data_packet.data.decode()
        else: # 否则 routing_ip_path长度小于等于0 按理来说数据包要转发到自己下面的用户
            if target_ip in gateway.user_access_table and gateway.user_access_table[target_ip][
                'satellite_ip'] == self.ip_address:
                target_entity = gateway.user_access_table[target_ip]['user']
                target_buffer = target_entity.receiver_buffer
                message = data_packet.data.decode()
            else:
                # print('Packet loss because user not access in me')
                global_variables.count_total_loss_packet_number = global_variables.count_total_loss_packet_number + 1
                return return_dict
        information = {'message':message, 'source_ip':source_ip, 'target_ip':target_ip, 'network_ttl': 64, 'network_protocol':network_protocol
            , 'target_mac':'aa', 'data_packet_size': data_packet.size, 'current_time': get_current_timestamp_ms()
            , 'target_buffer': target_buffer, 'target_entity': target_entity}
        return_dict['can_i_forward'] = True
        return_dict['information'] = information
        return return_dict





