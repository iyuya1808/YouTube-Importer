from __future__ import annotations

from pathlib import Path
from typing import Dict, Tuple

from yt_dlp import YoutubeDL


def download_audio_with_metadata(url: str, tmp_dir: Path) -> Tuple[Path, Dict]:
    """
    指定したYouTube URLから音声（または動画）をダウンロードし、
    保存ファイルパスとメタデータを返す。

    - Androidクライアント設定のみを使用します。
    - CookieファイルやPOトークンは一切使用しません。
    """
    tmp_dir.mkdir(parents=True, exist_ok=True)

    output_template = str(tmp_dir / "%(id)s.%(ext)s")

    # Androidクライアント設定のみを使用
    ydl_opts = {
        # 音声のみ（できればm4a）を取得。Whisper側でそのまま渡せる形式にする。
        "format": "bestaudio[ext=m4a]/bestaudio/best",
        "outtmpl": output_template,
        "noplaylist": True,
        # 端末ログを最小限にする
        "quiet": True,
        "no_warnings": True,
        # YouTubeのボット検出をある程度回避するための設定（Androidクライアント固定）
        "extractor_args": {
            "youtube": {
                "player_client": ["android"],
                "player_skip": ["webpage", "configs"],
            }
        },
        # User-AgentをAndroidクライアントに合わせる
        "user_agent": "com.google.android.youtube/19.09.37 (Linux; U; Android 11) gzip",
        # 追加のHTTPヘッダー
        "http_headers": {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-us,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Charset": "ISO-8859-1,utf-8;q=0.7,*;q=0.7",
            "Keep-Alive": "300",
            "Connection": "keep-alive",
        },
        # リトライ設定
        "retries": 5,
        "fragment_retries": 5,
        # タイムアウト設定
        "socket_timeout": 60,
        # 待機時間を追加（レート制限回避）
        "sleep_interval": 1,
        "max_sleep_interval": 5,
    }

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)

    # 実際に保存されたファイルパスを info から取得
    audio_path: Path | None = None
    requested = info.get("requested_downloads") or []
    if requested:
        audio_path = Path(requested[0].get("filepath"))
    elif "_filename" in info:
        audio_path = Path(info["_filename"])

    if not audio_path or not audio_path.exists() or audio_path.stat().st_size == 0:
        raise FileNotFoundError("音声ファイルのダウンロードに失敗しました（ファイルが空か存在しません）。")

    metadata = {
        "title": info.get("title"),
        "uploader": info.get("uploader"),
        "duration": info.get("duration"),
        "description": info.get("description"),
    }

    return audio_path, metadata


