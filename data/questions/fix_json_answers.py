#!/usr/bin/env python3
"""
Convert answer keys in JSON files from text values to A/B/C/D format.

This script:
1. Reads all JSON files in data/ and data/questions/
2. For each pilgan question, converts answer from text to letter
3. Matches answer text with options array position
4. Updates JSON files with new format

Usage:
    python data/questions/fix_json_answers.py
"""
import json
import os
from pathlib import Path


def convert_answer_to_letter(answer_text, options):
    """Convert answer text to letter (A, B, C, D) based on position in options."""
    try:
        # Find the index of the answer in options
        index = options.index(answer_text)
        # Convert to letter (0=A, 1=B, 2=C, 3=D)
        return chr(65 + index)
    except ValueError:
        # Answer not found in options
        print(f"  ⚠️  WARNING: Answer '{answer_text}' not found in options: {options}")
        return None


def process_json_file(filepath):
    """Process a single JSON file and convert answer keys."""
    print(f"\n📄 Processing: {filepath}")
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            questions = json.load(f)
        
        if not isinstance(questions, list):
            print(f"  ⚠️  Skipping: Not a list of questions")
            return False
        
        modified = False
        converted_count = 0
        error_count = 0
        
        for i, question in enumerate(questions):
            # Only process pilgan questions
            if question.get('type') != 'pilgan':
                continue
            
            answer = question.get('answer')
            options = question.get('options', [])
            
            # Check if already in A/B/C/D format
            if answer in ['A', 'B', 'C', 'D']:
                continue
            
            # Convert to letter
            letter = convert_answer_to_letter(answer, options)
            
            if letter:
                question['answer'] = letter
                converted_count += 1
                modified = True
                print(f"  ✓ Question {i+1}: '{answer}' → '{letter}'")
            else:
                error_count += 1
                print(f"  ✗ Question {i+1}: Could not convert '{answer}'")
        
        # Save back to file if modified
        if modified:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(questions, f, ensure_ascii=False, indent=2)
            print(f"\n  💾 Saved {converted_count} conversions")
        
        if error_count > 0:
            print(f"  ⚠️  {error_count} questions need manual review")
        
        return modified
        
    except json.JSONDecodeError as e:
        print(f"  ✗ ERROR: Invalid JSON - {e}")
        return False
    except Exception as e:
        print(f"  ✗ ERROR: {e}")
        return False


def main():
    """Main function to process all JSON files."""
    print("="*70)
    print("🔧 Converting Answer Keys: Text → A/B/C/D Format")
    print("="*70)
    
    # Get all JSON files from current directory
    base_dir = Path.cwd()
    json_files = []
    
    # Files in data/ directory
    data_dir = base_dir / 'data'
    if data_dir.exists():
        json_files.extend(data_dir.glob('*.json'))
    
    # Files in data/questions/ directory
    questions_dir = data_dir / 'questions'
    if questions_dir.exists():
        json_files.extend(questions_dir.glob('*.json'))
    
    if not json_files:
        print("\n❌ No JSON files found!")
        return
    
    print(f"\n📊 Found {len(json_files)} JSON files\n")
    
    total_modified = 0
    
    for json_file in sorted(json_files):
        if process_json_file(json_file):
            total_modified += 1
    
    print("\n" + "="*70)
    print(f"✅ Complete! Modified {total_modified}/{len(json_files)} files")
    print("="*70)
    print("\n💡 Next steps:")
    print("   1. Review the changes with 'git diff'")
    print("   2. Re-import questions to database")
    print("   3. Verify with: python manage.py fix_answer_keys\n")


if __name__ == '__main__':
    main()
