import asyncio
import cProfile
import pstats

import random
from concurrent.futures import ThreadPoolExecutor
from src.unils.ReadFile import load_config_ini_to_dict, load_npy
from src.simulation.Satellite import Satellite
from src.simulation.Constellation import Constellation
from src.simulation.Timer import Timer
from src.simulation.Websocket import Websocket
from src.simulation.GlobalVariables import GlobalVariables
from src.simulation.User import User
from simulation.Gateway import Gateway




async def packet_arrive_rate(globalVariables):
    while True:
        if globalVariables.count_total_packet_number > 0 and globalVariables.count_total_arrive_packet_number > 0:
            print('packet_loss_rate', str(round(globalVariables.count_total_loss_packet_number / globalVariables.count_total_packet_number * 100, 4)) + ' %')
            print('delay', str(globalVariables.count_total_packet_delay / globalVariables.count_total_arrive_packet_number) + ' ms')
            print('throughput', globalVariables.count_total_arrive_packet_size / 1024, ' GB/s')
        await asyncio.sleep(1)

async def start_user_receive_behavior_async(users):
    tasks = [asyncio.create_task(user.start_user_receive_behavior_async()) for user in users]
    await asyncio.gather(*tasks)
async def start_user_access_and_switch_satellite_behavior_async(users, satellites, gateway):
    tasks = [asyncio.create_task(user.start_user_access_and_switch_satellite_behavior_async(satellites=satellites, gateway=gateway)) for user in users]
    await asyncio.gather(*tasks)
async def start_user_send_behavior_async(users, gateway, global_variables):
    tasks = [asyncio.create_task(user.start_user_send_behavior_async(gateway=gateway, global_variables=global_variables)) for user in users]
    await asyncio.gather(*tasks)
async def start_user_behavior(users, gateway, global_variables, satellites):
    tasks = [asyncio.create_task(user.start_user_behavior_async(gateway, global_variables, satellites)) for user in users]
    await asyncio.gather(*tasks)



