# YouTube Importer

YouTube動画から音声をダウンロードし、Whisperを使用して文字起こしを行うPythonツールです。文字起こし結果はブログ記事生成用のプロンプトテンプレート付きで保存されます。

## 機能

- YouTube動画から音声のみをダウンロード
- OpenAI Whisperを使用した日本語音声の文字起こし
- 動画のメタデータ（タイトル、チャンネル名、長さ、概要）の取得
- 文字起こし結果の自動保存（最大5件まで保持）
- ブログ記事生成用のプロンプトテンプレート付き出力

## 必要な環境

- Python 3.8以上
- FFmpeg（yt-dlpで必要）

### FFmpegのインストール

**macOS:**
```bash
brew install ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**Windows:**
[FFmpeg公式サイト](https://ffmpeg.org/download.html)からダウンロードしてインストールしてください。

## インストール

1. プロジェクトのディレクトリに移動します。

2. 依存パッケージをインストールします：
```bash
pip install -r requirements.txt
```

## 使い方

このツールは、**Cookieファイルなし** で動作する前提になっています。
一部の厳しく保護された動画ではボット検出により失敗する場合がありますが、
その場合は別の動画URLで試してください。

### 1. YouTube URLの設定

**方法1: main.pyで直接設定（推奨）**

`main.py`を開き、`YOUTUBE_URL`変数に文字起こししたいYouTube動画のURLを設定します：

```python
YOUTUBE_URL = "https://www.youtube.com/watch?v=..."
```

**方法2: 環境変数で設定**

環境変数`YOUTUBE_URL`を設定します：

```bash
export YOUTUBE_URL="https://www.youtube.com/watch?v=..."
```

環境変数が設定されている場合は、環境変数が優先されます。

### 2. スクリプトの実行

```bash
python main.py
```

### 3. 結果の確認

文字起こし結果は`transcripts/`ディレクトリに保存されます。ファイル名は`transcript_YYYYMMDD_HHMMSS.txt`の形式です。

## 出力ファイルの内容

保存される文字起こしファイルには以下の内容が含まれます：

- ブログ記事生成用のプロンプトテンプレート
- 動画のメタ情報（タイトル、チャンネル名、URL、長さ、概要）
- 文字起こしテキスト

## プロジェクト構成

```
YouTube Importer/
├── main.py                 # メインスクリプト（URLを設定して実行）
├── youtube_downloader.py   # YouTube音声ダウンロード機能
├── whisper_runner.py       # Whisper文字起こし機能
├── requirements.txt        # 依存パッケージ一覧
├── transcripts/            # 文字起こし結果保存ディレクトリ
└── tmp/                    # 一時ファイル保存ディレクトリ
```

## 依存パッケージ

- `yt-dlp`: YouTube動画のダウンロード
- `openai-whisper`: 音声認識・文字起こし
- `numpy`: Whisperの依存パッケージ

## 注意事項

- 初回実行時、Whisperモデル（`small`）のダウンロードに時間がかかります
- 文字起こし結果は最大5件まで保持され、それ以上は古いファイルから自動削除されます
- ダウンロードした音声ファイルは文字起こし完了後に自動削除されます

### YouTubeのボット検出について

- **特定の動画が制限されている場合**: 一部の動画は特に厳しく保護されており、ボット検出に引っかかりやすい場合があります。その場合は、別の動画URLで試してください。
- **エラーが発生した場合**: Androidクライアント設定でアクセスを試みますが、それでも失敗する場合は、その動画がダウンロードできない可能性があります。

## カスタマイズ

### Whisperモデルの変更

`whisper_runner.py`の`_get_model()`関数内でモデルサイズを変更できます：

```python
_model = whisper.load_model("small")  # tiny, base, small, medium, large
```

モデルサイズが大きいほど精度が上がりますが、処理時間とメモリ使用量が増加します。

### 保存ファイル数の変更

`main.py`の以下の部分で保存ファイル数を変更できます：

```python
while len(existing) >= 5:  # この数値を変更
```

## ライセンス

このプロジェクトのライセンス情報は各依存パッケージのライセンスに従います。

