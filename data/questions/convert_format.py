#!/usr/bin/env python3
"""
Script to convert question JSON format from old to new format.
Old format uses: question_text, question_type, answer_key, points, tags
New format uses: text, type, answer (with actual answer value)
"""
import json
import glob

def convert_question(q):
    """Convert a single question from old to new format"""
    # Get the answer value from options using answer_key
    answer_index = ord(q['answer_key']) - ord('A')
    answer_value = q['options'][answer_index]
    
    return {
        "grade": q['grade'],
        "subject": q['subject'],
        "topic": q['topic'],
        "type": q['question_type'],
        "difficulty": q['difficulty'],
        "text": q['question_text'],
        "options": q['options'],
        "answer": answer_value,
        "explanation": q['explanation']
    }

def convert_file(input_file, output_file):
    """Convert a JSON file from old to new format"""
    print(f"Converting {input_file}...")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        old_questions = json.load(f)
    
    new_questions = [convert_question(q) for q in old_questions]
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(new_questions, f, ensure_ascii=False, indent=2)
    
    print(f"  ✓ Converted {len(new_questions)} questions")

if __name__ == "__main__":
    # Find all JSON files in current directory
    json_files = glob.glob("*.json")
    
    print(f"Found {len(json_files)} JSON files")
    
    for json_file in json_files:
        convert_file(json_file, json_file)
    
    print(f"\n✅ All {len(json_files)} files converted successfully!")
