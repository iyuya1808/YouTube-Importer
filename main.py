from __future__ import annotations

from pathlib import Path
from datetime import datetime

from youtube_downloader import download_audio_with_metadata
from whisper_runner import transcribe_audio


PROMPT_HEADER = """
## 1. ブログ記事の生成
以下の「【YouTubeの概要とその動画の文字起こし】」の内容に基づき、以下の「記事の仕様」を**全て厳守**して、SEOに強いブログ記事を生成してください。
なお、文字起こしの内容には誤認識や抜け漏れが含まれている可能性があります。そのため、必要に応じて内容を補完・要約しながら、自然で読みやすいブログ記事になるように構成してください。
文字起こし自体の言語が日本語以外（例: 英語）であっても、最終的な記事は必ず自然な日本語で執筆してください。

### 記事の仕様
#### 1. 構成形式

- **記事タイトル（h1）:** SEOを意識した魅力的なタイトルで、内容が一目で分かるものにする。

- **序論:**
    - 見出しなしで本文のみを記述。
    - 記事の背景、問題提起、読者の興味を引く導入文、この記事で何が分かるかを明示する。
    - **結びは必ず「ぜひ最後までご覧ください。」とする。**

- **本文（h2〜h4の階層構造）:**
    - 適切な階層構造で情報を整理する（h2 > h3 > h4）。
    - h2を大きなトピック、h3をh2の中の小トピック、h4をさらに詳細な内容とする。
    - h2よりもh3を多めに設置する。
    - 記事全体が極端に長くなりそうな場合は、本文を「前半」と「後半」に分けて生成する。
        - 最初のレスポンスでは、序論から本文の「前半」までを出力する。
        - ユーザーから「後半も続けて」などのメッセージが送られた場合に、前半の続きとして本文の「後半」とまとめを出力する。

- **まとめ（h2）:**
    - 記事全体の要約、重要なポイントの再確認、今後の展望や読者へのメッセージを含める。
    - **結びは必ず「最後までご覧いただき、ありがとうございます。」とする。**


#### 2. 文章の書き方とトーン

- 自然な日本語を用い、AI特有の機械的な表現を避ける。
- 口語的な表現（例：「〜ですね」「〜でしょう」）を適度に使用し、親しみやすいトーンで読者に語りかける。
- 適度に体言止めなどの表現も使用し、文章にリズムと変化を持たせて読みやすくする。
- 具体例や数字を積極的に用いる。
- 箇条書きは最小限にとどめ、基本的に文章で説明する。
- **h2などの文字は本文中に入れない。**
- **必ず「。」が来たら段落を変える。**
- **文字起こしや動画概要にリンク（URL）が含まれている場合は、そのリンクをブログ記事の中に適切に記述してください。リンクは文中に自然に組み込むか、関連する箇所で明示的に紹介してください。**
- **比較や一覧、数値データなど、表にまとめた方が読者にとってわかりやすい部分は、適度に表（テーブル）を使用して整理してください。表は見やすく、理解しやすい形式で作成してください。**


#### 3. 避けるべき表現

- 過度にフォーマルな表現
- 機械的な列挙
- テンプレート的な文章
- 「〜について解説します」などの定型文の多用
- 「非常に」「大変」「～の通り」「～でしょうか」など、AIが多用しがちな強調表現や定型的な口語表現


---
## 2. スラッグ提案
上記で生成した記事の内容に基づき、SEOに有利な半角英数字のスラッグ（URLの一部）を3つ提案して、記事の末尾に追記してください。
ただし、スラッグはあまり長くならないようにすること。
---



### 【YouTubeの概要とその動画の文字起こし】"""


# ここに文字起こししたいYouTubeのURLを設定してください。
# 
# 設定方法（優先順位順）:
# 1. 環境変数 YOUTUBE_URL が設定されている場合はそちらを優先します
# 2. 環境変数がない場合、以下の YOUTUBE_URL 変数に直接URLを設定してください
#    例: YOUTUBE_URL = "https://www.youtube.com/watch?v=..."
#
# 注意: 一部の動画は特に制限されている可能性があります。別の動画で試してください。
import os

# ここに直接YouTubeのURLを設定できます
# 環境変数 YOUTUBE_URL が設定されている場合はそちらが優先されます
# 環境変数がない場合、以下の変数に直接URLを設定してください:
# 例: YOUTUBE_URL = "https://www.youtube.com/watch?v=..."
YOUTUBE_URL = "https://www.youtube.com/watch?v=bPN84-mbZ2E"  # ここに直接URLを設定してください


def run(url: str) -> None:
    base_dir = Path(__file__).resolve().parent
    tmp_dir = base_dir / "tmp"
    tmp_dir.mkdir(exist_ok=True)

    try:
        audio_path, metadata = download_audio_with_metadata(url, tmp_dir)
    except Exception as e:
        print(f"[エラー] YouTubeのダウンロードに失敗しました: {e}")
        return
    title = metadata.get("title") or "(不明)"
    uploader = metadata.get("uploader") or "(不明)"
    duration = metadata.get("duration")
    description = metadata.get("description") or "(概要なし)"

    try:
        text = transcribe_audio(audio_path)
    except Exception as e:
        import traceback
        error_msg = f"[エラー] Whisperでの文字起こしに失敗しました: {e}\n{traceback.format_exc()}"
        print(error_msg)
        return
    finally:
        try:
            audio_path.unlink(missing_ok=True)
        except Exception:
            pass

    # transcriptを最大5件まで保存（6件目以降は一番古いファイルを削除）
    transcripts_dir = base_dir / "transcripts"
    transcripts_dir.mkdir(exist_ok=True)

    existing = sorted(
        transcripts_dir.glob("transcript_*.txt"),
        key=lambda p: p.stat().st_mtime,
    )
    while len(existing) >= 5:
        oldest = existing.pop(0)
        try:
            oldest.unlink()
        except Exception:
            pass

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = transcripts_dir / f"transcript_{timestamp}.txt"

    with out_path.open("w", encoding="utf-8") as f:
        # 先頭にプロンプトとガイドライン
        f.write(PROMPT_HEADER + "\n\n")

        # メタ情報
        f.write(f"タイトル: {title}\n")
        f.write(f"チャンネル: {uploader}\n")
        f.write(f"URL: {url}\n")
        if duration is not None:
            minutes = int(duration) // 60
            seconds = int(duration) % 60
            f.write(f"長さ: 約 {minutes} 分 {seconds} 秒\n")
        f.write("\n--- 動画概要 ---\n")
        f.write(f"{description}\n")
        f.write("\n--- 文字起こし ---\n\n")
        f.write(text)

    # 最終的な成功メッセージのみを表示
    print(f"✓ 完了: transcripts ディレクトリに {out_path.name} を保存しました。")


if __name__ == "__main__":
    # 環境変数から取得、なければ変数から取得
    url = os.getenv("YOUTUBE_URL") or YOUTUBE_URL
    
    if not url:
        print("エラー: YouTube URLが設定されていません。")
        print("")
        print("設定方法:")
        print("  1. 環境変数で設定: export YOUTUBE_URL='https://www.youtube.com/watch?v=...'")
        print("  2. main.pyの YOUTUBE_URL 変数に直接URLを設定:")
        print("     YOUTUBE_URL = \"https://www.youtube.com/watch?v=...\"")
        print("")
        exit(1)
    run(url)

