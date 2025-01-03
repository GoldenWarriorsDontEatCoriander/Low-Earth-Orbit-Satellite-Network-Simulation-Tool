

# 存储全局变量的地方，用于绘制/计算指标
class GlobalVariables:
    def __init__(self):
        # 绘制 / 存储卫星的2D 3D位置
        self.globle_satellite_position_2D_GCS = {}
        self.globle_satellite_position_3D_ECI = {}

        # 绘制 / 存储用户的2D 3D位置
        self.globle_user_position_2D_GCS = {}
        self.globle_user_position_3D_ECI = []

        # 绘制 / 存储用户 卫星的连接关系
        self.globle_user_satellite_connect = []

        self.count_total_packet_number = 0  # 生成的总数据包量
        self.count_total_packet_size = 0  # 生成的总数数据包大小 / 用于计算吞吐量
        self.count_total_arrive_packet_number = 0  # 总到达的数据包数量
        self.count_total_arrive_packet_size = 0  # 总到达的数据包大小
        self.count_total_loss_packet_number = 0  # 丢弃的数据包数量

        self.count_total_packet_delay = 0  # 总到达的数据包时延



