from enum import Enum
from typing import List, Dict
from datetime import datetime
import json
import os
import logging

class UserRole(Enum):
    """用户角色"""
    ADMIN = "admin"  # 管理员
    EDITOR = "editor"  # 编辑
    USER = "user"  # 普通用户
    GUEST = "guest"  # 访客

class Permission(Enum):
    """权限类型"""
    READ = "read"  # 读取
    WRITE = "write"  # 写入
    DELETE = "delete"  # 删除
    MANAGE = "manage"  # 管理
    UPLOAD = "upload"  # 上传
    DOWNLOAD = "download"  # 下载

class PermissionManager:
    """权限管理器"""
    def __init__(self, config_path: str = "config/permissions.json"):
        self.config_path = config_path
        self.logger = logging.getLogger(__name__)
        self.role_permissions: Dict[UserRole, List[Permission]] = {}
        self.user_roles: Dict[str, UserRole] = {}
        self.operation_logs: List[Dict] = []
        
        self._load_config()
    
    def _load_config(self):
        """加载权限配置"""
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                self.role_permissions = {
                    UserRole(role): [Permission(p) for p in permissions]
                    for role, permissions in config.get('role_permissions', {}).items()
                }
                self.user_roles = {
                    user: UserRole(role)
                    for user, role in config.get('user_roles', {}).items()
                }
        else:
            self._initialize_default_permissions()
    
    def _initialize_default_permissions(self):
        """初始化默认权限"""
        self.role_permissions = {
            UserRole.ADMIN: list(Permission),
            UserRole.EDITOR: [
                Permission.READ,
                Permission.WRITE,
                Permission.UPLOAD,
                Permission.DOWNLOAD
            ],
            UserRole.USER: [
                Permission.READ,
                Permission.DOWNLOAD
            ],
            UserRole.GUEST: [
                Permission.READ
            ]
        }
        self._save_config()
    
    def _save_config(self):
        """保存权限配置"""
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump({
                'role_permissions': {
                    role.value: [p.value for p in permissions]
                    for role, permissions in self.role_permissions.items()
                },
                'user_roles': {
                    user: role.value
                    for user, role in self.user_roles.items()
                }
            }, f, ensure_ascii=False, indent=2)
    
    def check_permission(self, user_id: str, permission: Permission) -> bool:
        """检查用户权限"""
        role = self.user_roles.get(user_id, UserRole.GUEST)
        return permission in self.role_permissions.get(role, [])
    
    def assign_role(self, user_id: str, role: UserRole):
        """分配用户角色"""
        self.user_roles[user_id] = role
        self._save_config()
        self._log_operation(user_id, f"分配角色: {role.value}")
    
    def add_permission(self, role: UserRole, permission: Permission):
        """添加角色权限"""
        if role not in self.role_permissions:
            self.role_permissions[role] = []
        if permission not in self.role_permissions[role]:
            self.role_permissions[role].append(permission)
            self._save_config()
            self._log_operation("system", f"添加权限: {permission.value} 到角色: {role.value}")
    
    def remove_permission(self, role: UserRole, permission: Permission):
        """移除角色权限"""
        if role in self.role_permissions and permission in self.role_permissions[role]:
            self.role_permissions[role].remove(permission)
            self._save_config()
            self._log_operation("system", f"移除权限: {permission.value} 从角色: {role.value}")
    
    def _log_operation(self, user_id: str, operation: str):
        """记录操作日志"""
        self.operation_logs.append({
            "user_id": user_id,
            "operation": operation,
            "timestamp": datetime.now().isoformat()
        })
    
    def get_operation_logs(self, user_id: str = None) -> List[Dict]:
        """获取操作日志"""
        if user_id:
            return [log for log in self.operation_logs if log["user_id"] == user_id]
        return self.operation_logs