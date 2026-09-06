#!/usr/bin/env python3
"""
Carousel Input Validator — validates builder-input format files only.

Builder input format:
  Handle: @CompassEnglishAcademy
  BgColor: #RRGGBB
  TextColor: #RRGGBB
  [Optional: AccentColor, CardColor]

  Slide 1:
  Title: ...
  Content: ...
  Badge: ... (optional)
  Highlight: ... (optional)

  Slide 2:
  ...

Required: Handle, BgColor, TextColor, at least one Slide block
Each slide: Title and Content required; Badge/Highlight optional
Slides: numbered 1..N with no gaps
"""
import sys
import re

def validate_builder_input(filepath):
    """Validate carousel builder input file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return False, [f"Error reading file: {e}"]
    
    errors = []
    
    # Parse header
    lines = content.split('\n')
    header_idx = 0
    header = {}
    
    for i, line in enumerate(lines):
        if not line.strip():
            header_idx = i + 1
            break
        if ':' in line:
            key, value = line.split(':', 1)
            header[key.strip()] = value.strip()
    
    # Validate header
    required_header = ['Handle', 'BgColor', 'TextColor']
    for field in required_header:
        if field not in header:
            errors.append(f"Header missing required field: '{field}'")
        elif not header[field]:
            errors.append(f"Header field '{field}' is empty")
        elif field in ['BgColor', 'TextColor']:
            if not re.match(r'^#[0-9A-Fa-f]{6}$', header[field]):
                errors.append(f"Header field '{field}': invalid hex color '{header[field]}'")
    
    if header.get('Handle', '').startswith('@'):
        pass  # good
    else:
        errors.append(f"Header field 'Handle': must start with '@' (got '{header.get('Handle', '')}')")
    
    # Parse slides
    slides = {}
    current_slide = None
    
    for i in range(header_idx, len(lines)):
        line = lines[i]
        line_stripped = line.strip()
        
        if not line_stripped:
            continue
        
        # Detect Slide N:
        slide_match = re.match(r'^Slide\s+(\d+):', line_stripped)
        if slide_match:
            current_slide = int(slide_match.group(1))
            slides[current_slide] = {}
            continue
        
        # Detect field: Name: value
        if ':' in line_stripped and current_slide is not None:
            key, value = line_stripped.split(':', 1)
            key = key.strip()
            value = value.strip()
            if key in ['Title', 'Content', 'Badge', 'Highlight']:
                slides[current_slide][key] = value
    
    # Validate slides
    if not slides:
        errors.append("No slides found (expected 'Slide 1:', 'Slide 2:', etc.)")
    else:
        slide_nums = sorted(slides.keys())
        
        # Check numbering (1-indexed, no gaps)
        expected = list(range(1, max(slide_nums) + 1))
        if slide_nums != expected:
            missing = set(expected) - set(slide_nums)
            if missing:
                errors.append(f"Gap in slide numbering: missing Slide {min(missing)}")
        
        # Validate each slide
        for num in slide_nums:
            slide = slides[num]
            
            # Title and Content required
            if 'Title' not in slide or not slide['Title']:
                errors.append(f"Slide {num}: missing or empty 'Title'")
            if 'Content' not in slide or not slide['Content']:
                errors.append(f"Slide {num}: missing or empty 'Content'")
    
    return len(errors) == 0, errors

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 validate_carousel_builder_input.py <file>")
        sys.exit(1)
    
    filepath = sys.argv[1]
    valid, errors = validate_builder_input(filepath)
    
    if valid:
        print(f"✓ Format valid: {filepath}")
        sys.exit(0)
    else:
        print(f"✗ Format invalid: {filepath}")
        for error in errors:
            print(f"  {error}")
        sys.exit(1)
