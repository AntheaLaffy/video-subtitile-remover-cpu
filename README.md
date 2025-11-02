简体中文 | [English](README_en.md)

## 项目简介

![License](https://img.shields.io/badge/License-Apache%202-red.svg)
![python version](https://img.shields.io/badge/Python-3.11+-blue.svg)
![support os](https://img.shields.io/badge/OS-Windows/macOS/Linux-green.svg)  

video-subtitile-remover-cpu fork自YaoFANGUK的VSR项目，继承GPL v2协议

Video-subtitle-remover (VSR) 是一款基于AI技术，将视频中的硬字幕去除的软件。

VSR主要实现了以下功能：
- **无损分辨率**将视频中的硬字幕去除，生成去除字幕后的文件
- 通过AI算法模型，对去除字幕文本的区域进行填充（非相邻像素填充与马赛克去除）
- 支持自定义字幕位置，仅去除定义位置中的字幕（传入位置）
- 支持全视频自动去除所有文本（不传入位置）

注意：
- **无损的只是分辨率并不意味着视频的处理是无损的**  
- **恰恰相反，去除硬字幕是需要重新编码的，这意味着一定有损失。**  
- **一个更明显的：很多的mp4封装的视频编码其实是AVC1，而这个项目支持的格式其实是mp4v，所以处理时会把视频转为mp4v进行处理**  
- **所以你会发现视频合成后的帧数与原视频不一致，不过差异很小可以忽略**
<p style="text-align:center;"><img src="https://github.com/AntheaLaffy/vsr-webui/raw/main/test/vsr.png" alt="webui"/></p>


**PS：我的小窝，欢迎来逛：拉菲的八二年酒窖**

<img src="https://github.com/AntheaLaffy/resourses/raw/main/my-group.jpg" width="300px">

**VSR-WebUI使用说明————如果你想以cpu运行的化**
一、直接到我的release里把exe打包文件下载下来 （如果太大超过2G的化应该放不上，也许我会放在huggingface上）

二、如果你想通过源码

1. 克隆仓库 （如果没有装git的化直接下载zip文件就行，但是那些超过25m的模型是不包括在zip文件夹里的，你需要一个个去找很麻烦////不如去把git软件安装下来）
```bash
git clone https://github.com/AntheaLaffy/video-subtitile-remover-cpu.git
```
```bash
cd video-subtitile-remover-cpu
```
2. 确认python版本
首先确定你的python版本是不是3.10.x
```bash
python -V
```
2.1 如果不是3.10开头
需要提前创建&激活虚拟环境:
（1）方法一：若安装了conda
```bash
conda create --prefix ./env python=3.10
```
接下来所有命令都要以env/python.exe开头,用env/python.exe替换python

例如：原写法
```bash
python gui.py
```
conda写法
```bash
env/python.exe gui.py
```
(2) 方法二：使用virtualenv 工具
```bash
pip install virtualenv
```
```bash
virtualenv -p ./python3.10 env
```
激活
```bash
env\Scripts\activate
```
(3) 方法三：安装一个python3.10
```bash
python3.10 -m venv env
```
激活
```bash
env\Scripts\activate
```

3. 安装依赖(注意conda环境要把python改为env/python.exe)
我这里给了smart_install.py，可以自动根据你使用的是gpu还是cpu安装
```bash
python smart_install.py
```
4.程序启动
```bash
python gui.py
```

## 算法选择&高级参数设置

- STTN算法：真人最优
- LAMA算法：动画风格最优
- PROPATINTER算法：剧烈抖动的最优

如果是cpu的化不建议把参数调高
