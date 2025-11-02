#!/usr/bin/env python3
"""
一键智能安装依赖：
Windows + 64 位  → 优先 DirectML
检测到 CUDA     → GPU 版
其余           → CPU 版
"""
import os
import sys
import subprocess
import shutil

ONNX_CPU    = "onnxruntime==1.20.1"
ONNX_GPU    = "onnxruntime-gpu==1.20.1"
ONNX_DML    = "onnxruntime-directml==1.20.1"

def detect_onnx():
    """返回最适合当前机器的 onnxruntime 包名"""
    if sys.platform == "win32" and shutil.which("dmlinfo") is None:
        # 简单 heuristic：Windows 64 位就认为支持 DirectML
        return ONNX_DML
    # 检测 CUDA
    cuda_exist = (
        shutil.which("nvcc") or
        os.path.exists("/usr/local/cuda/bin/nvcc") or
        os.environ.get("CUDA_PATH", "")
    )
    return ONNX_GPU if cuda_exist else ONNX_CPU

def main():
    onnx_pkg = detect_onnx()
    locked = "requirements-locked.txt"
    # 生成锁定文件
    with open("requirements-base.txt", encoding="utf-8") as f:
        base = f.read().strip()
    with open(locked, "w", encoding="utf-8") as f:
        f.write(base + "\n" + onnx_pkg + "\n")
    print(f"[INFO] 锁定 onnxruntime 包：{onnx_pkg}")
    # 安装
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", locked], shell=True)
    print("\033[36m🎉 全部依赖安装完成！\033[0m")


if __name__ == "__main__":
    main()