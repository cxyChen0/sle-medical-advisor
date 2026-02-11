# 贡献指南

感谢您对 SLE 医疗顾问系统项目的关注！我们欢迎任何形式的贡献。

## 如何贡献

### 报告问题

如果您发现了 bug 或有新的功能建议，请：

1. 检查 [Issues](https://github.com/cxyChen0/sle-medical-advisor/issues) 确认问题是否已被报告
2. 如果没有，创建一个新的 Issue，详细描述：
   - 问题的标题
   - 问题的详细描述
   - 复现步骤（如果是 bug）
   - 预期行为
   - 实际行为
   - 环境信息（操作系统、Python/Node 版本等）

### 提交代码

如果您想修复 bug 或添加新功能：

1. Fork 本仓库
2. 创建您的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交您的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启一个 Pull Request

### 代码规范

#### 前端

- 使用 ESLint 进行代码检查：`npm run lint`
- 遵循 React 最佳实践
- 使用有意义的变量和函数名
- 添加必要的注释

#### 后端

- 遵循 PEP 8 代码风格
- 使用有意义的变量和函数名
- 添加必要的文档字符串
- 编写测试用例

### 提交信息

请使用清晰的提交信息，例如：

- `fix: 修复检查单解析的错误`
- `feat: 添加数据可视化功能`
- `docs: 更新 README`
- `test: 添加 API 测试用例`

### Pull Request 流程

1. 确保您的代码通过所有测试
2. 更新相关文档
3. 确保 PR 描述清晰，说明您做了什么以及为什么
4. 等待代码审查

## 开发环境设置

### 前端

```bash
cd sle-frontend
npm install
npm run dev
```

### 后端

```bash
cd sle-backend
pip install -r requirements.txt
python main.py
```

## 测试

在提交 PR 之前，请确保：

1. 前端代码通过 lint 检查：`npm run lint`
2. 后端测试通过：
   ```bash
   python test_api.py
   python test_report_parser.py
   python test_normalization.py
   ```

## 行为准则

- 尊重所有贡献者
- 接受建设性的批评
- 关注对社区最有利的事情
- 对其他社区成员表示同理心

## 获取帮助

如果您有任何问题，请通过以下方式联系我们：

- 提交 [Issue](https://github.com/cxyChen0/sle-medical-advisor/issues)
- 发送邮件至：3100321917@qq.com

## 许可证

通过贡献代码，您同意您的贡献将根据 MIT License 进行许可。
