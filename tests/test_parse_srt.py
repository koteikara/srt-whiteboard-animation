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
    @staticmethod
    def cue(index, start, end, text):
        return {"index": index, "startMs": start, "endMs": end,
                "durMs": end - start, "text": text}

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

    def test_prefers_japanese_sentence_end_near_target(self):
        cues = [
            self.cue(1, 0, 9000, "前半です"),
            self.cue(2, 9000, 18000, "まだ続きます。"),
            self.cue(3, 18000, 29000, "句点なし"),
            self.cue(4, 29000, 38000, "後半です。"),
        ]
        scenes = parse_srt_module.group_scenes(cues, 25, 15, 35)
        self.assertEqual(scenes[0]["cueRange"], [1, 2])

    def test_prefers_long_gap_as_boundary(self):
        cues = [
            self.cue(1, 0, 10000, "説明を続けます"),
            self.cue(2, 10000, 21000, "ここで一息"),
            self.cue(3, 22500, 30000, "次の話題"),
            self.cue(4, 30000, 41000, "終了"),
        ]
        scenes = parse_srt_module.group_scenes(cues, 25, 15, 35)
        self.assertEqual(scenes[0]["cueRange"], [1, 2])

    def test_never_exceeds_max_when_a_boundary_is_available(self):
        cues = [
            self.cue(1, 0, 12000, "一。"),
            self.cue(2, 12000, 24000, "二。"),
            self.cue(3, 24000, 36000, "三。"),
            self.cue(4, 36000, 48000, "四。"),
        ]
        scenes = parse_srt_module.group_scenes(cues, 30, 20, 35)
        self.assertTrue(all(scene["sceneDurationMs"] <= 35000 for scene in scenes))
        self.assertEqual([scene["cueRange"] for scene in scenes], [[1, 2], [3, 4]])

    def test_rejects_inconsistent_duration_options(self):
        with self.assertRaises(ValueError):
            parse_srt_module.group_scenes([], 30, 35, 40)


if __name__ == "__main__":
    unittest.main()
