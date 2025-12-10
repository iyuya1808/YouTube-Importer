from __future__ import annotations

import time
from pathlib import Path
from datetime import datetime

from youtube_downloader import download_audio_with_metadata
from whisper_runner import transcribe_audio


def get_prompt_header(num_videos: int) -> str:
    """
    動画数に応じたプロンプトヘッダーを生成する。
    """
    if num_videos > 1:
        video_note = f"\n**重要: 以下の{num_videos}つの動画の文字起こしから、1つの統合されたブログ記事を作成してください。複数の動画の内容を関連付けながら、1つのまとまった記事として構成してください。**\n\n**注意: 複数の動画はそれぞれ異なる言語で文字起こしされている可能性があります（例: 1つ目の動画が日本語、2つ目の動画が英語など）。各動画の文字起こしテキストの言語を適切に理解し、最終的な記事は必ず自然な日本語で執筆してください。**\n"
    else:
        video_note = ""
    
    return f"""
## 1. ブログ記事の生成
以下の「【YouTubeの概要とその動画の文字起こし】」の内容に基づき、以下の「記事の仕様」を**全て厳守**して、SEOに強いブログ記事を生成してください。
{video_note}
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
# 1. 環境変数 YOUTUBE_URL または YOUTUBE_URLS が設定されている場合はそちらを優先します
#    - 複数のURLはカンマ区切りで指定できます
#    - 例: export YOUTUBE_URLS='https://www.youtube.com/watch?v=...,https://www.youtube.com/watch?v=...'
# 2. 環境変数がない場合、以下の YOUTUBE_URLS 変数に直接URLを設定してください
#    - 1つのURLでもリスト形式で指定してください
#    - 例: YOUTUBE_URLS = ["https://www.youtube.com/watch?v=..."]
#    - 例: YOUTUBE_URLS = ["https://www.youtube.com/watch?v=...", "https://www.youtube.com/watch?v=..."]
#
# 注意: 一部の動画は特に制限されている可能性があります。別の動画で試してください。
import os

# ここに直接YouTubeのURLを設定できます（リスト形式）
# 環境変数 YOUTUBE_URL または YOUTUBE_URLS が設定されている場合はそちらが優先されます
# 環境変数がない場合、以下の変数に直接URLを設定してください:
# 例: YOUTUBE_URLS = ["https://www.youtube.com/watch?v=..."]
# 例: YOUTUBE_URLS = ["https://www.youtube.com/watch?v=...", "https://www.youtube.com/watch?v=..."]
YOUTUBE_URLS = [
    "https://www.youtube.com/watch?v=T0ExPDCTAI0",
    "https://www.youtube.com/watch?v=WbP9w3HRhso"
]  # ここに直接URLを設定してください（リスト形式）


def run(urls: list[str]) -> None:
    """
    複数のYouTube URLを処理して、1つのtranscriptファイルにまとめる。
    """
    base_dir = Path(__file__).resolve().parent
    tmp_dir = base_dir / "tmp"
    tmp_dir.mkdir(exist_ok=True)

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

    video_data_list = []

    # 各URLを処理
    for idx, url in enumerate(urls, 1):
        print(f"[{idx}/{len(urls)}] 処理中: {url}")
        
        # 複数動画の場合、前の動画処理後に待機時間を設ける（ボット検出回避）
        if idx > 1:
            wait_time = 3  # 3秒待機
            print(f"     （ボット検出回避のため{wait_time}秒待機中...）")
            time.sleep(wait_time)
        
        try:
            audio_path, metadata = download_audio_with_metadata(url, tmp_dir)
        except Exception as e:
            error_str = str(e)
            # ボット検出エラーの場合、より分かりやすいメッセージを表示
            if "bot" in error_str.lower() or "Sign in to confirm" in error_str:
                print(f"[{idx}/{len(urls)}] ⚠️  エラー: この動画はボット検出によりダウンロードできませんでした")
                print(f"     URL: {url}")
                print(f"     対処法: 別の動画で試すか、しばらく時間をおいてから再試行してください")
            else:
                print(f"[{idx}/{len(urls)}] ⚠️  エラー: YouTubeのダウンロードに失敗しました")
                print(f"     URL: {url}")
                print(f"     詳細: {error_str[:200]}")  # 長いエラーメッセージは最初の200文字のみ
            continue
        
        title = metadata.get("title") or "(不明)"
        uploader = metadata.get("uploader") or "(不明)"
        duration = metadata.get("duration")
        description = metadata.get("description") or "(概要なし)"

        try:
            text, detected_language = transcribe_audio(audio_path)
            # 言語コードを日本語名に変換
            language_names = {
                "ja": "日本語",
                "en": "英語",
                "ko": "韓国語",
                "zh": "中国語",
                "es": "スペイン語",
                "fr": "フランス語",
                "de": "ドイツ語",
                "it": "イタリア語",
                "pt": "ポルトガル語",
                "ru": "ロシア語",
                "ar": "アラビア語",
                "hi": "ヒンディー語",
                "th": "タイ語",
                "vi": "ベトナム語",
            }
            language_display = language_names.get(detected_language, detected_language)
            print(f"[{idx}/{len(urls)}] 検出言語: {language_display} ({detected_language})")
        except Exception as e:
            import traceback
            print(f"[{idx}/{len(urls)}] ⚠️  エラー: Whisperでの文字起こしに失敗しました")
            print(f"     詳細: {str(e)[:200]}")  # 長いエラーメッセージは最初の200文字のみ
            try:
                audio_path.unlink(missing_ok=True)
            except Exception:
                pass
            continue
        finally:
            try:
                audio_path.unlink(missing_ok=True)
            except Exception:
                pass

        video_data_list.append({
            "title": title,
            "uploader": uploader,
            "url": url,
            "duration": duration,
            "description": description,
            "transcript": text,
        })
        print(f"[{idx}/{len(urls)}] ✓ 完了")

    if not video_data_list:
        print("[エラー] 処理に成功した動画がありませんでした。")
        return

    # ファイルに書き込み
    with out_path.open("w", encoding="utf-8") as f:
        # 先頭にプロンプトとガイドライン（動画数に応じて変更）
        prompt_header = get_prompt_header(len(video_data_list))
        f.write(prompt_header + "\n\n")

        # 各動画の情報を書き込み（タイトル、チャンネル、URL、長さ、概要）
        for idx, video_data in enumerate(video_data_list, 1):
            if len(video_data_list) > 1:
                f.write(f"## 動画 {idx}/{len(video_data_list)}\n\n")
            
            f.write(f"タイトル: {video_data['title']}\n")
            f.write(f"チャンネル: {video_data['uploader']}\n")
            f.write(f"URL: {video_data['url']}\n")
            if video_data['duration'] is not None:
                minutes = int(video_data['duration']) // 60
                seconds = int(video_data['duration']) % 60
                f.write(f"長さ: 約 {minutes} 分 {seconds} 秒\n")
            f.write("\n--- 動画概要 ---\n")
            f.write(f"{video_data['description']}\n")
            
            if idx < len(video_data_list):
                f.write("\n\n")

        # 文字起こしセクションを1回だけ出力
        f.write("\n--- 文字起こし ---\n\n")
        
        # 各動画の文字起こしを出力
        for idx, video_data in enumerate(video_data_list, 1):
            if len(video_data_list) > 1:
                # 複数動画の場合
                if idx == 1:
                    f.write("【1つ目の動画】\n\n")
                elif idx == 2:
                    f.write("【2つ目の動画】\n\n")
                elif idx == 3:
                    f.write("【3つ目の動画】\n\n")
                else:
                    f.write(f"【{idx}つ目の動画】\n\n")
            else:
                # 1つの動画のみの場合
                pass  # 見出しなし
            
            f.write(video_data['transcript'])
            
            if idx < len(video_data_list):
                f.write("\n\n")

    # 最終的な成功メッセージのみを表示
    print(f"\n✓ 完了: transcripts ディレクトリに {out_path.name} を保存しました。")
    print(f"   処理した動画数: {len(video_data_list)}/{len(urls)}")
    if len(video_data_list) < len(urls):
        failed_count = len(urls) - len(video_data_list)
        print(f"   ⚠️  {failed_count}つの動画でエラーが発生しました（上記のエラーメッセージを確認してください）")


if __name__ == "__main__":
    # 環境変数から取得、なければ変数から取得
    urls_str = os.getenv("YOUTUBE_URLS") or os.getenv("YOUTUBE_URL")
    
    if urls_str:
        # 環境変数から取得（カンマ区切りまたはスペース区切りで複数指定可能）
        urls = [url.strip() for url in urls_str.replace(",", " ").split() if url.strip()]
    else:
        # 変数から取得
        if isinstance(YOUTUBE_URLS, str):
            # 文字列の場合、カンマ区切りまたはスペース区切りで分割
            urls = [url.strip() for url in YOUTUBE_URLS.replace(",", " ").split() if url.strip()]
        elif isinstance(YOUTUBE_URLS, list):
            # リストの場合、そのまま使用
            urls = YOUTUBE_URLS
        else:
            urls = []
    
    if not urls or len(urls) == 0:
        print("エラー: YouTube URLが設定されていません。")
        print("")
        print("設定方法:")
        print("  1. 環境変数で設定:")
        print("     export YOUTUBE_URLS='https://www.youtube.com/watch?v=...,https://www.youtube.com/watch?v=...'")
        print("     または")
        print("     export YOUTUBE_URL='https://www.youtube.com/watch?v=...'")
        print("  2. main.pyの YOUTUBE_URLS 変数に直接URLを設定:")
        print("     リスト形式: YOUTUBE_URLS = [\"https://www.youtube.com/watch?v=...\", \"https://www.youtube.com/watch?v=...\"]")
        print("     文字列形式: YOUTUBE_URLS = \"https://www.youtube.com/watch?v=..., https://www.youtube.com/watch?v=...\"")
        print("")
        exit(1)
    
    run(urls)

