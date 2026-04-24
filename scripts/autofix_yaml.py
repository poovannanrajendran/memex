import os
import re

def fix_yaml_titles():
    print("Scanning wiki for invalid YAML titles...")
    wiki_root = 'wiki'
    fixed_count = 0
    
    # Pattern to find title: "..." with unescaped internal quotes
    # This is tricky with regex, so we'll use a more surgical line-by-line approach
    
    for root, dirs, files in os.walk(wiki_root):
        for name in files:
            if name.endswith('.md'):
                fpath = os.path.join(root, name)
                with open(fpath, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                changed = False
                new_lines = []
                for line in lines:
                    if line.startswith('title: "') and line.strip().endswith('"'):
                        # Extract the content between the first and last quote
                        # Example: title: "A whole new meaning to "mini-me""
                        # We want: A whole new meaning to "mini-me"
                        content_match = re.match(r'^title: "(.*)"\s*$', line)
                        if content_match:
                            content = content_match.group(1)
                            # If there are internal unescaped double quotes
                            # (excluding the ones at the very start/end which we already handled)
                            
                            # Simple fix: Replace all " with \" then put back the outer ones
                            # But wait, we don't want to double escape if they are already escaped
                            
                            # Best approach: Strip all escapes, then escape all "
                            clean_content = content.replace('\\"', '"')
                            if '"' in clean_content:
                                escaped_content = clean_content.replace('"', '\\"')
                                new_line = f'title: "{escaped_content}"\n'
                                if new_line != line:
                                    line = new_line
                                    changed = True
                    
                    new_lines.append(line)
                
                if changed:
                    with open(fpath, 'w', encoding='utf-8') as f:
                        f.writelines(new_lines)
                    print(f"Fixed title in: {fpath}")
                    fixed_count += 1

    print(f"Finished. Fixed {fixed_count} files.")

if __name__ == "__main__":
    fix_yaml_titles()
