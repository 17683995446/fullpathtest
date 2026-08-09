#!/usr/bin/env python3
import os
"""
GitHub仓库创建脚本
"""

import requests
import json
import sys

def create_github_repo(token, repo_name="fullpathtest", private=True):
    """
    创建GitHub仓库
    
    Args:
        token: GitHub Personal Access Token
        repo_name: 仓库名
        private: 是否私有
    
    Returns:
        仓库URL或None
    """
    url = "https://api.github.com/user/repos"
    
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    data = {
        "name": repo_name,
        "description": "FullPathTest v4.0 - A production-grade code quality testing platform with AI, plugins, enterprise features, and more",
        "private": private,
        "auto_init": False,
        "has_issues": True,
        "has_projects": True,
        "has_wiki": True
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 201:
            repo_info = response.json()
            print(f"✅ 仓库创建成功！")
            print(f"   仓库URL: {repo_info['html_url']}")
            print(f"   Git URL: {repo_info['clone_url']}")
            return repo_info['clone_url']
        
        elif response.status_code == 422:
            print(f"⚠️ 仓库可能已存在，尝试获取...")
            
            # 尝试获取仓库
            get_url = f"https://api.github.com/repos/USERNAME/{repo_name}"
            response_get = requests.get(get_url, headers=headers)
            
            if response_get.status_code == 200:
                repo_info = response_get.json()
                print(f"✅ 仓库已存在")
                print(f"   仓库URL: {repo_info['html_url']}")
                print(f"   Git URL: {repo_info['clone_url']}")
                return repo_info['clone_url']
            else:
                print(f"❌ 创建仓库失败: {response.status_code}")
                print(f"   响应: {response.text}")
                return None
        else:
            print(f"❌ 创建仓库失败: {response.status_code}")
            print(f"   响应: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ 异常: {e}")
        import traceback
        traceback.print_exc()
        return None


def get_username(token):
    """获取当前用户用户名"""
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    try:
        response = requests.get("https://api.github.com/user", headers=headers)
        if response.status_code == 200:
            user_info = response.json()
            return user_info['login']
    except:
        pass
    return None


if __name__ == "__main__":
    # 从环境或参数获取token
    token = os.environ.get("GITHUB_TOKEN", "")
    
    username = get_username(token)
    if username:
        print(f"✅ 身份验证成功！用户: {username}")
    else:
        print(f"⚠️ 无法获取用户名")
    
    # 创建仓库
    print(f"\n创建仓库...")
    repo_url = create_github_repo(token, repo_name="fullpathtest", private=True)
    
    if repo_url:
        print(f"\n✅ 准备推送...")
        print(f"使用命令:")
        print(f"  git remote add origin {repo_url}")
        print(f"  git branch -M main")
        print(f"  git push -u origin main")
