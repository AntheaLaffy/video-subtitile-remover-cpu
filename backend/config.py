import warnings
from enum import Enum, unique
warnings.filterwarnings("ignore")
import os
import torch
import logging
import platform
import stat
import onnxruntime as ort
# -------------- 兼容性补丁 --------------
import os
import shutil
from backend.fsplit.main import split as _split   # 如果后面真要用再保留

class Filesplit:
    """临时壳，split 用 fsplit，merge 用自定义逻辑"""
    def split(self, file, num=2, dest=None):
        return _split(file, num, dest)

    def merge(self, *, input_dir, output_dir=''):
        output_dir = output_dir or input_dir
        os.makedirs(output_dir, exist_ok=True)

        manifest = os.path.join(input_dir, 'fs_manifest.csv')
        if os.path.exists(manifest):
            with open(manifest) as f:
                next(f)  # 跳过表头
                parts = [line.strip().split(',')[0]  # 只取第一列（文件名）
                         for line in f if line.strip()]
        else:
            parts = sorted([p for p in os.listdir(input_dir) if p.endswith('.pt')])

        out_file = os.path.join(output_dir, 'big-lama.pt')
        with open(out_file, 'wb') as dst:
            for p in parts:
                src_path = os.path.join(input_dir, p)
                with open(src_path, 'rb') as src:
                    shutil.copyfileobj(src, dst)
# -------------- 兼容性补丁 --------------

ffmpeg_dir = r'D:\工作区编程\字幕去除\video-subtitle-remover\backend\ffmpeg\win_x64'
# 合成 ffmpeg.exe
fs = Filesplit()
fs.merge(input_dir=ffmpeg_dir, output_dir=ffmpeg_dir)
# 项目版本号
VERSION = "1.1.1"
# ×××××××××××××××××××× [不要改] start ××××××××××××××××××××
logging.disable(logging.DEBUG)  # 关闭DEBUG日志的打印
logging.disable(logging.WARNING)  # 关闭WARNING日志的打印
try:
    import torch_directml

    device = torch_directml.device(torch_directml.default_device())
    USE_DML = True
except Exception:
    USE_DML = False
    try:
        if torch.cuda.is_available():
            device = torch.device("cuda:0")
        else:
            device = torch.device("cpu")
    except Exception:
        device = torch.device("cpu")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LAMA_MODEL_PATH = os.path.join(BASE_DIR, "models", "big-lama")
STTN_MODEL_PATH = os.path.join(BASE_DIR, "models", "sttn", "infer_model.pth")
VIDEO_INPAINT_MODEL_PATH = os.path.join(BASE_DIR, "models", "video")
MODEL_VERSION = "V4"
DET_MODEL_BASE = os.path.join(BASE_DIR, "models")
DET_MODEL_PATH = os.path.join(DET_MODEL_BASE, MODEL_VERSION, "ch_det")

# 查看该路径下是否有模型完整文件，没有的话合并小文件生成完整文件
if "big-lama.pt" not in (os.listdir(LAMA_MODEL_PATH)):
    fs = Filesplit()
    fs.merge(input_dir=LAMA_MODEL_PATH)

if "inference.pdiparams" not in os.listdir(DET_MODEL_PATH):
    fs = Filesplit()
    fs.merge(input_dir=DET_MODEL_PATH)

if "ProPainter.pth" not in os.listdir(VIDEO_INPAINT_MODEL_PATH):
    fs = Filesplit()
    fs.merge(input_dir=VIDEO_INPAINT_MODEL_PATH)

# 指定ffmpeg可执行程序路径
sys_str = platform.system()
if sys_str == "Windows":
    ffmpeg_bin = os.path.join("win_x64", "ffmpeg.exe")
elif sys_str == "Linux":
    ffmpeg_bin = os.path.join("linux_x64", "ffmpeg")
else:
    ffmpeg_bin = os.path.join("macos", "ffmpeg")
FFMPEG_PATH = os.path.join(BASE_DIR, "", "ffmpeg", ffmpeg_bin)

if "ffmpeg.exe" not in os.listdir(os.path.join(BASE_DIR, "", "ffmpeg", "win_x64")):
    fs = Filesplit()
    fs.merge(input_dir=os.path.join(BASE_DIR, "", "ffmpeg", "win_x64"))
# 确保 ffmpeg.exe 存在后再设置权限
if os.path.isfile(FFMPEG_PATH):
    os.chmod(FFMPEG_PATH, stat.S_IRWXU + stat.S_IRWXG + stat.S_IRWXO)
else:
    print(f"[WARN] FFmpeg not found at {FFMPEG_PATH}")

# 是否使用ONNX(DirectML/AMD/Intel)
ONNX_PROVIDERS = []
available_providers = ort.get_available_providers()
for provider in available_providers:
    if provider in ["CPUExecutionProvider"]:
        continue
    if provider not in [
        "DmlExecutionProvider",  # DirectML，适用于 Windows GPU
        "ROCMExecutionProvider",  # AMD ROCm
        "MIGraphXExecutionProvider",  # AMD MIGraphX
        "VitisAIExecutionProvider",  # AMD VitisAI，适用于 RyzenAI & Windows, 实测和DirectML性能似乎差不多
        "OpenVINOExecutionProvider",  # Intel GPU
        "MetalExecutionProvider",  # Apple macOS
        "CoreMLExecutionProvider",  # Apple macOS
        "CUDAExecutionProvider",  # Nvidia GPU
    ]:
        continue
    ONNX_PROVIDERS.append(provider)
# ×××××××××××××××××××× [不要改] end ××××××××××××××××××××


@unique
class InpaintMode(Enum):
    """
    图像重绘算法枚举
    """

    STTN = "sttn"
    LAMA = "lama"
    PROPAINTER = "propainter"


