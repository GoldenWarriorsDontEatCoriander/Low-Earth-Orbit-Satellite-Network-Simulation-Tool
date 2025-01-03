from src.unils.RandomGenerator import generate_random_session_id

# 根据协议定义不同的内容，返回不同的数据包

async def find_path(M, N, src, dst):
    src_row, src_col = src // N, src % N
    dst_row, dst_col = dst // N, dst % N
    path = []
    current_row, current_col = src_row, src_col

    # 计算行上的最短路径
    row_direction = 1 if (dst_row - src_row) % M <= M // 2 else -1
    while current_row != dst_row:
        path.append(current_row * N + current_col)
        current_row = (current_row + row_direction) % M

    # 计算列上的最短路径
    col_direction = 1 if (dst_col - src_col) % N <= N // 2 else -1
    while current_col != dst_col:
        path.append(current_row * N + current_col)
        current_col = (current_col + col_direction) % N

    path.append(dst_row * N + dst_col)  # 添加目标节点
    return path

