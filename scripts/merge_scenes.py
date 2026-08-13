#!/usr/bin/env python3
"""
複数シーンの結合：各シーンのホワイトボードアニメーションMP4を、指定順にカット結合して1本の動画にします。

システムのffmpegが利用できる場合は、再エンコードせずにロスレス結合（-c copy）します。
映像ごとのサイズやコーデックが異なる場合、またはffmpegがない場合は、PyAVでフレーム単位に再エンコードし、最初の映像に合わせて拡大縮小と余白追加を行います。元の映像は残ります。

使用方法：
  <ENV_PY> merge_scenes.py --inputs a.mp4 b.mp4 c.mp4 --output final.mp4
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def _ffmpeg_concat_copy(inputs: list[Path], output: Path) -> bool:
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg is None:
        return False
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8") as f:
        for p in inputs:
            f.write(f"file '{p.resolve().as_posix()}'\n")
        list_path = Path(f.name)
    try:
        res = subprocess.run(
            [ffmpeg, "-y", "-loglevel", "error", "-f", "concat", "-safe", "0",
             "-i", str(list_path), "-c", "copy", str(output)],
            capture_output=True, text=True,
        )
        if res.returncode == 0:
            print(f"  ffmpegによるロスレス結合が完了しました：{output}")
            return True
        print(f"  [警告] ffmpeg -c copyに失敗したため、再エンコードを試します：{res.stderr.strip()[:200]}")
        res = subprocess.run(
            [ffmpeg, "-y", "-loglevel", "error", "-f", "concat", "-safe", "0",
             "-i", str(list_path), "-c:v", "libx264", "-crf", "20",
             "-pix_fmt", "yuv420p", "-vf", "scale='trunc(iw/2)*2':'trunc(ih/2)*2'", str(output)],
            capture_output=True, text=True,
        )
        if res.returncode == 0:
            print(f"  ffmpegによる再エンコード結合が完了しました：{output}")
            return True
        print(f"  [警告] ffmpegによる再エンコード結合にも失敗しました：{res.stderr.strip()[:200]}")
        return False
    finally:
        list_path.unlink(missing_ok=True)


def _pyav_concat(inputs: list[Path], output: Path) -> bool:
    try:
        import av
    except ImportError:
        return False
    import numpy as np  # noqa: F401
    first = av.open(str(inputs[0]))
    vs = first.streams.video[0]
    w, h = vs.codec_context.width, vs.codec_context.height
    rate = vs.average_rate
    first.close()

    out = av.open(str(output), mode="w")
    ostream = out.add_stream("h264", rate=rate)
    ostream.width, ostream.height = w, h
    ostream.pix_fmt = "yuv420p"
    ostream.options = {"crf": "24", "preset": "medium"}
    for p in inputs:
        cont = av.open(str(p))
        for frame in cont.decode(video=0):
            if frame.width != w or frame.height != h:
                frame = frame.reformat(width=w, height=h)
            for pkt in ostream.encode(frame):
                out.mux(pkt)
        cont.close()
    for pkt in ostream.encode(None):
        out.mux(pkt)
    out.close()
    print(f"  PyAVによる結合が完了しました：{output}")
    return True


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="複数のホワイトボードアニメーションMP4を指定順に結合します")
    p.add_argument("--inputs", nargs="+", required=True, help="再生順に並べたMP4ファイルの一覧")
    p.add_argument("--output", required=True, help="結合後の出力先")
    args = p.parse_args(argv)

    inputs = [Path(x) for x in args.inputs]
    missing = [str(x) for x in inputs if not x.exists()]
    if missing:
        print(f"[エラー] 入力ファイルが見つかりません：{', '.join(missing)}", file=sys.stderr)
        return 1
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)

    if _ffmpeg_concat_copy(inputs, output) or _pyav_concat(inputs, output):
        print(f"OUTPUT={output.resolve()}")
        return 0
    print("[エラー] 結合できませんでした：ffmpegとPyAVのどちらも利用できません", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
