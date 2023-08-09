import gradio as gr
import cv2
import os
from media_processor import get_meta_from_video, crop_frame, process_video



# 定義 Gradio 的介面
app = gr.Blocks()
with app:
    # Variable
    origin_frist_frame = gr.State(None)
    gr.Markdown(
                '''
                <div style="text-align:center;">
                    <span style="font-size:3em; font-weight:bold;">Crop fix position video</span>
                </div>
                '''
            )

    # Front-end
    with gr.Row():

        with gr.Column(scale=0.5):
            input_video = gr.Video(label='Input video',height=550)
            with gr.Row():
                left_bound = gr.Slider(label = "左邊界",
                                    minimum= 0,step=0.05,maximum=1,
                                        value=0.1,interactive=True)
                upper_bound = gr.Slider(label = "上邊界",
                                        minimum= 0,step=0.05,maximum=1,
                                        value=0.1,interactive=True)
            with gr.Row():
                right_bound = gr.Slider(label = "右邊界",
                                        minimum= 0,step=0.05,maximum=1,
                                        value=0.9,interactive=True)
                buttom_bound = gr.Slider(label = "下邊界",
                                        minimum= 0,step=0.05,maximum=1,
                                        value=0.9,interactive=True)
            with gr.Row():
                output_codec = gr.Dropdown(choices=["H264", "FFV1", "MJPG"], label="編碼選擇",value="H264", interactive=True)
                output_format = gr.Dropdown(choices=[".mp4", ".avi"], label="檔案副檔名", value=".mp4", interactive=True)

        with gr.Column(scale=0.5):
            result_frame = gr.Image(label='Crop result of first frame',interactive=True, height=550)
            output_btn = gr.Button("Export Crop Video", interactive=True)
            output_file = gr.File(label="下載剪裁後的影片")

    # Back-end
    input_video.change(
        fn=get_meta_from_video,
        inputs=[
            input_video,
        ],
        outputs=[
            origin_frist_frame, result_frame
        ]
    )

    for it in [result_frame,left_bound,upper_bound, right_bound,buttom_bound]:
        it.change(
            fn=crop_frame,
            inputs=[
                origin_frist_frame, left_bound, upper_bound, right_bound, buttom_bound
            ],
            outputs=[
                result_frame
            ]
        )
        
    output_btn.click(
        fn=process_video,
        inputs=[
            input_video, left_bound, upper_bound, right_bound, buttom_bound, output_codec, output_format,
        ],
        outputs=[
            output_file
        ]    
    )

    
if __name__ == "__main__":
    app.queue(concurrency_count=5)
    app.launch(debug=True, enable_queue=True, share=False)