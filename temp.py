from datetime import datetime
import time

# 当前时间戳
timestamp = 1756966146
print(f"时间戳: {timestamp}")

# 转换为datetime
dt = datetime.fromtimestamp(timestamp)
print(f"datetime对象: {dt}")
print(f"类型: {type(dt)}")

# 输出示例：
# 时间戳: 1634567890.123456
# datetime对象: 2021-10-19 10:38:10.123456
# "timestamp":1756966146000,"time":"2025-09-04 14:09:06"