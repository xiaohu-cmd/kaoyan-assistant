import sqlite3, datetime

db = sqlite3.connect('/opt/kaoyan-assistant/data/kaoyan.db')
db.row_factory = sqlite3.Row

words = db.execute("SELECT * FROM vocab_words").fetchall()
print(f"Found {len(words)} words")

db.execute("DELETE FROM flashcards WHERE is_vocab = 1")

now = datetime.datetime.now().isoformat()
count = 0
for w in words:
    phonetic = w['phonetic'] or ''
    pos = w['part_of_speech'] or ''
    meaning = w['meaning'] or ''
    front = w['word']
    back = f"{phonetic} {pos}\n{meaning}"
    if w['example_sentence']:
        back += f"\n\n例: {w['example_sentence']}"
        if w['example_translation']:
            back += f"\n{w['example_translation']}"

    db.execute(
        "INSERT INTO flashcards (subject_id, front_text, back_text, tags, is_vocab, next_review_date, created_at) VALUES (2, ?, ?, ?, 1, ?, ?)",
        (front, back, w['frequency_level'], now, now)
    )
    count += 1

db.commit()
print(f"Created {count} flashcards from vocabulary")
db.close()
