import imageio_ffmpeg
import tempfile
import os
import subprocess
import speech_recognition as sr

FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()


def convert_to_wav(uploaded_file):
    suffix = uploaded_file.name.split(".")[-1].lower()

    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{suffix}") as tmp:
        # Ensure we always read the full uploaded audio (important for mp3 retries).
        try:
            uploaded_file.seek(0)
        except Exception:
            pass
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name

    wav_path = tmp_path.replace(f".{suffix}", ".wav")

    source_path = tmp_path

    if suffix == "mp3":
        # Convert mp3 -> wav using bundled ffmpeg directly.
        # This avoids pydub's ffprobe lookup warnings on systems
        # where ffprobe/avprobe is not installed.
        subprocess.run(
            [FFMPEG_EXE, "-y", "-i", tmp_path, wav_path],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    else:
        wav_path = tmp_path
        source_path = None

    return wav_path, source_path


def transcribe_audio(uploaded_file):
    recognizer = sr.Recognizer()

    try:
        wav_path, tmp_input_path = convert_to_wav(uploaded_file)

        with sr.AudioFile(wav_path) as source:
            audio = recognizer.record(source)

        text = recognizer.recognize_google(audio)
        return text

    except sr.UnknownValueError:
        return "❌ Could not understand audio"

    except sr.RequestError:
        return "❌ Speech service unavailable"

    except Exception as e:
        return f"❌ Transcription failed: {str(e)}"

    finally:
        try:
            if 'wav_path' in locals() and os.path.exists(wav_path):
                os.remove(wav_path)
            if 'tmp_input_path' in locals() and tmp_input_path and os.path.exists(tmp_input_path):
                os.remove(tmp_input_path)
        except Exception:
            pass