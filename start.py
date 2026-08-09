#!/usr/bin/env python3
"""
FullPathTest V4.0 - 完整系统启动脚本

集成启动：
1. CLI界面
2. Web可视化界面
3. 完整系统

使用方法:
  python start.py          # 启动Web界面
  python start.py --cli    # 启动CLI
  python start.py --test   # 运行测试
  python start.py --report # 生成报告
"""

import sys
import argparse
import subprocess
from pathlib import Path


def start_web_server(host: str = "0.0.0.0", port: int = 8000):
    """启动Web服务器"""
    print("🌐 启动 FullPathTest Web 界面...")
    print(f"📊 访问地址: http://{host}:{port}")
    print("🔧 API地址: http://{host}:{port}/api/health")
    print("⏹️ 按 Ctrl+C 停止")
    print()
    
    try:
        from fullpathtest.web.app import start_web_server
        start_web_server(host=host, port=port)
    except KeyboardInterrupt:
        print("\n✅ Web服务器已停止")
    except Exception as e:
        print(f"❌ Web服务器启动失败: {e}")


def run_cli():
    """运行CLI界面"""
    print("🚀 启动 FullPathTest CLI...")
    print()
    
    try:
        from fullpathtest.cli.main import cli
        # 处理CLI参数并运行
        cli_args = sys.argv[2:] if len(sys.argv) > 2 else ['--help']
        sys.argv = ['fullpathtest'] + cli_args
        cli()
    except Exception as e:
        print(f"❌ CLI启动失败: {e}")


def run_tests():
    """运行测试"""
    print("🧪 运行完整测试套件...")
    print()
    
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short"],
            cwd="/workspace"
        )
        if result.returncode == 0:
            print("\n✅ 所有测试通过！")
        else:
            print(f"\n⚠️ 测试完成，部分失败 (退出码: {result.returncode})")
    except Exception as e:
        print(f"❌ 测试运行失败: {e}")


def generate_report():
    """生成综合报告"""
    print("📊 生成综合评分报告...")
    print()
    
    try:
        from generate_score_report import generate_report
        report = generate_report()
        print(report)
        print("✅ 报告已生成并保存到 COMPREHENSIVE_REPORT.md")
    except Exception as e:
        print(f"❌ 报告生成失败: {e}")


def show_welcome():
    """显示欢迎信息"""
    banner = """
╔═══════════════════════════════════════════════════════════════════════════╗
║                                                                             ║
║    ███████╗██╗   ██╗██╗     ██╗         ██████╗  █████╗ ████████╗██╗  ██╗    ║
║    ██╔════╝██║   ██║██║     ██║         ██╔══██╗██╔══██╗╚══██╔══╝██║  ██║    ║
║    █████╗  ██║   ██║██║     ██║         ██████╔╝███████║   ██║   ███████║    ║
║    ██╔══╝  ██║   ██║██║     ██║         ██╔═══╝ ██╔══██║   ██║   ██╔══██║    ║
║    ██║     ╚██████╔╝███████╗███████╗    ██║     ██║  ██║   ██║   ██║  ██║    ║
║    ╚═╝      ╚═════╝ ╚══════╝╚══════╝    ╚═╝     ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝    ║
║                                                                             ║
║               极致轻量化全路径代码测试系统 - V4.0                         ║
║                                                                             ║
╚═══════════════════════════════════════════════════════════════════════════╝
    """
    print(banner)
    print("📋 使用说明:")
    print("  python start.py          启动Web可视化界面 (默认)")
    print("  python start.py --cli    启动CLI命令行界面")
    print("  python start.py --test   运行完整测试套件")
    print("  python start.py --report 生成综合评分报告")
    print("  python start.py --help   显示帮助信息")
    print()
    print("⭐ 项目文件:")
    print("  - README.md              项目主文档")
    print("  - SPEC.md                系统规格说明")
    print("  - QUICKSTART.md          快速入门指南")
    print("  - COMPREHENSIVE_REPORT.md 多维度评分报告")
    print()


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="FullPathTest V4.0 - 极致轻量化全路径代码测试系统"
    )
    
    parser.add_argument(
        "--cli",
        action="store_true",
        help="启动命令行界面"
    )
    
    parser.add_argument(
        "--test",
        action="store_true",
        help="运行完整测试套件"
    )
    
    parser.add_argument(
        "--report",
        action="store_true",
        help="生成综合评分报告"
    )
    
    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="Web服务器主机地址 (默认: 0.0.0.0)"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Web服务器端口 (默认: 8000)"
    )
    
    args = parser.parse_args()
    
    if args.cli:
        run_cli()
    elif args.test:
        run_tests()
    elif args.report:
        generate_report()
    else:
        show_welcome()
        start_web_server(host=args.host, port=args.port)


if __name__ == "__main__":
    main()
