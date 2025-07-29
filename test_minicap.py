#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的minicap连接测试脚本
"""

import socket
import struct
import time

def test_minicap_connection():
    """测试minicap连接"""
    print("=== Minicap连接测试 ===")
    
    try:
        # 创建socket连接
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)  # 设置5秒超时
        
        print("正在连接到 localhost:1313...")
        sock.connect(('localhost', 1313))
        print("✓ 连接成功!")
        
        # 读取banner - 逐字节读取
        print("正在读取banner信息...")
        
        # 读取版本和长度
        version = sock.recv(1)
        length = sock.recv(1)
        
        if not version or not length:
            print("✗ 无法读取banner")
            return False
            
        version = version[0]
        banner_length = length[0]
        
        print(f"✓ 版本: {version}, Banner长度: {banner_length}")
        
        # 初始化banner数据
        banner = {
            'version': version,
            'length': banner_length,
            'pid': 0,
            'realWidth': 0,
            'realHeight': 0,
            'virtualWidth': 0,
            'virtualHeight': 0,
            'orientation': 0,
            'quirks': 0
        }
        
        # 逐字节读取剩余的banner数据
        read_bytes = 2  # 已经读取了version和length
        while read_bytes < banner_length:
            byte_data = sock.recv(1)
            if not byte_data:
                print("✗ Banner数据读取中断")
                return False
                
            byte_val = byte_data[0]
            
            if read_bytes == 2:  # pid byte 0
                banner['pid'] = byte_val
            elif read_bytes == 3:  # pid byte 1
                banner['pid'] += byte_val << 8
            elif read_bytes == 4:  # pid byte 2
                banner['pid'] += byte_val << 16
            elif read_bytes == 5:  # pid byte 3
                banner['pid'] += byte_val << 24
            elif read_bytes == 6:  # realWidth byte 0
                banner['realWidth'] = byte_val
            elif read_bytes == 7:  # realWidth byte 1
                banner['realWidth'] += byte_val << 8
            elif read_bytes == 8:  # realWidth byte 2
                banner['realWidth'] += byte_val << 16
            elif read_bytes == 9:  # realWidth byte 3
                banner['realWidth'] += byte_val << 24
            elif read_bytes == 10:  # realHeight byte 0
                banner['realHeight'] = byte_val
            elif read_bytes == 11:  # realHeight byte 1
                banner['realHeight'] += byte_val << 8
            elif read_bytes == 12:  # realHeight byte 2
                banner['realHeight'] += byte_val << 16
            elif read_bytes == 13:  # realHeight byte 3
                banner['realHeight'] += byte_val << 24
            elif read_bytes == 14:  # virtualWidth byte 0
                banner['virtualWidth'] = byte_val
            elif read_bytes == 15:  # virtualWidth byte 1
                banner['virtualWidth'] += byte_val << 8
            elif read_bytes == 16:  # virtualWidth byte 2
                banner['virtualWidth'] += byte_val << 16
            elif read_bytes == 17:  # virtualWidth byte 3
                banner['virtualWidth'] += byte_val << 24
            elif read_bytes == 18:  # virtualHeight byte 0
                banner['virtualHeight'] = byte_val
            elif read_bytes == 19:  # virtualHeight byte 1
                banner['virtualHeight'] += byte_val << 8
            elif read_bytes == 20:  # virtualHeight byte 2
                banner['virtualHeight'] += byte_val << 16
            elif read_bytes == 21:  # virtualHeight byte 3
                banner['virtualHeight'] += byte_val << 24
            elif read_bytes == 22:  # orientation
                banner['orientation'] = byte_val * 90
            elif read_bytes == 23:  # quirks
                banner['quirks'] = byte_val
            
            read_bytes += 1
        
        print("✓ Banner信息:")
        print(f"  PID: {banner['pid']}")
        print(f"  真实分辨率: {banner['realWidth']}x{banner['realHeight']}")
        print(f"  虚拟分辨率: {banner['virtualWidth']}x{banner['virtualHeight']}")
        print(f"  方向: {banner['orientation']}°")
        print(f"  特性: {banner['quirks']}")
        
        # 尝试读取一帧数据
        print("正在尝试读取第一帧...")
        sock.settimeout(10)  # 增加超时时间
        
        # 读取帧长度
        frame_length_bytes = sock.recv(4)
        if len(frame_length_bytes) < 4:
            print("✗ 无法读取帧长度")
            return False
            
        frame_length = struct.unpack('<I', frame_length_bytes)[0]
        print(f"✓ 帧长度: {frame_length} 字节")
        
        # 读取帧数据
        frame_data = b''
        bytes_read = 0
        
        while bytes_read < frame_length:
            chunk = sock.recv(min(4096, frame_length - bytes_read))
            if not chunk:
                print("✗ 连接中断")
                return False
            frame_data += chunk
            bytes_read += len(chunk)
        
        print(f"✓ 成功读取帧数据: {len(frame_data)} 字节")
        
        # 验证JPEG头部
        if frame_data[:2] == b'\xff\xd8':
            print("✓ 帧数据是有效的JPEG格式")
            
            # 保存测试帧
            with open('test_frame.jpg', 'wb') as f:
                f.write(frame_data)
            print("✓ 已保存测试帧到 test_frame.jpg")
        else:
            print("✗ 帧数据不是有效的JPEG格式")
            return False
        
        sock.close()
        print("✓ 测试完成!")
        return True
        
    except socket.timeout:
        print("✗ 连接超时")
        return False
    except ConnectionRefusedError:
        print("✗ 连接被拒绝，请确保:")
        print("  1. minicap正在设备上运行")
        print("  2. 已执行: adb forward tcp:1313 localabstract:minicap")
        return False
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False

if __name__ == "__main__":
    test_minicap_connection() 