import wikipedia
import re

wiki = wikipedia.page('Young Sheldon')
text = str(wiki.content)
text = text.replace('\n', '')
text = text.replace('=', '')
facts = text.split('.')

y = open('ysheldon.txt', 'w')
for f in facts:
    print(f)
    print('\n\n\n\n')
    y.write(f + '\n')

y.close()