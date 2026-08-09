"""
FullPathTest v4.0 - 企业级功能基础
包含多租户、权限管理、审计日志等企业级特性
"""

import os
import json
import hashlib
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Set
from enum import Enum
from datetime import datetime
from pathlib import Path

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("enterprise")


class RoleType(Enum):
    """角色类型"""
    ADMIN = "admin"
    MANAGER = "manager"
    DEVELOPER = "developer"
    VIEWER = "viewer"
    GUEST = "guest"


class Permission(Enum):
    """权限"""
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    ADMIN = "admin"
    EXECUTE = "execute"
    CONFIG = "config"


@dataclass
class User:
    """用户"""
    user_id: str
    username: str
    email: str
    role: RoleType
    tenant_id: str
    permissions: Set[Permission] = field(default_factory=set)
    created_at: datetime = field(default_factory=datetime.now)
    is_active: bool = True


@dataclass
class Tenant:
    """租户"""
    tenant_id: str
    name: str
    description: str = ""
    config: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    is_active: bool = True


@dataclass
class AuditLogEntry:
    """审计日志条目"""
    log_id: str
    timestamp: datetime
    tenant_id: str
    user_id: str
    action: str
    resource: str
    result: str
    details: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'log_id': self.log_id,
            'timestamp': self.timestamp.isoformat(),
            'tenant_id': self.tenant_id,
            'user_id': self.user_id,
            'action': self.action,
            'resource': self.resource,
            'result': self.result,
            'details': self.details
        }


class TenantManager:
    """租户管理器"""
    
    def __init__(self, data_dir: str = "data/tenants"):
        self.data_dir = Path(data_dir)
        self.tenants: Dict[str, Tenant] = {}
        self._initialize()
    
    def _initialize(self):
        """初始化"""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建默认租户
        self.create_tenant(
            tenant_id="default",
            name="Default Tenant",
            description="Default system tenant"
        )
    
    def create_tenant(self, tenant_id: str, name: str, description: str = "", config: Dict[str, Any] = None) -> bool:
        """创建租户"""
        if tenant_id in self.tenants:
            logger.warning(f"Tenant {tenant_id} already exists")
            return False
        
        tenant = Tenant(
            tenant_id=tenant_id,
            name=name,
            description=description,
            config=config or {}
        )
        
        self.tenants[tenant_id] = tenant
        logger.info(f"Created tenant: {tenant_id}")
        return True
    
    def get_tenant(self, tenant_id: str) -> Optional[Tenant]:
        """获取租户"""
        return self.tenants.get(tenant_id)
    
    def list_tenants(self) -> List[Tenant]:
        """列出所有租户"""
        return [t for t in self.tenants.values() if t.is_active]
    
    def update_tenant(self, tenant_id: str, name: str = None, description: str = None, config: Dict[str, Any] = None) -> bool:
        """更新租户"""
        tenant = self.tenants.get(tenant_id)
        if not tenant:
            return False
        
        if name:
            tenant.name = name
        if description:
            tenant.description = description
        if config:
            tenant.config.update(config)
        
        logger.info(f"Updated tenant: {tenant_id}")
        return True
    
    def delete_tenant(self, tenant_id: str) -> bool:
        """删除租户（软删除）"""
        tenant = self.tenants.get(tenant_id)
        if not tenant:
            return False
        
        tenant.is_active = False
        logger.info(f"Deactivated tenant: {tenant_id}")
        return True


class PermissionManager:
    """权限管理器"""
    
    def __init__(self):
        self.role_permissions: Dict[RoleType, Set[Permission]] = self._init_role_permissions()
    
    def _init_role_permissions(self) -> Dict[RoleType, Set[Permission]]:
        """初始化角色权限映射"""
        return {
            RoleType.ADMIN: {
                Permission.READ,
                Permission.WRITE,
                Permission.DELETE,
                Permission.ADMIN,
                Permission.EXECUTE,
                Permission.CONFIG
            },
            RoleType.MANAGER: {
                Permission.READ,
                Permission.WRITE,
                Permission.EXECUTE,
                Permission.CONFIG
            },
            RoleType.DEVELOPER: {
                Permission.READ,
                Permission.WRITE,
                Permission.EXECUTE
            },
            RoleType.VIEWER: {
                Permission.READ
            },
            RoleType.GUEST: set()
        }
    
    def get_permissions_for_role(self, role: RoleType) -> Set[Permission]:
        """获取角色权限"""
        return self.role_permissions.get(role, set())
    
    def has_permission(self, user: User, permission: Permission) -> bool:
        """检查用户是否有特定权限"""
        if permission in user.permissions:
            return True
        
        role_perms = self.get_permissions_for_role(user.role)
        return permission in role_perms
    
    def grant_permission(self, user: User, permission: Permission) -> bool:
        """授予权限"""
        if permission not in user.permissions:
            user.permissions.add(permission)
            logger.info(f"Granted {permission} to {user.user_id}")
            return True
        return False
    
    def revoke_permission(self, user: User, permission: Permission) -> bool:
        """撤销权限"""
        if permission in user.permissions:
            user.permissions.remove(permission)
            logger.info(f"Revoked {permission} from {user.user_id}")
            return True
        return False


