feat: 添加Python客户端程序用于连接minicap socket

## 新增文件
- `minicap_client.py` - 完整的minicap客户端程序
  - 支持连接minicap socket并接收图像数据
  - 自动读取banner信息（设备分辨率、PID等）
  - 支持接收多帧图像并保存为JPEG文件
  - 包含完整的错误处理和超时机制

- `test_minicap.py` - 简单的连接测试脚本
  - 快速验证minicap连接是否正常
  - 读取设备信息并保存单帧测试图像
  - 适合调试和验证环境配置

- `客户端使用说明.md` - 详细的使用文档
  - 包含完整的使用步骤和故障排除指南
  - 说明minicap协议格式和技术细节
  - 提供示例输出和常见问题解决方案

## 技术实现
- 使用纯Python标准库，无需额外依赖
- 正确实现minicap协议：逐字节读取24字节banner + 4字节帧长度 + JPEG数据
- 支持小端序数据解析和JPEG格式验证
- 提供中文界面和详细的调试信息输出

## 使用方式
1. 启动minicap服务端：`./run.sh autosize`
2. 设置端口转发：`adb forward tcp:1313 localabstract:minicap`
3. 运行测试：`python test_minicap.py`
4. 接收多帧：`python minicap_client.py`

## 解决的问题
- 修复了banner数据读取时的字节序问题
- 实现了正确的minicap协议解析
- 提供了完整的客户端功能用于接收和保存屏幕截图 