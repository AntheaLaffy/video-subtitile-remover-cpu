简体中文 | [English](README_en.md)

## Project Introduction

![License](https://img.shields.io/badge/License-Apache%202-red.svg)
![python version](https://img.shields.io/badge/Python-3.10-blue.svg)
![support os](https://img.shields.io/badge/OS-Windows/macOS/Linux-green.svg)

**video-subtitle-remover-cpu** is forked from YaoFANGUK's VSR project and inherits the GPL v2 license.

Video-subtitle-remover (VSR) is a software that uses AI technology to remove hardcoded subtitles from videos.

VSR mainly implements the following features:
- **Lossless resolution** removal of hardcoded subtitles from videos, generating a subtitle-free output file.
- Uses AI algorithm models to inpaint the areas where subtitles were removed (non-adjacent pixel filling and mosaic removal).
- Supports custom subtitle areas — only removes subtitles within the specified region (by providing coordinates).
- Supports automatic removal of all text in the video (without specifying a region).

**Note:**
- **"Lossless resolution" does not mean the video processing is lossless.**
- **On the contrary, removing hardcoded subtitles requires re-encoding, which means there will be quality loss.**
- **A more obvious issue: many MP4 videos use the AVC1 codec, but this project supports MP4V. So during processing, the video will be converted to MP4V.**
- **As a result, the frame rate of the processed video may differ slightly from the original, though the difference is usually negligible.**

<img src="https://github.com/AntheaLaffy/vsr-webui/raw/main/test/vsr.png" alt="webui">

**PS: My little corner — feel free to drop by: 拉菲的八二年酒窖**

<img src="https://github.com/AntheaLaffy/resourses/raw/main/my-group.jpg" width="300px">

## VSR-WebUI Usage Instructions — If You Want to Run It on CPU

### Option 1: Download the Precompiled Executable from My Release
(If it's too large, over 2GB, I might upload it to Hugging Face instead.)

### Option 2: Run from Source

1. **Clone the Repository**
(If you don’t have Git installed, you can download the ZIP directly. However, models larger than 25MB are not included in the ZIP, so you’ll have to download them manually — which is a hassle. It's better to just install Git.)
```bash
git clone https://github.com/AntheaLaffy/video-subtitile-remover-cpu.git
```
```
cd video-subtitile-remover-cpu
```
2. **Check Python Version**

Make sure your Python version is 3.10.x:
```
python -V
```
If your version is not 3.10.x:

You need to create and activate a virtual environment:

Option 1: If you have Conda installed

```
conda create --prefix ./env python=3.10
```
For example:
```
python gui.py
```
Becomes:
```
env/python.exe gui.py
```
Option 2: Install Python 3.10 manually
- Note: After installing Python 3.10, you don’t have to create a virtual environment, but you can if you want.
(Optional) Create and activate a virtual environment:
```
python3.10 -m venv env
```
Activate it:
```
env\Scripts\activate
```

3. Install Dependencies

(Note: If using Conda, replace python with env/python.exe)

I’ve provided a smart_install.py script that automatically installs the required packages based on whether you're using CPU or GPU:

```
python smart_install.py
```

4. Launch the Program
```
python gui.py
```
## Algorithm Selection & Advanced Parameter Settings
- STTN Algorithm: Best for live-action videos
- LAMA Algorithm: Best for animated content
- ProPAINter Algorithm: Best for videos with heavy motion/shaking

  If you're using CPU, it’s not recommended to set parameters too high.
