import base64
import json

# 原始info数据
info_array = [10, 148, 2, 101, 121, 74, 104, 89, 50, 78, 118, 100, 87, 53, 48, 88, 51, 78, 53, 99, 51, 82, 108, 98, 86, 57, 112, 90, 67, 73, 54, 73, 106, 70, 102, 73, 105, 119, 105, 98, 51, 78, 107, 97, 49, 57, 110, 89, 87, 49, 108, 88, 50, 108, 107, 73, 106, 111, 105, 77, 84, 107, 50, 77, 122, 99, 51, 79, 68, 81, 51, 73, 105, 119, 105, 100, 88, 78, 108, 99, 108, 57, 112, 90, 67, 73, 54, 73, 110, 112, 48, 77, 84, 69, 119, 78, 67, 73, 115, 73, 110, 82, 112, 98, 87, 85, 105, 79, 106, 69, 51, 77, 122, 99, 49, 77, 122, 77, 50, 77, 106, 65, 48, 78, 122, 65, 115, 73, 109, 57, 122, 90, 71, 116, 102, 100, 88, 78, 108, 99, 108, 57, 112, 90, 67, 73, 54, 73, 106, 70, 102, 101, 110, 81, 120, 77, 84, 65, 48, 73, 105, 119, 105, 90, 88, 104, 48, 90, 87, 53, 107, 73, 106, 111, 105, 77, 106, 73, 121, 78, 110, 119, 48, 77, 68, 65, 51, 78, 106, 65, 121, 102, 68, 77, 120, 78, 68, 107, 105, 76, 67, 74, 106, 97, 71, 70, 117, 98, 109, 86, 115, 88, 50, 108, 107, 73, 106, 111, 105, 77, 83, 73, 115, 73, 110, 78, 112, 90, 50, 52, 105, 79, 105, 73, 49, 78, 84, 99, 51, 89, 50, 77, 51, 79, 71, 70, 107, 78, 106, 108, 109, 79, 84, 69, 50, 79, 54, 99, 48, 78, 106, 100, 106, 90, 87, 77, 49, 89, 122, 107, 122, 77, 109, 69, 119, 78, 121, 74, 57]

def extract_base64(byte_array):
    # 跳过前三个字节
    data = byte_array[3:]
    # 转换为字符串
    text = ''.join([chr(b) for b in data if 32 <= b <= 126])
    return text

def decode_login_info():
    try:
        # 提取base64字符串
        base64_str = extract_base64(info_array)
        print("\n原始base64字符串:")
        print(base64_str)
        
        # 解码base64
        decoded = base64.b64decode(base64_str)
        
        # 解析JSON
        try:
            # 尝试UTF-8解码
            decoded_str = decoded.decode('utf-8')
        except:
            # 如果UTF-8解码失败，尝试忽略错误
            decoded_str = decoded.decode('utf-8', errors='ignore')
            
        print("\n解码后的JSON字符串:")
        print(decoded_str)
        
        # 解析JSON
        data = json.loads(decoded_str)
        print("\n解析后的数据:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
        
        # 分析数据结构
        print("\n数据结构分析:")
        for key, value in data.items():
            print(f"{key}: {value} ({type(value)})")
        
    except Exception as e:
        print(f"解析错误: {e}")

if __name__ == "__main__":
    decode_login_info()
