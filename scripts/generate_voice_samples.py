"""Generate voice samples for all Arabic voices across Google Chirp3-HD and ElevenLabs.

Uses the same narrator paragraph from chapter 15 (al-liss-wal-kilab) for all samples.
"""
import base64
import json
import subprocess
import time
from pathlib import Path

import httpx


# ---------------------------------------------------------------------------
# Sample text — narrator paragraph from chapter 15
# ---------------------------------------------------------------------------

SAMPLE_TEXT = (
    "تجنَّبَ الطريق الملاصق للثكنات، واخترقَ الصحراء نحو مدفن الشهيد ليبلغه في أقصر وقت، "
    "وكان كأنما يهتدي ببوصلة مُركَّبة في رأسه، لسابق درايته بصحراء العباسية، "
    "وعندما لاحَتْ له قبة المدفن الضخمة تحت ضوء النجوم، راحت عيناه تُفتِّشان عن المكان الذي تنزوي فيه السيارة، "
    "ودار حول المدفن وهو يحد بصره، ولا يعثر على ضالته، حتى بلغ ضلعه الجنوبي، "
    "فتراءى له شبح هيكلها راقدًا على بُعدٍ، مضى نحوها مُصمِّمًا، "
    "ثم ما لبث أن أحنى ظهره حتى انخفض رأسه إلى مستوى ركبته، "
    "واقترب منها فوضح لأذنَيهِ أن الصمت يتخلخل بهمسات مغرقة في السر، "
    "سيذعر قلب هانئ، وتتبدَّد مسرة، ولكن لا ذنب لك، الاختلال يطبق علينا مثل قبة السماء، وقديمًا قال رءوف علوان"
)

# Shorter version for Chirp3-HD (stricter sentence length limit)
SAMPLE_TEXT_SHORT = (
    "تجنَّبَ الطريق الملاصق للثكنات واخترقَ الصحراء نحو مدفن الشهيد ليبلغه في أقصر وقت. "
    "وكان كأنما يهتدي ببوصلة مُركَّبة في رأسه لسابق درايته بصحراء العباسية. "
    "وعندما لاحَتْ له قبة المدفن الضخمة تحت ضوء النجوم راحت عيناه تُفتِّشان عن المكان الذي تنزوي فيه السيارة. "
    "ودار حول المدفن وهو يحد بصره ولا يعثر على ضالته حتى بلغ ضلعه الجنوبي. "
    "فتراءى له شبح هيكلها راقدًا على بُعدٍ ومضى نحوها مُصمِّمًا. "
    "ثم ما لبث أن أحنى ظهره حتى انخفض رأسه إلى مستوى ركبته. "
    "واقترب منها فوضح لأذنَيهِ أن الصمت يتخلخل بهمسات مغرقة في السر."
)


# ---------------------------------------------------------------------------
# Credentials
# ---------------------------------------------------------------------------

