#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NEKO HQ (terminal) — Claude CLI kedi kafesi, dogrudan terminalde.
Warp'ta bir panede `python3 neko_tui.py` (ya da `neko`), baska panede `claude`.
Her oturum bir kedi olur; calisinca yazar, sessizlikte uyur.
Arayuzden: ok tuslari ile kedi sec, [n] isim, [c] renk, [h] sapka, [q] cik.
Yalnizca Python standart kutuphanesi (macOS/Linux/Warp).
"""
import os, sys, json, time, re, select, argparse, shutil
try:
    import termios, tty
    HAVE_TTY=True
except Exception:
    HAVE_TTY=False

W, H = 200, 60
COUNTER_Y = 44
HOME=os.path.expanduser("~"); APP_DIR=os.path.join(HOME,".neko-hq")
LOG=os.path.join(APP_DIR,"activity.log"); OVR_FILE=os.path.join(APP_DIR,"cats.json")
SETTINGS=os.path.join(HOME,".claude","settings.json")
SELF=os.path.abspath(__file__); PY=sys.executable or "python3"; MARK="# neko-hq"

NAMES=["Pamuk","Zeytin","Boncuk","Sansli","Mirnav","Duman","Tarcin","Karamel"]
HAT_ORDER=["santa","bow","beanie","party","crown","cap","flower","none"]
HATS=["none","santa","party","bow","beanie","crown","cap","flower"]
PAL_HEX=[
 {"F":"#f0a64b","d":"#cf7f2c","l":"#ffc878","B":"#fce3c2","I":"#f3a9bb","N":"#e07a92","iris":"#7fb24a","s":"#cf7f2c"},
 {"F":"#9aa3b2","d":"#79839a","l":"#c2cad6","B":"#e6ebf2","I":"#f3a9bb","N":"#d97f96","iris":"#6fae9a","s":"#79839a"},
 {"F":"#3a3e48","d":"#24262e","l":"#565b6b","B":"#f1f2f4","I":"#e79aa8","N":"#d97f96","iris":"#8fd06a","s":None},
 {"F":"#efe6d3","d":"#cfc3a8","l":"#fffaf0","B":"#fffaf0","I":"#f3a9bb","N":"#e07a92","iris":"#caa24a","s":None},
 {"F":"#e7c27a","d":"#b98e44","l":"#f7df9f","B":"#fff7ea","I":"#f3a9bb","N":"#e07a92","iris":"#7faf6a","s":"#9a6b3a"},
 {"F":"#b9897a","d":"#956a5e","l":"#d8b0a3","B":"#f4e7df","I":"#f3a9bb","N":"#d97f96","iris":"#6fae9a","s":"#7a5446"},
]
TOOL_TASKS={"Bash":"terminalde komut","Read":"dosya okuyor","Edit":"kod yaziyor","Write":"kod yaziyor",
 "MultiEdit":"kod duzenliyor","Grep":"kodda ariyor","Glob":"dosya tariyor","WebSearch":"web'de ariyor",
 "WebFetch":"sayfa getiriyor","Task":"alt-ajan acti","TodoWrite":"liste yaziyor"}
TOOL_SHORT={"Bash":"komut","Read":"okuyor","Edit":"yaziyor","Write":"yaziyor","MultiEdit":"duzenliyor",
 "Grep":"ariyor","Glob":"tariyor","WebSearch":"web","WebFetch":"web","Task":"alt-ajan","TodoWrite":"liste"}

def hx(s):
    s=s.lstrip("#"); return (int(s[0:2],16),int(s[2:4],16),int(s[4:6],16))
PAL=[{k:(hx(v) if v else None) for k,v in p.items()} for p in PAL_HEX]

OUT=(34,26,18); WHT=(252,252,252); PUP=(20,22,30)
WALL=[(247,235,214),(239,225,201),(229,212,186)]
COUNTER=(150,98,56); COUNTERT=(176,120,72); COUNTERD=(96,60,32); COUNTERE=(70,44,22)
SIGN=(94,58,30); SIGNL=(122,74,38); SIGNT=(243,220,174)
SKY=[(150,205,242),(176,216,245)]; SUN=(255,209,74); CLOUD=(255,255,255); BLDG=(176,150,170); BLDG2=(150,124,150)
TREE=(74,165,82); TREED=(47,122,52); FRAME=(110,74,40); SILL=(138,94,54)
CB=(40,52,46); CBF=(110,74,40); CHALK=(244,239,230); CH1=(244,193,208); CH2=(191,224,194); CH3=(188,214,240)
SHELF=(122,80,44); SHELFD=(90,58,32)
POT=(194,98,47); POTD=(151,67,33); LEAF=(74,165,82); LEAFD=(47,122,52); LEAFL=(98,193,104); VINE=(63,143,68)
MACH=(211,79,79); MACHD=(168,58,58); CHROME=(201,206,214); CAKE=(247,197,214); CAKEI=(232,154,176); CHERRY=(210,59,84); CREAM=(255,244,234)
LAPC=(52,57,74); LAPK=(207,210,216); SCR=(16,35,27); CODE=(123,224,143); CODEB=(111,182,239)
MUG=(217,83,79); STEAM=(238,246,255)
F1=(239,138,160); F2=(242,196,99); F3=(143,208,160); F4=(143,191,230); F5=(198,156,224)
BADGE=(247,236,206); SELC=(255,214,82)

DIGITS={"1":["010","110","010","010","111"],"2":["111","001","111","100","111"],"3":["111","001","111","001","111"],
"4":["101","101","111","001","001"],"5":["111","100","111","001","111"],"6":["111","100","111","101","111"],
"7":["111","001","010","010","010"],"8":["111","101","111","101","111"]}

class Buf:
    def __init__(s,w,h): s.w=w; s.h=h; s.d=[[(0,0,0) for _ in range(w)] for _ in range(h)]
    def band(s,y0,y1,c):
        for y in range(max(0,y0),min(s.h,y1)):
            r=s.d[y]
            for x in range(s.w): r[x]=c
    def px(s,x,y,w,h,c):
        if c is None: return
        x0=max(0,int(x)); y0=max(0,int(y)); x1=min(s.w,int(x+w)); y1=min(s.h,int(y+h))
        for yy in range(y0,y1):
            r=s.d[yy]
            for xx in range(x0,x1): r[xx]=c

def rrect(b,x,y,w,h,fill,out):
    for j in range(h):
        ins=2 if (j==0 or j==h-1) else (1 if (j==1 or j==h-2) else 0)
        b.px(x+ins,y+j,w-2*ins,1,out)
    for j in range(1,h-1):
        ins=2 if (j==1 or j==h-2) else (1 if (j==2 or j==h-3) else 0)
        b.px(x+1+ins,y+j,w-2-2*ins,1,fill)

def digit(b,x,y,ch,col):
    g=DIGITS.get(ch)
    if not g: return
    for r in range(5):
        for c in range(3):
            if g[r][c]=="1": b.px(x+c,y+r,1,1,col)

b_step=0

def cat(b,ox,oy,P,pose,t):
    F,d,l,B,I,N,iris,s=P["F"],P["d"],P["l"],P["B"],P["I"],P["N"],P["iris"],P["s"]
    blink=(t//9)%13==0
    b.px(ox+4,oy+22,13,1,(70,48,28))
    # tail
    b.px(ox+15,oy+15,4,2,OUT); b.px(ox+15,oy+15,3,1,F)
    b.px(ox+17,oy+10,3,6,OUT); b.px(ox+17,oy+11,2,5,F)
    b.px(ox+15,oy+8,3,4,OUT);  b.px(ox+15,oy+9,2,3,F)
    if s: b.px(ox+17,oy+12,2,1,s); b.px(ox+15,oy+9,2,1,s)
    # body
    rrect(b,ox+4,oy+14,12,8,F,OUT)
    b.px(ox+7,oy+16,6,5,B)
    if s: b.px(ox+5,oy+16,1,5,s); b.px(ox+14,oy+16,1,5,s)
    # ears
    b.px(ox+3,oy,3,1,OUT); b.px(ox+2,oy+1,5,1,OUT); b.px(ox+3,oy+1,3,1,F); b.px(ox+3,oy+2,4,2,F); b.px(ox+4,oy+2,2,2,I)
    b.px(ox+14,oy,3,1,OUT); b.px(ox+13,oy+1,5,1,OUT); b.px(ox+14,oy+1,3,1,F); b.px(ox+13,oy+2,4,2,F); b.px(ox+14,oy+2,2,2,I)
    # head
    rrect(b,ox+2,oy+3,16,12,F,OUT)
    b.px(ox+4,oy+4,12,1,l)
    b.px(ox+1,oy+9,1,3,F); b.px(ox+18,oy+9,1,3,F)
    b.px(ox+4,oy+13,12,1,d)
    if s: b.px(ox+8,oy+4,2,3,s); b.px(ox+5,oy+5,1,2,s); b.px(ox+13,oy+5,1,2,s)
    # muzzle
    b.px(ox+5,oy+10,10,4,B)
    # eyes
    ey=oy+6; exL=ox+4; exR=ox+11
    if pose=="sleep" or blink:
        b.px(exL,ey+3,4,1,OUT); b.px(exL,ey+2,1,1,OUT); b.px(exL+3,ey+2,1,1,OUT)
        b.px(exR,ey+3,4,1,OUT); b.px(exR,ey+2,1,1,OUT); b.px(exR+3,ey+2,1,1,OUT)
    else:
        dd=1 if pose=="read" else 0
        b.px(exL,ey,4,5,WHT); b.px(exR,ey,4,5,WHT)
        b.px(exL,ey,4,1,OUT); b.px(exR,ey,4,1,OUT)
        b.px(exL,ey+1+dd,4,4-dd,iris); b.px(exR,ey+1+dd,4,4-dd,iris)
        b.px(exL+1,ey+2+dd,2,2,PUP); b.px(exR+1,ey+2+dd,2,2,PUP)
        b.px(exL+1,ey+1,1,1,WHT); b.px(exR+1,ey+1,1,1,WHT)
        b.px(exL+2,ey+3,1,1,(210,230,255)); b.px(exR+2,ey+3,1,1,(210,230,255))
    # nose + smile
    b.px(ox+9,oy+11,2,1,N); b.px(ox+10,oy+12,1,1,N)
    b.px(ox+7,oy+13,1,1,d); b.px(ox+12,oy+13,1,1,d); b.px(ox+9,oy+13,2,1,d)
    # blush
    b.px(ox+3,oy+11,2,1,(244,176,188)); b.px(ox+15,oy+11,2,1,(244,176,188))
    # whiskers
    b.px(ox+0,oy+10,3,1,WHT); b.px(ox+0,oy+12,3,1,WHT)
    b.px(ox+17,oy+10,3,1,WHT); b.px(ox+17,oy+12,3,1,WHT)
    # paws
    py=oy+21
    if pose=="walk":
        k=(t//2)%2
        b.px(ox+5,py,3,1,F); b.px(ox+11,py,3,1,F)
        if k==0: b.px(ox+4,py,1,1,F)
        else: b.px(ox+13,py,1,1,F)
    elif pose=="read":
        b.px(ox+5,oy+17,10,5,(233,231,223)); b.px(ox+9,oy+17,1,5,(196,193,184))
        b.px(ox+5,py,3,1,F); b.px(ox+11,py,3,1,F)
    else:
        k=(t//3)%2
        b.px(ox+5,py-(1 if (pose=="type" and k==0) else 0),3,1,F)
        b.px(ox+11,py-(1 if (pose=="type" and k==1) else 0),3,1,F)
    if pose=="sleep" and (t//12)%2==0:
        b.px(ox+18,oy+1,1,1,OUT); b.px(ox+20,oy-2,1,1,OUT)
    if pose=="type" and (t//10)%3==0:
        b.px(ox+16,oy-2,6,2,WHT); b.px(ox+17,oy-1,1,1,OUT); b.px(ox+19,oy-1,1,1,OUT)

def item(b,ox,oy,kind):
    if not kind or kind=="none": return
    cx=ox+10
    if kind=="santa":
        b.px(cx-1,oy-4,2,1,(214,64,64)); b.px(cx-2,oy-3,4,1,(214,64,64))
        b.px(cx-3,oy-2,6,1,(214,64,64)); b.px(cx-4,oy-1,8,1,(214,64,64)); b.px(cx-5,oy,10,1,(214,64,64))
        b.px(cx-4,oy-1,3,1,(176,42,42))
        b.px(cx-6,oy+1,12,1,WHT)
        b.px(cx,oy-5,3,2,WHT)
    elif kind=="bow":
        b.px(cx-6,oy-2,4,4,F1); b.px(cx+1,oy-2,4,4,F1); b.px(cx-2,oy-1,3,2,(210,90,120)); b.px(cx-1,oy-2,1,4,(210,90,120))
    elif kind=="beanie":
        b.px(cx-6,oy,13,1,(70,128,150)); b.px(cx-5,oy-1,11,1,(96,158,180)); b.px(cx-3,oy-3,7,2,(96,158,180)); b.px(cx-1,oy-5,3,2,WHT); b.px(cx-6,oy+1,13,1,(58,110,132))
    elif kind=="party":
        b.px(cx,oy-6,1,1,WHT); b.px(cx,oy-5,1,1,F2); b.px(cx-1,oy-4,3,1,F1); b.px(cx-2,oy-3,5,1,F3); b.px(cx-3,oy-2,7,1,F4); b.px(cx-4,oy-1,9,1,F2); b.px(cx-5,oy,11,1,F1)
    elif kind=="crown":
        c=(240,200,70); b.px(cx-5,oy-1,11,2,c); b.px(cx-5,oy-4,2,3,c); b.px(cx-1,oy-4,2,3,c); b.px(cx+4,oy-4,2,3,c)
        b.px(cx-5,oy-5,1,1,F1); b.px(cx,oy-5,1,1,F4); b.px(cx+5,oy-5,1,1,F3)
    elif kind=="cap":
        b.px(cx-5,oy-1,11,2,(70,112,196)); b.px(cx-4,oy-3,8,2,(86,128,210)); b.px(cx+5,oy,5,1,(56,96,176))
    elif kind=="flower":
        b.px(cx-8,oy,2,2,F1); b.px(cx-9,oy+1,1,1,F1); b.px(cx-6,oy+1,1,1,F1); b.px(cx-8,oy-1,1,1,F1); b.px(cx-7,oy,1,1,F2)

def laptop(b,lx,ly,tool):
    sc=SCR; cc=CODE
    if tool=="Bash": sc=(12,18,14)
    elif tool in ("WebSearch","WebFetch"): sc=(14,27,40); cc=CODEB
    b.px(lx,ly-6,14,7,LAPC); b.px(lx+1,ly-5,12,5,sc)
    for q in range(3):
        ax=lx+2+((b_step+q*3)%9); b.px(ax,ly-4+q,4,1,cc)
    b.px(lx-1,ly+1,16,2,LAPK); b.px(lx-1,ly+1,16,1,(224,226,230))

def window(b,X,Y,w,h):
    b.px(X-2,Y-2,w+4,h+4,FRAME)
    b.px(X,Y,w,h*2//3,SKY[0]); b.px(X,Y+h*2//3,w,h-h*2//3,SKY[1])
    b.px(X+w-9,Y+2,6,6,SUN); b.px(X+4,Y+6,9,2,CLOUD); b.px(X+7,Y+4,7,2,CLOUD)
    b.px(X+3,Y+h-9,6,9,BLDG); b.px(X+w-11,Y+h-7,7,7,BLDG2); b.px(X+5,Y+h-7,1,2,(120,150,200)); b.px(X+w-9,Y+h-5,1,2,(120,150,200))
    b.px(X+w//2-8,Y+h-6,5,6,TREED); b.px(X+w//2-10,Y+h-10,8,5,TREE)
    b.px(X+w//2-1,Y,1,h,FRAME); b.px(X,Y+h//3,w,1,FRAME); b.px(X,Y+h*2//3,w,1,FRAME)
    b.px(X-3,Y+h+1,w+6,2,SILL)

def chalk(b,X,Y,w,h):
    b.px(X-2,Y-2,w+4,h+4,CBF); b.px(X,Y,w,h,CB); b.px(X,Y,w,1,(58,72,64))
    b.px(X+4,Y+3,w-12,2,CHALK)
    b.px(X+4,Y+8,2,2,CH1); b.px(X+8,Y+9,w-18,1,CHALK)
    b.px(X+4,Y+13,2,2,CH2); b.px(X+8,Y+14,w-22,1,CHALK)
    b.px(X+4,Y+18,2,2,CH3); b.px(X+8,Y+19,w-16,1,CHALK)
    b.px(X+w-9,Y+3,6,5,CHALK); b.px(X+w-3,Y+4,1,3,CHALK); b.px(X+w-8,Y+2,1,1,STEAM)

def shelves(b,X,Y):
    cups=[(217,83,79),(98,158,200),(110,180,120),(240,190,90),(198,156,224)]
    for i in range(2):
        yy=Y+i*9
        b.px(X,yy,30,1,SHELF); b.px(X,yy+1,30,1,SHELFD)
        for j in range(5):
            cx=X+1+j*6; c=cups[(i*5+j)%5]; b.px(cx,yy-4,4,4,c); b.px(cx+4,yy-3,1,2,c); b.px(cx,yy-4,4,1,(255,255,255))
    b.px(X+22,Y-5,8,5,LEAF); b.px(X+24,Y-2,4,3,POT)

def hang(b,X):
    b.px(X+2,0,1,5,(120,98,72)); b.px(X-1,5,8,3,POT); b.px(X-1,5,8,1,(216,114,66))
    b.px(X,8,1,4,VINE); b.px(X+2,8,1,5,VINE); b.px(X+4,8,1,3,VINE); b.px(X+6,8,1,4,VINE)
    b.px(X+1,11,1,1,LEAFL); b.px(X+5,12,1,1,LEAFL)

def bunting(b):
    b.px(0,5,W,1,(120,108,86)); cols=[F1,F2,F3,F4,F5]; i=0
    for fx in range(4,W-7,16):
        c=cols[i%5]; i+=1; b.px(fx,6,7,1,c); b.px(fx+1,7,5,1,c); b.px(fx+2,8,3,1,c); b.px(fx+3,9,1,1,c)

def sign(b):
    X=80; b.px(X,0,40,11,SIGN); b.px(X,0,40,1,SIGNL); b.px(X,10,40,1,(62,38,15)); b.px(X+1,1,38,1,(116,70,34))
    b.px(X+9,5,4,2,SIGNT); b.px(X+8,3,1,1,SIGNT); b.px(X+10,2,1,1,SIGNT); b.px(X+13,2,1,1,SIGNT); b.px(X+16,3,1,1,SIGNT)
    b.px(X+21,4,6,5,CREAM); b.px(X+27,5,1,2,CREAM); b.px(X+22,3,1,1,STEAM)
    b.px(X+31,3,2,2,F1); b.px(X+34,3,2,2,F1); b.px(X+31,5,5,1,F1); b.px(X+32,6,3,1,F1); b.px(X+33,7,1,1,F1)

def station(b):
    b.px(4,COUNTER_Y-15,20,15,MACH); b.px(4,COUNTER_Y-15,20,1,(232,110,110)); b.px(4,COUNTER_Y-15,1,15,(232,110,110))
    b.px(7,COUNTER_Y-12,14,5,CHROME); b.px(8,COUNTER_Y-11,12,3,(14,28,22)); b.px(9,COUNTER_Y-10,2,1,(120,200,150))
    b.px(12,COUNTER_Y-5,2,4,(150,156,164)); b.px(11,COUNTER_Y-1,4,1,(150,156,164))
    b.px(20,COUNTER_Y-14,3,2,(255,231,154) if (b_step%20<10) else (200,160,60))
    if (b_step//5)%2==0: b.px(10,COUNTER_Y-17,1,2,STEAM)
    b.px(28,COUNTER_Y-4,14,3,CREAM); b.px(34,COUNTER_Y-1,2,1,CREAM)
    rrect(b,30,COUNTER_Y-9,11,5,CAKE,CAKEI); b.px(31,COUNTER_Y-8,9,1,CREAM); b.px(35,COUNTER_Y-11,1,2,CHERRY); b.px(33,COUNTER_Y-7,1,1,CAKEI)

def cafe_back(b):
    b.band(0,18,WALL[0]); b.band(18,32,WALL[1]); b.band(32,COUNTER_Y,WALL[2])
    bunting(b); sign(b)
    window(b,8,11,38,18)
    chalk(b,78,11,46,18)
    shelves(b,152,14)
    hang(b,56); hang(b,140)
    station(b)
    b.px(0,COUNTER_Y-1,W,2,COUNTERT)

def counter_front(b, agents, pos):
    b.px(0,COUNTER_Y+1,W,H-(COUNTER_Y+1),COUNTER)
    b.px(0,COUNTER_Y+1,W,1,(168,112,66))
    for x in range(0,W,20): b.px(x,COUNTER_Y+2,1,H-(COUNTER_Y+2),COUNTERD)
    b.px(0,H-2,W,2,COUNTERE)
    for i,(cx,_) in enumerate(pos):
        digit(b,cx-1,COUNTER_Y+5,str(agents[i]["slot"]+1),BADGE)

def layout(n):
    if n<=0: return []
    xs,xe=44,190
    if n==1: return [((xs+xe)//2,COUNTER_Y)]
    return [(int(xs+(xe-xs)*i/(n-1)),COUNTER_Y) for i in range(n)]

def workstation(b,cx,P,busy,tool,hat,selected):
    pose="sleep"
    if busy>0: pose="read" if tool in ("Read","WebSearch") else "type"
    oy=COUNTER_Y-20
    cat(b,cx-10,oy,P,pose,b_step)
    item(b,cx-10,oy,hat)
    if selected:
        b.px(cx-2,oy-9,5,1,SELC); b.px(cx-1,oy-8,3,1,SELC); b.px(cx,oy-7,1,1,SELC)
    if pose!="read": laptop(b,cx-7,COUNTER_Y-1,tool)
    b.px(cx+8,COUNTER_Y-5,3,4,MUG); b.px(cx+8,COUNTER_Y-5,3,1,(235,110,106))
    if busy>0 and (b_step//6)%2==0: b.px(cx+9,COUNTER_Y-7,1,1,STEAM)

def draw_office(b, agents, sel):
    cafe_back(b)
    pos=layout(len(agents))
    for i,(cx,_) in enumerate(pos):
        a=agents[i]; workstation(b,cx,a["pal"],a["busy"],a["tool"],a["hat"], i==sel)
    counter_front(b, agents, pos)

# ---------- store ----------
class Store:
    def __init__(s,path): s.path=path; s.offset=0; s.buf=b""; s.sessions={}; s.glob=[]; s.counter=0
    def poll(s,now):
        try: st=os.stat(s.path)
        except OSError: return
        if st.st_size<s.offset: s.offset=0; s.buf=b""
        if st.st_size!=s.offset:
            try:
                with open(s.path,"rb") as f: f.seek(s.offset); data=f.read(); s.offset=f.tell()
                s.buf+=data; parts=s.buf.split(b"\n"); s.buf=parts.pop()
                for ln in parts: s._p(ln,now)
            except OSError: pass
    def _p(s,ln,now):
        if not ln.strip(): return
        st=ln.decode("utf-8","ignore"); ts=now; rest=st; sp=st.find(" ")
        if sp>0 and st[:sp].isdigit():
            try: ts=int(st[:sp])
            except: ts=now
            rest=st[sp+1:]
        sid=ev=tool=None
        try:
            d=json.loads(rest); sid=d.get("session_id"); ev=d.get("hook_event_name"); tool=d.get("tool_name")
        except Exception:
            m=re.search(r'"session_id"\s*:\s*"([^"]+)"',rest); sid=m.group(1) if m else None
            m=re.search(r'"tool_name"\s*:\s*"([^"]+)"',rest); tool=m.group(1) if m else None
        sid=sid or "default"; se=s.sessions.get(sid)
        if se is None: se={"first":ts,"slot":s.counter,"events":[]}; s.counter+=1; s.sessions[sid]=se
        se["events"].append((ts,ev or "?",tool)); s.glob.append((ts,ev or "?",tool))
    def prune(s,now):
        for sid in list(s.sessions):
            evs=[e for e in s.sessions[sid]["events"] if e[0]>=now-130]
            if not evs: del s.sessions[sid]
            else: s.sessions[sid]["events"]=evs
        s.glob=[e for e in s.glob if e[0]>=now-60]
    def agents(s,now):
        out=[]
        for sid,se in sorted(s.sessions.items(),key=lambda kv:(kv[1]["first"],kv[0])):
            evs=se["events"]
            if not evs or evs[-1][0]<now-130: continue
            busy=max(0,min(5,sum(1 for e in evs if e[0]>=now-8)))
            tool=None
            for ts,ev,tl in evs:
                if ts>=now-5 and tl: tool=tl
            out.append({"slot":se["slot"],"busy":busy,"tool":tool})
            if len(out)>=8: break
        return out
    def headline(s,now):
        pr=any(ev=="UserPromptSubmit" and ts>=now-4 for ts,ev,_ in s.glob)
        best=None
        for ts,ev,tool in s.glob:
            if ts>=now-5 and (best is None or ts>=best[0]): best=(ts,ev,tool)
        ev,tool=(best[1],best[2]) if best else (None,None)
        if pr: return "yeni gorev geldi!"
        if ev in ("Stop","SubagentStop"): return "is tamamlandi"
        t=TOOL_TASKS.get(tool)
        return t if t else ("kafe sakin - kediler uyukluyor" if not tool else str(tool))

def load_ovr():
    try:
        with open(OVR_FILE,encoding="utf-8") as f: return json.load(f)
    except Exception: return {}
def save_ovr(o):
    try:
        os.makedirs(APP_DIR,exist_ok=True)
        with open(OVR_FILE,"w",encoding="utf-8") as f: json.dump(o,f,ensure_ascii=False)
    except Exception: pass
def resolve(agents,ovr):
    out=[]
    for a in agents:
        slot=a["slot"]; o=ovr.get(str(slot),{})
        name=o.get("name") or NAMES[slot%len(NAMES)]
        ci=o.get("color"); ci=ci if isinstance(ci,int) else slot%len(PAL)
        hat=o.get("hat") or HAT_ORDER[slot%len(HAT_ORDER)]
        a2=dict(a); a2["name"]=name; a2["pal"]=PAL[ci%len(PAL)]; a2["ci"]=ci%len(PAL); a2["hat"]=hat; out.append(a2)
    return out

DSC=[(3,0),(2,1),(3,3),(3,5),(3.5,8),(3,2)]; DTOT=sum(x[0] for x in DSC); DTOOLS=["Edit","Bash","WebSearch","Read","Write"]
def demo_agents(now):
    a=now%DTOT; acc=0; n=0
    for d,nn in DSC:
        acc+=d
        if a<acc: n=nn; break
    return [{"slot":i,"busy":0 if (int(now/1.3+i)%5==0) else 3+(i%3),"tool":None if (int(now/1.3+i)%5==0) else DTOOLS[(i+int(now/1.7))%len(DTOOLS)]} for i in range(n)]

def render_terminal(b):
    HALF="\u2580"; rows=[]
    for ry in range(0,b.h,2):
        top=b.d[ry]; bot=b.d[ry+1] if ry+1<b.h else top; line=[]
        for x in range(b.w):
            tr,tg,tb=top[x]; br,bg,bb=bot[x]
            line.append("\x1b[38;2;%d;%d;%d;48;2;%d;%d;%dm%s"%(tr,tg,tb,br,bg,bb,HALF))
        rows.append("".join(line)+"\x1b[0m")
    return rows
def render_ascii(b):
    ramp=" .:-=+*#%@"; rows=[]
    for y in range(b.h):
        rows.append("".join(ramp[min(9,(r*299+g*587+bl*114)//1000*10//256)] for r,g,bl in b.d[y]))
    return rows
def render_png(b,path,scale=6):
    from PIL import Image
    img=Image.new("RGB",(b.w,b.h)); px=img.load()
    for y in range(b.h):
        for x in range(b.w): px[x,y]=b.d[y][x]
    img.resize((b.w*scale,b.h*scale),Image.NEAREST).save(path)

# ---------- hooks ----------
HOOK_CMD=('mkdir -p "$HOME/.neko-hq" && '
 '{ printf \'%s \' "$(date +%s)"; cat | tr -d \'\\n\'; printf \'\\n\'; } >> "$HOME/.neko-hq/activity.log" '+MARK)
HEVENTS=[("UserPromptSubmit",False),("PreToolUse",True),("Stop",False),("SubagentStop",False)]
def _blk(needs): return ({"matcher":"","hooks":[{"type":"command","command":HOOK_CMD}]} if needs else {"hooks":[{"type":"command","command":HOOK_CMD}]})
def _has(lst): return any(MARK in (h.get("command") or "") for x in lst for h in x.get("hooks",[]))
def install_hooks():
    data={}
    if os.path.exists(SETTINGS):
        try:
            with open(SETTINGS,encoding="utf-8") as f: t=f.read().strip(); data=json.loads(t) if t else {}
        except Exception as e: print("ayar okunamadi:",e); return
    hk=data.setdefault("hooks",{}); add=0
    for ev,needs in HEVENTS:
        lst=hk.setdefault(ev,[])
        if not _has(lst): lst.append(_blk(needs)); add+=1
    if add==0: print("• Hook'lar zaten kurulu."); return
    os.makedirs(os.path.dirname(SETTINGS),exist_ok=True)
    if os.path.exists(SETTINGS): shutil.copyfile(SETTINGS,SETTINGS+".bak")
    with open(SETTINGS,"w",encoding="utf-8") as f: json.dump(data,f,indent=2,ensure_ascii=False); f.write("\n")
    print("• Hook'lar kuruldu (%d). Claude Code'u yeniden baslat (veya /hooks)."%add)
def uninstall_hooks():
    if not os.path.exists(SETTINGS): print("ayar yok."); return
    try:
        with open(SETTINGS,encoding="utf-8") as f: data=json.loads(f.read() or "{}")
    except Exception: print("ayar okunamadi."); return
    hk=data.get("hooks",{}); rm=0
    for ev,_ in HEVENTS:
        if ev in hk:
            new=[x for x in hk[ev] if not _has([x])]; rm+=len(hk[ev])-len(new)
            if new: hk[ev]=new
            else: del hk[ev]
    if not hk: data.pop("hooks",None)
    with open(SETTINGS,"w",encoding="utf-8") as f: json.dump(data,f,indent=2,ensure_ascii=False); f.write("\n")
    print("• Hook'lar kaldirildi (%d)."%rm)

# ---------- UI ----------
def meter(busy): return "".join("#" if i<busy else "." for i in range(5))
NEED_ROWS=H//2+5
def build_screen(b,agents,headline,sel,mode,namebuf,cols,rows):
    if cols<W or rows<NEED_ROWS:
        return "\n".join(["","  Terminali biraz buyut:","  en az %d sutun x %d satir gerekli."%(W,NEED_ROWS),
                          "  (su an %d x %d)"%(cols,rows),"","  Warp'ta pane'i genislet."])
    out=[]
    out.append("\x1b[1m"+("  NEKO HQ   yogunluk %s   |  %s"%(meter(max([a['busy'] for a in agents],default=0)),headline))[:cols]+"\x1b[0m")
    out+=render_terminal(b)
    out.append("")
    if not agents:
        out.append("  (henuz kedi yok — yan panede `claude` calistirip soru sor)")
    else:
        segs=[]
        for i,a in enumerate(agents):
            r,g,bl=a["pal"]["F"]
            dot=("\x1b[38;2;%d;%d;%dm\u25cf\x1b[0m"%(r,g,bl)) if a["busy"]>0 else "\x1b[2m\u25cb\x1b[0m"
            if i==sel and mode=="name": nm="["+namebuf+"\u2588]"
            else: nm=a["name"]
            seg=" %d%s%s "%(a["slot"]+1,dot,nm[:10])
            if i==sel: seg="\x1b[7m"+seg+"\x1b[0m"
            segs.append(seg)
        out.append("  "+" ".join(segs))
        st=TOOL_TASKS.get(agents[sel]["tool"],"calisiyor") if agents[sel]["busy"]>0 else "uyuyor"
        out.append("  \u2192 secili: %s  (%s)"%(agents[sel]["name"],st))
    out.append("")
    if mode=="name": out.append("  isim yaz · Enter=tamam · Esc=iptal")
    else: out.append("  \u2190 \u2192 sec · [n] isim · [c] renk · [h] sapka · [q] cik")
    return "\n".join(out)

def parse_keys(buf):
    keys=[]; i=0
    while i<len(buf):
        c=buf[i]
        if c=="\x1b" and i+2<len(buf) and buf[i+1]=="[" and buf[i+2] in "ABCD":
            keys.append({"A":"UP","B":"DOWN","C":"RIGHT","D":"LEFT"}[buf[i+2]]); i+=3
        elif c=="\x1b": keys.append("ESC"); i+=1
        else: keys.append(c); i+=1
    return keys

def main():
    global b_step
    ap=argparse.ArgumentParser()
    ap.add_argument("--demo",action="store_true"); ap.add_argument("--png"); ap.add_argument("--scale",type=int,default=6)
    ap.add_argument("--frames",type=int,default=0); ap.add_argument("--ascii",action="store_true")
    ap.add_argument("--install-hooks",action="store_true"); ap.add_argument("--uninstall-hooks",action="store_true")
    ap.add_argument("--no-install",action="store_true")
    a=ap.parse_args()
    if a.install_hooks: install_hooks(); return
    if a.uninstall_hooks: uninstall_hooks(); return
    os.makedirs(APP_DIR,exist_ok=True)
    store=Store(LOG); ovr=load_ovr()

    if a.png or a.ascii or a.frames:
        b_step=18; ags=resolve(demo_agents(time.time()),ovr)
        buf=Buf(W,H); draw_office(buf,ags,0)
        if a.png: render_png(buf,a.png,a.scale); print("png:",a.png); return
        if a.ascii: print("\n".join(render_ascii(buf))); return
        for fr in range(a.frames):
            b_step=18+fr; ags=resolve(demo_agents(time.time()+fr),ovr)
            buf=Buf(W,H); draw_office(buf,ags,0)
            sys.stdout.write("\x1b[H"+build_screen(buf,ags,"demo",0,"normal","",W,NEED_ROWS)+"\n")
        return

    if not a.no_install:
        try: install_hooks()
        except Exception: pass
        try: open(LOG,"a").close()
        except Exception: pass
    istty=sys.stdin.isatty() and HAVE_TTY; fd=old=None
    if istty:
        fd=sys.stdin.fileno(); old=termios.tcgetattr(fd); tty.setcbreak(fd)
        sys.stdout.write("\x1b[?1049h\x1b[?25l\x1b[2J")
    sel=0; mode="normal"; namebuf=""
    try:
        while True:
            now=time.time()
            if a.demo: ags_raw=demo_agents(now)
            else: store.poll(now); store.prune(now); ags_raw=store.agents(now)
            ags=resolve(ags_raw,ovr); head="demo" if a.demo else store.headline(now)
            if ags and sel>=len(ags): sel=len(ags)-1
            if sel<0: sel=0
            if istty:
                buf_in=""
                while select.select([sys.stdin],[],[],0)[0]:
                    ch=sys.stdin.read(1)
                    if ch=="": break
                    buf_in+=ch
                for key in parse_keys(buf_in):
                    if mode=="name":
                        if key in ("\r","\n"):
                            if ags and namebuf.strip():
                                ovr.setdefault(str(ags[sel]["slot"]),{})["name"]=namebuf.strip()[:10]; save_ovr(ovr)
                            mode="normal"; namebuf=""
                        elif key=="ESC": mode="normal"; namebuf=""
                        elif key in ("\x7f","\b"): namebuf=namebuf[:-1]
                        elif len(key)==1 and key.isprintable() and len(namebuf)<10: namebuf+=key
                    else:
                        if key in ("q","Q"): raise KeyboardInterrupt
                        elif key in ("RIGHT","DOWN","d"):
                            if ags: sel=(sel+1)%len(ags)
                        elif key in ("LEFT","UP","a"):
                            if ags: sel=(sel-1)%len(ags)
                        elif len(key)==1 and key.isdigit() and key!="0":
                            k=int(key)-1
                            if k<len(ags): sel=k
                        elif key in ("n","N"):
                            if ags: mode="name"; namebuf=""
                        elif key in ("c","C"):
                            if ags:
                                o=ovr.setdefault(str(ags[sel]["slot"]),{}); cur=o.get("color"); cur=cur if isinstance(cur,int) else ags[sel]["ci"]
                                o["color"]=(cur+1)%len(PAL); save_ovr(ovr)
                        elif key in ("h","H"):
                            if ags:
                                o=ovr.setdefault(str(ags[sel]["slot"]),{}); cur=o.get("hat") or ags[sel]["hat"]
                                o["hat"]=HATS[(HATS.index(cur)+1)%len(HATS)] if cur in HATS else HATS[1]; save_ovr(ovr)
            buf=Buf(W,H); draw_office(buf,ags,sel)
            sz=shutil.get_terminal_size((W,NEED_ROWS)); cols=sz.columns; rows=sz.lines
            small=(cols<W or rows<NEED_ROWS)
            screen=build_screen(buf,ags,head,sel,mode,namebuf,cols,rows)
            sys.stdout.write(("\x1b[H\x1b[2J" if small else "\x1b[H")+screen)
            sys.stdout.flush(); b_step+=1
            if not istty: break
            time.sleep(0.1)
    except KeyboardInterrupt: pass
    finally:
        if istty:
            sys.stdout.write("\x1b[?25h\x1b[?1049l"); sys.stdout.flush()
            try: termios.tcsetattr(fd,termios.TCSADRAIN,old)
            except Exception: pass

if __name__=="__main__": main()
