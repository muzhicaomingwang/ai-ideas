#!/usr/bin/env python3
"""
测试Gmail MCP集成方案

验证不同的Gmail MCP调用方式
"""

import json
import subprocess
import sys


def test_json_rpc_call():
    """测试通过JSON-RPC调用Gmail MCP"""
    print("=" * 60)
    print("测试方案: JSON-RPC over stdio")
    print("=" * 60)

    # MCP服务器通过stdin接收JSON-RPC请求
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/list",
        "params": {}
    }

    try:
        # 启动MCP服务器
        process = subprocess.Popen(
            ["npx", "@gongrzhe/server-gmail-autoauth-mcp@1.1.11"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # 发送请求
        request_json = json.dumps(request) + "\n"
        stdout, stderr = process.communicate(input=request_json, timeout=10)

        print(f"✅ stdout: {stdout[:500]}")

        if stderr:
            print(f"⚠️ stderr: {stderr[:500]}")

        # 尝试解析响应
        for line in stdout.split('\n'):
            if line.strip():
                try:
                    response = json.loads(line)
                    if "result" in response:
                        tools = response["result"].get("tools", [])
                        print(f"\n✅ 找到 {len(tools)} 个工具:")
                        for tool in tools[:5]:
                            print(f"  - {tool.get('name')}")
                        return True
                except json.JSONDecodeError:
                    pass

    except subprocess.TimeoutExpired:
        print("❌ 超时")
        process.kill()
    except Exception as e:
        print(f"❌ 错误: {e}")

    return False


def test_direct_python_import():
    """测试直接导入Python库"""
    print("\n" + "=" * 60)
    print("测试方案: 直接使用Google API Python库")
    print("=" * 60)

    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
        from pathlib import Path

        # 检查Gmail MCP的credentials
        creds_path = Path.home() / ".gmail-mcp" / "credentials.json"

        if not creds_path.exists():
            print("❌ Gmail MCP credentials不存在")
            return False

        print(f"✅ 找到credentials: {creds_path}")

        # 尝试加载credentials
        with open(creds_path, "r") as f:
            creds_data = json.load(f)

        print(f"✅ Credentials包含字段: {list(creds_data.keys())}")

        # 构建Gmail服务（这需要正确的credentials格式）
        # 注意: Gmail MCP的credentials可能与标准OAuth格式不同

        return True

    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        print("提示: pip install google-auth google-auth-oauthlib google-api-python-client")
        return False
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False


if __name__ == "__main__":
    print("GMailHelper - Gmail MCP集成测试\n")

    # 测试方案1: JSON-RPC
    success1 = test_json_rpc_call()

    # 测试方案2: 直接使用Python库
    success2 = test_direct_python_import()

    print("\n" + "=" * 60)
    print("测试总结:")
    print("=" * 60)
    print(f"JSON-RPC方案: {'✅ 可用' if success1 else '❌ 不可用'}")
    print(f"Python库方案: {'✅ 可用' if success2 else '❌ 不可用'}")

    print("\n推荐方案: JSON-RPC over stdio (MCP标准)")
