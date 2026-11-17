# tiny-chess-01 engine (MIT). Mailbox board, side to move upper-case;
# alpha-beta + null move + quiescence, fixed node budget (no clock).
import json,os,urllib.request as U
E=os.environ['MAKEFUN_ENV_URL']
def P(p,o):return json.load(U.urlopen(U.Request(E+p,json.dumps(o).encode(),{'content-type':'application/json'})))
N,S,W,O=-10,10,-1,1
D={'P':(N,N+N,N+W,N+O),'N':(-21,-19,-12,-8,8,12,19,21),'B':(-11,-9,9,11),'R':(N,O,S,W)}
D['Q']=D['K']=D['B']+D['R']
V={'P':100,'N':320,'B':330,'R':500,'Q':900,'K':60000}
T={};R={}
for p,v in V.items():
 t=[0]*120
 for i in range(21,99):
  r=9-i//10;f=i%10-1;c=-abs(2*f-7)-abs(2*r-7)
  t[i]=v+{'P':2*r*r+8*(2<f<5)*(r>1),'N':3*c,'B':2*c,'R':12*(r==6),'Q':c,'K':(r==0)*(f!=3)*(f!=4)*20-12*r}[p]
 T[p]=t
M=50000
def G(b):
 for i,p in enumerate(b):
  if p.isupper():
   for d in D[p]:
    j=i+d
    while 1:
     q=b[j]
     if q.isspace()or q.isupper():break
     if p=='P':
      if d in(N,N+N)and q!='.':break
      if d==N+N and(not 80<i<89 or b[i+N]!='.'):break
      if d in(N+W,N+O)and q=='.':break
     yield i,j
     if p in'PNK'or q.islower():break
     j+=d
def X(b,s,i,j,r='Q'):
 p=b[i];q=b[j];s+=T[p][j]-T[p][i];b=list(b)
 if q.islower():s+=T[q.upper()][119-j]
 b[j]=p;b[i]='.'
 if p=='P':
  if j<29:b[j]=r;s+=T[r][j]-T['P'][j]
  if j-i in(9,11)and q=='.':b[j+S]='.';s+=T['P'][119-j-S]
 if p=='K'and abs(j-i)==2:
  k=i//10*10+(8 if j>i else 1);m=(i+j)//2;b[k]='.';b[m]='R';s+=T['R'][m]-T['R'][k]
 return''.join(b)[::-1].swapcase(),-s
def Y(b,i,j):
 p=b[i];q=b[j];return T[p][j]-T[p][i]+(T[q.upper()][119-j]if q.islower()else 0)
def A(b):return any(b[j]=='k'for i,j in G(b))
def Q(b,s,a,e):
 global n;n+=1
 if s>=e:return s
 a=max(a,s)
 for i,j in sorted((m for m in G(b)if b[m[1]].islower()or b[m[0]]=='P'and m[1]<29),key=lambda m:-V[b[m[1]].upper()if b[m[1]]!='.'else'P']+V[b[m[0]]]/1e5):
  if b[j]=='k':return M
  v=-Q(*X(b,s,i,j),-e,-a)
  if v>a:
   a=v
   if a>=e:break
 return a
def Z(b,s,d,a,e,y):
 global n;n+=1
 if n>L:1/0
 if y and b in H:return 0
 if d<1:return Q(b,s,a,e)
 t=R.get(b);m=None
 if t:
  m=t[3]
  if t[0]>=d and(t[2]==0 or t[2]>0 and t[1]>=e or t[2]<0 and t[1]<=a):return t[1]
 if y and d>2 and s>=e:
  v=-Z(b[::-1].swapcase(),-s,d-3,-e,1-e,y+1)
  if v>=e:return v
 o=a;w=-M-1;c=None
 for i,j in sorted(G(b),key=lambda k:(k!=m,-Y(b,*k))):
  if b[j]=='k':return M
  v=-Z(*X(b,s,i,j),d-1,-e,-max(a,w),y+1)
  if v>w:
   w=v;c=(i,j)
   if w>=e:break
 if w==-M:w=-M+y if A(b[::-1].swapcase())else 0
 R[b]=(d,w,(w>=e)-(w<=o),c)
 return w
def C(u,k):
 x=lambda s:(10-int(s[1]))*10+ord(s[0])-96
 i,j=x(u),x(u[2:4])
 return(119-i,119-j)if k else(i,j)
while 1:
 g=P('/game',{})
 if g['status']=='done':break
 H=set()
 while g['status']=='your_move':
  F=g['fen'].split();k=F[1]=='b';b=' '*9+'\n'
  b=b*2+''.join(' '+''.join('.'*int(c)if c.isdigit()else c for c in r)+'\n'for r in F[0].split('/'))+b*2
  if k:b=b[::-1].swapcase()
  s=sum(T[p][i]if p.isupper()else-T[p.upper()][119-i]for i,p in enumerate(b)if p.isalpha())
  H.add(b)
  if len(R)>4e5:R.clear()
  ms=[(u,)+C(u,k)for u in g['legal_moves']];n=0;L=5e5;bm=ms[0]
  for d in range(1,30):
   if n>1.5e5:break
   try:
    w=-M-1
    for u,i,j in sorted(ms,key=lambda m:m!=bm):
     v=-Z(*X(b,s,i,j,(u[4:]or'q').upper()),d-1,-M-1,-w,1)
     if v>w:w=v;c=(u,i,j)
    bm=c
   except ZeroDivisionError:break
  g=P('/move',{'game':g['game'],'move':bm[0]})
