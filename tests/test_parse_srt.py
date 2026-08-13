import codecs
import importlib.util
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).parents[1] / "scripts" / "parse_srt.py"
SPEC = importlib.util.spec_from_file_location("parse_srt", MODULE_PATH)
parse_srt_module = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(parse_srt_module)


SAMPLE = "1\r\n00:00:00,000 --> 00:00:02,500\r\n日本語の字幕です。\r\n\r\n"


class ReadSrtTests(unittest.TestCase):
    def write_bytes(self, data: bytes) -> Path:
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        path = Path(directory.name) / "日本語 字幕.srt"
        path.write_bytes(data)
        return path

    def test_reads_utf8(self):
        self.assertEqual(parse_srt_module.read_srt(self.write_bytes(SAMPLE.encode("utf-8"))), SAMPLE)

    def test_reads_utf8_bom_without_returning_bom(self):
        path = self.write_bytes(codecs.BOM_UTF8 + SAMPLE.encode("utf-8"))
        self.assertEqual(parse_srt_module.read_srt(path), SAMPLE)

    def test_reads_cp932(self):
        self.assertEqual(parse_srt_module.read_srt(self.write_bytes(SAMPLE.encode("cp932"))), SAMPLE)

    def test_honors_explicit_encoding(self):
        path = self.write_bytes(SAMPLE.encode("cp932"))
        self.assertEqual(parse_srt_module.read_srt(path, "cp932"), SAMPLE)
        with self.assertRaises(UnicodeDecodeError):
            parse_srt_module.read_srt(path, "utf-8")

    def test_rejects_unknown_encoding(self):
        with self.assertRaises(LookupError):
            parse_srt_module.read_srt(self.write_bytes(b"x"), "not-an-encoding")


class ParseSrtTests(unittest.TestCase):
    def test_parses_japanese_and_multiline_text(self):
        cues = parse_srt_module.parse_srt(
            "\ufeff1\n00:00:01,250 --> 00:00:03.500\n一行目です。\n二行目です。\n"
        )
        self.assertEqual(
            cues,
            [{"index": 1, "startMs": 1250, "endMs": 3500, "durMs": 2250,
              "text": "一行目です。 二行目です。"}],
        )

    def test_scene_output_keeps_existing_schema(self):
        cues = parse_srt_module.parse_srt(SAMPLE)
        scenes = parse_srt_module.group_scenes(cues, 30, 25, 35)
        self.assertEqual(
            set(scenes[0]),
            {"sceneIndex", "startMs", "endMs", "sceneDurationMs", "cueRange", "text"},
        )


if __name__ == "__main__":
    unittest.main()
