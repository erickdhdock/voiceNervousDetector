# Voice Detection

Audio-only interview voice analysis using Gemini. The CLI uploads an audio file,
asks Gemini to return a fixed JSON report, saves that report locally, prints token
usage, and then deletes the uploaded file from Gemini Files.

## What It Measures

The prompt is designed for interview-style speech and separates speaker delivery
from recording conditions.

The JSON report includes:

- Speaker nervousness, confidence, clarity, and pace/fluency
- Environment noise and interview suitability
- Microphone quality
- Intelligibility and accent impact on understandability
- Speech context and professional tone
- Prioritized advice
- Reliability notes and limits

The assessment is audio-only. The prompt explicitly tells the model not to infer
or mention video, eye contact, appearance, nationality, ethnicity, or other
protected traits.

## Requirements

- Python 3.10+
- A Gemini API key
- `google-genai`

Install the Python dependency:

```bash
pip install google-genai
```

## Setup

Create a local `.env` file from the example:

```bash
cp .env.example .env
```

Then set your key:

```bash
GEMINI_API_KEY=your_key_here
```

`markVoice.py` looks for an API key in this order:

1. `GEMINI_API_KEY` or `API_KEY` environment variables
2. `GEMINI_API_KEY` or `API_KEY` in `.env`
3. `API_KEY` imported from `temp.py`

The `.env` file is ignored by git.

## Usage

Run the analyzer with a local audio file:

```bash
python markVoice.py path/to/audio.wav
```

Supported inputs are audio files that Gemini can process, such as WAV, MP3, or
M4A.

By default, the report is written next to the input file using this naming
pattern:

```text
path/to/audio.wav.analysis.json
```

To choose the output path:

```bash
python markVoice.py path/to/audio.wav --out reports/audio.analysis.json
```

## How It Works

`markVoice.py` is the CLI entry point.

1. Parses the audio path and optional `--out` argument.
2. Reads the Gemini API key from the environment, `.env`, or `temp.py`.
3. Checks that the audio file exists.
4. Uploads the file with `client.files.upload(...)`.
5. Calls `client.models.generate_content(...)` with:
   - `model="gemini-2.5-flash-lite"`
   - the uploaded audio file
   - the structured prompt from `prompt.py`
   - `response_mime_type="application/json"`
   - `temperature=0.2`
6. Parses the model response as JSON.
7. Writes the formatted JSON report to disk.
8. Prints token usage with `helper/token_usage.py`.
9. Deletes the uploaded file from Gemini in a `finally` block.

## Files

- `markVoice.py` - command-line runner and Gemini API integration
- `prompt.py` - strict JSON prompt and assessment rubric
- `helper/token_usage.py` - token usage printer for Gemini responses
- `.env.example` - API key template

## Output

The output shape is fixed by `prompt.py` and starts like this:

```json
{
  "schema": "voice_mvp_v1",
  "speaker": {
    "nervousness": {},
    "confidence": {},
    "clarity": {},
    "pace_fluency": {}
  },
  "environment": {},
  "intelligibility": {},
  "context": {},
  "advice": [],
  "reliability": {}
}
```

Each scored category includes short summaries and, where useful, timestamped
segments with evidence from the audio.

## Troubleshooting

If you see:

```text
Error: Set GEMINI_API_KEY in .env, environment variables, or temp.py
```

then no API key was found. Add one to `.env` or export it in your shell.

If you see:

```text
Error: Could not find file at '...'
```

check that the audio path is correct and is relative to your current working
directory, or use an absolute path.

If Gemini returns invalid JSON, the script prints the raw response so the prompt
or parser can be adjusted.

## Notes

- `sample/` is ignored by git and can be used for local audio files and generated
  reports.
- Generated reports are local JSON files; they are not automatically uploaded
  anywhere else.
- Uploaded audio is deleted from Gemini after analysis completes or fails inside
  the generation step.
