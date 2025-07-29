#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Minicap客户端程序
用于连接minicap socket并接收图像数据
"""

import socket
import struct
import time
import os
from datetime import datetime

class MinicapClient:
    def __init__(self, host='localhost', port=1313):
        self.host = host
        self.port = port
        self.socket = None
        self.banner = None
        
    def connect(self):
        """连接到minicap socket"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            print(f"已连接到 {self.host}:{self.port}")
            return True
        except Exception as e:
            print(f"连接失败: {e}")
            return False
    
    def read_banner(self):
        """读取banner信息"""
        try:
            # 读取版本和长度
            version = self.socket.recv(1)
            length = self.socket.recv(1)
            
            if not version or not length:
                print("无法读取banner")
                return False
                
            version = version[0]
            banner_length = length[0]
            
            print(f"版本: {version}, Banner长度: {banner_length}")
            
            # 初始化banner数据
            self.banner = {
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
                byte_data = self.socket.recv(1)
                if not byte_data:
                    print("Banner数据读取中断")
                    return False
                    
                byte_val = byte_data[0]
                
                if read_bytes == 2:  # pid byte 0
                    self.banner['pid'] = byte_val
                elif read_bytes == 3:  # pid byte 1
                    self.banner['pid'] += byte_val << 8
                elif read_bytes == 4:  # pid byte 2
                    self.banner['pid'] += byte_val << 16
                elif read_bytes == 5:  # pid byte 3
                    self.banner['pid'] += byte_val << 24
                elif read_bytes == 6:  # realWidth byte 0
                    self.banner['realWidth'] = byte_val
                elif read_bytes == 7:  # realWidth byte 1
                    self.banner['realWidth'] += byte_val << 8
                elif read_bytes == 8:  # realWidth byte 2
                    self.banner['realWidth'] += byte_val << 16
                elif read_bytes == 9:  # realWidth byte 3
                    self.banner['realWidth'] += byte_val << 24
                elif read_bytes == 10:  # realHeight byte 0
                    self.banner['realHeight'] = byte_val
                elif read_bytes == 11:  # realHeight byte 1
                    self.banner['realHeight'] += byte_val << 8
                elif read_bytes == 12:  # realHeight byte 2
                    self.banner['realHeight'] += byte_val << 16
                elif read_bytes == 13:  # realHeight byte 3
                    self.banner['realHeight'] += byte_val << 24
                elif read_bytes == 14:  # virtualWidth byte 0
                    self.banner['virtualWidth'] = byte_val
                elif read_bytes == 15:  # virtualWidth byte 1
                    self.banner['virtualWidth'] += byte_val << 8
                elif read_bytes == 16:  # virtualWidth byte 2
                    self.banner['virtualWidth'] += byte_val << 16
                elif read_bytes == 17:  # virtualWidth byte 3
                    self.banner['virtualWidth'] += byte_val << 24
                elif read_bytes == 18:  # virtualHeight byte 0
                    self.banner['virtualHeight'] = byte_val
                elif read_bytes == 19:  # virtualHeight byte 1
                    self.banner['virtualHeight'] += byte_val << 8
                elif read_bytes == 20:  # virtualHeight byte 2
                    self.banner['virtualHeight'] += byte_val << 16
                elif read_bytes == 21:  # virtualHeight byte 3
                    self.banner['virtualHeight'] += byte_val << 24
                elif read_bytes == 22:  # orientation
                    self.banner['orientation'] = byte_val * 90
                elif read_bytes == 23:  # quirks
                    self.banner['quirks'] = byte_val
                
                read_bytes += 1
            
            print("Banner信息:")
            for key, value in self.banner.items():
                print(f"  {key}: {value}")
            
            return True
            
        except Exception as e:
            print(f"读取banner失败: {e}")
            return False
    
    def save_frame(self, frame_data, frame_count):
        """保存帧数据为JPEG文件"""
        filename = f"frame_{frame_count:04d}_{datetime.now().strftime('%H%M%S')}.jpg"
        try:
            with open(filename, 'wb') as f:
                f.write(frame_data)
            print(f"已保存帧: {filename} (大小: {len(frame_data)} 字节)")
            return filename
        except Exception as e:
            print(f"保存帧失败: {e}")
            return None
    
    def receive_frames(self, max_frames=10, save_frames=True):
        """接收图像帧"""
        if not self.banner:
            print("请先读取banner信息")
            return
        
        frame_count = 0
        read_frame_bytes = 0
        frame_body_length = 0
        frame_body = b''
        
        print(f"开始接收帧，最多接收 {max_frames} 帧...")
        
        try:
            while frame_count < max_frames:
                # 读取帧长度 (4字节)
                if read_frame_bytes < 4:
                    data = self.socket.recv(4 - read_frame_bytes)
                    if not data:
                        print("连接已关闭")
                        break
                    
                    for byte in data:
                        frame_body_length += (byte << (read_frame_bytes * 8))
                        read_frame_bytes += 1
                
                # 读取帧数据
                if read_frame_bytes == 4 and frame_body_length > 0:
                    remaining = frame_body_length - len(frame_body)
                    if remaining > 0:
                        chunk = self.socket.recv(remaining)
                        if not chunk:
                            print("连接已关闭")
                            break
                        frame_body += chunk
                    
                    # 检查是否接收到完整的帧
                    if len(frame_body) == frame_body_length:
                        # 验证JPEG头部
                        if frame_body[:2] == b'\xff\xd8':
                            frame_count += 1
                            print(f"接收到第 {frame_count} 帧 (大小: {len(frame_body)} 字节)")
                            
                            if save_frames:
                                self.save_frame(frame_body, frame_count)
                            
                            # 重置状态
                            frame_body = b''
                            frame_body_length = 0
                            read_frame_bytes = 0
                        else:
                            print("帧数据不是有效的JPEG格式")
                            break
                
        except KeyboardInterrupt:
            print("\n用户中断")
        except Exception as e:
            print(f"接收帧时出错: {e}")
        finally:
            print(f"总共接收了 {frame_count} 帧")
    
    def close(self):
        """关闭连接"""
        if self.socket:
            self.socket.close()
            print("连接已关闭")

def main():
    """主函数"""
    print("=== Minicap客户端 ===")
    print("使用说明:")
    print("1. 确保minicap已在设备上运行")
    print("2. 执行: adb forward tcp:1313 localabstract:minicap")
    print("3. 运行此客户端程序")
    print()
    
    client = MinicapClient()
    
    # 连接
    if not client.connect():
        return
    
    # 读取banner
    if not client.read_banner():
        client.close()
        return
    
    # 接收帧
    try:
        client.receive_frames(max_frames=5, save_frames=True)
    except KeyboardInterrupt:
        print("\n程序被用户中断")
    
    # 关闭连接
    client.close()

if __name__ == "__main__":
    main() 