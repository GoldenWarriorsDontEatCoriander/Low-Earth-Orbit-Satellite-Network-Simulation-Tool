import json
import asyncio
from aiohttp import web
from src.unils.Calculation import position_2D_to_3D

class Websocket:
    def __init__(self):
        self.app = web.Application()
        self.app['websockets'] = set()
        self.app.router.add_get('/ws', self.websocket_handler)

    # 在等待时间内向webserver发送一组数据  通过类寻找变量
    async def start_websocket_task_async(self, type, obj, attribute, request_wait_time):
        while True:
            data = getattr(obj, attribute, "start_websocket_task_async() do not given right obj or attribute!")
            message = {'type': type, 'data': data}
            for ws in self.app['websockets']:
                await ws.send_str(json.dumps(message))
            await asyncio.sleep(request_wait_time)

    # 在等待时间内向webserver发送一组数据  通过类寻找变量
    async def start_websocket_task_data_async(self, type, data, request_wait_time):
        while True:
            message = {'type': type, 'data': data}
            for ws in self.app['websockets']:
                await ws.send_str(json.dumps(message))
            await asyncio.sleep(request_wait_time)

    async def start_websocket_network_delay_async(self, type, timer, global_variables, request_wait_time):
        while True:
            if global_variables.count_total_arrive_packet_number == 0:
                delay = 0
            else:
                delay = global_variables.count_total_packet_delay / global_variables.count_total_arrive_packet_number
            data = {'time': timer.now_time_seconds, 'delay':delay}
            message = {'type': type, 'data': data}
            for ws in self.app['websockets']:
                await ws.send_str(json.dumps(message))
            await asyncio.sleep(request_wait_time)

    async def start_websocket_network_arrive_rate_async(self, type, timer, global_variables, request_wait_time):
        while True:
            if global_variables.count_total_packet_number == 0:
                arrive_rate = 0
            else:
                arrive_rate = round(global_variables.count_total_loss_packet_number / global_variables.count_total_packet_number * 100, 4)
            data = {'time': timer.now_time_seconds, 'arrive_rate':arrive_rate}
            message = {'type': type, 'data': data}
            for ws in self.app['websockets']:
                await ws.send_str(json.dumps(message))
            await asyncio.sleep(request_wait_time)

    async def user_satellite_connect_task(self, gateway):
        while True:
            data = []
            for value in gateway.user_access_table.values():
                data.append({'user_x': value['user'].position_3D_ECI[0], 'user_y': value['user'].position_3D_ECI[1],'user_z':value['user'].position_3D_ECI[2],
                             'satellite_x': value['satellite'].position_3D_ECI[0], 'satellite_y': value['satellite'].position_3D_ECI[1],'satellite_z': value['satellite'].position_3D_ECI[2]})
            for ws in self.app['websockets']:
                message = {'type': 'user-satellite-connection', 'data': data}

                # await ws.send_str(json.dumps(global_positions_2d))
                await ws.send_str(json.dumps(message))
            await asyncio.sleep(1)


    async def const_position(self, type, position, request_wait_time):
        while True:
            position_array = position_2D_to_3D(lat=position[0], lon=position[1])
            message = {'type': type, 'data': list(position_array)}
            for ws in self.app['websockets']:
                await ws.send_str(json.dumps(message))
            await asyncio.sleep(request_wait_time)


    # 启动webserver
    async def start_web_server(self, port):
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, 'localhost', port)
        await site.start()
        print("Web server running on http://localhost:" + str(port))

    async def websocket_handler(self, request):
        ws = web.WebSocketResponse()
        await ws.prepare(request)

        # 将新的WebSocket连接添加到连接池
        request.app['websockets'].add(ws)

        try:
            # 永远循环，直到WebSocket连接被关闭
            async for msg in ws:
                pass  # 在这个例子中，服务器不处理从客户端接收的消息
        finally:
            # 当WebSocket连接关闭时，从连接池移除
            request.app['websockets'].remove(ws)
        return ws