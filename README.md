- # PushPlus 通知集成

  这是一个适用于 Home Assistant 的 PushPlus 通知集成，允许你通过 PushPlus 服务发送通知消息到你的设备。

  ## 功能介绍

  通过该集成，你可以在 Home Assistant 中配置 PushPlus 通知服务，实现将自动化、脚本或手动触发的消息通过 PushPlus 平台发送到手机、微信等终端。

  ## 安装方法

  1. 下载本项目的所有文件
  2. 将 `pushplus` 文件夹复制到 Home Assistant 的 `custom_components` 目录下
  3. 重启 Home Assistant

  ## 配置步骤

  1. 在 [PushPlus 官网](https://www.pushplus.plus/) 注册账号并获取你的 Token（在个人中心可查看）
  2. 在 Home Assistant 中，进入 `设置 > 设备与服务 > 集成`
  3. 点击右下角 `添加集成`，搜索 `PushPlus 通知`
  4. 在配置表单中输入你的 PushPlus Token
  5. 完成配置，集成将自动创建 `notify.pushplus` 服务

  ## 使用方法

  可以通过调用 `notify.pushplus` 服务发送通知，支持以下参数：

  - `message` (必填): 通知内容
  - `title` (可选): 通知标题，默认值为 "Home Assistant 通知"

  ### 服务调用示例

  #### 手动调用（开发者工具）

  ```yaml
  service: notify.pushplus
  data:
    message: "这是一条来自Home Assistant的测试消息"
    title: "测试通知"
  ```

  #### 在自动化中使用

  ```yaml
  automation:
    - alias: "温度过高时发送通知"
      trigger:
        platform: numeric_state
        entity_id: sensor.temperature
        above: 30
      action:
        service: notify.pushplus
        data:
          title: "温度警告"
          message: "当前温度过高，已超过30°C"
  ```

  ## 常见问题

  - **发送失败？**

    1. 检查 PushPlus Token 是否正确
    2. 确认网络连接正常，Home Assistant 能够访问 `https://www.pushplus.plus`
    3. 查看 Home Assistant 日志，搜索 "pushplus" 获取详细错误信息

  - **标题不生效？**

    若未指定标题或标题为空，将自动使用默认标题 "Home Assistant 通知"

  ## 版本信息

  当前版本：1.0.0

  ## 依赖

  - requests>=2.25.1（Home Assistant 会自动安装）

  ## 文档与支持

  - [项目文档](https://github.com/flamestsui/pushplus)
  - 如有问题，请提交 Issue 到项目仓库
