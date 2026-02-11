import requests
import json

# 测试健康检查接口
print("测试健康检查接口...")
response = requests.get("http://127.0.0.1:8000/health")
print(f"状态码: {response.status_code}")
print(f"响应: {response.json()}")
print()

# 测试表单名称归一化接口
print("测试表单名称归一化接口...")
url = "http://127.0.0.1:8000/normalize"
headers = {"Content-Type": "application/json"}
data = {
    "terms": ["ANA", "白细胞", "尿蛋白", "C3补体", "抗dsDNA抗体"]
}

response = requests.post(url, headers=headers, data=json.dumps(data))
print(f"状态码: {response.status_code}")
if response.status_code == 200:
    print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
else:
    print(f"错误: {response.text}")
print()

# 测试获取患者病史接口
print("测试获取患者病史接口...")
response = requests.get("http://127.0.0.1:8000/medical-history/1")
print(f"状态码: {response.status_code}")
if response.status_code == 200:
    print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
else:
    print(f"错误: {response.text}")
