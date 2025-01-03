import asyncio
import numpy as np

class Constellation:
    def __init__(self, orbit_number, satellite_number_pre_orbit, orbit_inclination, orbit_height, orbit_omega
                 , semi_major_axis, satellites, timer, global_variables, gateway):
        self.orbit_number = orbit_number  # 轨道数量
        self.satellite_number_pre_orbit = satellite_number_pre_orbit  # 每条轨道的卫星数量
        self.orbit_inclination = np.radians(orbit_inclination)  # 轨道倾角 角度转为弧度
        self.orbit_height = orbit_height  # 轨道高度 km

        mu_earth = 3.986e14  # 地球的标准重力参数 mu 单位: m^3/s^2
        a_meters = semi_major_axis * 1000  # 半长轴转换为米
        self.orbit_period_seconds = 2 * np.pi * np.sqrt(a_meters ** 3 / mu_earth)  # 卫星运行周期，单位: 秒
        self.earth_period_hours = 2 * np.pi / 24

        self.semi_major_axis = semi_major_axis

        self.timer = timer
        self.global_variables = global_variables
        self.satellites = satellites  # 存储卫星列表
        self.gateway = gateway
        for satellite in satellites:
            satellite.init_position_parameters(orbit_number=orbit_number, satellite_number_pre_orbit=satellite_number_pre_orbit
                                               , semi_major_axis=semi_major_axis, eccentricity=0, orbit_inclination=self.orbit_inclination, orbit_omega=np.radians(orbit_omega))
            satellite.init_neighbor(satellites=satellites, orbit_number=orbit_number, satellite_number=satellite_number_pre_orbit)
        return

    # 开启位置更新的异步任务任务
    async def start_satellite_position_update_async(self):
        tasks = [asyncio.create_task(satellite.update_position_async(semi_major_axis=self.semi_major_axis, eccentricity=0
                                                                     , orbit_period_seconds=self.orbit_period_seconds
                                                                     , earth_period_hours=self.earth_period_hours
                                                                     , timer=self.timer
                                                                     , global_variables=self.global_variables
                                                                     , gateway=self.gateway)) for satellite in self.satellites]
        await asyncio.gather(*tasks)

    # 开启卫星接收的异步任务
    async def start_satellite_receive_async(self):
        tasks = [asyncio.create_task(satellite.start_satellite_receive_behavior_async(gateway=self.gateway, global_variables=self.global_variables)) for satellite in self.satellites]
        await asyncio.gather(*tasks)
    # 开启存活状态检测的异步任务
    async def state_satellite_send_survival_information_async(self):
        tasks = [asyncio.create_task(satellite.start_satellite_send_survival_information(timer=self.timer)) for satellite in self.satellites]

    async def start_satellite_behavior(self):
        tasks = [asyncio.create_task(satellite.start_satellite_behavior_async(self.semi_major_axis, 0, self.orbit_period_seconds, self.earth_period_hours
                                    , self.timer, self.global_variables, self.gateway)) for satellite in self.satellites]
        await asyncio.gather(*tasks)

