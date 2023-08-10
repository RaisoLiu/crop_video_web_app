import os
import cv2
import gradio as gr


def process_video(input_video, input_img_seq, input_file_type, left, right, top, bottom, output_codec, output_format, progress=gr.Progress()):
    cropped_video_path = ""

    if input_file_type == "video":
        cropped_video_path = crop_video(input_video, left, right, top, bottom, output_codec, output_format, progress)
    if input_file_type == "imgs":
        cropped_video_path = crop_imgs(input_img_seq, left, right, top, bottom, output_codec, output_format, progress)

    return cropped_video_path


def get_meta_from_video(input_video):
    if input_video is None:
        return None, None, None

    cap = cv2.VideoCapture(input_video)

    _, first_frame = cap.read()
    cap.release()

    first_frame = cv2.cvtColor(first_frame, cv2.COLOR_BGR2RGB)
    return first_frame, first_frame, "video"


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


def crop_frame(origin_frist_frame, left, right, top, bottom):
    if not check_bounds(left, right, top, bottom):
        gr.Error("[E] Bounding out of range")
        return None

    height, width, _ = origin_frist_frame.shape

    left, right = int(left*width), int(right*width)
    top, bottom = int(top*height), int(bottom*height)
    return origin_frist_frame[top:bottom, left:right]


def check_bounds(left, right, top, bottom):
    if any(val is None for val in [left, right, top, bottom]):
        return False
    if not (0 <= left < right <= 1) or not (0 <= top < bottom <= 1):
        return False
    return True


def get_codec(codec):
    codecs = {
        "MP4V": cv2.VideoWriter_fourcc(*"mp4v"),
        "H264": cv2.VideoWriter_fourcc(*"h264"),
        "AVC1": cv2.VideoWriter_fourcc(*"avc1"),
        "FFV1": cv2.VideoWriter_fourcc(*"FFV1"),
        "MJPG": cv2.VideoWriter_fourcc(*"MJPG")
    }
    return codecs.get(codec)


def process_frames(frames, left, right, top, bottom, codec, extension, progress):
    # Calculate cropped dimensions
    height, width, _ = frames[0].shape
    left, right = int(left*width), int(right*width)
    top, bottom = int(top*height), int(bottom*height)
    cropped_width, cropped_height = right - left, bottom - top

    # Prepare VideoWriter
    os.makedirs("uploads", exist_ok=True)
    file_name = frames[0].name.split(
        '/')[-1].split('.')[0] if hasattr(frames[0], 'name') else "output"
    output_path = os.path.join("uploads", file_name + extension)
    out = cv2.VideoWriter(output_path, get_codec(
        codec), 30, (cropped_width, cropped_height))

    # Process frames
    for i, frame in enumerate(frames):
        cropped_frame = frame[top:bottom, left:right]
        out.write(cropped_frame)
        if i % 10 == 0:
            progress(i / len(frames), desc="Cropping Video")
    out.release()
    return output_path


def crop_video(input_video, left, right, top, bottom, codec, extension, progress):
    cap = cv2.VideoCapture(input_video)
    frames = [cap.read()[1]
              for _ in range(int(cap.get(cv2.CAP_PROP_FRAME_COUNT)))]
    return process_frames(frames, left, right, top, bottom, codec, extension, progress)


def crop_imgs(input_file, left, right, top, bottom, codec, extension, progress):
    file_path = f'./assets/{input_file.name.split("/")[-1].split(".")[0]}'
    img_paths = sorted([os.path.join(file_path, img_name)
                       for img_name in os.listdir(file_path)])
    frames = [cv2.cvtColor(cv2.imread(img_path), cv2.COLOR_BGR2RGB)
              for img_path in img_paths]
    return process_frames(frames, left, right, top, bottom, codec, extension, progress)
