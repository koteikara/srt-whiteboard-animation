# CMS記事作成イントロ 絵コンテ

製品の姿を写しすぎると、研修動画は特定の画面に縛られる。そこで操作の意味は保ちつつ、画面は一般的なカード、入力欄、人物の関係に置き換える。タイトル部分にも白板アニメーションを使い、後半の操作説明へ同じ筆致でつなぐ。

## シーン1　記事が確認へ届くまで

- 時間：`00:00:00,000`〜`00:00:23,000`
- `sceneDurationMs`：`23000`
- 字幕範囲：1〜5
- 核心：記事作成は「作成」「入力」「確認依頼」の三段階で進む。
- 画面主体：中央の記事カード、カードへ伸びる鉛筆、三つの工程を表す簡素な記号、確認を受け取る人物。
- 構図：中央に白い記事カードを置く。左下の鉛筆から記事カードへ動線を作り、カードの右側に三つの小さな工程記号を横一列で配置する。最後の記号から右端の人物へ矢印を伸ばす。各主体の間には広い余白を残す。
- 描画順：記事カード → 鉛筆 → 三つの工程記号 → 確認担当者 → 工程を結ぶ矢印。
- 匿名化：製品名、ロゴ、実在するメニュー、ボタン、画面レイアウトを描かない。記事カード内にも文字を入れない。

### 画像生成プロンプト

16:9 horizontal whiteboard illustration on warm old-paper background #F5EBD7. Extremely simple hand-drawn line art, restrained Notion-like doodle style, dark gray outlines, generous empty space. In the center, a generic blank article card made of a rectangle and a few unlabeled horizontal strokes. At lower left, a simple pencil pointing toward the card. To the right of the card, three small sequential symbols with ample separation: a blank page with a plus sign, a pencil touching two blank input lines, and a small person receiving a check-mark card. Connect the sequence with thin arrows. Use only subtle red, orange, and blue accents, with ink as the dominant appearance. No words, no letters, no numbers, no labels, no logo, no branded interface, no recognizable software UI, no photo, no 3D, no complex background, no high-saturation colors. Keep all subjects fully inside the canvas and separated for automatic region masking.

## シーン2　管理画面での操作

- 時間：`00:00:23,000`〜`00:00:48,000`
- `sceneDurationMs`：`25000`
- 字幕範囲：6〜10
- 核心：管理画面を開き、新規記事を入力・保存して、担当者へ確認を依頼する。
- 画面主体：抽象化した管理画面、記事の追加を示すカード、二つの入力欄、保存を示す小箱、確認担当者。
- 構図：左から右へ操作が流れる。左端に汎用的な管理画面の枠、中央左に追加される記事カード、中央に二つの空欄、中央右に保存を示す小箱、右端に確認担当者を置く。実在製品の画面とは一致しない簡略図にする。
- 描画順：管理画面の外枠 → 管理領域を示す無記名カード → 新しい記事カード → 二つの入力欄 → 確認用の目の記号 → 保存の小箱 → 確認担当者と依頼矢印 → 完了を示すチェック。
- 匿名化：具体的なナビゲーション名、アイコン配置、配色、ボタン文言、URL、ユーザー名を描かない。固有製品のスクリーンショットに見える構図を避ける。

### 画像生成プロンプト

16:9 horizontal whiteboard illustration on warm old-paper background #F5EBD7. Extremely simple hand-drawn line art, restrained Notion-like doodle style, dark gray outlines, generous empty space. Show a left-to-right generic content-management workflow without resembling any real product. At far left, an abstract browser-like frame with a narrow sidebar containing only blank geometric blocks. Next, a blank page card with a plus symbol. In the center, two large empty input rectangles and a small eye symbol for preview. To their right, a simple storage box symbol. At far right, a small neutral person receiving the page card, followed by a check mark. Connect the stages with thin arrows. Use only subtle red, orange, and blue accents. No words, no letters, no numbers, no labels, no logo, no product-specific menu, no recognizable brand layout, no photo, no 3D, no complex background, no high-saturation colors. Keep each subject distinct, fully inside the canvas, and separated by generous gaps for automatic region masking.

## 字幕と画面要素の対応

| 字幕 | 画面上の出来事 |
|---|---|
| 1 | 記事カードの外形が現れる。 |
| 2 | 鉛筆から記事カードへ線が伸び、右側に確認担当者が現れる。 |
| 3 | 三つの工程記号の置き場所が順に現れる。 |
| 4 | 作成、入力、確認依頼に対応する記号が一つずつ完成する。 |
| 5 | 三工程を結ぶ矢印が完成し、操作画面へ視線を渡す。 |
| 6 | 抽象化した管理画面と無記名の管理カードが現れる。 |
| 7 | 新しい記事カードが追加される。 |
| 8 | 二つの入力欄と目の記号が現れる。 |
| 9 | 保存の小箱、確認担当者、依頼矢印が順に現れる。 |
| 10 | 最後のチェックが描かれ、完成状態を0.5秒以上保持する。 |

二幕を並べても、記事カードは同じ比率、人物は同じ簡略度にそろえる。違うのは視点だけである。最初の幕は流れの全体像、後半は手元の操作へ寄る。
