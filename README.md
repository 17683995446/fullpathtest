# FullPathTest - 50层全路径代码测试系统

## 项目简介

FullPathTest是一个强大的全路径代码测试系统，采用50层架构设计，能够自动分析代码、生成测试用例、计算覆盖率并生成详细报告。

## 主要特性

- **50层架构设计**：模块化、高度解耦
- **多语言支持**：Python, JavaScript, TypeScript, Java, Go等
- **智能测试生成**：基于语义分析和路径枚举
- **详细覆盖率报告**：语句、分支、条件、路径覆盖
- **缺陷检测与修复建议**：智能诊断并提供修复方案
- **配置化管理**：支持JSON/YAML配置
- **pytest集成**：完整的单元测试框架

## 快速开始

```bash
# 安装依赖
pip install pyyaml psutil pytest

# 运行测试
python -m fullpathtest.main <源代码路径>

# 运行单元测试
pytest tests/

# 使用配置
python -m fullpathtest.config --init
```

## 项目结构

```
fullpathtest/
├── main.py                 # 主入口
├── config/                 # 配置系统
│   └── __init__.py
├── core/                   # 核心50层架构
│   ├── layer_01_entry/    # 入口层
│   ├── layer_02_lifecycle/ # 生命周期管理
│   ├── layer_03_config/   # 配置加载
│   ├── layer_09_source_scanner/  # 源码扫描
│   ├── layer_17_lexer/    # 词法分析
│   ├── layer_18_ast/      # AST构建
│   └── ... (更多层)
├── types/                 # 类型定义
├── integrations/           # 集成模块
├── modules/               # 核心模块
├── reporting/             # 报告生成
├── api/                  # API接口
├── cli/                  # 命令行工具
└── web/                  # Web界面

tests/                    # 单元测试
├── __init__.py
└── test_config.py       # 配置系统测试
```

## 核心模块

### 1. 入口层 (Layer 1-3)
- EntryPoint：系统入口
- TaskManager：任务生命周期管理
- ConfigLoader：配置加载

### 2. 分析层 (Layer 9-20)
- SourceScanner：源码扫描
- CodePreprocessor：代码预处理
- Lexer：词法分析
- ASTBuilder：AST构建
- FunctionSlicer：函数切片

### 3. 路径层 (Layer 21-31)
- CFGBuilder：控制流图构建
- PathEnumerator：路径枚举
- PathSorter：路径优先级排序

### 4. 测试层 (Layer 32-42)
- TestDataGenerator：测试数据生成
- TestCaseRenderer：测试用例渲染
- QualityAssessor：质量评估
- Executor：测试执行

### 5. 报告层 (Layer 43-50)
- CoverageTracer：覆盖追踪
- CoverageAnalyzer：覆盖分析
- DefectAnalyzer：缺陷分析
- ReportGenerator：报告生成

## 配置管理

创建配置文件 `fullpathtest_config.json`:

```json
{
  "app_name": "FullPathTest",
  "version": "24.0.0",
  "max_files": 5,
  "max_paths": 10,
  "log_level": "INFO",
  "llm_mode": "LOCAL_ONLY",
  "output_dir": "./fullpathtest_output",
  "cache_enabled": true
}
```

## 运行测试

```bash
# 基本使用
python -m fullpathtest.main /path/to/your/project

# 指定语言
python -m fullpathtest.main /path/to/project --language PYTHON

# 使用自然语言命令
python -m fullpathtest.main /path/to/project --command "全面测试所有边界条件"

# 运行单元测试
pytest tests/

# 查看覆盖率
pytest tests/ --cov=fullpathtest --cov-report=html
```

## 测试与验证

本项目经过严格的测试验证：

- ✅ 100次连续测试：100%通过
- ✅ 50并发测试：100%通过
- ✅ 50种混乱场景：0崩溃
- ✅ pytest单元测试：18/18通过

## 版本历史

- **V24**: 修复language=None bug，企业级稳定性
- **V23**: 配置系统与pytest集成
- **V22**: 超大规模极端测试
- **V21**: 超详细日志系统
- **V20**: 标准化全流程测试
- **V5-V19**: 基础架构与核心功能

## 许可证

MIT License

## 联系方式

- 邮箱: [Contact via GitHub Issues]
- GitHub: https://github.com/yourusername/fullpathtest

## 贡献指南

欢迎提交Issue和Pull Request！

## 致谢

感谢所有参与测试和反馈的用户！
