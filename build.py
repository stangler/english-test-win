#!/usr/bin/env python3
"""
csv → json/words-data.js 変換スクリプト
列構成: Lesson / Part / 英語 / 日本語

日本語→英語クイズ専用。english-word-typing-app と同様に
window.WORDS 形式の JS ファイルとして出力するため、file:// で
直接 index.html を開いても CORS エラーなく動作する。
"""

import csv
import json
import re
import sys
from pathlib import Path


def parse_ja_answer(ja_text: str) -> list[str]:
    """
    日本語テキストから正解候補リストを生成する（クイズの「問題文」として使用）。
    例: 「私はネコを好みます。（=私はネコが好きです。）」
    → ["私はネコを好みます。", "私はネコが好きです。"]
    例: 「たびたび、よく」
    → ["たびたび", "よく"]
    """
    if not ja_text:
        return []

    answers = []
    if '。' in ja_text:
        answers.append(ja_text)
    else:
        for part in re.split(r'、', ja_text):
            part = part.strip()
            answers.append(part)

    for m in re.finditer(r'（=([^）]+)）', ja_text):
        alt = m.group(1).strip()
        if alt and alt not in answers:
            answers.append(alt)

    seen = set()
    unique_answers = []
    for ans in answers:
        if ans and ans not in seen:
            seen.add(ans)
            unique_answers.append(ans)

    return unique_answers if unique_answers else [ja_text]


# ことができます直前の動詞 → 可能形語幹
POTENTIAL_MAP = {
    'かく': 'かけ', 'ひく': 'ひけ', 'およぐ': 'およげ',
    'はしる': 'はしれ', 'のむ': 'のめ', 'よむ': 'よめ',
    'おどる': 'おどれ', 'うたう': 'うたえ', 'つくる': 'つくれ',
    'のる': 'のれ', 'いく': 'いけ', 'ふく': 'ふけ', 'さす': 'させ',
    'はなす': 'はなせ', 'まつ': 'まて', 'かう': 'かえ',
    'あそぶ': 'あそべ', 'とぶ': 'とべ', 'のぼる': 'のぼれ',
    'とる': 'とれ', 'つかう': 'つかえ',
    '読む': '読め', '書く': '書け', '走る': '走れ',
    '泳ぐ': '泳げ', '踊る': '踊れ', '歌う': '歌え',
    '飲む': '飲め', '乗る': '乗れ', '行く': '行け',
    '吹く': '吹け', '作る': '作れ', '使う': '使え',
    '話す': '話せ', '待つ': '待て', '買う': '買え',
    '弾く': '弾け', '描く': '描け',
}

VERB_PATTERN = re.compile(
    r'^(.*?)(' + '|'.join(re.escape(k) for k in sorted(POTENTIAL_MAP.keys(), key=len, reverse=True)) + r')ことができ(ます|ません|ますか)。$'
)

PRONOUN_ALTS = [
    (['私は', '私が'], ['ぼくは', '僕は', 'ぼくが', '僕が']),
    (['ぼくは', '僕は'], ['私は', 'ぼくが', '僕が', '私が']),
]


def expand_pronoun(ans: str) -> list[str]:
    extras = []
    for originals, alts in PRONOUN_ALTS:
        for orig in originals:
            if ans.startswith(orig):
                rest = ans[len(orig):]
                for alt in alts:
                    candidate = alt + rest
                    if candidate not in extras and candidate != ans:
                        extras.append(candidate)
    return extras


def expand_answers(answers: list[str]) -> list[str]:
    """別解を自動展開する"""
    result = list(answers)

    for ans in list(result):
        for extra in expand_pronoun(ans):
            if extra not in result:
                result.append(extra)

        sfx = None
        if ans.endswith('ことができます。'):
            sfx = 'ます'
        elif ans.endswith('ことができません。'):
            sfx = 'ません'
        elif ans.endswith('ことができますか。'):
            sfx = 'ますか'

        if sfx:
            m2 = re.match(r'^(.*を)することができ(ます|ません|ますか)。$', ans)
            if m2:
                alt = m2.group(1)[:-1] + 'ができ' + m2.group(2) + '。'
                if alt not in result:
                    result.append(alt)

            m3 = re.match(r'^(.*(?:演奏|料理|えんそう|りょうり))することができ(ます|ません|ますか)。$', ans)
            if m3:
                alt = m3.group(1) + 'でき' + m3.group(2) + '。'
                if alt not in result:
                    result.append(alt)

            m4 = VERB_PATTERN.match(ans)
            if m4:
                prefix, verb, s = m4.group(1), m4.group(2), m4.group(3)
                pot = POTENTIAL_MAP.get(verb)
                if pot:
                    alt = prefix + pot + s + '。'
                    if alt not in result:
                        result.append(alt)

        for src, dst in [('をみます。', 'を見ます。'), ('をみますか。', 'を見ますか。')]:
            if src in ans:
                alt = ans.replace(src, dst)
                if alt not in result:
                    result.append(alt)

    return result


def build(csv_path: Path, out_path: Path):
    with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)
        rows = list(reader)

    data = []
    for row in rows[1:]:
        if not any(row):
            continue
        row = row + [""] * (4 - len(row))
        lesson_raw, part_raw, en, ja = row[0], row[1], row[2], row[3]

        if not en or not ja:
            continue

        lesson = lesson_raw.strip() if lesson_raw is not None else ""
        part = part_raw.strip() if part_raw is not None and part_raw.strip() != "" else ""
        try:
            part = str(int(float(part))) if part else ""
        except (ValueError, TypeError):
            pass

        ja_str = ja.strip()
        en_str = en.strip()

        ja_answers = parse_ja_answer(ja_str)
        ja_answers = expand_answers(ja_answers)

        data.append({
            "lesson": lesson,
            "part": part,
            "en": en_str,
            "ja": ja_str,
            "ja_answers": ja_answers,
        })

    out_path.parent.mkdir(parents=True, exist_ok=True)
    js = "window.WORDS = " + json.dumps(data, ensure_ascii=False, indent=2) + ";\n"
    out_path.write_text(js, encoding="utf-8")
    print(f"✓ {len(data)} 件出力 → {out_path}")


if __name__ == "__main__":
    args = sys.argv[1:]
    csv_args = [a for a in args if not a.startswith("--")]

    default_csv = next(Path("csv").glob("*.csv"), Path("csv/EIGO_NO_PARTNERに出てくる文.csv"))
    csv_file = Path(csv_args[0]) if csv_args else default_csv
    out = Path("json/words-data.js")

    build(csv_file, out)
