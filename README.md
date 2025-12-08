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
1. [FFmpeg公式サイト](https://ffmpeg.org/download.html)からWindows用のビルドをダウンロードします（[直接リンク: gyan.dev](https://www.gyan.dev/ffmpeg/builds/)）
2. ダウンロードしたZIPファイルを解凍します
3. 解凍したフォルダ内の`bin`フォルダのパス（例: `C:\ffmpeg\bin`）を環境変数`PATH`に追加します
   - 「システムのプロパティ」→「環境変数」→「システム環境変数」の`Path`を編集
   - 新しい行を追加して`bin`フォルダのパスを入力
4. コマンドプロンプトまたはPowerShellを再起動し、`ffmpeg -version`でインストールを確認します

## インストール

1. プロジェクトのディレクトリに移動します。

   **macOS/Linux:**
   ```bash
   cd "YouTube Importer"
   ```

   **Windows:**
   ```cmd
   cd "YouTube Importer"
   ```

2. 依存パッケージをインストールします：
```bash
pip install -r requirements.txt
```

   **注意:** Windowsで`pip`コマンドが見つからない場合は、`python -m pip install -r requirements.txt`を使用してください。

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

**macOS/Linux:**
```bash
export YOUTUBE_URL="https://www.youtube.com/watch?v=..."
```

**Windows (コマンドプロンプト):**
```cmd
set YOUTUBE_URL=https://www.youtube.com/watch?v=...
```

**Windows (PowerShell):**
```powershell
$env:YOUTUBE_URL="https://www.youtube.com/watch?v=..."
```

環境変数が設定されている場合は、環境変数が優先されます。

### 2. スクリプトの実行

**macOS/Linux:**
```bash
python main.py
```

**Windows:**
```cmd
python main.py
```

または

```powershell
python main.py
```

### 3. 結果の確認

文字起こし結果は`transcripts/`ディレクトリに保存されます。ファイル名は`transcript_YYYYMMDD_HHMMSS.txt`の形式です。

## 出力ファイルの内容

保存される文字起こしファイルには以下の内容が含まれます：

1. **ブログ記事生成用のプロンプトテンプレート**
   - SEOに強いブログ記事を生成するための詳細なガイドライン
   - 記事の構成形式（タイトル、序論、本文、まとめ）
   - 文章の書き方とトーンに関する指示
   - スラッグ提案の指示

2. **動画のメタ情報**
   - タイトル
   - チャンネル名
   - URL
   - 動画の長さ（分・秒）
   - 動画概要（説明文）

3. **文字起こしテキスト**
   - Whisperによる音声認識結果
   - 自動言語判定に対応（日本語以外の動画にも対応可能）

## プロジェクト構成

```
YouTube Importer/
├── main.py                 # メインスクリプト（URLを設定して実行）
├── youtube_downloader.py   # YouTube音声ダウンロード機能
├── whisper_runner.py       # Whisper文字起こし機能
├── requirements.txt        # 依存パッケージ一覧
├── .gitignore             # Git除外設定
├── transcripts/            # 文字起こし結果保存ディレクトリ
└── tmp/                    # 一時ファイル保存ディレクトリ（.gitignoreで除外）
```

### ファイルの役割

- **main.py**: メインエントリーポイント。YouTube URLを設定し、ダウンロード→文字起こし→保存の一連の処理を実行します。ブログ記事生成用のプロンプトテンプレートも含まれています。

- **youtube_downloader.py**: `yt-dlp`を使用してYouTube動画から音声をダウンロードします。Androidクライアント設定を使用してボット検出を回避します。メタデータ（タイトル、チャンネル名、長さ、概要）も取得します。

- **whisper_runner.py**: OpenAI Whisperを使用して音声ファイルを文字起こしします。モデルは`small`を使用し、自動言語判定に対応しています。

- **transcripts/**: 文字起こし結果が保存されるディレクトリ。ファイル名は`transcript_YYYYMMDD_HHMMSS.txt`形式です。最大5件まで保持され、それ以上は古いファイルから自動削除されます。

- **tmp/**: ダウンロードした音声ファイルの一時保存ディレクトリ。文字起こし完了後に自動削除されます。

## 依存パッケージ

- `yt-dlp>=2025.01.12`: YouTube動画のダウンロード
- `openai-whisper==20240930`: 音声認識・文字起こし
- `numpy<2`: Whisperの依存パッケージ

## 注意事項

- **初回実行時**: Whisperモデル（`small`）のダウンロードに時間がかかります（約500MB）
- **ファイル管理**: 文字起こし結果は最大5件まで保持され、それ以上は古いファイルから自動削除されます
- **一時ファイル**: ダウンロードした音声ファイルは文字起こし完了後に自動削除されます
- **Windowsの場合**: パスに日本語やスペースが含まれている場合、一部の処理で問題が発生する可能性があります。可能であれば、プロジェクトを英語名のフォルダに配置することを推奨します
- **音声形式**: ダウンロードは`m4a`形式を優先し、それ以外の形式にも対応します
- **言語対応**: Whisperは自動言語判定に対応しているため、日本語以外の動画にも対応可能です

### YouTubeのボット検出について

- **特定の動画が制限されている場合**: 一部の動画は特に厳しく保護されており、ボット検出に引っかかりやすい場合があります。その場合は、別の動画URLで試してください。
- **エラーが発生した場合**: Androidクライアント設定でアクセスを試みますが、それでも失敗する場合は、その動画がダウンロードできない可能性があります。
- **技術的な対策**: 本ツールは以下の対策を実装しています：
  - AndroidクライアントのUser-Agentを使用
  - 適切なHTTPヘッダーの設定
  - リトライ機能（最大5回）
  - レート制限回避のための待機時間設定

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

### プロンプトテンプレートのカスタマイズ

`main.py`の`PROMPT_HEADER`変数を編集することで、ブログ記事生成用のプロンプトテンプレートをカスタマイズできます。デフォルトでは、SEOに強いブログ記事を生成するための詳細なガイドラインが含まれています。

## ライセンス

このプロジェクトのライセンス情報は各依存パッケージのライセンスに従います。

