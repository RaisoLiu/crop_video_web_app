import cv2
import os
from tqdm import tqdm

def process_video(input_video, left_bound, upper_bound, right_bound, buttom_bound,output_codec, output_format):
    # 調用 video_processor.py 中的函數處理影片
    print(input_video, left_bound)
    cropped_video_path = crop_video(input_video, left_bound, upper_bound, right_bound, buttom_bound,output_codec, output_format)
    
    # 回傳結果
    return cropped_video_path

def crop_frame(origin_frist_frame, left_bound, upper_bound, right_bound, buttom_bound):
    h, w, _ = origin_frist_frame.shape
    
    if left_bound < 0 or left_bound >= right_bound or right_bound > 1:
        print("[E] left_bound or right_bound")
        return None
    if upper_bound < 0 and upper_bound >= buttom_bound and buttom_bound > 1:
        print("[E] upper_bound or buttom_bound")
        return None


    left_bound, upper_bound, right_bound, buttom_bound = int(left_bound*w), int(upper_bound*h), int(right_bound*w), int(buttom_bound*h)
    return origin_frist_frame[upper_bound:buttom_bound, left_bound:right_bound]

def get_meta_from_video(input_video):
    if input_video is None:
        return None, None
    
    cap = cv2.VideoCapture(input_video)
    
    _, first_frame = cap.read()
    cap.release()

    first_frame = cv2.cvtColor(first_frame, cv2.COLOR_BGR2RGB)
    return first_frame, first_frame

def crop_video(input_video, left, top, right, bottom, codec, extension):
    # 讀取影片
    cap = cv2.VideoCapture(input_video)
    
    # 獲取影片屬性
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))


    top, bottom, left, right = int(top*height), int(bottom*height), int(left*width), int(right*width)


    print(width,height,fps)
    print("=====")
    
    # 定義編碼方式
    codecs = {
        "H264": cv2.VideoWriter_fourcc(*"H264"),
        "FFV1": cv2.VideoWriter_fourcc(*"FFV1"),
        "MJPG": cv2.VideoWriter_fourcc(*"MJPG")
    }
    
    # 計算剪裁後的尺寸
    cropped_width = (right - left)
    cropped_height = (bottom - top)
    print(cropped_width, cropped_height)
    # 建立 VideoWriter 物件
    output_path = os.path.join("uploads", "cropped_video" + extension)
    out = cv2.VideoWriter(output_path, codecs[codec], fps, (cropped_width, cropped_height))
    

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # 剪裁 frame
        cropped_frame = frame[top:bottom, left:right]

        # 寫入 output
        out.write(cropped_frame)

    cap.release()
    out.release()
    
    return output_path

# if __name__ == "__main__":
#     # 這是一個測試，您可以根據需要調整
#     crop_video("example.mp4", 10, 490, 10, 490, "H264", ".mp4")