async def main():
    config_ini_path = '../config/config.ini'
    population_npy_path = '../resource/population_matrix.npy'
    population_array = load_npy(population_npy_path)
    config_dict = load_config_ini_to_dict(config_ini_path)
    orbit_number = int(config_dict['Constellation-Parameters']['orbit_number'])
    satellite_number_pre_orbit = int(config_dict['Constellation-Parameters']['satellite_number_pre_orbit'])
    orbit_inclination = int(config_dict['Constellation-Parameters']['orbit_inclination'])
    orbit_height = int(config_dict['Constellation-Parameters']['orbit_height'])
    orbit_omega = int(config_dict['Constellation-Parameters']['orbit_omega'])
    satellite_cone_angle = int(config_dict['Satellite-Parameters']['satellite_cone_angle'])
    satellite_to_ground_power = int(config_dict['Satellite-Parameters']['satellite_to_ground_power'])
    satellite_to_ground_gain = int(config_dict['Satellite-Parameters']['satellite_to_ground_gain'])
    satellite_to_ground_frequency = int(config_dict['Satellite-Parameters']['satellite_to_ground_frequency'])
    satellite_to_satellite_transmit_power = int(config_dict['Satellite-Parameters']['satellite_to_satellite_transmit_power'])
    satellite_to_satellite_transmit_gain = int(config_dict['Satellite-Parameters']['satellite_to_satellite_transmit_gain'])
    satellite_to_satellite_receive_gain = int(config_dict['Satellite-Parameters']['satellite_to_satellite_receive_gain'])
    satellite_buffer_size = float(config_dict['Satellite-Parameters']['satellite_buffer_size'])
    user_number = int(config_dict['User-Parameters']['user_number'])
    user_to_satellite_gain = int(config_dict['User-Parameters']['user_to_satellite_gain'])
    user_receiver_sensitivity = int(config_dict['User-Parameters']['user_receiver_sensitivity'])
    user_snr = int(config_dict['User-Parameters']['user_snr'])
    user_data_rate = int(config_dict['User-Parameters']['user_data_rate'])
    earth_radius = int(config_dict['Environment-Parameters']['earth_radius'])
    earth_mu = float(config_dict['Environment-Parameters']['earth_mu'])
    network_running_step_time = int(config_dict['Time-Parameters']['network_running_step_time'])
    port = int(config_dict['Webserver-Parameters']['port'])
    request_wait_time = int(config_dict['Webserver-Parameters']['request_wait_time'])



    timer = Timer(network_running_step_time=network_running_step_time)
    global_variables = GlobalVariables()
    websocket = Websocket()
    gateway = Gateway(orbit_number=orbit_number, satellite_number_pre_orbit=satellite_number_pre_orbit)
    gateway.orbit_number = orbit_number
    gateway.satellite_number_pre_orbit = satellite_number_pre_orbit

    satellites = [Satellite(id=i * satellite_number_pre_orbit + o, orbit_id=i, satellite_id=o, height=orbit_height
                            , satellite_cone_angle=satellite_cone_angle
                            , satellite_to_ground_power=satellite_to_ground_power
                            , satellite_to_ground_gain=satellite_to_ground_gain
                            , satellite_to_ground_frequency=satellite_to_ground_frequency
                            , satellite_to_satellite_transmit_power=satellite_to_satellite_transmit_power
                            , satellite_to_satellite_transmit_gain=satellite_to_satellite_transmit_gain
                            , satellite_to_satellite_receive_gain=satellite_to_satellite_receive_gain
                            , satellite_buffer_size=satellite_buffer_size, gateway=gateway) for i in range(0, orbit_number) for o in range(0, satellite_number_pre_orbit)]
    users = [User(user_id=i, population_array=population_array, user_to_satellite_gain=user_to_satellite_gain
                  , user_receiver_sensitivity=user_receiver_sensitivity, user_snr=user_snr
                  , user_data_rate=user_data_rate, gateway=gateway, globalVariables=global_variables) for i in range(0, user_number)]

    constellation = Constellation(orbit_number=orbit_number, satellite_number_pre_orbit=satellite_number_pre_orbit
                                  , orbit_inclination=orbit_inclination, orbit_height=orbit_height
                                  , semi_major_axis=orbit_height + earth_radius, orbit_omega=orbit_omega
                                  , satellites=satellites, timer=timer, global_variables=global_variables, gateway=gateway)
    # 运行时间更新的异步任务
    asyncio.create_task(timer.update_time())
    # 运行星座运动的异步任务
    # asyncio.create_task(constellation.start_satellite_position_update_async())
    # asyncio.create_task(constellation.start_satellite_receive_async())
    # asyncio.create_task(constellation.state_satellite_send_survival_information_async())
    asyncio.create_task(constellation.start_satellite_behavior())

    # asyncio.create_task(start_user_receive_behavior_async(users=users))
    # asyncio.create_task(start_user_access_and_switch_satellite_behavior_async(users=users, satellites=satellites, gateway=gateway))
    # asyncio.create_task(start_user_send_behavior_async(users=users, gateway=gateway, global_variables=global_variables))
    asyncio.create_task(start_user_behavior(users=users, gateway=gateway, global_variables=global_variables, satellites=satellites))




    # 开启websocket服务并发送数据 用于绘制效果
    asyncio.create_task(websocket.start_web_server(port=port))
    asyncio.create_task(websocket.start_websocket_task_async(type='satellite-3D-position'
                                                             , obj=global_variables, attribute='globle_satellite_position_3D_ECI'
                                                             , request_wait_time=request_wait_time))
    user_position = [{'user_id':user.id , 'x':user.position_3D_ECI[0] , 'y':user.position_3D_ECI[1], 'z':user.position_3D_ECI[2]} for user in users]
    asyncio.create_task(websocket.start_websocket_task_data_async(type='user-position'
                                                             , data=user_position
                                                             , request_wait_time=request_wait_time))
    asyncio.create_task(websocket.user_satellite_connect_task(gateway=gateway))
    asyncio.create_task(websocket.start_websocket_network_delay_async(type='network-delay', timer=timer, global_variables=global_variables, request_wait_time=request_wait_time))
    asyncio.create_task(websocket.start_websocket_network_arrive_rate_async(type='network-arrive-rate', timer=timer,
                                                                      global_variables=global_variables,
                                                                      request_wait_time=request_wait_time))

    asyncio.create_task(packet_arrive_rate(globalVariables=global_variables))

    import time
    while True:
        if timer.now_time_seconds < 60:
            await asyncio.sleep(1)
        else:
            break
    return




if __name__ == '__main__':
    profiler = cProfile.Profile()
    profiler.enable()
    asyncio.run(main())
    profiler.disable()
    stats = pstats.Stats(profiler).sort_stats('cumulative')
    stats.print_stats()