try:
    with open('single_test_output.txt', 'r', encoding='utf-16') as f:
        content = f.read()
except UnicodeError:
    with open('single_test_output.txt', 'r', encoding='utf-8') as f:
        content = f.read()

# Find the error section
if 'ERRORS' in content:
    start = content.find('ERRORS')
    print(content[start:start+2000])
elif 'FAILURES' in content:
    start = content.find('FAILURES')
    print(content[start:start+2000])
else:
    print(content[:2000])