def get_credential(env_var: str, pass_path: str) -> str | None:
    import os
    val = os.environ.get(env_var)
    if val:
        return val.strip()
    try:
        result = subprocess.run(
            ["pass", pass_path], capture_output=True, text=True, check=True
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


# ---------------------------------------------------------------------------
# Google Chirp3-HD
# ---------------------------------------------------------------------------

GOOGLE_CHIRP3_HD_VOICES = {
    # Female (14)
    "Achernar": "FEMALE",
    "Aoede": "FEMALE",
    "Autonoe": "FEMALE",
    "Callirrhoe": "FEMALE",
    "Despina": "FEMALE",
    "Erinome": "FEMALE",
    "Gacrux": "FEMALE",
    "Kore": "FEMALE",
    "Laomedeia": "FEMALE",
    "Leda": "FEMALE",
    "Pulcherrima": "FEMALE",
    "Sulafat": "FEMALE",
    "Vindemiatrix": "FEMALE",
    "Zephyr": "FEMALE",
    # Male (16)
    "Achird": "MALE",
    "Algenib": "MALE",
    "Algieba": "MALE",
    "Alnilam": "MALE",
    "Charon": "MALE",
    "Enceladus": "MALE",
    "Fenrir": "MALE",
    "Iapetus": "MALE",
    "Orus": "MALE",
    "Puck": "MALE",
    "Rasalgethi": "MALE",
    "Sadachbia": "MALE",
    "Sadaltager": "MALE",
    "Schedar": "MALE",
    "Umbriel": "MALE",
    "Zubenelgenubi": "MALE",
}


def generate_google_samples(output_dir: Path, only_missing: bool = True):
    """Generate Chirp3-HD samples for all voices."""
    api_key = get_credential("GOOGLE_TTS_API_KEY", "amr/google_api")
    if not api_key:
        print("ERROR: No Google API key found")
        return

    output_dir.mkdir(parents=True, exist_ok=True)
    client = httpx.Client(timeout=60)

    for name, gender in GOOGLE_CHIRP3_HD_VOICES.items():
        voice_name = f"ar-XA-Chirp3-HD-{name}"
        g_label = "F" if gender == "FEMALE" else "M"
        out_file = output_dir / f"Chirp3-HD-{name}.mp3"

        if only_missing and out_file.exists():
            print(f"  SKIP {name} (exists)")
            continue

        print(f"  Generating {name} ({g_label})...", end=" ", flush=True)
        try:
            resp = client.post(
                f"https://texttospeech.googleapis.com/v1beta1/text:synthesize?key={api_key}",
                json={
                    "input": {"text": SAMPLE_TEXT_SHORT},
                    "voice": {
                        "languageCode": "ar-XA",
                        "name": voice_name,
                    },
                    "audioConfig": {
                        "audioEncoding": "MP3",
                        "sampleRateHertz": 24000,
                    },
                },
            )
            resp.raise_for_status()
            audio_b64 = resp.json()["audioContent"]
            out_file.write_bytes(base64.b64decode(audio_b64))
            size_kb = out_file.stat().st_size / 1024
            print(f"OK ({size_kb:.0f}KB)")
        except httpx.HTTPStatusError as e:
            print(f"FAILED ({e.response.status_code}: {e.response.text[:200]})")
        except Exception as e:
            print(f"FAILED ({e})")

        time.sleep(0.3)

    client.close()


# ---------------------------------------------------------------------------
# ElevenLabs
# ---------------------------------------------------------------------------

# Voice ID → (display_name, accent, gender)
ELEVENLABS_VOICES = {
    # --- Already sampled (skip if exists) ---
    "XTa3iQyMA6f1qrI4F6kZ": ("Sara", "MSA", "F"),
    "LjKPkQHpXCsWoy7Pjq4U": ("Alice", "Egyptian", "F"),
    "EUojVLG1QfxaqqH4ce6s": ("Razan", "MSA", "F"),
    "tavIIPLplRB883FzWU0V": ("Mona", "MSA", "F"),
    "u0TsaWvt0v8migutHM3M": ("Ghizlane", "MSA", "F"),
    "B5xxC4eQoOFJnY4R5XkI": ("Salma", "Levantine", "F"),
    "ML7jGRDg4E9hIl5qEm1Z": ("Suhair", "MSA", "F"),
    "DWMVT5WflKt0P8OPpIrY": ("Hanafi", "Egyptian", "M"),
    "Jez3JdhBInQTvlAvDOWR": ("Moncellence", "Egyptian", "M"),
    "QRq5hPRAKf5ZhSlTBH6r": ("Yahya", "MSA", "M"),
    "ocqVw6LVSdCxCra4XhMH": ("Abdullah", "Egyptian", "M"),
    "VwC51uc4PUblWEJSPzeo": ("Abrar_Sabbah", "MSA", "F"),
    "9SPZl4Mlgwj7QT4gVprb": ("Adam", "Egyptian", "M"),
    "yrPIy5b3iLnVLIBfUSw8": ("Amr", "Egyptian", "M"),
    "R6nda3uM038xEEKi7GFl": ("Anas", "MSA", "M"),
    "t8atLZaWuCcW6gENDwwa": ("Ashraf", "MSA", "M"),
    "qi4PkV9c01kb869Vh7Su": ("Asmaa", "MSA", "F"),
    "JbTItPM48g6ErYIsuhRs": ("Cherif_Malli", "MSA", "M"),
    "w4LX7bK479eHGM1k15Em": ("Habibah", "MSA", "F"),
    "wxweiHvoC2r2jFM7mS8b": ("Haytham", "Egyptian", "M"),
    "fkqevZRU7Xj52dY1CTkq": ("Hijazi", "MSA", "M"),
    "meAbY2VpJkt1q46qk56T": ("Hoda", "Egyptian", "F"),
    "Ojb0nFbyzZn95u0i5a5p": ("Marco_Nady", "Egyptian", "M"),
    "KXptrwcsEqqFSwRKJukF": ("Meisam", "MSA", "M"),
    "Qp2PG6sgef1EHtrNQKnf": ("Mohamed_Ben", "MSA", "M"),
    "HJ8unGw6UFYkApOU0Oea": ("Omars", "MSA", "M"),
    "i2bK1jTwxz2ZhfV2NANO": ("Ramy_Ibrahim", "Egyptian", "M"),
    "mRdG9GYEjJmIzqbYTidv": ("Sana", "MSA", "F"),
    # --- NEW: High priority ---
    "rFDdsCQRZCUL8cPOWtnP": ("Ghaida_narrative", "Syrian", "F"),
    "Wim44P0dU9HtjyzNnFsv": ("Ghaida_cheerful", "Syrian", "F"),
    "4wf10lgibMnboGJGCLrP": ("Farah", "Jordanian", "F"),
    "jAAHNNqlbAX9iWjJPEtE": ("Sara_Jordanian", "Jordanian", "F"),
    "v7UCHHCrHj1KBa4E41gb": ("Heba_Mansuri", "Saudi", "F"),
    "RzNYiYBiH7YrpC9QKXyc": ("Sakina", "Arabic", "F"),
    "GLRyn2pNxpZ4FAjmlY3z": ("Rima_M", "Tunisian", "F"),
    "MI88rOZjXbH22N8KHXUo": ("Ali_Saudi", "Saudi", "M"),
    "yXEnnEln9armDCyhkXcA": ("Jeddawi", "Saudi", "M"),
    "jpofSqItAIlT4TLP5CrK": ("Ilyass", "Algerian", "M"),
    "nH7M8bGCLQbKoS0wBZj7": ("Salim", "Tunisian", "M"),
    "7DwruJn2XVUNMherEcad": ("Ibrahim", "Levantine", "M"),
    "8sSDN08XkFeN2zqNwCZk": ("Odai", "Palestinian", "M"),
    "ZCXYdzd5Evtsll2EdoCi": ("Yousef", "MSA", "M"),
    "VxSsN5NGusWQZXue7VE9": ("Hammam", "Egyptian", "M"),
    "K6EjAWq39CfwwPD4jafo": ("Nasser", "MSA", "M"),
    "rPNcQ53R703tTmtue1AT": ("Mazen_Lawand", "MSA", "M"),
    "DANw8bnAVbjDEHwZIoYa": ("Ghawi", "Gulf", "M"),
    # --- NEW: Medium priority ---
    "QsV9PCczMIklRM6xLPAS": ("Heba_Mansuri_care", "Saudi", "F"),
    "GTQ4ImqrRljZAa9VJX6B": ("Salma_bilingual", "Arabic", "F"),
    "aCChyB4P5WEomwRsOKRh": ("Salma_mature", "Arabic", "F"),
    "IYnFszSKzmym2OstwHS0": ("Hadi_N", "Levantine", "M"),
    "oJQlz7pz2yWd7MRmDUXm": ("Fadi", "Levantine", "M"),
    "HRaipzPqzrU15BUS5ypU": ("Mr_FF", "Syrian", "M"),
    "oUCSlKjkoFDoKamPHpAV": ("Karim", "MSA", "M"),
    "tlETan7Okc4pzjD0z62P": ("Mohammed", "Arabic", "M"),
    "RjFuvnufLX42TYe37ekK": ("Adeeb_conv", "Saudi", "M"),
    "s83SAGdFTflAwJcAV81K": ("Adeeb_narr", "Saudi", "M"),
    "TfevL8tqOhb9PBTrfU9u": ("Sahl", "Gulf", "M"),
    "F1gAsD7Cj4WPfrcu1yKu": ("Mahmoud_social", "Arabic", "M"),
    "Os2frcqCuUz8b9F93RuI": ("Mahmoud_conv", "Arabic", "M"),
    "xa8eOqmKc5EbIYyKGw0u": ("Emirati", "Arabic", "M"),
    "evtDwF7UqN7X6HhwtdoK": ("Mohamed_Sudan", "Arabic", "M"),
    "tlz2I4zMDRDFMFFHKQv6": ("Mohammed_Yemeni", "Arabic", "M"),
    # --- NEW: Lower priority ---
    "drMurExmkWVIH5nW8snR": ("Khaled_Alnajjar", "Palestinian", "M"),
    "VqHyN6PYNu3uNKGdbxKs": ("ELareef", "Egyptian", "M"),
    "bHCN6EPPyN5hYpU9UVUz": ("Ahmed", "Egyptian", "M"),
    "amSNjVC0vWYiE8iGimVb": ("Maged_Magdy", "Egyptian", "M"),
    "8KMBeKnOSHXjLqGuWsAE": ("Sultan", "Saudi", "M"),
    "3nav5pHC1EYvWOd5LmnA": ("Saud", "Saudi", "M"),
    "H48IdiQwyf50CXpP0dy0": ("Faisal_Ali", "Saudi", "M"),
    "pCKbQ4EPGE06zpEPGNvS": ("Abdullah_MSA", "MSA", "M"),
    "pO3ZuaXj0mFWxTrn1tPt": ("Mehdi_VO", "MSA", "M"),
    "PmGnwGtnBs40iau7JfoF": ("Jawad_Moroccan", "Moroccan", "M"),
    "JoySr0ZYKEotnyhsN3Ji": ("Jawad_MSA", "MSA", "M"),
    "EzoxNTKsg4JNN7wxAgut": ("Hakim", "Arabic", "M"),
}


def generate_elevenlabs_samples(output_dir: Path, only_missing: bool = True):
    """Generate ElevenLabs samples for all Arabic voices."""
    api_key = get_credential("ELEVENLABS_API_KEY", "amr/elevenlabs_api")
    if not api_key:
        print("ERROR: No ElevenLabs API key found")
        return

    output_dir.mkdir(parents=True, exist_ok=True)
    client = httpx.Client(timeout=60)

    for voice_id, (name, accent, gender) in ELEVENLABS_VOICES.items():
        out_file = output_dir / f"{name}_{accent}_{gender}.mp3"

        if only_missing and out_file.exists():
            print(f"  SKIP {name} (exists)")
            continue

        print(f"  Generating {name} ({accent}, {gender})...", end=" ", flush=True)
        try:
            resp = client.post(
                f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
                headers={
                    "xi-api-key": api_key,
                    "Content-Type": "application/json",
                },
                json={
                    "text": SAMPLE_TEXT,
                    "model_id": "eleven_multilingual_v2",
                    "voice_settings": {
                        "stability": 0.5,
                        "similarity_boost": 0.75,
                    },
                },
            )
            resp.raise_for_status()
            out_file.write_bytes(resp.content)
            size_kb = out_file.stat().st_size / 1024
            print(f"OK ({size_kb:.0f}KB)")
        except httpx.HTTPStatusError as e:
            print(f"FAILED ({e.response.status_code}: {e.response.text[:200]})")
        except Exception as e:
            print(f"FAILED ({e})")

        time.sleep(1.0)  # ElevenLabs rate limiting

    client.close()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys

    base = Path("output/epub/al-liss-wal-kilab/05_audio/poc4a")

    if len(sys.argv) < 2 or sys.argv[1] in ("google", "all"):
        print(f"\n=== Google Chirp3-HD (30 voices) ===")
        print(f"Sample text: {len(SAMPLE_TEXT)} chars")
        print(f"Output: {base / 'google'}\n")
        generate_google_samples(base / "google")

    if len(sys.argv) < 2 or sys.argv[1] in ("elevenlabs", "all"):
        print(f"\n=== ElevenLabs ({len(ELEVENLABS_VOICES)} voices) ===")
        print(f"Sample text: {len(SAMPLE_TEXT)} chars")
        print(f"Output: {base / 'elevenlabs'}\n")
        generate_elevenlabs_samples(base / "elevenlabs")

    print("\nDone!")
