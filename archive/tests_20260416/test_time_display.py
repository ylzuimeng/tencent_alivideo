#!/usr/bin/env python
"""
测试时间显示功能

验证：
1. UTC 时间转换为北京时间
2. API 响应包含时区信息
3. Jinja2 过滤器工作正常
"""

from utils.time_helpers import utcnow, serialize_datetime, format_datetime_beijing
from datetime import datetime, timezone

print("=" * 60)
print("时间显示功能测试")
print("=" * 60)

# 测试 1: UTC 时间获取
print("\n1. 测试 utcnow() 函数")
utc_dt = utcnow()
print(f"   UTC 时间: {utc_dt}")
print(f"   时区信息: {utc_dt.tzinfo}")
assert utc_dt.tzinfo == timezone.utc, "UTC 时间时区不正确"
print("   ✓ 通过")

# 测试 2: 时间序列化
print("\n2. 测试 serialize_datetime() 函数")
bj_str = serialize_datetime(utc_dt, to_beijing=True)
print(f"   序列化结果: {bj_str}")
assert '+08:00' in bj_str, "序列化结果不包含北京时间时区信息"
print("   ✓ 通过")

# 测试 3: 格式化函数
print("\n3. 测试 format_datetime_beijing() 函数")
formatted = format_datetime_beijing(utc_dt)
print(f"   格式化结果: {formatted}")
assert ':' in formatted, "格式化结果格式不正确"
print("   ✓ 通过")

# 测试 4: 时区转换验证
print("\n4. 测试 UTC 转北京时间（应该 +8 小时）")
test_utc = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
test_bj_str = serialize_datetime(test_utc, to_beijing=True)
print(f"   UTC 时间: 2024-01-01 12:00:00")
print(f"   北京时间: {test_bj_str}")
assert '20:00:00' in test_bj_str or 'T20:00:00' in test_bj_str, "时区转换错误"
print("   ✓ 通过")

# 测试 5: Jinja2 过滤器（需要导入 app）
print("\n5. 测试 Jinja2 过滤器")
try:
    from app import app
    with app.app_context():
        # 使用 Flask 的模板引擎测试过滤器
        result = app.jinja_env.filters['beijing_time'](test_utc)
        print(f"   过滤器输出: {result}")
        assert '20:00' in result or '2024-01-01' in result, "Jinja2 过滤器工作异常"
        print("   ✓ 通过")
except Exception as e:
    print(f"   ✗ 失败: {e}")

print("\n" + "=" * 60)
print("所有测试完成！")
print("=" * 60)