# ×××××××××××××××××××× [可以改] start ××××××××××××××××××××
# 是否使用h264编码，如果需要安卓手机分享生成的视频，请打开该选项
USE_H264 = True

# ×××××××××× 通用设置 start ××××××××××
"""
MODE可选算法类型
- InpaintMode.STTN 算法：对于真人视频效果较好，速度快，可以跳过字幕检测
- InpaintMode.LAMA 算法：对于动画类视频效果好，速度一般，不可以跳过字幕检测
- InpaintMode.PROPAINTER 算法： 需要消耗大量显存，速度较慢，对运动非常剧烈的视频效果较好
"""
# 【设置inpaint算法】
MODE = InpaintMode.STTN
# 【设置像素点偏差】
# 用于判断是不是非字幕区域(一般认为字幕文本框的长度是要大于宽度的，如果字幕框的高大于宽，且大于的幅度超过指定像素点大小，则认为是错误检测)
THRESHOLD_HEIGHT_WIDTH_DIFFERENCE = 10
# 用于放大mask大小，防止自动检测的文本框过小，inpaint阶段出现文字边，有残留
SUBTITLE_AREA_DEVIATION_PIXEL = 20
# 同于判断两个文本框是否为同一行字幕，高度差距指定像素点以内认为是同一行
THRESHOLD_HEIGHT_DIFFERENCE = 20
# 用于判断两个字幕文本的矩形框是否相似，如果X轴和Y轴偏差都在指定阈值内，则认为时同一个文本框
PIXEL_TOLERANCE_Y = 20  # 允许检测框纵向偏差的像素点数
PIXEL_TOLERANCE_X = 20  # 允许检测框横向偏差的像素点数
# ×××××××××× 通用设置 end ××××××××××

# ×××××××××× InpaintMode.STTN算法设置 start ××××××××××
# 以下参数仅适用STTN算法时，才生效
"""
1. STTN_SKIP_DETECTION
含义：是否使用跳过检测
效果：设置为True跳过字幕检测，会省去很大时间，但是可能误伤无字幕的视频帧或者会导致去除的字幕漏了

2. STTN_NEIGHBOR_STRIDE
含义：相邻帧数步长, 如果需要为第50帧填充缺失的区域，STTN_NEIGHBOR_STRIDE=5，那么算法会使用第45帧、第40帧等作为参照。
效果：用于控制参考帧选择的密度，较大的步长意味着使用更少、更分散的参考帧，较小的步长意味着使用更多、更集中的参考帧。

3. STTN_REFERENCE_LENGTH
含义：参数帧数量，STTN算法会查看每个待修复帧的前后若干帧来获得用于修复的上下文信息
效果：调大会增加显存占用，处理效果变好，但是处理速度变慢

4. STTN_MAX_LOAD_NUM
含义：STTN算法每次最多加载的视频帧数量
效果：设置越大速度越慢，但效果越好
注意：要保证STTN_MAX_LOAD_NUM大于STTN_NEIGHBOR_STRIDE和STTN_REFERENCE_LENGTH
"""
STTN_SKIP_DETECTION = True
# 参考帧步长
STTN_NEIGHBOR_STRIDE = 5
# 参考帧长度（数量）
STTN_REFERENCE_LENGTH = 10
# 设置STTN算法最大同时处理的帧数量
STTN_MAX_LOAD_NUM = 50
if STTN_MAX_LOAD_NUM < STTN_REFERENCE_LENGTH * STTN_NEIGHBOR_STRIDE:
    STTN_MAX_LOAD_NUM = STTN_REFERENCE_LENGTH * STTN_NEIGHBOR_STRIDE
# ×××××××××× InpaintMode.STTN算法设置 end ××××××××××

# ×××××××××× InpaintMode.PROPAINTER算法设置 start ××××××××××
# 【根据自己的GPU显存大小设置】最大同时处理的图片数量，设置越大处理效果越好，但是要求显存越高
# 1280x720p视频设置80需要25G显存，设置50需要19G显存
# 720x480p视频设置80需要8G显存，设置50需要7G显存
PROPAINTER_MAX_LOAD_NUM = 70
# ×××××××××× InpaintMode.PROPAINTER算法设置 end ××××××××××

# ×××××××××× InpaintMode.LAMA算法设置 start ××××××××××
# 是否开启极速模式，开启后不保证inpaint效果，仅仅对包含文本的区域文本进行去除
LAMA_SUPER_FAST = False
# ×××××××××× InpaintMode.LAMA算法设置 end ××××××××××
# ×××××××××××××××××××× [可以改] end ××××××××××××××××××××

# ---------------------------------
# 供 GUI 实时刷新的字典
# key 与控件 key 一致，value 直接写给对应全局变量
# ---------------------------------
# 当前文件就是 backend.config，直接赋值即可
GUI_CTRL_MAP = {
    "-MODE-":          lambda v: globals().__setitem__('MODE', InpaintMode[v]),
    "-SKIP_DET-":      lambda v: globals().__setitem__('STTN_SKIP_DETECTION', v),
    "-STRIDE-":        lambda v: globals().__setitem__('STTN_NEIGHBOR_STRIDE', int(v)),
    "-REF_LEN-":       lambda v: globals().__setitem__('STTN_REFERENCE_LENGTH', int(v)),
    "-MAX_LOAD-":      lambda v: globals().__setitem__('STTN_MAX_LOAD_NUM', int(v)),
    "-SUPER_FAST-":    lambda v: globals().__setitem__('LAMA_SUPER_FAST', v),
    "-USE_H264-":      lambda v: globals().__setitem__('USE_H264', v),
}