class AuditLogger:
    """审计日志记录器"""
    
    def __init__(self, log_dir: str = "data/audit"):
        self.log_dir = Path(log_dir)
        self.logs: Dict[str, List[AuditLogEntry]] = {}  # tenant_id -> logs
        self._initialize()
    
    def _initialize(self):
        """初始化"""
        self.log_dir.mkdir(parents=True, exist_ok=True)
    
    def _generate_log_id(self) -> str:
        """生成日志ID"""
        return hashlib.md5(f"{datetime.now().isoformat()}{os.urandom(16)}".encode()).hexdigest()[:16]
    
    def log(
        self,
        tenant_id: str,
        user_id: str,
        action: str,
        resource: str,
        result: str,
        details: Dict[str, Any] = None
    ):
        """记录审计日志"""
        log_entry = AuditLogEntry(
            log_id=self._generate_log_id(),
            timestamp=datetime.now(),
            tenant_id=tenant_id,
            user_id=user_id,
            action=action,
            resource=resource,
            result=result,
            details=details or {}
        )
        
        if tenant_id not in self.logs:
            self.logs[tenant_id] = []
        
        self.logs[tenant_id].append(log_entry)
        logger.debug(f"Audit log: {user_id} {action} {resource} - {result}")
        
        return log_entry
    
    def get_logs(self, tenant_id: str = None, user_id: str = None, limit: int = 100) -> List[AuditLogEntry]:
        """获取审计日志"""
        all_logs = []
        
        if tenant_id:
            all_logs = self.logs.get(tenant_id, []).copy()
        else:
            for tenant_logs in self.logs.values():
                all_logs.extend(tenant_logs)
        
        if user_id:
            all_logs = [l for l in all_logs if l.user_id == user_id]
        
        # 按时间倒序
        all_logs.sort(key=lambda x: x.timestamp, reverse=True)
        return all_logs[:limit]
    
    def export_logs(self, tenant_id: str = None, output_path: str = "audit_export.json"):
        """导出审计日志"""
        logs = self.get_logs(tenant_id)
        data = [log.to_dict() for log in logs]
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Exported {len(logs)} logs to {output_path}")


class UserManager:
    """用户管理器"""
    
    def __init__(self):
        self.users: Dict[str, User] = {}
    
    def create_user(
        self,
        user_id: str,
        username: str,
        email: str,
        role: RoleType,
        tenant_id: str
    ) -> User:
        """创建用户"""
        if user_id in self.users:
            logger.warning(f"User {user_id} already exists")
            return self.users[user_id]
        
        user = User(
            user_id=user_id,
            username=username,
            email=email,
            role=role,
            tenant_id=tenant_id
        )
        
        self.users[user_id] = user
        logger.info(f"Created user: {user_id}")
        return user
    
    def get_user(self, user_id: str) -> Optional[User]:
        """获取用户"""
        return self.users.get(user_id)
    
    def list_users(self, tenant_id: str = None) -> List[User]:
        """列出用户"""
        users = [u for u in self.users.values() if u.is_active]
        if tenant_id:
            users = [u for u in users if u.tenant_id == tenant_id]
        return users


class EnterpriseSystem:
    """企业级系统"""
    
    def __init__(self, data_dir: str = "data"):
        self.tenant_manager = TenantManager(str(Path(data_dir) / "tenants"))
        self.permission_manager = PermissionManager()
        self.audit_logger = AuditLogger(str(Path(data_dir) / "audit"))
        self.user_manager = UserManager()
    
    def get_status(self) -> Dict[str, Any]:
        """获取系统状态"""
        return {
            'tenants': len(self.tenant_manager.list_tenants()),
            'users': len(self.user_manager.list_users()),
            'audit_logs': sum(len(logs) for logs in self.audit_logger.logs.values())
        }


def create_enterprise_system(data_dir: str = "data") -> EnterpriseSystem:
    """创建企业级系统"""
    return EnterpriseSystem(data_dir)


def demo_enterprise_system():
    """企业级系统演示"""
    print("\n" + "="*60)
    print("FullPathTest v4.0 - 企业级功能演示")
    print("="*60 + "\n")
    
    # 创建系统
    system = create_enterprise_system()
    
    # 创建租户
    print("🏢 创建租户...")
    system.tenant_manager.create_tenant("acme", "ACME Corp", "A sample company")
    
    # 创建用户
    print("👤 创建用户...")
    admin_user = system.user_manager.create_user(
        user_id="admin",
        username="admin",
        email="admin@acme.com",
        role=RoleType.ADMIN,
        tenant_id="acme"
    )
    
    dev_user = system.user_manager.create_user(
        user_id="dev1",
        username="dev1",
        email="dev1@acme.com",
        role=RoleType.DEVELOPER,
        tenant_id="acme"
    )
    
    # 记录审计日志
    print("📝 记录审计日志...")
    system.audit_logger.log(
        tenant_id="acme",
        user_id="admin",
        action="create_user",
        resource="dev1",
        result="success"
    )
    
    system.audit_logger.log(
        tenant_id="acme",
        user_id="dev1",
        action="analyze_code",
        resource="project1",
        result="success",
        details={'files': 100, 'issues': 5}
    )
    
    # 检查权限
    print("🔐 检查权限...")
    has_admin_perm = system.permission_manager.has_permission(admin_user, Permission.ADMIN)
    has_delete_perm = system.permission_manager.has_permission(dev_user, Permission.DELETE)
    
    print(f"  - Admin has ADMIN: {has_admin_perm}")
    print(f"  - Dev has DELETE: {has_delete_perm}")
    
    # 获取状态
    print("\n📊 系统状态:")
    status = system.get_status()
    print(f"  - Tenants: {status['tenants']}")
    print(f"  - Users: {status['users']}")
    print(f"  - Audit logs: {status['audit_logs']}")
    
    # 显示审计日志
    print("\n📋 最近审计日志:")
    logs = system.audit_logger.get_logs(tenant_id="acme", limit=5)
    for i, log in enumerate(logs, 1):
        print(f"  {i}. [{log.timestamp.strftime('%H:%M:%S')}] {log.user_id} {log.action} {log.resource}")
    
    print("\n" + "="*60)
    print("演示完成！")
    print("="*60 + "\n")


if __name__ == "__main__":
    demo_enterprise_system()
