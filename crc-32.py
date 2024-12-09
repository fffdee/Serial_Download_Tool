import binascii

def calculate_crc32(data):
    crc = binascii.crc32(data)
    return "%08X" % (crc & 0xFFFFFFFF)  # 返回十六进制格式，并确保是8位

# 示例数据
data = b"Hello, world!"

# 计算CRC-32校验和
crc32_checksum = calculate_crc32(data)
print(f"CRC-32 checksum: {crc32_checksum}")
