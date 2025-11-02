# -*- coding: utf-8 -*-
"""
@Author  : Fang Yao
@Time    : 2023/4/1 6:07 下午
@FileName: gui.py
@desc: 字幕去除器图形化界面
"""
import os
import configparser
import FreeSimpleGUI as sg
import cv2
import sys
from threading import Thread
import multiprocessing

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from backend import config as cfg

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import backend.main
from backend.tools.common_tools import is_image_file


class SubtitleRemoverGUI:
    def __init__(self):
        self.font = "Arial 10"
        self.theme = "LightBrown12"
        sg.theme(self.theme)
        self.icon = os.path.join(os.path.dirname(__file__), "design", "vsr.ico")
        self.screen_width, self.screen_height = sg.Window.get_screen_size()
        self.subtitle_config_file = os.path.join(
            os.path.dirname(__file__), "subtitle.ini"
        )
        # 视频预览尺寸
        self.video_preview_width = 960
        self.video_preview_height = self.video_preview_width * 9 // 16
        self.horizontal_slider_size = (120, 20)
        self.output_size = (100, 10)
        self.progressbar_size = (60, 20)
        if self.screen_width // 2 < 960:
            self.video_preview_width = 640
            self.video_preview_height = self.video_preview_width * 9 // 16
            self.horizontal_slider_size = (60, 20)
            self.output_size = (58, 10)
            self.progressbar_size = (28, 20)

        self.layout = None
        self.window = None
        self.video_path = None
        self.video_cap = None
        self.fps = None
        self.frame_count = None
        self.frame_width = None
        self.frame_height = None
        self.xmin = None
        self.xmax = None
        self.ymin = None
        self.ymax = None
        self.sr = None

    # ---------------- 事件处理 ----------------
    def _file_event_handler(self, event, values):
        if event == "-FILE-":
            self.video_paths = values["-FILE-"].split(";")
            self.video_path = self.video_paths[0]
            if self.video_path != "":
                self.video_cap = cv2.VideoCapture(self.video_path)
            if self.video_cap is None:
                return
            if self.video_cap.isOpened():
                ret, frame = self.video_cap.read()
                if ret:
                    for video in self.video_paths:
                        print(f"Open Video Success：{video}")
                    self.frame_count = self.video_cap.get(cv2.CAP_PROP_FRAME_COUNT)
                    self.frame_height = self.video_cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
                    self.frame_width = self.video_cap.get(cv2.CAP_PROP_FRAME_WIDTH)
                    self.fps = self.video_cap.get(cv2.CAP_PROP_FPS)
                    resized_frame = self._img_resize(frame)
                    self.window["-DISPLAY-"].update(
                        data=cv2.imencode(".png", resized_frame)[1].tobytes()
                    )
                    self.window["-SLIDER-"].update(range=(1, self.frame_count))
                    self.window["-SLIDER-"].update(1)
                    y_p, h_p, x_p, w_p = self.parse_subtitle_config()
                    y = self.frame_height * y_p
                    h = self.frame_height * h_p
                    x = self.frame_width * x_p
                    w = self.frame_width * w_p
                    self.window["-Y-SLIDER-"].update(range=(0, self.frame_height), disabled=False)
                    self.window["-Y-SLIDER-"].update(y)
                    self.window["-X-SLIDER-"].update(range=(0, self.frame_width), disabled=False)
                    self.window["-X-SLIDER-"].update(x)
                    self.window["-Y-SLIDER-H-"].update(range=(0, self.frame_height - y))
                    self.window["-Y-SLIDER-H-"].update(h)
                    self.window["-X-SLIDER-W-"].update(range=(0, self.frame_width - x))
                    self.window["-X-SLIDER-W-"].update(w)
                    self._update_preview(frame, (y, h, x, w))

    def _slide_event_handler(self, event, values):
        if (
            event == "-SLIDER-"
            or event == "-Y-SLIDER-"
            or event == "-Y-SLIDER-H-"
            or event == "-X-SLIDER-"
            or event == "-X-SLIDER-W-"
        ):
            if is_image_file(self.video_path):
                img = cv2.imread(self.video_path)
                self.window["-Y-SLIDER-H-"].update(
                    range=(0, self.frame_height - values["-Y-SLIDER-"])
                )
                self.window["-X-SLIDER-W-"].update(
                    range=(0, self.frame_width - values["-X-SLIDER-"])
                )
                y = int(values["-Y-SLIDER-"])
                h = int(values["-Y-SLIDER-H-"])
                x = int(values["-X-SLIDER-"])
                w = int(values["-X-SLIDER-W-"])
                self._update_preview(img, (y, h, x, w))
            elif self.video_cap is not None and self.video_cap.isOpened():
                frame_no = int(values["-SLIDER-"])
                self.video_cap.set(cv2.CAP_PROP_POS_FRAMES, frame_no)
                ret, frame = self.video_cap.read()
                if ret:
                    self.window["-Y-SLIDER-H-"].update(
                        range=(0, self.frame_height - values["-Y-SLIDER-"])
                    )
                    self.window["-X-SLIDER-W-"].update(
                        range=(0, self.frame_width - values["-X-SLIDER-"])
                    )
                    y = int(values["-Y-SLIDER-"])
                    h = int(values["-Y-SLIDER-H-"])
                    x = int(values["-X-SLIDER-"])
                    w = int(values["-X-SLIDER-W-"])
                    self._update_preview(frame, (y, h, x, w))

    def _run_event_handler(self, event, values):
        if event == "-RUN-":
            if self.video_cap is None:
                print("Please Open Video First")
            else:
                self.__disable_button()
                self.xmin = int(values["-X-SLIDER-"])
                self.xmax = int(values["-X-SLIDER-"] + values["-X-SLIDER-W-"])
                self.ymin = int(values["-Y-SLIDER-"])
                self.ymax = int(values["-Y-SLIDER-"] + values["-Y-SLIDER-H-"])
                if self.ymax > self.frame_height:
                    self.ymax = self.frame_height
                if self.xmax > self.frame_width:
                    self.xmax = self.frame_width
                if len(getattr(self, 'video_paths', [])) <= 1:
                    subtitle_area = (self.ymin, self.ymax, self.xmin, self.xmax)
                else:
                    print(f"{'Processing multiple videos or images'}")
                    global_size = None
                    for temp_video_path in getattr(self, 'video_paths', []):
                        temp_cap = cv2.VideoCapture(temp_video_path)
                        if global_size is None:
                            global_size = (
                                int(temp_cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                                int(temp_cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
                            )
                        else:
                            temp_size = (
                                int(temp_cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                                int(temp_cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
                            )
                            if temp_size != global_size:
                                print(
                                    "not all video/images in same size, processing in full screen"
                                )
                                subtitle_area = None
                    else:
                        subtitle_area = (self.ymin, self.ymax, self.xmin, self.xmax)
                y_p = self.ymin / self.frame_height
                h_p = (self.ymax - self.ymin) / self.frame_height
                x_p = self.xmin / self.frame_width
                w_p = (self.xmax - self.xmin) / self.frame_width
                self.set_subtitle_config(y_p, h_p, x_p, w_p)

                def task():
                    while getattr(self, 'video_paths', []):
                        video_path = self.video_paths.pop()
                        if subtitle_area is not None:
                            print(
                                f"{'SubtitleArea'}：({self.ymin},{self.ymax},{self.xmin},{self.xmax})"
                            )
                        self.sr = backend.main.SubtitleRemover(
                            video_path, subtitle_area, True
                        )
                        self.__disable_button()
                        self.sr.run()

                Thread(target=task, daemon=True).start()
                self.video_cap.release()
                self.video_cap = None

    def __disable_button(self, disable=True):
        self.window["-Y-SLIDER-"].update(disabled=disable)
        self.window["-X-SLIDER-"].update(disabled=disable)
        self.window["-Y-SLIDER-H-"].update(disabled=disable)
        self.window["-X-SLIDER-W-"].update(disabled=disable)
        self.window["-RUN-"].update(disabled=disable)
        self.window["-FILE-"].update(disabled=disable)
        self.window["-FILE_BTN-"].update(disabled=disable)

    def _update_preview(self, frame, y_h_x_w):
        y, h, x, w = y_h_x_w
        draw = cv2.rectangle(
            img=frame,
            pt1=(int(x), int(y)),
            pt2=(int(x) + int(w), int(y) + int(h)),
            color=(0, 255, 0),
            thickness=3,
        )
        resized_frame = self._img_resize(draw)
        self.window["-DISPLAY-"].update(
            data=cv2.imencode(".png", resized_frame)[1].tobytes()
        )

    def _img_resize(self, image):
        top, bottom, left, right = (0, 0, 0, 0)
        height, width = image.shape[0], image.shape[1]
        longest_edge = height
        if width < longest_edge:
            dw = longest_edge - width
            left = dw // 2
            right = dw - left
        constant = cv2.copyMakeBorder(
            image, top, bottom, left, right, cv2.BORDER_CONSTANT, value=[0, 0, 0]
        )
        return cv2.resize(
            constant, (self.video_preview_width, self.video_preview_height)
        )

    def set_subtitle_config(self, y, h, x, w):
        with open(self.subtitle_config_file, mode="w", encoding="utf-8") as f:
            f.write("[AREA]\n")
            f.write(f"Y = {y}\n")
            f.write(f"H = {h}\n")
            f.write(f"X = {x}\n")
            f.write(f"W = {w}\n")

    def parse_subtitle_config(self):
        y_p, h_p, x_p, w_p = 0.78, 0.21, 0.05, 0.9
        if not os.path.exists(self.subtitle_config_file):
            self.set_subtitle_config(y_p, h_p, x_p, w_p)
            return y_p, h_p, x_p, w_p
        else:
            try:
                config = configparser.ConfigParser()
                config.read(self.subtitle_config_file, encoding="utf-8")
                conf_y_p, conf_h_p, conf_x_p, conf_w_p = (
                    float(config["AREA"]["Y"]),
                    float(config["AREA"]["H"]),
                    float(config["AREA"]["X"]),
                    float(config["AREA"]["W"]),
                )
                return conf_y_p, conf_h_p, conf_x_p, conf_w_p
            except Exception:
                self.set_subtitle_config(y_p, h_p, x_p, w_p)
                return y_p, h_p, x_p, w_p

    # ---------------- 布局 ----------------
    def _create_layout(self):
        garbage = os.path.join(os.path.dirname(__file__), "output")
        if os.path.exists(garbage):
            import shutil
            shutil.rmtree(garbage, True)

        # ---------------- 参数控制面板 ----------------
        param_frame = sg.Frame(
            title="算法参数",
            layout=[
                [sg.Text("算法", size=(12, 1)),
                 sg.Combo(["STTN", "LAMA", "PROPAINTER"], default_value=cfg.MODE.value,
                          key="-MODE-", enable_events=True, readonly=True)],

                [sg.Checkbox("跳过字幕检测", default=cfg.STTN_SKIP_DETECTION,
                             key="-SKIP_DET-", enable_events=True)],

                [sg.Text("步长", size=(12, 1)),
                 sg.Slider((1, 20), cfg.STTN_NEIGHBOR_STRIDE, 1, orientation="h",
                           size=(25, 15), key="-STRIDE-", enable_events=True)],

                [sg.Text("参考帧数", size=(12, 1)),
                 sg.Slider((1, 30), cfg.STTN_REFERENCE_LENGTH, 1, orientation="h",
                           size=(25, 15), key="-REF_LEN-", enable_events=True)],

                [sg.Text("最大加载帧", size=(12, 1)),
                 sg.Slider((10, 100), cfg.STTN_MAX_LOAD_NUM, 1, orientation="h",
                           size=(25, 15), key="-MAX_LOAD-", enable_events=True)],

                [sg.Checkbox("LAMA 极速模式", default=cfg.LAMA_SUPER_FAST,
                             key="-SUPER_FAST-", enable_events=True)],

                [sg.Checkbox("输出 H264", default=cfg.USE_H264,
                             key="-USE_H264-", enable_events=True)],
            ],
            font=self.font,
            pad=((0, 0), (10, 10)),
            size=(320, 260)  # 固定大小，防止闪一下
        )

        # ------------- 可折叠参数面板（右侧） -------------
        advanced_col = sg.Column(
            layout=[[param_frame]],
            key="-ADVANCED_COL-",
            visible=False,
            pad=(0, 0)
        )

        # 用来切换显示/隐藏的按钮（放在右侧顶部）
        toggle_btn = sg.Button("高级参数 ▼", key="-TOGGLE_ADV-", size=(12, 1), font=self.font)

        # 右侧列：按钮 + 折叠面板
        right_col = sg.Column(
            layout=[
                [toggle_btn],
                [advanced_col],
                [sg.Stretch()],  # 弹性空白，把按钮顶到上面
            ],
            element_justification="right",  # 整体右对齐
            pad=(0, 0)
        )

        self.layout = [
            # 第一行：视频预览（左） + 右侧按钮区（右）
            [
                sg.Image(
                    size=(self.video_preview_width, self.video_preview_height),
                    background_color="black",
                    key="-DISPLAY-",
                ),
                right_col,
            ],
            # 第二行：打开按钮 + 快进快退条（整行）
            [
                sg.Input(key="-FILE-", visible=False, enable_events=True),
                sg.FilesBrowse(
                    button_text="Open",
                    file_types=(
                        ("All Files", "*.*"),
                        ("mp4", "*.mp4"),
                        ("flv", "*.flv"),
                        ("wmv", "*.wmv"),
                        ("avi", "*.avi"),
                    ),
                    key="-FILE_BTN-",
                    size=(10, 1),
                    font=self.font,
                ),
                sg.Slider(
                    size=self.horizontal_slider_size,
                    range=(1, 1),
                    key="-SLIDER-",
                    orientation="h",
                    enable_events=True,
                    font=self.font,
                    disable_number_display=True,
                ),
            ],
            # 第三行：输出区域（左） + 字幕区域滑块（右）
            [
                sg.Output(size=self.output_size, font=self.font),
                sg.Column(
                    layout=[
                        [
                            sg.Frame(
                                title="Vertical",
                                font=self.font,
                                key="-FRAME1-",
                                layout=[
                                    [
                                        sg.Slider(
                                            range=(0, 0),
                                            orientation="v",
                                            size=(10, 20),
                                            disable_number_display=True,
                                            enable_events=True,
                                            font=self.font,
                                            pad=((10, 10), (20, 20)),
                                            default_value=0,
                                            key="-Y-SLIDER-",
                                        ),
                                        sg.Slider(
                                            range=(0, 0),
                                            orientation="v",
                                            size=(10, 20),
                                            disable_number_display=True,
                                            enable_events=True,
                                            font=self.font,
                                            pad=((10, 10), (20, 20)),
                                            default_value=0,
                                            key="-Y-SLIDER-H-",
                                        ),
                                    ]
                                ],
                                pad=((15, 5), (0, 0)),
                            ),
                            sg.Frame(
                                title="Horizontal",
                                font=self.font,
                                key="-FRAME2-",
                                layout=[
                                    [
                                        sg.Slider(
                                            range=(0, 0),
                                            orientation="v",
                                            size=(10, 20),
                                            disable_number_display=True,
                                            pad=((10, 10), (20, 20)),
                                            enable_events=True,
                                            font=self.font,
                                            default_value=0,
                                            key="-X-SLIDER-",
                                        ),
                                        sg.Slider(
                                            range=(0, 0),
                                            orientation="v",
                                            size=(10, 20),
                                            disable_number_display=True,
                                            pad=((10, 10), (20, 20)),
                                            enable_events=True,
                                            font=self.font,
                                            default_value=0,
                                            key="-X-SLIDER-W-",
                                        ),
                                    ]
                                ],
                                pad=((15, 5), (0, 0)),
                            ),
                        ]
                    ],
                    element_justification="right",
                    pad=(0, 0)
                ),
            ],
            # 第四行：运行按钮 + 进度条（整行，永远底部）
            [
                sg.Button(button_text="Run", key="-RUN-", font=self.font, size=(20, 1)),
                sg.ProgressBar(
                    100,
                    orientation="h",
                    size=self.progressbar_size,
                    key="-PROG-",
                    auto_size_text=True,
                ),
            ],
        ]

    def run(self):
        self._create_layout()
        self.window = sg.Window(
            title=f"Video Subtitle Remover v{backend.main.config.VERSION}",
            layout=self.layout,
            icon=self.icon,
            resizable=True,
            finalize=True,
        )
        self.window.set_min_size((900, 650))

        while True:
            event, values = self.window.read(timeout=10)

            # 展开/收起高级参数
            if event == "-TOGGLE_ADV-":
                visible = not self.window["-ADVANCED_COL-"].visible
                self.window["-ADVANCED_COL-"].update(visible=visible)
                self.window["-TOGGLE_ADV-"].update(
                    text="高级参数 ▼" if not visible else "高级参数 ▲"
                )

            # 实时应用算法参数
            if event in cfg.GUI_CTRL_MAP:
                cfg.GUI_CTRL_MAP[event](values[event])

            self._file_event_handler(event, values)
            self._slide_event_handler(event, values)
            self._run_event_handler(event, values)

            if event == sg.WIN_CLOSED:
                break

            if self.sr is not None:
                self.window["-PROG-"].update(self.sr.progress_total)
                if self.sr.preview_frame is not None:
                    self.window["-DISPLAY-"].update(
                        data=cv2.imencode(
                            ".png", self._img_resize(self.sr.preview_frame)
                        )[1].tobytes()
                    )
                if self.sr.isFinished:
                    self.__disable_button(False)
                    self.sr = None
                if len(getattr(self, 'video_paths', [])) >= 1:
                    self.__disable_button(True)


if __name__ == "__main__":
    try:
        multiprocessing.set_start_method("spawn")
        subtitleRemoverGUI = SubtitleRemoverGUI()
        subtitleRemoverGUI.run()
    except Exception as e:
        print(f"[{type(e)}] {e}")
        import traceback
        traceback.print_exc()
        msg = traceback.format_exc()
        err_log_path = os.path.join(os.path.expanduser("~"), "VSR-Error-Message.log")
        with open(err_log_path, "w", encoding="utf-8") as f:
            f.writelines(msg)
        import platform
        if platform.system() == "Windows":
            os.system("pause")
        else:
            input()