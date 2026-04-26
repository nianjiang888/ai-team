# 一人公司AI团队 - 快速上手指南

## 30秒上手

### 第1步：安装
```bash
pip install -r requirements.txt
```

### 第2步：配置
```bash
copy config.yaml config.local.yaml
```
用记事本打开 `config.local.yaml`，把 `your-api-key-here` 换成你的真实API Key。

支持的平台：
- **OpenAI**（GPT-4o-mini）：去 https://platform.openai.com 获取
- **DeepSeek**：去 https://platform.deepseek.com 获取
- **智谱**（GLM-4）：去 https://open.bigmodel.cn 获取

### 第3步：启动
```bash
python start.py
```
浏览器会自动打开 http://localhost:5678

## 如何使用

### 派发任务
1. 在看板顶部选择一个AI员工
2. 在输入框里描述你要做什么
3. 点击"派发"按钮
4. 等待产出，在"待审批"中查看结果

### 修改配置
编辑 `config.local.yaml`：

```yaml
# 切换模型
llm:
  provider: "deepseek"        # 换成 deepseek
  api_key: "sk-xxx"           # 填入key
  model: "deepseek-chat"      # 模型名

# 关闭不需要的员工
agents:
  analyst:
    enabled: false             # 不需要数据分析师就关掉
```

## 常见问题

**Q: 启动报错 "No module named flask"**
A: 运行 `pip install -r requirements.txt`

**Q: 启动报错 "找不到配置文件"**
A: 确保项目根目录有 `config.yaml` 文件

**Q: 任务提交后没反应**
A: 检查API Key是否正确配置，查看终端输出的错误信息
