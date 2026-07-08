from faster_whisper import WhisperModel

_model = None

# "base" = tez, o'rtacha aniqlik. "small" = biroz sekinroq, yaxshiroq aniqlik.
# Birinchi ishga tushganda model avtomatik yuklab olinadi (internet kerak, keyin offline ishlaydi).
MODEL_SIZE = "small"


def get_model() -> WhisperModel:
    global _model
    if _model is None:
        _model = WhisperModel(MODEL_SIZE, device="cpu", compute_type="int8")
    return _model


def transcribe(audio_path: str) -> tuple[str, float]:
    """Returns (transcribed_text, duration_seconds)."""
    model = get_model()
    segments, info = model.transcribe(audio_path, language="en", vad_filter=True)
    text = " ".join(segment.text.strip() for segment in segments).strip()
    return text, info.duration
