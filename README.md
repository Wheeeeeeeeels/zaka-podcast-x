# zaka-podcast

工业级播客自动生成系统，支持自动生成内容、音频处理和发布到多个平台。

## 核心特性

- 🎙️ AI驱动的内容生成
  - 使用GPT-3.5/4生成高质量播客内容
  - 支持自定义内容风格和主题
  - 智能标题和描述生成

- 🔊 专业级音频处理
  - 高质量文本转语音
  - 背景音乐混音
  - 音频质量优化
  - 支持多种音频格式

- 📱 多平台发布
  - 小宇宙平台集成
  - 可扩展的平台支持
  - 自动发布和更新

- 🛠️ 工业级特性
  - 完整的错误处理和日志系统
  - 配置管理和环境变量支持
  - Docker容器化部署
  - 自动化测试
  - 代码质量保证
  - 性能监控和优化

## 技术栈

- Python 3.11+
- OpenAI GPT API
- gTTS & pydub
- Docker & Docker Compose
- pytest & coverage
- Sphinx文档

## 快速开始

### 使用Docker（推荐）

1. 克隆仓库
```bash
git clone https://github.com/yourusername/zaka-podcast.git
cd zaka-podcast
```

2. 配置环境变量
```bash
cp .env.example .env
# 编辑.env文件，填入必要的API密钥和配置
```

3. 启动服务
```bash
docker-compose up -d
```

### 本地开发

1. 创建虚拟环境
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
.\venv\Scripts\activate  # Windows
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 运行测试
```bash
pytest
```

4. 启动服务
```bash
python main.py
```

## 配置说明

详细配置选项请参考 `.env.example` 文件。主要配置包括：

- OpenAI API配置
- 音频处理配置
- 播客平台API配置
- 日志配置
- 性能配置

## 开发指南

### 代码规范

- 使用black进行代码格式化
- 使用flake8进行代码检查
- 使用mypy进行类型检查
- 使用isort进行导入排序

### 测试

```bash
# 运行所有测试
pytest

# 运行测试并生成覆盖率报告
pytest --cov=.

# 运行特定测试
pytest tests/test_podcast_generator.py
```

### 文档

```bash
# 生成文档
cd docs
make html
```

## 部署

### 生产环境部署

1. 确保所有环境变量正确配置
2. 使用Docker Compose部署
3. 配置适当的资源限制
4. 设置监控和告警

### 监控

- 日志文件位于 `logs/app.log`
- 使用日志级别控制输出详细程度
- 支持日志轮转和归档

## 贡献指南

1. Fork项目
2. 创建特性分支
3. 提交更改
4. 推送到分支
5. 创建Pull Request

## 许可证

MIT License

## 支持

如有问题，请提交Issue或联系维护团队。