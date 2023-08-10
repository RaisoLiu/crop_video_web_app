import cv2
import os
import gradio as gr


def process_video(input_video, input_img_seq, input_file_type, left_bound, upper_bound, right_bound, buttom_bound, output_codec, output_format, progress=gr.Progress()):
    cropped_video_path = ""

    if input_file_type == "video":
        cropped_video_path = crop_video(input_video, left_bound, upper_bound,
                                        right_bound, buttom_bound, output_codec, output_format, progress)
    if input_file_type == "imgs":
        cropped_video_path = crop_imgs(input_img_seq, left_bound, upper_bound,
                                       right_bound, buttom_bound, output_codec, output_format, progress)

    return cropped_video_path


def crop_frame(origin_frist_frame, left_bound, upper_bound, right_bound, buttom_bound):
    if left_bound == None or upper_bound == None or right_bound == None or buttom_bound == None:
        return None

    h, w, _ = origin_frist_frame.shape

    if left_bound < 0 or left_bound >= right_bound or right_bound > 1:
        gr.Error("[E] left_bound or right_bound")
        return None
    if upper_bound < 0 and upper_bound >= buttom_bound and buttom_bound > 1:
        gr.Error("[E] upper_bound or buttom_bound")
        return None

    left_bound, upper_bound, right_bound, buttom_bound = int(
        left_bound*w), int(upper_bound*h), int(right_bound*w), int(buttom_bound*h)
    return origin_frist_frame[upper_bound:buttom_bound, left_bound:right_bound]


def get_meta_from_video(input_video):
    if input_video is None:
        return None, None

    cap = cv2.VideoCapture(input_video)

    _, first_frame = cap.read()
    cap.release()

    first_frame = cv2.cvtColor(first_frame, cv2.COLOR_BGR2RGB)
    return first_frame, first_frame, "video"


def crop_video(input_video, left, top, right, bottom, codec, extension, progress):
    # 讀取影片
    cap = cv2.VideoCapture(input_video)
    file_name = input_video.split('/')[-1].split('.')[0]

    # 獲取影片屬性
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    num = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    top, bottom, left, right = int(
        top*height), int(bottom*height), int(left*width), int(right*width)

    # 定義編碼方式
    codecs = {
        "H264": cv2.VideoWriter_fourcc(*"H264"),
        "FFV1": cv2.VideoWriter_fourcc(*"FFV1"),
        "MJPG": cv2.VideoWriter_fourcc(*"MJPG")
    }

    # 計算剪裁後的尺寸
    cropped_width = (right - left)
    cropped_height = (bottom - top)

    # 建立 VideoWriter 物件
    os.makedirs("uploads", exist_ok=True)
    output_path = os.path.join("uploads", file_name + extension)
    out = cv2.VideoWriter(
        output_path, codecs[codec], fps, (cropped_width, cropped_height))

    cnt = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # 剪裁 frame
        cropped_frame = frame[top:bottom, left:right]

        # 寫入 output
        out.write(cropped_frame)

        if cnt % 10 == 0:
            progress(cnt / num, desc="Cropping Video")

        cnt += 1

    cap.release()
    out.release()

    return output_path


def get_meta_from_img_seq(input_img_seq):
    if input_img_seq is None:
        return None, None, None


    # Create dir
    file_name = input_img_seq.name.split('/')[-1].split('.')[0]
    file_path = f'./assets/{file_name}'
    if os.path.isdir(file_path):
        os.system(f'rm -r {file_path}')
    os.makedirs(file_path)
    # Unzip file
    os.system(f'unzip -qo {input_img_seq.name} -d ./assets ')

    imgs_path = sorted([os.path.join(file_path, img_name)
                       for img_name in os.listdir(file_path)])
    first_frame = imgs_path[0]
    first_frame = cv2.imread(first_frame)
    first_frame = cv2.cvtColor(first_frame, cv2.COLOR_BGR2RGB)

    return first_frame, first_frame, "imgs"


def crop_imgs(input_file, left, top, right, bottom, codec, extension, progress):
    # 讀取影片
    file_name = input_file.name.split('/')[-1].split('.')[0]
    file_path = f'./assets/{file_name}'

    imgs_path = sorted([os.path.join(file_path, img_name)
                       for img_name in os.listdir(file_path)])

    first_frame = imgs_path[0]
    first_frame = cv2.imread(first_frame)
    first_frame = cv2.cvtColor(first_frame, cv2.COLOR_BGR2RGB)

    # 獲取影片屬性
    height, width, _ = first_frame.shape
    fps = 30
    num = len(imgs_path)

    top, bottom, left, right = int(
        top*height), int(bottom*height), int(left*width), int(right*width)

    # 定義編碼方式
    codecs = {
        "H264": cv2.VideoWriter_fourcc(*"H264"),
        "FFV1": cv2.VideoWriter_fourcc(*"FFV1"),
        "MJPG": cv2.VideoWriter_fourcc(*"MJPG")
    }

    # 計算剪裁後的尺寸
    cropped_width = (right - left)
    cropped_height = (bottom - top)
    # 建立 VideoWriter 物件
    output_path = os.path.join("uploads", file_name + extension)
    out = cv2.VideoWriter(
        output_path, codecs[codec], fps, (cropped_width, cropped_height))

    for i in range(num):
        frame = imgs_path[i]
        frame = cv2.imread(frame)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # 剪裁 frame
        cropped_frame = frame[top:bottom, left:right]

        # 寫入 output
        out.write(cropped_frame)

        if i % 10 == 0:
            progress(i / num, desc="Cropping Video")

    out.release()

    return output_path
