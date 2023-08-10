import gradio as gr
import cv2
import os
from media_processor import get_meta_from_video, crop_frame, process_video, get_meta_from_img_seq


def clean_temp():
    os.system(f'rm -r ./assets/*')
    os.system(f'rm ./uploads/*')

    return None, None


# 定義 Gradio 的介面
app = gr.Blocks()
with app:
    # Variable
    origin_frist_frame = gr.State(None)
    input_file_type = gr.State(None)
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
            with gr.Tab(label="Video type input"):
                input_video = gr.Video(label='Input video', height=550)
            with gr.Tab(label="Image-Seq type input"):
                input_img_seq = gr.File(label='Input Image-Seq', height=550)

            with gr.Row():
                left_bound = gr.Slider(label="左邊界",
                                       minimum=0, step=0.05, maximum=1,
                                       value=0., interactive=True)
                right_bound = gr.Slider(label="右邊界",
                                        minimum=0, step=0.05, maximum=1,
                                        value=1., interactive=True)

            with gr.Row():
                upper_bound = gr.Slider(label="上邊界",
                                        minimum=0, step=0.05, maximum=1,
                                        value=0., interactive=True)
                bottom_bound = gr.Slider(label="下邊界",
                                         minimum=0, step=0.05, maximum=1,
                                         value=1., interactive=True)
            with gr.Row():
                output_codec = gr.Dropdown(
                    choices=["MP4V", "AVC1", "FFV1", "MJPG"], label="編碼選擇", value="AVC1", interactive=True)
                output_format = gr.Dropdown(
                    choices=[".mp4", ".avi"], label="檔案副檔名", value=".mp4", interactive=True)

        with gr.Column(scale=0.5):
            result_frame = gr.Image(
                label='Crop result of first frame', height=550)

            output_btn = gr.Button("Processing video", interactive=True)

            output_file = gr.File(label="Download processed video")
            clean_btn = gr.Button("Clean temporary files", interactive=True)

    # Back-end
    input_video.change(
        fn=get_meta_from_video,
        inputs=[
            input_video,
        ],
        outputs=[
            origin_frist_frame, result_frame, input_file_type
        ]
    )

    input_img_seq.change(
        fn=get_meta_from_img_seq,
        inputs=[
            input_img_seq,
        ],
        outputs=[
            origin_frist_frame, result_frame, input_file_type
        ]
    )

    for it in [result_frame, left_bound, right_bound, upper_bound, bottom_bound]:
        it.change(
            fn=crop_frame,
            inputs=[
                origin_frist_frame, left_bound, right_bound, upper_bound, bottom_bound
            ],
            outputs=[
                result_frame
            ]
        )

    output_btn.click(
        fn=process_video,
        inputs=[
            input_video, input_img_seq, input_file_type, left_bound, right_bound, upper_bound, bottom_bound, output_codec, output_format,
        ],
        outputs=[
            output_file
        ]
    )

    clean_btn.click(
        fn=clean_temp,
        outputs=[
            input_file_type, origin_frist_frame
        ]
    )


if __name__ == "__main__":
    app.queue(concurrency_count=5)
    app.launch(debug=True, enable_queue=True, share=False,
               server_name="0.0.0.0", server_port=10001)
