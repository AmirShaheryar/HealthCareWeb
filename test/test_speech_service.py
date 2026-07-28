import io
import os

import speech_recognition as sr

from services import speech_service


class DummyUploadFile:
    def __init__(self, name, data):
        self.name = name
        self._buffer = io.BytesIO(data)

    def read(self):
        return self._buffer.read()

    def seek(self, pos):
        self._buffer.seek(pos)


def test_convert_to_wav_with_wav_keeps_original_file():
    upload = DummyUploadFile("note.wav", b"wav-bytes")

    wav_path, source_path = speech_service.convert_to_wav(upload)

    assert os.path.exists(wav_path)
    assert source_path is None

    os.remove(wav_path)


def test_convert_to_wav_with_mp3_invokes_ffmpeg(monkeypatch):
    upload = DummyUploadFile("voice.mp3", b"mp3-bytes")

    def fake_run(cmd, check, stdout, stderr):
        assert cmd[0] == speech_service.FFMPEG_EXE
        assert cmd[3].endswith(".mp3")
        assert cmd[4].endswith(".wav")
        return None

    monkeypatch.setattr(speech_service.subprocess, "run", fake_run)

    wav_path, source_path = speech_service.convert_to_wav(upload)

    assert wav_path.endswith(".wav")
    assert source_path.endswith(".mp3")
    assert os.path.exists(source_path)

    os.remove(source_path)


def test_transcribe_audio_success(monkeypatch):
    upload = DummyUploadFile("voice.wav", b"bytes")

    monkeypatch.setattr(
        speech_service,
        "convert_to_wav",
        lambda _: ("fake.wav", None),
    )

    class FakeAudioFile:
        def __init__(self, path):
            self.path = path

        def __enter__(self):
            return "source"

        def __exit__(self, exc_type, exc, tb):
            return False

    monkeypatch.setattr(sr, "AudioFile", FakeAudioFile)
    monkeypatch.setattr(speech_service.os.path, "exists", lambda _: False)

    class FakeRecognizer:
        def record(self, source):
            assert source == "source"
            return "audio-data"

        def recognize_google(self, audio):
            assert audio == "audio-data"
            return "transcribed text"

    monkeypatch.setattr(sr, "Recognizer", lambda: FakeRecognizer())

    result = speech_service.transcribe_audio(upload)
    assert result == "transcribed text"


def test_transcribe_audio_handles_unknown_value(monkeypatch):
    upload = DummyUploadFile("voice.wav", b"bytes")

    monkeypatch.setattr(
        speech_service,
        "convert_to_wav",
        lambda _: ("fake.wav", None),
    )

    class FakeAudioFile:
        def __init__(self, path):
            self.path = path

        def __enter__(self):
            return "source"

        def __exit__(self, exc_type, exc, tb):
            return False

    monkeypatch.setattr(sr, "AudioFile", FakeAudioFile)
    monkeypatch.setattr(speech_service.os.path, "exists", lambda _: False)

    class FakeRecognizer:
        def record(self, source):
            return "audio-data"

        def recognize_google(self, audio):
            raise sr.UnknownValueError()

    monkeypatch.setattr(sr, "Recognizer", lambda: FakeRecognizer())

    result = speech_service.transcribe_audio(upload)
    assert result == "❌ Could not understand audio"


def test_transcribe_audio_handles_request_error(monkeypatch):
    upload = DummyUploadFile("voice.wav", b"bytes")

    monkeypatch.setattr(
        speech_service,
        "convert_to_wav",
        lambda _: ("fake.wav", None),
    )

    class FakeAudioFile:
        def __init__(self, path):
            self.path = path

        def __enter__(self):
            return "source"

        def __exit__(self, exc_type, exc, tb):
            return False

    monkeypatch.setattr(sr, "AudioFile", FakeAudioFile)
    monkeypatch.setattr(speech_service.os.path, "exists", lambda _: False)

    class FakeRecognizer:
        def record(self, source):
            return "audio-data"

        def recognize_google(self, audio):
            raise sr.RequestError("network")

    monkeypatch.setattr(sr, "Recognizer", lambda: FakeRecognizer())

    result = speech_service.transcribe_audio(upload)
    assert result == "❌ Speech service unavailable"
