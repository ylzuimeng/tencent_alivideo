import json

srt = """"[{\"content\":\"醉里挑灯看剑\",\"from\":0.15,\"to\":1.56},{\"content\":\"梦回吹角连营\",\"from\":1.91,\"to\":3.28},{\"content\":\"八百里\",\"from\":3.64,\"to\":4.2},{\"content\":\"分麾下炙\",\"from\":4.2,\"to\":5.06},{\"content\":\"五十弦\",\"from\":5.42,\"to\":6.04},{\"content\":\"翻赛外声\",\"from\":6.04,\"to\":6.89},{\"content\":\"沙场秋点兵\",\"from\":7.26,\"to\":8.48}]"""

def seconds_to_srt_time(t):
    """将秒转换为SRT时间格式HH:MM:SS,mmm"""
    total_ms = int(round(t * 1000))
    hours, remainder = divmod(total_ms, 3600000)
    minutes, remainder = divmod(remainder, 60000)
    seconds, milliseconds = divmod(remainder, 1000)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"

# 输入字符串
input_str = """[{"content":"醉里挑灯看剑","from":0.15,"to":1.56},
{"content":"梦回吹角连营","from":1.91,"to":3.28},
{"content":"八百里","from":3.64,"to":4.2},
{"content":"分麾下炙","from":4.2,"to":5.06},
{"content":"五十弦","from":5.42,"to":6.04},
{"content":"翻赛外声","from":6.04,"to":6.89},
{"content":"沙场秋点兵","from":7.26,"to":8.48}]"""

# 解析JSON数据
data = json.loads(input_str)

# 生成SRT内容
srt_blocks = []
for index, item in enumerate(data, start=1):
    start_time = seconds_to_srt_time(item['from'])
    end_time = seconds_to_srt_time(item['to'])
    content = item['content']
    block = f"{index}\n{start_time} --> {end_time}\n{content}\n"
    srt_blocks.append(block)

srt_content = '\n'.join(srt_blocks)

# 写入文件
with open('subtitle.srt', 'w', encoding='utf-8') as f:
    f.write(srt_content)

print("SRT文件生成成功！")