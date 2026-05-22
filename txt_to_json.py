import json
import sys
import os
import random

def convert_txt_to_json(input_file, output_file, topic_name="Yangi Mavzu"):
    if not os.path.exists(input_file):
        print(f"Xato: {input_file} topilmadi!")
        return

    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Barcha savollarni ++++ orqali ajratish
    raw_questions = content.split('++++')
    
    quiz_data = []
    
    for q_idx, block in enumerate(raw_questions):
        block = block.strip()
        if not block:
            continue
            
        # Savol va variantlarni ==== orqali ajratish
        parts = [p.strip() for p in block.split('====') if p.strip()]
        
        if len(parts) < 3:
            print(f"Ogohlantirish: {q_idx+1}-savolda variantlar yetishmaydi. O'tkazib yuborildi.")
            continue
            
        question_text = parts[0]
        options_texts = parts[1:]
        
        correct_answer_text = None
        wrong_answers = []
        
        for opt in options_texts:
            if opt.startswith('#'):
                correct_answer_text = opt[1:].strip()
            else:
                wrong_answers.append(opt.strip())
                
        if not correct_answer_text:
            print(f"Ogohlantirish: {q_idx+1}-savolda to'g'ri javob (# bilan) topilmadi. O'tkazib yuborildi.")
            continue
            
        # A, B, C, D variantlarini tayyorlash
        # To'g'ri javobni doim A ga qo'yish (yoki aralashtirish mumkin)
        # Hozirgi baza formatiga moslash uchun to'g'ri javobni A qilib olamiz
        # Bot o'zi quiz paytida ularni random qiladi
        
        options_dict = {
            "A": correct_answer_text
        }
        
        labels = ["B", "C", "D", "E", "F"]
        for i, wrong in enumerate(wrong_answers):
            if i < len(labels):
                options_dict[labels[i]] = wrong
                
        q_obj = {
            "id": len(quiz_data) + 1,
            "topic": topic_name,
            "question": question_text,
            "options": options_dict,
            "answer": "A"
        }
        quiz_data.append(q_obj)
        
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(quiz_data, f, indent=2, ensure_ascii=False)
        
    print(f"Muvaffaqiyatli yakunlandi! {len(quiz_data)} ta savol {output_file} fayliga saqlandi.")

if __name__ == "__main__":
    print("=== TXT dan JSON ga o'giruvchi dastur ===")
    if len(sys.argv) < 3:
        print("Foydalanish: python txt_to_json.py <kiritish_fayli.txt> <chiqarish_fayli.json> [Mavzu_nomi]")
        print("Misol: python txt_to_json.py yangi_savollar.txt data/yangi_baza.json 'Tarmoq protokollari'")
    else:
        in_file = sys.argv[1]
        out_file = sys.argv[2]
        topic = sys.argv[3] if len(sys.argv) > 3 else "Yangi Mavzu"
        convert_txt_to_json(in_file, out_file, topic)
