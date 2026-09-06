#!/usr/bin/env python3
"""
Validate carousel input format against specification.
Accepts both old (markdown) and new (header+slide) formats.

Usage:
  python3 validate_carousel_format.py <input_file.txt>

Exit codes:
  0 = valid
  1 = invalid format
"""
import sys
import re
from pathlib import Path


def validate_carousel(filepath: str) -> tuple[bool, list[str]]:
    """
    Validate carousel. Accepts old markdown format (## SLIDE N, **FIELD**)
    and new header+slide format (handle:, Slide N:, etc.)
    
    Returns (is_valid, error_list)
    """
    try:
        content = Path(filepath).read_text(encoding='utf-8')
    except FileNotFoundError:
        return False, [f"File not found: {filepath}"]
    except Exception as e:
        return False, [f"Cannot read file: {e}"]
    
    lines = content.split('\n')
    
    # Detect format
    is_old = any(re.match(r'^##\s+SLIDE', line, re.IGNORECASE) for line in lines)
    
    if is_old:
        return _validate_old(lines)
    else:
        return _validate_new(lines)


def _validate_old(lines: list[str]) -> tuple[bool, list[str]]:
    """Old markdown format: ## SLIDE N, **FIELD**, content (multi-line)"""
    errors = []
    slides = {}
    current_slide = None
    current_field = None
    
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        
        # Slide header: ## SLIDE N
        match = re.match(r'^##\s+SLIDE\s+(\d+)', stripped, re.IGNORECASE)
        if match:
            current_slide = int(match.group(1))
            slides[current_slide] = {}
            current_field = None
            i += 1
            continue
        
        if current_slide is None:
            i += 1
            continue
        
        # Field marker: **FIELD**
        if stripped.startswith('**') and stripped.endswith('**'):
            field = stripped.strip('*').upper()
            if field in ('HOOK', 'TITLE', 'CONTENT', 'HIGHLIGHT'):
                current_field = field
                slides[current_slide][field] = ""
            i += 1
            continue
        
        # Collect content for current field (multi-line support)
        if current_field and stripped:
            if slides[current_slide][current_field]:
                slides[current_slide][current_field] += " " + stripped
            else:
                slides[current_slide][current_field] = stripped
        
        i += 1
    
    # Validate
    if not slides:
        return False, ["No slides found"]
    
    nums = sorted(slides.keys())
    if nums[0] != 1:
        errors.append(f"First slide must be 1, got {nums[0]}")
    
    for i, num in enumerate(nums, 1):
        if num != i:
            errors.append(f"Gap in numbering: expected {i}, got {num}")
    
    if len(slides) > 10:
        errors.append(f"Too many slides: {len(slides)} (max 10)")
    
    required = {'HOOK', 'CONTENT', 'HIGHLIGHT'}
    for snum, data in slides.items():
        missing = required - set(data.keys())
        if missing:
            errors.append(f"Slide {snum}: Missing {missing}")
        for field, val in data.items():
            if not val or not val.strip():
                errors.append(f"Slide {snum}: Empty field '{field}'")
    
    return len(errors) == 0, errors


def _validate_new(lines: list[str]) -> tuple[bool, list[str]]:
    """New format: handle:, Slide N:, Badge:, Title:, Content:, Highlight:"""
    errors = []
    header = {}
    header_fields = {'handle', 'bgColor', 'textColor', 'accentColor', 'cardColor'}
    slides = {}
    current_slide = None
    current_field = None
    
    # Parse
    for line in lines:
        stripped = line.strip()
        
        # Header fields
        if ':' in stripped and 'Slide' not in stripped:
            key, val = stripped.split(':', 1)
            key = key.strip()
            val = val.strip()
            if key in header_fields:
                header[key] = val
            continue
        
        # Slide header
        match = re.match(r'^Slide\s+(\d+):', stripped)
        if match:
            current_slide = int(match.group(1))
            slides[current_slide] = {}
            current_field = None
            continue
        
        if current_slide is None:
            continue
        
        # Slide fields
        if ':' in stripped:
            field, val = stripped.split(':', 1)
            field = field.strip()
            val = val.strip()
            if field in ('Badge', 'Title', 'Content', 'Highlight'):
                current_field = field
                slides[current_slide][field] = val
            continue
        
        # Multi-line content
        if current_field == 'Content' and stripped:
            slides[current_slide]['Content'] += '\n' + stripped
    
    # Validate header
    if len(header) < 5:
        missing = header_fields - set(header.keys())
        errors.append(f"Missing header: {missing}")
    
    for key, val in header.items():
        if key in ('bgColor', 'textColor', 'accentColor', 'cardColor'):
            if not re.match(r'^#[0-9A-Fa-f]{6}$', val):
                errors.append(f"Invalid hex {key}: {val}")
        elif key == 'handle':
            if not val.startswith('@'):
                errors.append(f"Handle must start with @: {val}")
    
    # Validate slides
    if not slides:
        return False, ["No slides found"]
    
    nums = sorted(slides.keys())
    if nums[0] != 1:
        errors.append(f"First slide must be 1, got {nums[0]}")
    
    for i, num in enumerate(nums, 1):
        if num != i:
            errors.append(f"Gap in numbering: expected {i}, got {num}")
    
    if len(slides) > 10:
        errors.append(f"Too many slides: {len(slides)} (max 10)")
    
    required = {'Badge', 'Title', 'Content', 'Highlight'}
    for snum, data in slides.items():
        missing = required - set(data.keys())
        if missing:
            errors.append(f"Slide {snum}: Missing {missing}")
    
    return len(errors) == 0, errors


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 validate_carousel_format.py <file.txt>")
        sys.exit(1)
    
    filepath = sys.argv[1]
    is_valid, errors = validate_carousel(filepath)
    
    if is_valid:
        slide_count = len(re.findall(r'(?:^##\s+SLIDE|^Slide\s+\d+:)', 
                                      Path(filepath).read_text(),
                                      re.MULTILINE))
        print(f"✓ Format valid: {filepath}")
        print(f"  {slide_count} slides, all required fields present, no gaps.")
        sys.exit(0)
    else:
        print(f"✗ Format error in {filepath}:")
        for error in errors:
            print(f"  {error}")
        sys.exit(1)


if __name__ == '__main__':
    main()
