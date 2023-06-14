import os
from wordfilter import Wordfilter

classes_path = os.path.expanduser('./file/badwords_zh.txt')
with open(classes_path, 'r', encoding='UTF-8') as f:
    badwords_list = f.readlines()
badwords_list = [c.strip() for c in badwords_list]
print(badwords_list)

wordfilter = Wordfilter()
print(wordfilter.blacklisted('does this string have a bad word in it?'))  # False

# clear the list entirely
wordfilter.clearList()

# add new words
wordfilter.addWords(badwords_list)
print(wordfilter.blacklisted('雪豹闭嘴'))  # True
