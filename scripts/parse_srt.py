#!/usr/bin/env python3
"""SRTを解析し、字幕と推奨シーン分割をJSONで出力する。"""
from __future__ import annotations

import argparse
import codecs
import json
import re
import sys
from pathlib import Path

_TIME = re.compile(r"(\d+):(\d{2}):(\d{2})[,.](\d{1,3})")
_SENTENCE_END = re.compile(r"[。！？!?](?:[」』）】〉》〕］”’\"']*)$")
_AUTO_ENCODINGS = ("utf-8-sig", "cp932")


def _to_ms(h: str, m: str, s: str, ms: str) -> int:
    return ((int(h) * 60 + int(m)) * 60 + int(s)) * 1000 + int(ms.ljust(3, "0"))


def read_srt(path: Path, encoding: str | None = None) -> str:
    """SRTを読み込む。未指定時はUTF-8（BOM対応）、CP932の順に試す。"""
    data = path.read_bytes()
    if encoding:
        # Lookupを先に行い、未知の名前とデコード失敗を呼び出し側で区別できるようにする。
        codecs.lookup(encoding)
        return data.decode(encoding)

    for candidate in _AUTO_ENCODINGS:
        try:
            return data.decode(candidate)
        except UnicodeDecodeError:
            pass
    raise UnicodeDecodeError(
        "utf-8/cp932", data, 0, len(data), "UTF-8またはCP932として解釈できません"
    )


def parse_srt(text: str) -> list[dict]:
    """SRT本文を解析して字幕項目の一覧を返す。"""
    text = text.lstrip("\ufeff").replace("\r\n", "\n").replace("\r", "\n")
    blocks = re.split(r"\n\s*\n", text.strip())
    cues: list[dict] = []
    for block in blocks:
        lines = [line for line in block.split("\n") if line.strip()]
        if not lines:
            continue
        time_line_idx = next((i for i, line in enumerate(lines) if "-->" in line), None)
        if time_line_idx is None:
            continue
        times = _TIME.findall(lines[time_line_idx])
        if len(times) < 2:
            continue
        start = _to_ms(*times[0])
        end = _to_ms(*times[1])
        body = " ".join(lines[time_line_idx + 1 :]).strip()
        cues.append(
            {
                "index": len(cues) + 1,
                "startMs": start,
                "endMs": end,
                "durMs": max(0, end - start),
                "text": body,
            }
        )
    return cues


def group_scenes(
    cues: list[dict], target_sec: float, min_sec: float, max_sec: float
) -> list[dict]:
    """日本語の文末と字幕間の無音を考慮してシーンへまとめる。"""
    scenes: list[dict] = []
    target_ms, min_ms, max_ms = target_sec * 1000, min_sec * 1000, max_sec * 1000

    if not (0 <= min_ms <= target_ms <= max_ms):
        raise ValueError("0 <= min_sec <= target_sec <= max_sec となるよう指定してください")
    if not cues:
        return scenes

    def add_scene(bucket: list[dict]) -> None:
        start, end = bucket[0]["startMs"], bucket[-1]["endMs"]
        scenes.append(
            {
                "sceneIndex": len(scenes) + 1,
                "startMs": start,
                "endMs": end,
                "sceneDurationMs": max(0, end - start),
                "cueRange": [bucket[0]["index"], bucket[-1]["index"]],
                "text": " ".join(cue["text"] for cue in bucket).strip(),
            }
        )

    start_idx = 0
    while start_idx < len(cues):
        scene_start = cues[start_idx]["startMs"]
        if cues[-1]["endMs"] - scene_start <= max_ms:
            add_scene(cues[start_idx:])
            break

        candidates: list[tuple[tuple[int, int, float], int]] = []
        last_fitting = start_idx
        for end_idx in range(start_idx, len(cues)):
            span = cues[end_idx]["endMs"] - scene_start
            if span > max_ms:
                break
            last_fitting = end_idx
            if span < min_ms:
                continue

            text = cues[end_idx]["text"].rstrip()
            punctuation = 1 if _SENTENCE_END.search(text) else 0
            gap = 0
            if end_idx + 1 < len(cues):
                gap = max(0, cues[end_idx + 1]["startMs"] - cues[end_idx]["endMs"])
            # 文末、無音、目標時間への近さの順で境界を選ぶ。
            boundary_score = punctuation * 2 + (2 if gap >= 1000 else 1 if gap >= 500 else 0)
            candidates.append(((boundary_score, -abs(span - target_ms), span), end_idx))

        if candidates:
            end_idx = max(candidates, key=lambda item: item[0])[1]
        else:
            # 最短時間に届かなくても、上限を越える前の最後の字幕で切る。
            end_idx = last_fitting
        add_scene(cues[start_idx : end_idx + 1])
        start_idx = end_idx + 1
    return scenes


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="SRT解析とシーン分割案の生成")
    parser.add_argument("srt", help="字幕ファイルのパス（.srt）")
    parser.add_argument(
        "--encoding",
        help="入力文字コード（例: utf-8、utf-8-sig、cp932）。未指定時は自動判定",
    )
    parser.add_argument("--target-sec", type=float, default=30.0, help="目標秒数（既定: 30）")
    parser.add_argument("--min-sec", type=float, default=25.0, help="最短秒数（既定: 25）")
    parser.add_argument("--max-sec", type=float, default=35.0, help="最長秒数（既定: 35）")
    args = parser.parse_args(argv)

    try:
        raw = read_srt(Path(args.srt), args.encoding)
    except LookupError:
        print(f"[エラー] 未対応の文字コード名です: {args.encoding}", file=sys.stderr)
        return 1
    except UnicodeDecodeError:
        specified = f"（指定: {args.encoding}）" if args.encoding else ""
        print(
            f"[エラー] 字幕の文字コードを判定できませんでした{specified}。"
            "UTF-8、UTF-8 BOM付き、またはCP932で保存してください。",
            file=sys.stderr,
        )
        return 1
    except OSError as error:
        print(f"[エラー] 字幕ファイルを読み込めません: {error}", file=sys.stderr)
        return 1

    cues = parse_srt(raw)
    if not cues:
        print("[エラー] 字幕を解析できませんでした。SRT形式を確認してください。", file=sys.stderr)
        return 1
    scenes = group_scenes(cues, args.target_sec, args.min_sec, args.max_sec)

    total_ms = cues[-1]["endMs"] - cues[0]["startMs"]
    print(
        f"字幕数: {len(cues)}  総時間: {total_ms / 1000:.1f}s  推奨シーン数: {len(scenes)}",
        file=sys.stderr,
    )
    for scene in scenes:
        print(
            f"  シーン{scene['sceneIndex']:>2}  "
            f"{scene['startMs'] / 1000:6.1f}-{scene['endMs'] / 1000:6.1f}s "
            f"({scene['sceneDurationMs'] / 1000:4.1f}s, "
            f"字幕{scene['cueRange'][0]}-{scene['cueRange'][1]}): "
            f"{scene['text'][:40]}",
            file=sys.stderr,
        )

    json.dump({"cues": cues, "scenes": scenes}, sys.stdout, ensure_ascii=False, indent=2)
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
