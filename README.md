# MindPuncher

左右からやってくる敵をパンチで倒し、スコアを競う2Dアクションゲームです。通常・中・大のパンチを使い分け、敵の攻撃をガードしながら120秒間生き残りましょう。

**ブラウザでプレイ:** [MindPuncher を起動する](https://numashark.github.io/MindPuncher/)

## ゲームの特徴

- 歩行・飛行・突進の3種類の敵が登場
- パンチのチャージ時間に応じて、射程や威力の異なるパンチを使用
- 敵を連続で倒してコンボボーナスを獲得
- PC版はローカル、Web版はFirebaseまたはブラウザー内にランキングを保存
- ウィンドウ表示とフルスクリーン表示に対応

## 操作方法

| 操作 | キー |
| --- | --- |
| メニューの選択 | `W` / `S` または `↑` / `↓` |
| メニューの決定・パンチ | `Enter` または `Space` |
| プレイヤーの向きを変える | `A` / `D` または `←` / `→` |
| パンチをチャージ | パンチキーを押し続けて、離す |
| ゲーム中にリトライ | `R` |
| PC版を終了 | `Esc` |

パンチキーを短く押すと通常パンチ、長く押してから離すと中パンチや大パンチになります。チャージ中は前方をガードします。詳しいルールやヒントは、ゲーム内の「あそびかた」をご覧ください。

## PCで実行

PythonとPyxelが必要です。リポジトリのルートディレクトリで実行してください。

```bash
python -m pip install pyxel
python -m pyxel run mind_puncher.py
```

起動時にウィンドウモードまたはフルスクリーンを選択できます。ランキングはPC版ではゲームと同じディレクトリの `ranking.json` に保存されます。

## テスト

```bash
python -m unittest discover -s tests
```

## Web版・ランキング設定

Web版はGitHub Pagesで公開されています。Web版のランキングは、Firebase Realtime DatabaseのURLが設定されている場合はFirebaseに、未設定の場合はブラウザーの `localStorage` に保存されます。

Firebaseランキングを有効にする場合は、Firebaseプロジェクトの設定値を `docs/firebase_config.js` に記入し、Realtime Databaseに `firebase_rules.json` のルールを設定してください。App Checkを使う場合は、同ファイルにreCAPTCHA v3のサイトキーも設定します。Firebaseを利用しない場合は設定値を空のままにできます。

Web版を更新するには、ゲームをPyxelアプリにパッケージ化し、生成した `mind_puncher.pyxapp` を `docs/` に配置して変更を公開します。

```bash
python -m pyxel package . mind_puncher.py
```

`docs/index.html` の動作確認は、リポジトリのルートで次のコマンドを実行し、表示されたローカルURLをブラウザーで開いてください。

```bash
python -m http.server -d docs
```

## 開発資料

- [ゲーム仕様](SPEC.md)
- [Agents.md](Agents.md)
