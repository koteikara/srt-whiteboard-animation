#!/usr/bin/env python3
"""
連続筆跡アニメーション - 環境準備スクリプト

役割：
1. Skillディレクトリ内に独立したPython仮想環境を作成します。作成済みの場合は再利用します。
2. 実行に必要な外部ライブラリを読み込めるか確認します。
3. 不足しているライブラリを自動的にインストールします。
4. 呼び出し元が取得できるよう、最終行にENV_PY=<インタープリターのパス>を出力します。

使用方法：
python prepare_env.py          # 環境を作成して依存関係を補い、ENV_PYを出力
python prepare_env.py --check  # 確認のみ。不足があれば0以外の終了コードを返す
"""
from __future__ import annotations

import os
import subprocess
import sys
import venv
from pathlib import Path

# skill 根目录 = 本脚本向上两级
SKILL_ROOT = Path(__file__).resolve().parent.parent
VENV_ROOT = SKILL_ROOT / ".venv"

# 解释器导入名 -> pip 安装名
DEPS: dict[str, str] = {
    "cv2": "opencv-python",
    "numpy": "numpy",
    "av": "av",  # PyAV：纯 pip 安装的 H.264 编码，无需系统 ffmpeg
    "PIL": "Pillow",  # render_annotation_preview.py 画区域编号预览图（含中文标签）
}


def interpreter_path() -> Path:
    """虚拟环境里的 python 可执行文件位置（跨平台）。"""
    if sys.platform.startswith("win"):
        return VENV_ROOT / "Scripts" / "python.exe"
    return VENV_ROOT / "bin" / "python"


def ensure_venv(check_only: bool) -> Path:
    py = interpreter_path()
    if VENV_ROOT.exists() and py.exists():
        print(f"[OK] 既存の仮想環境を再利用します：{VENV_ROOT}")
        return py

    if check_only:
        print(f"[エラー] 仮想環境がまだ作成されていません：{VENV_ROOT}")
        sys.exit(1)

    print(f"[..] 仮想環境を作成しています：{VENV_ROOT}")
    venv.create(str(VENV_ROOT), with_pip=True)
    print("[OK] 仮想環境の準備ができました")
    return py


def can_import(py: Path, import_name: str) -> bool:
    probe = subprocess.run(
        [str(py), "-c", f"import {import_name}"],
        capture_output=True,
    )
    return probe.returncode == 0


def install(py: Path, packages: list[str]) -> bool:
    if not packages:
        return True
    print(f"[..] 依存関係をインストールしています：{', '.join(packages)}")
    res = subprocess.run(
        [str(py), "-m", "pip", "install", "--quiet", *packages],
        capture_output=True,
        text=True,
    )
    if res.returncode != 0:
        print(f"[エラー] インストールに失敗しました：\n{res.stderr}")
        return False
    print("[OK] 依存関係のインストールが完了しました")
    return True


def main() -> None:
    check_only = "--check" in sys.argv

    py = ensure_venv(check_only)

    missing: list[str] = []
    for import_name, pip_name in DEPS.items():
        if can_import(py, import_name):
            print(f"[ok] {pip_name}")
        else:
            print(f"[miss] {pip_name}")
            missing.append(pip_name)

    if missing:
        if check_only:
            print(f"\n不足している依存関係は{len(missing)}件です：{', '.join(missing)}")
            sys.exit(1)
        if not install(py, missing):
            sys.exit(1)

    # 末行：供调用方捕获的约定输出
    print(f"\nENV_PY={py}")


if __name__ == "__main__":
    main()
