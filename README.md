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

把源码下载下来
进入命令行,安装依赖文件，这个requirement是在我的cpu笔记本上构建的
```bash
pip install -r requirements-cpu.txt
```
之后启动gui.py
```bash
python gui.py
```

## 算法选择&高级参数设置

- STTN算法：真人最优
- LAMA算法：动画风格最优
- PROPATINTER算法：剧烈抖动的最优

如果是cpu的化不建议把参数调高
