import importlib.util
import tempfile
import unittest
from fractions import Fraction
from pathlib import Path
from unittest import mock


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "merge_scenes.py"
SPEC = importlib.util.spec_from_file_location("merge_scenes", SCRIPT)
merge_scenes = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(merge_scenes)


try:
    import av
    import numpy as np
except ImportError:  # pragma: no cover - dependency is optional
    av = None
    np = None


@unittest.skipIf(av is None, "PyAV is not installed")
class PyAvConcatTests(unittest.TestCase):
    def _make_video(self, path: Path, frames: int = 6, rate: int = 12) -> None:
        output = av.open(str(path), mode="w")
        stream = output.add_stream("h264", rate=rate)
        stream.width = 64
        stream.height = 48
        stream.pix_fmt = "yuv420p"
        for index in range(frames):
            pixels = np.full((48, 64, 3), index * 20, dtype=np.uint8)
            frame = av.VideoFrame.from_ndarray(pixels, format="rgb24")
            frame.pts = index
            frame.time_base = Fraction(1, rate)
            for packet in stream.encode(frame):
                output.mux(packet)
        for packet in stream.encode(None):
            output.mux(packet)
        output.close()

    def test_main_concatenates_with_pyav_when_ffmpeg_is_unavailable(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "scene.mp4"
            merged = root / "merged.mp4"
            self._make_video(source)

            with mock.patch.object(merge_scenes.shutil, "which", return_value=None):
                result = merge_scenes.main([
                    "--inputs", str(source), str(source), "--output", str(merged)
                ])

            self.assertEqual(result, 0)
            self.assertTrue(merged.exists())
            container = av.open(str(merged))
            stream = container.streams.video[0]
            decoded = list(container.decode(video=0))
            duration = float(stream.duration * stream.time_base)
            container.close()

            self.assertEqual(len(decoded), 12)
            self.assertGreaterEqual(duration, 0.9)


if __name__ == "__main__":
    unittest.main()
