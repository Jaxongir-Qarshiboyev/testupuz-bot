"""Quiz ma'lumotlarini yuklash"""
import json
import os
import random

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

# Fanlar ro'yxati
SUBJECTS = {}


def load_subject(subject_id: str, filename: str, display_name: str, full_name: str):
    """Fanni yuklash"""
    filepath = os.path.join(DATA_DIR, filename)
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Mavzularni ajratish
    topics = {}
    for item in data:
        t = item["topic"]
        if t not in topics:
            topics[t] = []
        topics[t].append(item)

    SUBJECTS[subject_id] = {
        "id": subject_id,
        "name": display_name,
        "full_name": full_name,
        "questions": data,
        "topics": topics,
        "topic_names": list(topics.keys()),
        "total": len(data),
        "total_topics": len(topics),
    }
    return SUBJECTS[subject_id]


def get_subject(subject_id: str):
    """Fan ma'lumotlarini olish"""
    return SUBJECTS.get(subject_id)


def get_topics_with_counts(subject_id: str):
    """Mavzular va savol sonlari"""
    subj = SUBJECTS.get(subject_id)
    if not subj:
        return []
    return [(name, len(qs)) for name, qs in subj["topics"].items()]


def get_questions(subject_id: str, topic_index: int = None,
                  count: int = None, order: str = "sequential"):
    """Savollarni olish"""
    subj = SUBJECTS.get(subject_id)
    if not subj:
        return []

    if topic_index is not None and 0 <= topic_index < len(subj["topic_names"]):
        topic_name = subj["topic_names"][topic_index]
        questions = list(subj["topics"][topic_name])
    else:
        questions = list(subj["questions"])

    if order == "random":
        random.shuffle(questions)

    if count and count < len(questions):
        questions = questions[:count]

    return questions


def init_all_subjects():
    """Barcha fanlarni yuklash"""
    load_subject("miich", "miich_quiz.json", "MIICH",
                 "Mobil Ilovalar Ishlab Chiqish")
    load_subject("dt_sifati", "dt_sifati_quiz.json", "DT Sifati",
                 "Dasturiy Ta'minot Sifatini Ta'minlash")
    load_subject("ekspert", "ekspert_quiz.json", "Ekspert Tizimlar",
                 "Sun'iy Intellekt va Ekspert Tizimlar")
    load_subject("dt_maruzalar", "dt_maruzalar_quiz.json", "DT Ma'ruzalar",
                 "Dasturiy Ta'minot Sifati — Ma'ruzalar")
    load_subject("dt_arxitektura", "dt_arxitektura_quiz_min.json", "DT Arxitektura",
                 "Dasturiy Ta'minot Arxitekturasi (Yakuniy)")
    load_subject("dt_arxitektura_nazorat", "dt_arxitektura_nazorat_quiz_min.json", "DT Arxitektura Nazorat",
                 "Dasturiy Ta'minot Arxitekturasi (Oraliq va Nazorat)")
