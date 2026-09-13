with open('test_mcq.py', 'r') as f:
    content = f.read()
    
content = content.replace('json\\n', '')
content = content.replace('\\n', '')

with open('test_mcq.py', 'w') as f:
    f.write(content)
