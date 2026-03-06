import logging
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult

from . import DOMAIN

_LOGGER = logging.getLogger(__name__)

# 配置项键名（与__init__.py保持一致）
CONF_TOKEN = "token"
CONF_CHANNEL = "channel"


@config_entries.HANDLERS.register(DOMAIN)
class PushPlusConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """PushPlus配置流处理类"""
    VERSION = 1  # 版本号（必须为整数）

    async def async_step_user(self, user_input=None) -> FlowResult:
        """处理用户UI配置步骤"""
        errors = {}

        if user_input is not None:
            # 验证Token不为空
            if not user_input[CONF_TOKEN].strip():
                errors[CONF_TOKEN] = "missing_token"
            else:
                # 确保配置唯一（通过Token区分，避免重复配置）
                await self.async_set_unique_id(user_input[CONF_TOKEN])
                self._abort_if_unique_id_configured()

                # 创建配置项
                return self.async_create_entry(
                    title="PushPlus 通知",
                    data=user_input
                )

        # 显示配置表单（UI界面）
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_TOKEN): str,
                vol.Optional(CONF_CHANNEL, default="wechat,app,extension"): str,
            }),
            errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        return PushPlusOptionsFlowHandler()


class PushPlusOptionsFlowHandler(config_entries.OptionsFlow):
    async def async_step_init(self, user_input=None) -> FlowResult:
        if user_input is not None:
            new_data = {
                CONF_TOKEN: user_input[CONF_TOKEN],
                CONF_CHANNEL: user_input.get(CONF_CHANNEL, ""),
            }
            self.hass.config_entries.async_update_entry(
                self.config_entry, data=new_data
            )
            return self.async_create_entry(title="", data={})

        current_token = self.config_entry.data.get(CONF_TOKEN, "")
        current_channel = self.config_entry.data.get(CONF_CHANNEL, "")

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required(CONF_TOKEN, default=current_token): str,
                vol.Optional(CONF_CHANNEL, default=current_channel): str,
            }),
        )