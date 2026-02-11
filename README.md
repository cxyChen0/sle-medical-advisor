# SLE 医疗顾问系统

一个基于人工智能的系统性红斑狼疮（SLE）医疗咨询助手，为患者提供专业的检查单解读、疾病咨询和生活建议。

## 功能特性

### 检查单解读
- 支持病理报告和化验报告的智能解析
- 利用 OCR 技术识别中文医疗文档
- 自动提取关键指标并进行标准化处理
- 提供详细的指标解读和健康评估

### 疾病咨询
- 交互式症状询问系统
- 基于患者历史记录的个性化建议
- 智能药品推荐
- 就医提醒和预警

### 数据可视化
- 健康指标趋势图表
- 检查结果对比分析
- 直观的数据展示界面

## 技术栈

### 前端
- **React 18.2.0** - 现代化的前端框架
- **Vite 5.0.8** - 快速的构建工具
- **React Router DOM** - 路由管理
- **Axios** - HTTP 客户端
- **Chart.js & react-chartjs-2** - 数据可视化
- **Lucide React** - 图标库

### 后端
- **Python** - 后端开发语言
- **Flask** - Web 框架
- **cnocr** - 中文 OCR 识别
- **AI 语义分析** - 智能医疗咨询

## 项目结构

```
sle-medical-advisor/
├── sle-frontend/          # 前端项目
│   ├── src/              # 源代码
│   ├── index.html        # 入口 HTML
│   ├── package.json      # 依赖配置
│   └── vite.config.js    # Vite 配置
├── sle-backend/          # 后端项目
│   ├── app/              # 应用模块
│   ├── cnocr_models/     # OCR 模型
│   ├── scripts/          # 脚本工具
│   ├── test_results/     # 测试结果
│   ├── app.py            # Flask 应用
│   ├── main.py           # 主程序
│   └── requirements.txt  # Python 依赖
└── README.md             # 项目说明
```

## 安装说明

### 前端安装

```bash
cd sle-frontend
npm install
```

### 后端安装

```bash
cd sle-backend
pip install -r requirements.txt
```

## 使用方法

### 启动前端

```bash
cd sle-frontend
npm run dev
```

前端服务将在 `http://localhost:5173` 启动

### 启动后端

```bash
cd sle-backend
python main.py
```

后端 API 服务将在 `http://localhost:5000` 启动

## 测试

### 后端测试

```bash
cd sle-backend

# API 测试
python test_api.py

# 报告解析测试
python test_report_parser.py

# 数据标准化测试
python test_normalization.py

# AI 语义测试
python test_ai_semantic.py

# AI 验证测试
python test_ai_validation.py
```

## 开发

### 前端开发

```bash
cd sle-frontend
npm run dev      # 启动开发服务器
npm run build    # 构建生产版本
npm run lint     # 代码检查
```

### 后端开发

```bash
cd sle-backend
python main.py    # 启动后端服务
```

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License

## 联系方式

如有问题或建议，请通过 GitHub Issues 联系我们。

## 免责声明

本系统仅用于辅助医疗咨询，不能替代专业医生的诊断和治疗建议。如有健康问题，请及时就医。
