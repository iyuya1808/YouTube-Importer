from __future__ import annotations

from pathlib import Path

import whisper


_model = None


def _get_model():
    global _model
    if _model is None:
        # モデルサイズは必要に応じて変更可能（tiny, base, small, medium, large）
        _model = whisper.load_model("small")
    return _model


def transcribe_audio(audio_path: Path) -> str:
    """
    mp3音声ファイルをWhisperで文字起こししてテキストを返す。
    """
    model = _get_model()
    # language を指定しないことで、Whisper に自動言語判定させる
    # これにより、英語など日本語以外の動画にも対応できる
    result = model.transcribe(str(audio_path), verbose=False)
    return result.get("text", "").strip()


