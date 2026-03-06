import json

subjects = ['python', 'de', 'etc', 'ci', 'dm', 'coa', 'python2', 'fsd2', 'toc']
for s in subjects:
    with open(f'questions/{s}.json', encoding='utf-8') as f:
        data = json.load(f)
    keys = sorted(data.keys())
    total = sum(len(v) for v in data.values())
    print(f'{s:10s}: {total:4d} MCQs | Keys: {keys}')

print('\nAll JSON files valid!')
