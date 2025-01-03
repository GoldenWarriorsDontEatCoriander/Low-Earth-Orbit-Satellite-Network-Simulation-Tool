import configparser
import numpy as np

def load_config_ini(file_path):
    config = configparser.ConfigParser(comment_prefixes=('#', ';'))
    # 读取INI文件
    config.read('../config/config.ini', encoding='utf-8')

    # 读取轨道相关参数
    orbit_number = int(config['Constellation-Parameters']['orbit_number'])
    satellite_number_pre_orbit = int(config['Constellation-Parameters']['satellite_number_pre_orbit'])
    orbit_inclination = int(config['Constellation-Parameters']['orbit_inclination'])
    orbit_height = int(config['Constellation-Parameters']['orbit_height'])
    orbit_omega = int(config['Constellation-Parameters']['orbit_omega'])

    # 读取卫星相关参数
    satellite_cone_angle = int(config['Satellite-Parameters']['satellite_cone_angle'])
    satellite_to_ground_power = int(config['Satellite-Parameters']['satellite_to_ground_power'])
    satellite_to_ground_gain = int(config['Satellite-Parameters']['satellite_to_ground_gain'])
    satellite_to_ground_frequency = int(config['Satellite-Parameters']['satellite_to_ground_frequency'])
    satellite_to_satellite_transmit_power = int(config['Satellite-Parameters']['satellite_to_satellite_transmit_power'])
    satellite_to_satellite_transmit_gain = int(config['Satellite-Parameters']['satellite_to_satellite_transmit_gain'])
    satellite_to_satellite_receive_gain = int(config['Satellite-Parameters']['satellite_to_satellite_receive_gain'])
    satellite_buffer_size = float(config['Satellite-Parameters']['satellite_buffer_size'])

    # 读取用户相关参数
    user_number = int(config['User-Parameters']['user_number'])
    user_receiver_sensitivity = int(config['User-Parameters']['user_receiver_sensitivity'])
    user_snr = int(config['User-Parameters']['user_snr'])
    user_data_rate = int(config['User-Parameters']['user_data_rate'])

    # 读取环境参数
    earth_radius = int(config['Environment-Parameters']['earth_radius'])
    earth_mu = float(config['Environment-Parameters']['earth_mu'])

    # 读取时间相关的参数
    network_running_step_time = int(config['Time-Parameters']['network_running_step_time'])

    return orbit_number, satellite_number_pre_orbit, orbit_inclination, orbit_height, orbit_omega\
        , satellite_cone_angle, satellite_to_ground_power, satellite_to_ground_gain, satellite_to_ground_frequency\
        , satellite_to_satellite_transmit_power, satellite_to_satellite_transmit_gain, satellite_to_satellite_receive_gain\
        , satellite_buffer_size\
        ,user_number, user_receiver_sensitivity, user_snr, user_data_rate\
        , earth_radius, earth_mu\
        , network_running_step_time

def load_config_ini_to_dict(file_path):
    # 创建配置解析器对象
    config = configparser.ConfigParser()
    # 读取INI文件
    config.read(file_path, encoding='utf-8')
    # 创建字典来存储配置数据
    config_dict = {}
    # 遍历所有的节，将它们添加到字典中
    for section in config.sections():
        config_dict[section] = {}
        for key, value in config.items(section):
            config_dict[section][key] = value
    return config_dict

def load_npy(file_path):
    population_array = np.load(file_path)
    return population_array