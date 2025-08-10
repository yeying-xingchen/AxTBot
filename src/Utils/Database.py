from tortoise.models import Model
from tortoise import fields
import bcrypt

class LoginForm(Model):
    id = fields.IntField(primary_key=True)
    username = fields.CharField(max_length=50, unique=True)
    email = fields.CharField(max_length=100, unique=True)
    password = fields.CharField(max_length=128)  # 存储哈希后的密码

    class Meta:
        table = "login_forms"

    @classmethod
    async def get_user(cls, username: str, password: str) -> bool:
        """异步验证用户凭据"""
        # 首先尝试通过用户名查找
        user = await cls.get_or_none(username=username)

        # 如果用户名找不到，尝试通过邮箱查找
        if not user:
            user = await cls.get_or_none(email=username)

        # 如果用户不存在或密码不匹配
        if not user:
            return False

        # 验证密码哈希
        if not bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
            return False

        return True

    @classmethod
    async def create_user(cls, username: str, email: str, password: str):
        """异步创建新用户"""
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        return await cls.create(username=username, email=email, password=hashed_password.decode('utf-8'))

    @classmethod
    async def user_exists(cls, username: str, email: str) -> bool:
        """异步检查用户是否存在"""
        return await cls.exists(username=username) or await cls.exists(email=email)
