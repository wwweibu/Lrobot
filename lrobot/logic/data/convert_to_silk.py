# 音频格式转换
import os
import av
import pilk


# TODO
def to_pcm(in_path: str) -> tuple[str, int]:
    """任意媒体文件转 pcm"""
    out_path = os.path.splitext(in_path)[0] + ".pcm"
    with av.open(in_path) as in_container:
        in_stream = in_container.streams.audio[0]
        sample_rate = in_stream.codec_context.sample_rate
        with av.open(out_path, "w", "s16le") as out_container:
            out_stream = out_container.add_stream(
                "pcm_s16le", rate=sample_rate, layout="mono"
            )
            try:
                for frame in in_container.decode(in_stream):
                    frame.pts = None
                    for packet in out_stream.encode(frame):
                        out_container.mux(packet)
            except:
                pass
    return out_path, sample_rate


def convert_to_silk(media_path: str) -> str:
    """任意媒体文件转 silk, 返回silk路径"""
    pcm_path, sample_rate = to_pcm(media_path)
    silk_path = os.path.splitext(pcm_path)[0] + ".silk"
    pilk.encode(pcm_path, silk_path, pcm_rate=sample_rate, tencent=True)
    os.remove(pcm_path)
    return silk_path


# 示例函数
# convert_to_silk("storage/file/firefly/1.mp3")
