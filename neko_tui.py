#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NEKO HQ (terminal) — Claude CLI kedi kafesi, dogrudan terminalde.
Warp'ta bir panede `neko` (ya da `python3 ~/.neko-hq/neko_tui.py`), digerinde `claude`.
Her oturum bir kedi olur; calisinca yazar, sessizlikte uyur. Kafasinda rastgele
sapkalar olur (ara sira degisir). Isim/secim/duzenleme her sey piksel icindedir.
Tuslar:  <-  ->  kedi sec · n isim · c renk · h sapka · q cik
Yalnizca Python standart kutuphanesi (macOS/Linux/Warp, truecolor).
"""
import os, sys, json, time, re, select, argparse, shutil, random
try:
    import termios, tty
    HAVE_TTY=True
except Exception:
    HAVE_TTY=False

W, H = 220, 48
COUNTER_Y = 34
HOME=os.path.expanduser("~"); APP_DIR=os.path.join(HOME,".neko-hq")
LOG=os.path.join(APP_DIR,"activity.log"); OVR_FILE=os.path.join(APP_DIR,"cats.json")
SETTINGS=os.path.join(HOME,".claude","settings.json")
SELF=os.path.abspath(__file__); PY=sys.executable or "python3"; MARK="# neko-hq"

NAMES=["Pamuk","Zeytin","Boncuk","Sansli","Mirnav","Duman","Tarcin","Karamel"]
ALL_HATS=["santa","bow","beanie","party","crown","cap","flower","tophat","headphones","wizard","chef","bandana","halo","star"]
PAL_HEX=[
 {"F":"#f0a64b","d":"#cf7f2c","l":"#ffc878","B":"#fce3c2","I":"#f3a9bb","N":"#e07a92","iris":"#7fb24a","s":"#cf7f2c"},
 {"F":"#9aa3b2","d":"#79839a","l":"#c2cad6","B":"#e6ebf2","I":"#f3a9bb","N":"#d97f96","iris":"#6fae9a","s":"#79839a"},
 {"F":"#3a3e48","d":"#24262e","l":"#565b6b","B":"#f1f2f4","I":"#e79aa8","N":"#d97f96","iris":"#8fd06a","s":None},
 {"F":"#efe6d3","d":"#cfc3a8","l":"#fffaf0","B":"#fffaf0","I":"#f3a9bb","N":"#e07a92","iris":"#caa24a","s":None},
 {"F":"#e7c27a","d":"#b98e44","l":"#f7df9f","B":"#fff7ea","I":"#f3a9bb","N":"#e07a92","iris":"#7faf6a","s":"#9a6b3a"},
 {"F":"#b9897a","d":"#956a5e","l":"#d8b0a3","B":"#f4e7df","I":"#f3a9bb","N":"#d97f96","iris":"#6fae9a","s":"#7a5446"},
]
TOOL_TASKS={"Bash":"komut","Read":"okuyor","Edit":"yaziyor","Write":"yaziyor","MultiEdit":"duzenliyor",
 "Grep":"ariyor","Glob":"tariyor","WebSearch":"web","WebFetch":"web","Task":"alt-ajan","TodoWrite":"liste"}

def hx(s):
    s=s.lstrip("#"); return (int(s[0:2],16),int(s[2:4],16),int(s[4:6],16))
PAL=[{k:(hx(v) if v else None) for k,v in p.items()} for p in PAL_HEX]

OUT=(34,26,18); WHT=(252,252,252); PUP=(20,22,30); BLK=(20,18,16)
WALL=[(247,235,214),(239,225,201),(229,212,186)]
COUNTER=(150,98,56); COUNTERT=(176,120,72); COUNTERD=(96,60,32); COUNTERE=(70,44,22)
SIGN=(94,58,30); SIGNL=(122,74,38); SIGNT=(243,220,174)
SKY=[(150,205,242),(176,216,245)]; SUN=(255,209,74); CLOUD=(255,255,255); BLDG=(176,150,170); BLDG2=(150,124,150)
TREE=(74,165,82); TREED=(47,122,52); FRAME=(110,74,40); SILL=(138,94,54)
CB=(40,52,46); CBF=(110,74,40); CHALK=(244,239,230); CH1=(244,193,208); CH2=(191,224,194); CH3=(188,214,240)
SHELF=(122,80,44); SHELFD=(90,58,32)
POT=(194,98,47); POTD=(151,67,33); LEAF=(74,165,82); LEAFD=(47,122,52); LEAFL=(98,193,104); VINE=(63,143,68)
MACH=(211,79,79); MACHD=(168,58,58); CHROME=(201,206,214); CAKE=(247,197,214); CAKEI=(232,154,176); CHERRY=(210,59,84); CREAM=(255,244,234)
PCASE=(206,228,236); PCASEF=(120,84,48); PIE=(232,178,96); PIEC=(120,72,140); DONUT=(244,170,150)
CLOCKF=(120,84,48); CLOCKB=(248,243,232); CLOCKH=(60,46,34)
PIC=(120,84,48); PICB=(250,246,236)
LAPC=(52,57,74); LAPK=(207,210,216); SCR=(16,35,27); CODE=(123,224,143); CODEB=(111,182,239)
MUG=(217,83,79); STEAM=(238,246,255)
F1=(239,138,160); F2=(242,196,99); F3=(143,208,160); F4=(143,191,230); F5=(198,156,224)
BADGE=(247,236,206); SELC=(255,214,82); GOLD=(240,200,70)

FONT={
"A":["010","101","111","101","101"],"B":["110","101","110","101","110"],"C":["011","100","100","100","011"],
"D":["110","101","101","101","110"],"E":["111","100","110","100","111"],"F":["111","100","110","100","100"],
"G":["011","100","101","101","011"],"H":["101","101","111","101","101"],"I":["111","010","010","010","111"],
"J":["001","001","001","101","010"],"K":["101","101","110","101","101"],"L":["100","100","100","100","111"],
"M":["101","111","111","101","101"],"N":["101","111","111","111","101"],"O":["010","101","101","101","010"],
"P":["110","101","110","100","100"],"Q":["010","101","101","110","011"],"R":["110","101","110","101","101"],
"S":["011","100","010","001","110"],"T":["111","010","010","010","010"],"U":["101","101","101","101","111"],
"V":["101","101","101","101","010"],"W":["101","101","111","111","101"],"X":["101","101","010","101","101"],
"Y":["101","101","010","010","010"],"Z":["111","001","010","100","111"],
"0":["111","101","101","101","111"],"1":["010","110","010","010","111"],"2":["110","001","010","100","111"],
"3":["111","001","011","001","111"],"4":["101","101","111","001","001"],"5":["111","100","110","001","110"],
"6":["011","100","110","101","010"],"7":["111","001","010","010","010"],"8":["010","101","010","101","010"],
"9":["010","101","011","001","110"]," ":["000","000","000","000","000"],
"-":["000","000","111","000","000"],".":["000","000","000","000","010"],"!":["010","010","010","000","010"],
}
TR={"Ç":"C","Ş":"S","İ":"I","Ğ":"G","Ö":"O","Ü":"U","Â":"A","Î":"I","Û":"U"}

def text_w(s): return max(0,len(s)*4-1)
def draw_text(b,x,y,s,col):
    cx=x
    for ch in s.upper():
        ch=TR.get(ch,ch); g=FONT.get(ch)
        if g:
            for r in range(5):
                row=g[r]
                for c in range(3):
                    if row[c]=="1": b.px(cx+c,y+r,1,1,col)
        cx+=4

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

b_step=0

def cat(b,ox,oy,P,pose,t):
    F,d,l,B,I,N,iris,s=P["F"],P["d"],P["l"],P["B"],P["I"],P["N"],P["iris"],P["s"]
    blink=(t//9)%13==0
    b.px(ox+3,oy+16,11,1,(70,48,28))
    b.px(ox+12,oy+11,3,2,OUT); b.px(ox+12,oy+11,2,1,F); b.px(ox+13,oy+8,2,4,OUT); b.px(ox+13,oy+9,1,3,F)
    if s: b.px(ox+13,oy+9,1,1,s)
    rrect(b,ox+3,oy+9,10,7,F,OUT); b.px(ox+6,oy+11,4,4,B)
    if s: b.px(ox+4,oy+11,1,4,s); b.px(ox+11,oy+11,1,4,s)
    b.px(ox+3,oy,2,1,F); b.px(ox+2,oy+1,4,1,F); b.px(ox+3,oy+1,1,1,I); b.px(ox+1,oy+1,1,1,OUT)
    b.px(ox+11,oy,2,1,F); b.px(ox+10,oy+1,4,1,F); b.px(ox+12,oy+1,1,1,I); b.px(ox+14,oy+1,1,1,OUT)
    rrect(b,ox+2,oy+1,12,9,F,OUT); b.px(ox+3,oy+2,10,1,l); b.px(ox+3,oy+8,10,1,d)
    if s: b.px(ox+7,oy+2,2,2,s); b.px(ox+4,oy+2,1,2,s); b.px(ox+11,oy+2,1,2,s)
    b.px(ox+4,oy+6,8,3,B)
    ey=oy+4; exL=ox+3; exR=ox+9
    if pose=="sleep" or blink:
        b.px(exL,ey+2,3,1,OUT); b.px(exR,ey+2,3,1,OUT)
    else:
        dd=1 if pose=="read" else 0
        b.px(exL,ey,3,4,WHT); b.px(exR,ey,3,4,WHT)
        b.px(exL,ey,3,1,OUT); b.px(exR,ey,3,1,OUT)
        b.px(exL,ey+1+dd,3,2,iris); b.px(exR,ey+1+dd,3,2,iris)
        b.px(exL+1,ey+1+dd,1,2,PUP); b.px(exR+1,ey+1+dd,1,2,PUP)
        b.px(exL,ey+1,1,1,WHT); b.px(exR,ey+1,1,1,WHT)
    b.px(ox+7,oy+7,2,1,N); b.px(ox+5,oy+8,1,1,d); b.px(ox+9,oy+8,1,1,d)
    b.px(ox+3,oy+7,1,1,(244,176,188)); b.px(ox+11,oy+7,1,1,(244,176,188))
    b.px(ox+0,oy+7,2,1,WHT); b.px(ox+13,oy+7,2,1,WHT)
    py=oy+15
    if pose=="read":
        b.px(ox+4,oy+12,8,4,(233,231,223)); b.px(ox+8,oy+12,1,4,(196,193,184))
        b.px(ox+4,py,2,1,F); b.px(ox+10,py,2,1,F)
    else:
        k=(t//3)%2
        b.px(ox+4,py-(1 if (pose=="type" and k==0) else 0),2,1,F)
        b.px(ox+10,py-(1 if (pose=="type" and k==1) else 0),2,1,F)
    if pose=="sleep" and (t//12)%2==0:
        b.px(ox+15,oy+0,1,1,OUT); b.px(ox+16,oy-2,1,1,OUT)

def item(b,ox,oy,kind):
    if not kind or kind=="none": return
    cx=ox+8
    if kind=="santa":
        b.px(cx,oy-3,2,1,(214,64,64)); b.px(cx-1,oy-2,4,1,(214,64,64)); b.px(cx-2,oy-1,6,1,(214,64,64)); b.px(cx-3,oy,8,1,(214,64,64))
        b.px(cx-3,oy,3,1,(176,42,42)); b.px(cx-4,oy+1,9,1,WHT); b.px(cx+1,oy-4,2,2,WHT)
    elif kind=="bow":
        b.px(cx-5,oy-1,3,3,F1); b.px(cx+0,oy-1,3,3,F1); b.px(cx-2,oy,2,1,(210,90,120)); b.px(cx-1,oy-1,1,3,(210,90,120))
    elif kind=="beanie":
        b.px(cx-5,oy,11,1,(70,128,150)); b.px(cx-4,oy-1,9,1,(96,158,180)); b.px(cx-2,oy-2,5,1,(96,158,180)); b.px(cx-1,oy-4,2,2,WHT); b.px(cx-5,oy+1,11,1,(58,110,132))
    elif kind=="party":
        b.px(cx,oy-5,1,1,WHT); b.px(cx,oy-4,1,1,F2); b.px(cx-1,oy-3,3,1,F1); b.px(cx-2,oy-2,5,1,F3); b.px(cx-3,oy-1,7,1,F4); b.px(cx-4,oy,9,1,F2)
    elif kind=="crown":
        b.px(cx-4,oy-1,9,2,GOLD); b.px(cx-4,oy-3,1,2,GOLD); b.px(cx,oy-3,1,2,GOLD); b.px(cx+4,oy-3,1,2,GOLD)
        b.px(cx-4,oy-4,1,1,F1); b.px(cx,oy-4,1,1,F4); b.px(cx+4,oy-4,1,1,F3)
    elif kind=="cap":
        b.px(cx-4,oy-1,9,2,(70,112,196)); b.px(cx-3,oy-2,6,1,(86,128,210)); b.px(cx+4,oy,4,1,(56,96,176))
    elif kind=="flower":
        b.px(cx-6,oy,2,2,F1); b.px(cx-7,oy+1,1,1,F1); b.px(cx-4,oy+1,1,1,F1); b.px(cx-6,oy-1,1,1,F1); b.px(cx-5,oy,1,1,F2)
    elif kind=="tophat":
        b.px(cx-5,oy+1,11,1,BLK); b.px(cx-3,oy-4,7,5,BLK); b.px(cx-3,oy-2,7,1,(180,60,70))
    elif kind=="headphones":
        b.px(cx-5,oy-2,1,5,(70,74,90)); b.px(cx+5,oy-2,1,5,(70,74,90)); b.px(cx-4,oy-3,9,1,(70,74,90))
        b.px(cx-6,oy+0,2,3,(120,124,140)); b.px(cx+5,oy+0,2,3,(120,124,140))
    elif kind=="wizard":
        b.px(cx,oy-5,1,2,(90,80,170)); b.px(cx-1,oy-3,3,1,(90,80,170)); b.px(cx-2,oy-2,5,1,(110,98,190)); b.px(cx-3,oy-1,7,1,(90,80,170)); b.px(cx-4,oy,9,1,(70,62,150))
        b.px(cx-1,oy-2,1,1,F2); b.px(cx+1,oy-1,1,1,WHT); b.px(cx-3,oy,1,1,F2)
    elif kind=="chef":
        b.px(cx-4,oy,9,2,WHT); b.px(cx-3,oy-3,2,3,WHT); b.px(cx,oy-4,2,4,WHT); b.px(cx+3,oy-3,2,3,WHT); b.px(cx-1,oy-3,2,2,WHT)
    elif kind=="bandana":
        b.px(cx-5,oy,11,2,(208,72,72)); b.px(cx-5,oy,11,1,(232,110,110)); b.px(cx+4,oy+1,1,3,(208,72,72)); b.px(cx-6,oy+1,2,1,(208,72,72))
        b.px(cx-3,oy+1,1,1,WHT); b.px(cx+1,oy+1,1,1,WHT)
    elif kind=="halo":
        b.px(cx-4,oy-4,9,1,GOLD); b.px(cx-4,oy-3,1,1,GOLD); b.px(cx+4,oy-3,1,1,GOLD); b.px(cx-3,oy-3,7,1,(255,236,150))
    elif kind=="star":
        b.px(cx-1,oy-5,2,1,F2); b.px(cx-2,oy-4,5,1,F2); b.px(cx-3,oy-3,7,1,F2); b.px(cx-2,oy-2,2,1,F2); b.px(cx+1,oy-2,2,1,F2); b.px(cx,oy-4,1,1,WHT)

def laptop(b,lx,ly,tool):
    sc=SCR; cc=CODE
    if tool=="Bash": sc=(12,18,14)
    elif tool in ("WebSearch","WebFetch"): sc=(14,27,40); cc=CODEB
    b.px(lx,ly-5,11,6,LAPC); b.px(lx+1,ly-4,9,4,sc)
    for q in range(2):
        ax=lx+2+((b_step+q*3)%7); b.px(ax,ly-3+q,3,1,cc)
    b.px(lx-1,ly+1,13,2,LAPK); b.px(lx-1,ly+1,13,1,(224,226,230))

def window(b,X,Y,w,h):
    b.px(X-2,Y-2,w+4,h+4,FRAME)
    b.px(X,Y,w,h*2//3,SKY[0]); b.px(X,Y+h*2//3,w,h-h*2//3,SKY[1])
    b.px(X+w-8,Y+2,5,5,SUN); b.px(X+3,Y+5,8,2,CLOUD); b.px(X+6,Y+3,6,2,CLOUD)
    b.px(X+3,Y+h-8,6,8,BLDG); b.px(X+w-10,Y+h-6,7,6,BLDG2)
    b.px(X+w//2-7,Y+h-6,5,6,TREED); b.px(X+w//2-9,Y+h-10,8,5,TREE)
    b.px(X+w//2-1,Y,1,h,FRAME); b.px(X,Y+h//2,w,1,FRAME)
    b.px(X-3,Y+h+1,w+6,2,SILL)

def chalk(b,X,Y,w,h):
    b.px(X-2,Y-2,w+4,h+4,CBF); b.px(X,Y,w,h,CB); b.px(X,Y,w,1,(58,72,64))
    b.px(X+4,Y+3,w-12,2,CHALK)
    b.px(X+4,Y+8,2,2,CH1); b.px(X+8,Y+9,w-18,1,CHALK)
    b.px(X+4,Y+13,2,2,CH2); b.px(X+8,Y+14,w-20,1,CHALK)
    b.px(X+w-9,Y+3,6,5,CHALK); b.px(X+w-3,Y+4,1,3,CHALK)

def shelves(b,X,Y):
    cups=[(217,83,79),(98,158,200),(110,180,120),(240,190,90),(198,156,224)]
    for i in range(2):
        yy=Y+i*8
        b.px(X,yy,32,1,SHELF); b.px(X,yy+1,32,1,SHELFD)
        for j in range(6):
            cx=X+1+j*5; c=cups[(i*6+j)%5]; b.px(cx,yy-4,4,4,c); b.px(cx,yy-4,4,1,(255,255,255))
    b.px(X+24,Y-5,8,5,LEAF); b.px(X+26,Y-2,4,3,POT)

def hang(b,X):
    b.px(X+2,0,1,5,(120,98,72)); b.px(X-1,5,8,3,POT); b.px(X-1,5,8,1,(216,114,66))
    b.px(X,8,1,4,VINE); b.px(X+2,8,1,5,VINE); b.px(X+4,8,1,3,VINE); b.px(X+6,8,1,4,VINE)
    b.px(X+1,11,1,1,LEAFL); b.px(X+5,12,1,1,LEAFL)

def clock(b,X,Y):
    b.px(X,Y,12,12,CLOCKF); b.px(X+1,Y+1,10,10,CLOCKB)
    b.px(X+6,Y+2,1,4,CLOCKH); b.px(X+6,Y+6,3,1,CLOCKH)
    sec=(b_step//5)%4
    pts=[(6,2),(9,6),(6,9),(3,6)][sec]
    b.px(X+pts[0],Y+pts[1],1,1,(208,80,80))

def picframe(b,X,Y,kind):
    b.px(X,Y,12,10,PIC); b.px(X+1,Y+1,10,8,PICB)
    if kind==0:
        b.px(X+3,Y+3,2,1,(80,70,60)); b.px(X+7,Y+3,2,1,(80,70,60)); b.px(X+4,Y+6,4,1,(208,120,120))
    else:
        b.px(X+3,Y+5,6,3,(120,180,120)); b.px(X+5,Y+3,2,2,(110,160,240))

def bunting(b):
    b.px(0,4,W,1,(120,108,86)); cols=[F1,F2,F3,F4,F5]; i=0
    for fx in range(4,W-7,15):
        c=cols[i%5]; i+=1; b.px(fx,5,7,1,c); b.px(fx+1,6,5,1,c); b.px(fx+2,7,3,1,c); b.px(fx+3,8,1,1,c)

def sign(b):
    X=92; b.px(X,0,36,10,SIGN); b.px(X,0,36,1,SIGNL); b.px(X,9,36,1,(62,38,15)); b.px(X+1,1,34,1,(116,70,34))
    b.px(X+8,4,4,2,SIGNT); b.px(X+7,2,1,1,SIGNT); b.px(X+9,1,1,1,SIGNT); b.px(X+12,1,1,1,SIGNT); b.px(X+15,2,1,1,SIGNT)
    b.px(X+19,3,5,4,CREAM); b.px(X+24,4,1,2,CREAM); b.px(X+20,2,1,1,STEAM)
    b.px(X+28,2,2,2,F1); b.px(X+31,2,2,2,F1); b.px(X+28,4,5,1,F1); b.px(X+29,5,3,1,F1); b.px(X+30,6,1,1,F1)

def station(b):
    Y=COUNTER_Y
    b.px(2,Y-13,17,13,MACH); b.px(2,Y-13,17,1,(232,110,110)); b.px(2,Y-13,1,13,(232,110,110))
    b.px(5,Y-10,11,4,CHROME); b.px(6,Y-9,9,2,(14,28,22)); b.px(7,Y-8,2,1,(120,200,150))
    b.px(9,Y-4,2,3,(150,156,164)); b.px(8,Y-1,4,1,(150,156,164))
    b.px(15,Y-12,3,2,(255,231,154) if (b_step%20<10) else (200,160,60))
    if (b_step//5)%2==0: b.px(7,Y-15,1,2,STEAM)
    # pastry display case
    bx=22; b.px(bx,Y-9,20,9,PCASE); b.px(bx,Y-9,20,1,(230,242,247)); b.px(bx,Y-1,20,1,PCASEF); b.px(bx,Y-9,1,9,(170,200,210)); b.px(bx+19,Y-9,1,9,(170,200,210))
    b.px(bx+2,Y-5,4,4,PIE); b.px(bx+2,Y-5,4,1,CREAM); b.px(bx+3,Y-2,1,1,(120,72,140))
    b.px(bx+8,Y-4,3,3,DONUT); b.px(bx+9,Y-3,1,1,PCASE)
    b.px(bx+13,Y-5,4,4,CAKE); b.px(bx+13,Y-5,4,1,CREAM); b.px(bx+15,Y-6,1,1,CHERRY)

def cafe_back(b):
    b.band(0,18,WALL[0]); b.band(18,30,WALL[1]); b.band(30,COUNTER_Y,WALL[2])
    bunting(b); sign(b)
    window(b,6,10,38,18)
    chalk(b,90,11,44,16)
    shelves(b,176,12)
    clock(b,54,3)
    picframe(b,70,4,0); picframe(b,150,4,1)
    hang(b,138)
    station(b)
    b.px(0,COUNTER_Y-1,W,2,COUNTERT)

def layout(n):
    if n<=0: return []
    xs,xe=52,210
    if n==1: return [((xs+xe)//2,COUNTER_Y)]
    return [(int(xs+(xe-xs)*i/(n-1)),COUNTER_Y) for i in range(n)]

def workstation(b,cx,P,busy,tool,hat,selected):
    pose="sleep"
    if busy>0: pose="read" if tool in ("Read","WebSearch") else "type"
    oy=COUNTER_Y-16
    cat(b,cx-8,oy,P,pose,b_step)
    item(b,cx-8,oy,hat)
    if selected:
        b.px(cx-2,oy-8,5,1,SELC); b.px(cx-1,oy-7,3,1,SELC); b.px(cx,oy-6,1,1,SELC)
    if pose!="read": laptop(b,cx-6,COUNTER_Y-1,tool)
    b.px(cx+7,COUNTER_Y-5,3,4,MUG); b.px(cx+7,COUNTER_Y-5,3,1,(235,110,106))
    if busy>0 and (b_step//6)%2==0: b.px(cx+8,COUNTER_Y-7,1,1,STEAM)

def counter_front(b, agents, pos, sel, mode, namebuf):
    b.px(0,COUNTER_Y+1,W,H-(COUNTER_Y+1),COUNTER)
    b.px(0,COUNTER_Y+1,W,1,(168,112,66))
    for x in range(0,W,20): b.px(x,COUNTER_Y+2,1,H-(COUNTER_Y+2),COUNTERD)
    b.px(0,H-2,W,2,COUNTERE)
    ny=COUNTER_Y+5
    n=len(pos); slotw=(pos[1][0]-pos[0][0]) if n>1 else W
    maxch=max(3,min(8,(slotw-2)//4))
    for i,(cx,_) in enumerate(pos):
        editing=(i==sel and mode=="name")
        raw=namebuf if editing else agents[i]["name"]
        label=raw[:maxch]; w=text_w(label)
        cur=editing and ((b_step//5)%2==0)
        totw=w+(3 if editing else 0); bx=cx-totw//2
        if i==sel:
            b.px(bx-2,ny-1,totw+4,7,SELC); draw_text(b,bx,ny,label,(60,44,20))
            if cur: b.px(bx+w+1,ny,2,5,(60,44,20))
        else:
            draw_text(b,bx,ny,label,BADGE)

def draw_office(b, agents, sel, mode="normal", namebuf=""):
    cafe_back(b)
    pos=layout(len(agents))
    for i,(cx,_) in enumerate(pos):
        a=agents[i]; workstation(b,cx,a["pal"],a["busy"],a["tool"],a["hat"], i==sel)
    counter_front(b, agents, pos, sel, mode, namebuf)

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

def load_ovr():
    try:
        with open(OVR_FILE,encoding="utf-8") as f: return json.load(f)
    except Exception: return {}
def save_ovr(o):
    try:
        os.makedirs(APP_DIR,exist_ok=True)
        with open(OVR_FILE,"w",encoding="utf-8") as f: json.dump(o,f,ensure_ascii=False)
    except Exception: pass

AUTO_HATS={}
def resolve(agents,ovr):
    out=[]
    for a in agents:
        slot=a["slot"]; o=ovr.get(str(slot),{})
        name=o.get("name") or NAMES[slot%len(NAMES)]
        ci=o.get("color"); ci=ci if isinstance(ci,int) else slot%len(PAL)
        if o.get("hat"): hat=o["hat"]
        else:
            if slot not in AUTO_HATS: AUTO_HATS[slot]=random.choice(ALL_HATS)
            hat=AUTO_HATS[slot]
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
def resample(src,dw,dh):
    out=Buf(dw,dh); sw=src.w; sh=src.h
    for y in range(dh):
        sy=y*sh//dh
        if sy>=sh: sy=sh-1
        srow=src.d[sy]; drow=out.d[y]
        for x in range(dw):
            sx=x*sw//dw
            if sx>=sw: sx=sw-1
            drow[x]=srow[sx]
    return out

def render_fit(scene,cols,rows):
    tw=cols; th=rows*2
    if tw<8 or th<4:
        return "\x1b[H\x1b[2J  pencere cok kucuk"
    f=min(tw/scene.w, th/scene.h); f=max(0.15,min(f,8.0))
    dw=int(scene.w*f); dh=int(scene.h*f)
    if dw<16: dw=min(tw,16)
    if dh<8: dh=min(th,8)
    if dw>tw: dw=tw
    if dh>th: dh=th
    sc=resample(scene,dw,dh)
    body=render_terminal(sc); rh=len(body)
    left=max(0,(cols-dw)//2); right=cols-dw-left
    top=min(max(0,(rows-rh)//2), max(0,rows-rh))
    blank=" "*cols; lp=" "*left; rp=" "*right
    lines=[blank]*top + [lp+r+rp for r in body]
    while len(lines)<rows: lines.append(blank)
    return "\x1b[H"+"\n".join(lines[:rows])

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

NEED_ROWS=H//2
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
            sys.stdout.write("\x1b[H"+"\n".join(render_terminal(buf))+"\n")
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
            ags=resolve(ags_raw,ovr)
            if ags and sel>=len(ags): sel=len(ags)-1
            if sel<0: sel=0
            # ara sira sapka degistir (manuel olmayanlar)
            for a2 in ags:
                slot=a2["slot"]
                if not ovr.get(str(slot),{}).get("hat") and random.random()<0.004:
                    AUTO_HATS[slot]=random.choice(ALL_HATS)
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
                                ovr.setdefault(str(ags[sel]["slot"]),{})["name"]=namebuf.strip()[:8]; save_ovr(ovr)
                            mode="normal"; namebuf=""
                        elif key=="ESC": mode="normal"; namebuf=""
                        elif key in ("\x7f","\b"): namebuf=namebuf[:-1]
                        elif len(key)==1 and key.isprintable() and len(namebuf)<8: namebuf+=key
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
                            if ags: mode="name"; namebuf=ags[sel]["name"]
                        elif key in ("c","C"):
                            if ags:
                                o=ovr.setdefault(str(ags[sel]["slot"]),{}); cur=o.get("color"); cur=cur if isinstance(cur,int) else ags[sel]["ci"]
                                o["color"]=(cur+1)%len(PAL); save_ovr(ovr)
                        elif key in ("h","H"):
                            if ags:
                                o=ovr.setdefault(str(ags[sel]["slot"]),{}); cur=o.get("hat") or ags[sel]["hat"]
                                o["hat"]=ALL_HATS[(ALL_HATS.index(cur)+1)%len(ALL_HATS)] if cur in ALL_HATS else ALL_HATS[0]; save_ovr(ovr)
            buf=Buf(W,H); draw_office(buf,ags,sel,mode,namebuf)
            sz=shutil.get_terminal_size((W,NEED_ROWS)); cols=sz.columns; rows=sz.lines
            sys.stdout.write(render_fit(buf,cols,rows))
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
