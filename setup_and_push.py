#!/usr/bin/env python3
import os
"""
完整的GitHub仓库创建和推送脚本
"""

import requests
import subprocess
import sys
import json

def main():
    token = os.environ.get("GITHUB_TOKEN", "")
    repo_name = "fullpathtest"
    
    # 设置API头
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    # 1. 获取用户名
    print("1. 获取GitHub用户信息...")
    user_url = "https://api.github.com/user"
    user_response = requests.get(user_url, headers=headers)
    
    if user_response.status_code != 200:
        print(f"❌ 身份验证失败: {user_response.status_code}")
        print(user_response.text)
        return False
    
    username = user_response.json()["login"]
    print(f"✅ 用户: {username}")
    
    # 2. 创建仓库
    print("\n2. 创建/检查仓库...")
    repo_url = f"https://api.github.com/user/repos"
    repo_data = {
        "name": repo_name,
        "description": "FullPathTest v4.0 - A production-grade code quality testing platform",
        "private": True,
        "auto_init": False
    }
    
    response = requests.post(repo_url, headers=headers, json=repo_data)
    
    if response.status_code == 201:
        print("✅ 仓库创建成功！")
    elif response.status_code == 422:
        print("ℹ️  仓库已存在")
    else:
        print(f"⚠️  响应: {response.status_code} - {response.text}")
    
    # 3. 设置Git remote
    print("\n3. 设置Git remote...")
    git_url = f"https://{username}:{token}@github.com/{username}/{repo_name}.git"
    
    subprocess.run(["git", "remote", "remove", "origin"], capture_output=True)
    result = subprocess.run(["git", "remote", "add", "origin", git_url])
    
    if result.returncode == 0:
        print("✅ Remote设置成功")
    else:
        print(f"⚠️  Remote可能已存在")
    
    # 4. 重命名为main分支
    print("\n4. 重命名分支为main...")
    subprocess.run(["git", "branch", "-M", "main"], check=True)
    print("✅ 分支已重命名为main")
    
    # 5. 推送代码
    print("\n5. 推送代码到GitHub...")
    push_result = subprocess.run(["git", "push", "-u", "origin", "main"])
    
    if push_result.returncode == 0:
        print("\n" + "="*60)
        print("✅ 所有操作成功完成！")
        print("="*60)
        print(f"\n仓库地址: https://github.com/{username}/{repo_name}")
        print(f"Git URL: {git_url}")
        print("\n🎉 项目已完整提交到GitHub！")
        return True
    else:
        print(f"\n❌ 推送失败")
        return False

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ 异常: {e}")
        import traceback
        traceback.print_exc()
