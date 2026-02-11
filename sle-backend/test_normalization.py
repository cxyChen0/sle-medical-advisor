import requests
import json

# 测试表单归一化接口 - 非医学术语
print("测试表单归一化接口 - 非医学术语...")
url = "http://127.0.0.1:8000/normalize"
headers = {"Content-Type": "application/json"}
data = {
    "terms": ["名称", "手机号", "联系电话", "手机", "客户姓名", "姓名", "收货人姓名"]
}

response = requests.post(url, headers=headers, data=json.dumps(data))
print(f"状态码: {response.status_code}")
if response.status_code == 200:
    print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
else:
    print(f"错误: {response.text}")
print()

# 测试表单归一化接口 - 医学术语
print("测试表单归一化接口 - 医学术语...")
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