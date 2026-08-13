# SRT白板アニメーション Skill（日本語版）

SRT字幕を、物語の順序に沿って描かれる白板手描き動画へ変換するCodex Skillです。領域マスクで要素の登場順を制御し、各領域では筆先が連続して線を描いた後、色を加えます。完成した幕はMP4として書き出せます。

このリポジトリは[geeklee/srt-whiteboard-animation](https://github.com/geeklee/srt-whiteboard-animation)を日本語対応したフォークです。原作者の著作権表示とMIT Licenseは[LICENSE](LICENSE)に記載しています。

## できること

- SRTを解析し、25〜35秒を目安に幕を分ける
- 字幕の出来事に基づいて絵コンテと画面構成案を作る
- 画像内の領域、順序、時刻、対応字幕をJSONで管理する
- ブラウザー上のプレビューで領域と時間を調整する
- 線画から彩色へ進む連続筆跡でMP4を生成する
- 複数の幕を1本の動画へ結合する

## 作業の流れ

字幕解析、線画、注釈、確認画像、最終注釈、各幕の動画、結合動画の順に作ります。各工程の完了後は必ず確認を挟みます。詳しい制約は[SKILL.md](SKILL.md)を参照してください。

![SRT白板アニメーションの例](examples/scene-01-monkey-mountain-stream.gif)

元の線画は[こちら](examples/scene-01-monkey-mountain.png)です。

## 動作環境

Python環境と依存パッケージをSkill内の`.venv`へ用意します。

```bash
python scripts/prepare_env.py --check
python scripts/prepare_env.py
```

確認コマンドの最終行に表示される`ENV_PY=<パス>`を、レンダリングと結合で使います。

## 基本コマンド

字幕を解析します。

```bash
python scripts/parse_srt.py <字幕.srt> --target-sec 30 --min-sec 25 --max-sec 35
```

領域確認画像を作ります。

```bash
python scripts/render_annotation_preview.py <画像> <注釈JSON> <出力画像>
```

`assets/preview.html`をChromeまたはEdgeで開き、「フォルダーを開く」から画像と同名の注釈JSONがあるフォルダーを選ぶと、領域、順序、時刻、字幕を調整できます。

各幕をレンダリングします。

```bash
<ENV_PY> scripts/render_stream_whiteboard.py <画像> <注釈JSON> <出力.mp4> assets/drawing-hand.png \
  --ink-path grid --color-fill contour-wipe
```

複数の幕を結合します。

```bash
<ENV_PY> scripts/merge_scenes.py --inputs 幕1.mp4 幕2.mp4 幕3.mp4 --output final.mp4
```

## ファイル配置

```text
assets/whiteboard/<プロジェクト名>/
├── scene-01-<名前>.png
├── scene-01-<名前>.annotation.json
├── scene-01-<名前>-whiteboard.mp4
└── scene-01-<名前>-preview.mp4
```

画像と注釈JSONは同じ基底名にしてください。たとえば`scene-01-demo.png`には`scene-01-demo.annotation.json`を対応させます。

## 表現上の基準

背景には暖かなベージュ`#F5EBD7`、線には濃い灰色を使います。赤、橙、青は控えめな差し色に限ります。場面画像には文字、写真表現、3D表現、複雑な背景を入れません。

重なった対象は`protectedRegions`で保護し、後から描く内容が先に見えないようにします。完成画面は各幕の末尾で0.5秒以上保持します。

## ライセンスと原作者

MIT Licenseで公開されています。著作権表示は次のとおりです。

`Copyright (c) 2026 江哥是老登啊`

原作者プロフィール：一个爱养鱼的老登 / AI Builder / 用 AI 团队打造一人公司

原作者の発信先：抖音、B站、公众号「江哥是老登啊」
