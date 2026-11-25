# Fabrique la version publique : retire du répertoire les numéros marqués « Ne pas donner aux usagers » (w:1)
import re,sys
s=open(sys.argv[1]).read()
i=s.find('<script>\n{');n=0
def rm(m):
    global n;n+=1;return ''
head,body=s[:i],s[i:]
body=re.sub(r"\{n:'(?:[^'\\]|\\.)*'[^{}]*\bw:(?:1|true|!0)\b[^{}]*\},?",rm,body)
open(sys.argv[2],'w').write(head+body);print('retirés',n)
