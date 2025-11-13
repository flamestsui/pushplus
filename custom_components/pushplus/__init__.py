import logging
import requests
import json
import functools
from typing import Any

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.config_entries import ConfigEntry
from homeassistant.components.notify import (
    BaseNotificationService,
    DOMAIN as NOTIFY_DOMAIN,
)
from homeassistant.helpers.typing import DiscoveryInfoType

# 集成唯一标识（与文件夹名一致）
DOMAIN = "pushplus"
# 配置项键名（与config_flow.py保持一致）
CONF_TOKEN = "token"

_LOGGER = logging.getLogger(__name__)


class PushPlusNotificationService(BaseNotificationService):
    """PushPlus通知服务实现"""

    def __init__(self, token: str):
        self._token = token
        self._url = "https://www.pushplus.plus/send"
        _LOGGER.debug(f"PushPlus服务初始化，token: {token[:4]}****")  # 脱敏显示

    def send_message(self, message: str = "", **kwargs):
        """同步发送通知（内部调用，由异步方法包装）"""
        if not self._token:
            _LOGGER.error("未配置PushPlus Token，请在集成设置中填写")
            return

        # 核心修改：默认标题为“Home Assistant通知”
        title = kwargs.get("title", "Home Assistant通知")
        # 若title为空字符串（用户显式传空），强制使用默认标题
        if not title.strip():
            title = "Home Assistant通知"

        # 构建请求数据
        data = {
            "token": self._token,
            "title": title,  # 使用处理后的标题
            "content": message
        }

        try:
            response = requests.post(
                self._url,
                data=json.dumps(data),
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            response.raise_for_status()  # 捕获HTTP错误（4xx/5xx）

            # 解析响应
            try:
                result = response.json()
            except json.JSONDecodeError:
                _LOGGER.error(f"响应格式错误，原始内容: {response.text[:200]}")
                return

            if result.get("code") != 200:
                _LOGGER.error(f"发送失败: {result.get('msg', '未知错误')}")
            else:
                _LOGGER.debug(f"发送成功，返回: {result}")

        except requests.exceptions.RequestException as e:
            _LOGGER.error(f"网络请求失败: {str(e)}")
        except Exception as e:
            _LOGGER.error(f"发送异常: {str(e)}")


async def async_get_service(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    discovery_info: DiscoveryInfoType | None = None
) -> BaseNotificationService:
    """从配置项获取服务实例（适配现代集成规范）"""
    return PushPlusNotificationService(config_entry.data[CONF_TOKEN])


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """加载配置项并注册通知服务"""
    # 注册配置更新监听（配置变更后自动重载）
    entry.async_on_unload(entry.add_update_listener(async_update_options))

    # 定义服务调用处理函数（异步包装同步发送方法）
    async def async_handle_service(call: ServiceCall) -> None:
        service = PushPlusNotificationService(entry.data[CONF_TOKEN])
        # 用functools绑定参数，通过async_add_executor_job执行同步函数（避免阻塞事件循环）
        send_func = functools.partial(
            service.send_message,
            message=call.data.get("message", ""),
            title=call.data.get("title", "")
        )
        await hass.async_add_executor_job(send_func)  # 替代async_add_job（兼容未来版本）

    # 注册服务到notify域（调用时使用"notify.pushplus"）
    hass.services.async_register(NOTIFY_DOMAIN, DOMAIN, async_handle_service)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """卸载配置项（移除服务）"""
    hass.services.async_remove(NOTIFY_DOMAIN, DOMAIN)
    return True


async def async_update_options(hass: HomeAssistant, entry: ConfigEntry):
    """配置更新后重新加载服务"""
    await hass.config_entries.async_reload(entry.entry_id)