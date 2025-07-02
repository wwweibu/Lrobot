#  TODO 配合activity修改
from datetime import datetime


def chinese_time(time_str, duration_dict):
    # 将时间、时长转化为简化格式输出
    if time_str == "待定":
        formatted_time = "待定"
    else:
        dt = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
        formatted_time = ""
        # 从左到右保留到不为零的最后一位
        if dt.year:
            formatted_time += f"{dt.year}年"
        if dt.month:
            formatted_time += f"{dt.month}月"
        if dt.day:
            formatted_time += f"{dt.day}日"
        if dt.hour or dt.minute or dt.second:
            formatted_time += f"{dt.hour}点" if dt.hour else ""
            formatted_time += f"{dt.minute}分" if dt.minute else ""
            formatted_time += f"{dt.second}秒" if dt.second else ""

    if duration_dict == "待定":
        duration_str = "待定"
    else:
        days = duration_dict.get("day", 0)
        hours = duration_dict.get("hour", 0)
        minutes = duration_dict.get("minute", 0)

        # 将所有时间单位合并成字符串
        duration_parts = []
        if days:
            duration_parts.append(f"{int(days)}天")
        if hours:
            duration_parts.append(f"{int(hours)}小时")
        if minutes:
            duration_parts.append(f"{int(minutes)}分钟")

        duration_str = " ".join(duration_parts)

    return formatted_time, duration_str
