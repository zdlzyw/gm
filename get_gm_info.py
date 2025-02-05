import requests
import json
import os
import sys

print(f"Python版本: {sys.version}")
print(f"当前工作目录: {os.getcwd()}")

class GMInfoClient:
    def __init__(self):
        self.base_url = "https://api-agame-cn-qa-outernal.youzu.com"
        self.op_id = self.get_op_id()
        self.op_game_id = self.get_op_game_id()
        print(f"初始化GMInfoClient: base_url={self.base_url}")
    
    def get_op_id(self):
        # TODO: 从配置文件或环境变量获取
        return "2106"  # 示例值，需要替换为实际的op_id
    
    def get_op_game_id(self):
        # TODO: 从配置文件或环境变量获取
        return "3244"  # 示例值，需要替换为实际的op_game_id
    
    def push_gm_info(self):
        """推送GM后台信息"""
        url = f"{self.base_url}/opinfo"
        params = {
            "opId": self.op_id,
            "opGameId": self.op_game_id
        }
        
        print(f"准备发送POST请求: {url}")
        print(f"参数: {params}")
        
        try:
            # 使用POST方法
            response = requests.post(url, json=params)
            print(f"请求已发送，状态码: {response.status_code}")
            response.raise_for_status()  # 检查响应状态
            
            # 打印响应内容
            print(f"Status Code: {response.status_code}")
            print(f"Response Headers: {json.dumps(dict(response.headers), indent=2)}")
            print(f"Response Body: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"请求失败: {e}")
            return None

def main():
    print("开始执行main函数")
    client = GMInfoClient()
    result = client.push_gm_info()
    
    if result:
        print("\nGM信息推送成功!")
    else:
        print("\nGM信息推送失败!")
    print("程序执行完毕")

if __name__ == "__main__":
    main()
