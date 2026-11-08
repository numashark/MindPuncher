# MindPuncher
左右から来る敵をパンチで倒してスコアを稼ぐ2Dアクションゲーム。
ゲーム仕様は SPEC.md に記載している。実装は必ず SPEC.md に従うこと。

## 技術スタック
- 言語: Python
- ゲームエンジン: Pyxel
- フレームレート: 60FPS（仕様中の「フレーム」はすべて60FPS基準）
- フォント: x10y12pxDonguriDuel（漢字は入っていないので、画面に出す文字には基本的に漢字を使わない）

## 実行・ビルド・テスト
コマンドはすべて `mind_puncher/` の1つ上のディレクトリで実行する（`pyxel` コマンドはPATHに無いので `python -m pyxel` を使う）。
- 実行: `python -m pyxel run mind_puncher/mind_puncher.py`
- ビルド: `python -m pyxel package mind_puncher mind_puncher/mind_puncher.py`（`mind_puncher.pyxapp` ができる）
- テスト: `python -m unittest discover -s mind_puncher/tests -t mind_puncher`
- Web版（github.io）の更新: ビルドしてできた `mind_puncher.pyxapp` を `mind_puncher/docs/` にコピーしてコミットする（GitHub Pages は main ブランチの `/docs` フォルダを公開する設定にする）
  - 手元の `ranking.json` などgit管理外のファイルが入らないよう、`git archive HEAD` で取り出したフォルダ（名前は `mind_puncher`）でビルドする
- Web版をローカルで確認: `python -m http.server -d mind_puncher/docs` を実行してブラウザで http://localhost:8000 を開く
- 仕様を1つ実装・追加するたびに、ビルドとテストを実行して成功を確認すること
- テストが失敗した場合は、修正してから次の仕様に進むこと

## ディレクトリ構成
- `mind_puncher/` 直下に `mind_puncher.py`（エントリポイント）、`Agents.md`、`SPEC.md` を置く
- 機能ごとにファイルを分け、`mind_puncher.py` から呼び出す
- 現在の構成:
  - `mind_puncher.py`: エントリポイント、画面の切り替え
  - `screen_mode.py`: 起動時のウィンドウ/フルスクリーン選択（PC版はダイアログ、Web版は起動ページで選ばれたモード）、DPI対応（表示スケールで画面端が欠けるのを防ぐ）、Web版かどうかの判定
  - `constants.py`: 定数（調整用の仮の値もここにまとめる）
  - `controls.py`: キー入力
  - `player.py`: プレイヤー（振り向き、チャージ、ガード、HP、スタミナ）
  - `punch.py`: パンチの種類と射程の判定
  - `enemy.py`: 敵キャラ（歩く敵、飛行する敵、突進する敵）
  - `spawner.py`: 敵の出現管理
  - `combat.py`: パンチの命中、吹き飛び、敵の攻撃、敵を倒したときの処理
  - `score.py`: スコアとコンボ
  - `game.py`: 1プレイ分の進行（ヒットストップ、時間切れ、ゲームオーバー）
  - `effects.py`: ヒットエフェクト
  - `render.py`: 背景、プレイヤー、敵の描画
  - `hud.py`: HPバー、スタミナバー、射程表示、画面の縁の点滅
  - `text.py`: フォントの読み込みと文字描画
  - `ranking.py`: ランキングの並べ替え・登録、ファイルやJSONとの変換
  - `ranking_store.py`: ランキングの保存先（PC版はファイル、Web版はFirebase Realtime Database、URL未設定のWeb版はlocalStorage）
  - `firebase_rules.json`: Web版のランキング用データベースに設定するセキュリティルール
  - `docs/`: Web版（github.io）の起動ページ（index.html）、Firebaseの設定（firebase_config.js）、公開用の `mind_puncher.pyxapp`
  - `scenes/`: タイトル、あそびかた、ランキング、ゲーム、スコア確認の各画面
  - `assets/`: フォント（x10y12pxDonguriDuel.ttf）
  - `tests/`: テストコード（描画以外のゲームロジックを確認する）
- ゲームロジック（player, punch, enemy, combat, game など）からは描画やキー入力を呼ばず、テストできる形を保つ
- ブラウザでしか使えないモジュール（`js`）とPC版でしか使えないモジュール（`tkinter`、`ctypes`）は関数の中で読み込み、どちらの環境でもimportだけで失敗しないようにする

## git規約
branchは機能ごとにdevelopから`stamina`や`enemy`などのように切り替えて作業、pushし、developへのプルリクエストまでを行う
commitは一つの修正要件、機能要件ごとに行う
人間が動作を確認してからdevelopへのマージを行うのでどのブランチでどのように作業したから報告すること

## コーディング規約
- 定数は大文字のスネークケースで書く（例: `MAX_HP`、`NORMAL_PUNCH_STAMINA`）
- コメントは日本語で書く
- コメントを書くのは次の2つだけ
  - 関数の説明
  - パラメーターとして調整する定数の説明

## 作業ルール
- 仕様にない機能は勝手に追加しない
- 仕様の不明点は、推測で実装せず必ず質問する
