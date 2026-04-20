import argparse
import json
import os
from pathlib import Path

from google import genai
from google.genai import types

from helper import token_usage
from prompt import prompt


def read_dotenv_key(path: str | Path = ".env") -> str | None:
    env_path = Path(path)
    if not env_path.exists():
        return None

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        if key.strip() not in {"GEMINI_API_KEY", "API_KEY"}:
            continue
        cleaned = value.strip().strip('"').strip("'")
        if cleaned:
            return cleaned
    return None


def get_api_key() -> str | None:
    env_key = os.getenv("GEMINI_API_KEY") or os.getenv("API_KEY")
    if env_key:
        return env_key

    dotenv_key = read_dotenv_key()
    if dotenv_key:
        return dotenv_key

    try:
        from temp import API_KEY as temp_api_key
    except Exception:
        return None
    return temp_api_key


def parse_json_response(text: str) -> dict:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:]
    return json.loads(cleaned.strip())


def default_output_path(audio_file_path: str) -> Path:
    path = Path(audio_file_path)
    return path.with_suffix(path.suffix + ".analysis.json")


def analyze_nervousness(audio_file_path: str, output_path: str | None = None) -> dict | None:
    api_key = get_api_key()
    if not api_key:
        print("Error: Set GEMINI_API_KEY in .env, environment variables, or temp.py")
        return None

    client = genai.Client(api_key=api_key)
    uploaded_file = None

    if not os.path.exists(audio_file_path):
        print(f"Error: Could not find file at '{audio_file_path}'")
        return None

    print("Uploading audio file to Gemini...")
    uploaded_file = client.files.upload(file=audio_file_path)

    print(f"Upload complete. File URI: {uploaded_file.uri}")
    print("Analyzing audio. This may take a few seconds...")

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=[uploaded_file, prompt],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.2,
            ),
        )

        report = parse_json_response(response.text)
        output = Path(output_path) if output_path else default_output_path(audio_file_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, indent=2), encoding="utf-8")

        print("\n--- Analysis Results ---")
        print(json.dumps(report, indent=2))
        print(f"\nSaved JSON report to: {output}")

        token_usage.analyse(response)
        return report

    except json.JSONDecodeError as exc:
        print(f"Error: Gemini did not return valid JSON: {exc}")
        print("\n--- Raw Response ---")
        print(response.text if "response" in locals() else "")
        return None
    except Exception as exc:
        print(f"An error occurred during generation: {exc}")
        return None

    finally:
        if uploaded_file is not None:
            client.files.delete(name=uploaded_file.name)
            print("\nCleaned up uploaded file from the server.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze interview voice/audio with Gemini JSON output.")
    parser.add_argument("audio", help="Path to a WAV/MP3/M4A audio file.")
    parser.add_argument("--out", help="Path to save JSON report. Defaults to <audio>.analysis.json.")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    analyze_nervousness(args.audio, args.out)
