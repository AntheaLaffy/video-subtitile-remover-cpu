#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
递归批量格式化 Python 文件
优先 black → 降级 autopep8
默认 8 线程，可改 -j 参数
"""
import os
import sys
import subprocess
import concurrent.futures
from pathlib import Path

TOOL = None
WORKERS = 8  # 线程数


def which(cmd):
    """跨平台判断命令是否存在"""
    try:
        subprocess.run([cmd, "--version"], capture_output=True, check=True)
        return True
    except Exception:
        return False


def choose_tool():
    global TOOL
    if which("black"):
        TOOL = ["black", "-q"]
    elif which("autopep8"):
        TOOL = ["autopep8", "-i", "--aggressive", "--aggressive"]
    else:
        print("\033[31m✘ 未找到 black 或 autopep8，请先安装\033[0m")
        sys.exit(1)


def format_file(file_path: Path):
    try:
        subprocess.run(TOOL + [str(file_path)], check=True)
        print(f"\033[32m✔\033[0m {file_path}")
    except subprocess.CalledProcessError:
        print(f"\033[31m✘\033[0m {file_path}")


def main():
    choose_tool()
    root = Path(__file__).parent.resolve()
    py_files = list(root.rglob("*.py"))
    if not py_files:
        print("未找到任何 .py 文件")
        return
    print(f"共发现 {len(py_files)} 个文件，开始格式化...\n")
    with concurrent.futures.ThreadPoolExecutor(max_workers=WORKERS) as exe:
        exe.map(format_file, py_files)
    print("\n\033[34m🎉 全部完成！\033[0m")


if __name__ == "__main__":
    main()
