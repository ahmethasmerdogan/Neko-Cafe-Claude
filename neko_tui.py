#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NEKO HQ (terminal) — Claude CLI kedi kafesi, dogrudan terminalde.
Warp'ta bir panede `neko` (ya da `python3 ~/.neko-hq/neko_tui.py`), digerinde `claude`.
Her oturum bir kedi olur; calisinca yazar, sessizlikte uyur. Kafasinda rastgele
sapkalar (ara sira degisir). Isim/secim/duzenleme her sey pikselin icinde.
Tuslar:  <-  ->  kedi sec · n isim · c renk · h sapka · q cik
Yalnizca Python standart kutuphanesi (macOS/Linux/Warp, truecolor). Pencereye gore olcekler.
"""
import os, sys, json, time, re, select, argparse, shutil, random
try:
    import termios, tty
    HAVE_TTY=True
except Exception:
    HAVE_TTY=False

W, H = 132, 56
COUNTER_Y = 40
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
CB=(40,52,46); CBF=(110,74,40); CHALK=(244,239,230); CH1=(244,193,208); CH2=(191,224,194)
SHELF=(122,80,44); SHELFD=(90,58,32)
POT=(194,98,47); POTD=(151,67,33); LEAF=(74,165,82); LEAFD=(47,122,52); LEAFL=(98,193,104); VINE=(63,143,68)
MACH=(211,79,79); MACHD=(168,58,58); CHROME=(201,206,214); CAKE=(247,197,214); CAKEI=(232,154,176); CHERRY=(210,59,84); CREAM=(255,244,234)
CLOCKF=(120,84,48); CLOCKB=(248,243,232); CLOCKH=(60,46,34); PIC=(120,84,48); PICB=(250,246,236)
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
    for ch in str(s).upper():
        ch=TR.get(ch,ch); g=FONT.get(ch)
        if g:
            for r in range(5):
                row=g[r]
                for c in range(3):
                    if row[c]=="1": b.px(cx+c,y+r,1,1,col)
        cx+=4
def draw_text_scaled(b,x,y,s,col,fs):
    cx=x
    for ch in str(s).upper():
        ch=TR.get(ch,ch); g=FONT.get(ch)
        if g:
            for r in range(5):
                row=g[r]
                for cc in range(3):
                    if row[cc]=="1": b.px(cx+cc*fs,y+r*fs,fs,fs,col)
        cx+=4*fs

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
    b.px(ox+4,oy+23,14,1,(70,48,28))
    # tail
    b.px(ox+16,oy+16,4,2,OUT); b.px(ox+16,oy+16,3,1,F)
    b.px(ox+18,oy+10,3,7,OUT); b.px(ox+18,oy+11,2,6,F)
    b.px(ox+16,oy+8,3,4,OUT);  b.px(ox+16,oy+9,2,3,F)
    if s: b.px(ox+18,oy+12,2,1,s); b.px(ox+16,oy+9,2,1,s)
    # body
    rrect(b,ox+4,oy+15,13,9,F,OUT); b.px(ox+7,oy+17,7,6,B)
    if s: b.px(ox+5,oy+17,1,6,s); b.px(ox+15,oy+17,1,6,s)
    # ears
    b.px(ox+3,oy,3,1,OUT); b.px(ox+2,oy+1,5,1,OUT); b.px(ox+3,oy+1,3,1,F); b.px(ox+3,oy+2,4,2,F); b.px(ox+4,oy+2,2,2,I)
    b.px(ox+15,oy,3,1,OUT); b.px(ox+14,oy+1,5,1,OUT); b.px(ox+15,oy+1,3,1,F); b.px(ox+14,oy+2,4,2,F); b.px(ox+15,oy+2,2,2,I)
    # head
    rrect(b,ox+2,oy+3,17,13,F,OUT); b.px(ox+4,oy+4,13,1,l); b.px(ox+1,oy+9,1,4,F); b.px(ox+19,oy+9,1,4,F); b.px(ox+4,oy+14,13,1,d)
    if s: b.px(ox+8,oy+4,2,3,s); b.px(ox+5,oy+5,1,2,s); b.px(ox+14,oy+5,1,2,s)
    # muzzle
    b.px(ox+5,oy+10,11,5,B)
    # eyes (big & cute)
    ey=oy+6; exL=ox+4; exR=ox+12
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
    b.px(ox+9,oy+11,3,1,N); b.px(ox+10,oy+12,1,1,N)
    b.px(ox+7,oy+13,1,1,d); b.px(ox+13,oy+13,1,1,d); b.px(ox+9,oy+13,3,1,d)
    # blush
    b.px(ox+3,oy+11,2,1,(244,176,188)); b.px(ox+16,oy+11,2,1,(244,176,188))
    # whiskers
    b.px(ox+0,oy+10,3,1,WHT); b.px(ox+0,oy+12,3,1,WHT)
    b.px(ox+18,oy+10,3,1,WHT); b.px(ox+18,oy+12,3,1,WHT)
    # paws
    py=oy+23
    if pose=="read":
        b.px(ox+5,oy+18,11,5,(233,231,223)); b.px(ox+9,oy+18,1,5,(196,193,184))
        b.px(ox+5,py,3,1,F); b.px(ox+11,py,3,1,F)
    else:
        k=(t//3)%2
        b.px(ox+5,py-(1 if (pose=="type" and k==0) else 0),3,1,F)
        b.px(ox+11,py-(1 if (pose=="type" and k==1) else 0),3,1,F)
    if pose=="sleep" and (t//12)%2==0:
        b.px(ox+19,oy+1,1,1,OUT); b.px(ox+21,oy-2,1,1,OUT)

def item(b,ox,oy,kind):
    if not kind or kind=="none": return
    cx=ox+10
    if kind=="santa":
        b.px(cx,oy-4,2,1,(214,64,64)); b.px(cx-1,oy-3,4,1,(214,64,64)); b.px(cx-2,oy-2,6,1,(214,64,64)); b.px(cx-3,oy-1,8,1,(214,64,64)); b.px(cx-4,oy,10,1,(214,64,64))
        b.px(cx-3,oy-1,3,1,(176,42,42)); b.px(cx-5,oy+1,12,1,WHT); b.px(cx+1,oy-5,3,2,WHT)
    elif kind=="bow":
        b.px(cx-6,oy-2,4,4,F1); b.px(cx+1,oy-2,4,4,F1); b.px(cx-2,oy-1,3,2,(210,90,120)); b.px(cx-1,oy-2,1,4,(210,90,120))
    elif kind=="beanie":
        b.px(cx-6,oy,13,1,(70,128,150)); b.px(cx-5,oy-1,11,1,(96,158,180)); b.px(cx-3,oy-3,7,2,(96,158,180)); b.px(cx-1,oy-5,3,2,WHT); b.px(cx-6,oy+1,13,1,(58,110,132))
    elif kind=="party":
        b.px(cx,oy-6,1,1,WHT); b.px(cx,oy-5,1,1,F2); b.px(cx-1,oy-4,3,1,F1); b.px(cx-2,oy-3,5,1,F3); b.px(cx-3,oy-2,7,1,F4); b.px(cx-4,oy-1,9,1,F2); b.px(cx-5,oy,11,1,F1)
    elif kind=="crown":
        b.px(cx-5,oy-1,11,2,GOLD); b.px(cx-5,oy-4,2,3,GOLD); b.px(cx-1,oy-4,2,3,GOLD); b.px(cx+4,oy-4,2,3,GOLD)
        b.px(cx-5,oy-5,1,1,F1); b.px(cx,oy-5,1,1,F4); b.px(cx+5,oy-5,1,1,F3)
    elif kind=="cap":
        b.px(cx-5,oy-1,11,2,(70,112,196)); b.px(cx-4,oy-3,8,2,(86,128,210)); b.px(cx+5,oy,5,1,(56,96,176))
    elif kind=="flower":
        b.px(cx-7,oy,2,2,F1); b.px(cx-8,oy+1,1,1,F1); b.px(cx-5,oy+1,1,1,F1); b.px(cx-7,oy-1,1,1,F1); b.px(cx-6,oy,1,1,F2)
    elif kind=="tophat":
        b.px(cx-6,oy+1,13,1,BLK); b.px(cx-4,oy-5,9,6,BLK); b.px(cx-4,oy-2,9,1,(180,60,70))
    elif kind=="headphones":
        b.px(cx-6,oy-2,1,6,(70,74,90)); b.px(cx+6,oy-2,1,6,(70,74,90)); b.px(cx-5,oy-3,11,1,(70,74,90))
        b.px(cx-7,oy+0,2,4,(120,124,140)); b.px(cx+6,oy+0,2,4,(120,124,140))
    elif kind=="wizard":
        b.px(cx,oy-6,1,2,(90,80,170)); b.px(cx-1,oy-4,3,1,(90,80,170)); b.px(cx-2,oy-3,5,1,(110,98,190)); b.px(cx-3,oy-2,7,1,(90,80,170)); b.px(cx-4,oy-1,9,1,(70,62,150)); b.px(cx-5,oy,11,1,(70,62,150))
        b.px(cx-1,oy-3,1,1,F2); b.px(cx+1,oy-2,1,1,WHT); b.px(cx-3,oy-1,1,1,F2)
    elif kind=="chef":
        b.px(cx-5,oy,11,2,WHT); b.px(cx-4,oy-4,2,4,WHT); b.px(cx,oy-5,2,5,WHT); b.px(cx+4,oy-4,2,4,WHT); b.px(cx-2,oy-4,3,3,WHT)
    elif kind=="bandana":
        b.px(cx-6,oy,13,2,(208,72,72)); b.px(cx-6,oy,13,1,(232,110,110)); b.px(cx+5,oy+1,1,4,(208,72,72)); b.px(cx-7,oy+1,2,1,(208,72,72))
        b.px(cx-3,oy+1,1,1,WHT); b.px(cx+2,oy+1,1,1,WHT)
    elif kind=="halo":
        b.px(cx-5,oy-5,11,1,GOLD); b.px(cx-5,oy-4,1,1,GOLD); b.px(cx+5,oy-4,1,1,GOLD); b.px(cx-4,oy-4,9,1,(255,236,150))
    elif kind=="star":
        b.px(cx-1,oy-6,2,1,F2); b.px(cx-3,oy-5,6,1,F2); b.px(cx-4,oy-4,8,1,F2); b.px(cx-3,oy-3,2,1,F2); b.px(cx+1,oy-3,2,1,F2); b.px(cx,oy-5,1,1,WHT)

def laptop(b,lx,ly,tool):
    sc=SCR; cc=CODE
    if tool=="Bash": sc=(12,18,14)
    elif tool in ("WebSearch","WebFetch"): sc=(14,27,40); cc=CODEB
    b.px(lx,ly-6,13,7,LAPC); b.px(lx+1,ly-5,11,5,sc)
    for q in range(2):
        ax=lx+2+((b_step+q*3)%8); b.px(ax,ly-4+q,4,1,cc)
    b.px(lx-1,ly+1,15,2,LAPK); b.px(lx-1,ly+1,15,1,(224,226,230))

def window(b,X,Y,w,h):
    b.px(X-2,Y-2,w+4,h+4,FRAME)
    b.px(X,Y,w,h*2//3,SKY[0]); b.px(X,Y+h*2//3,w,h-h*2//3,SKY[1])
    b.px(X+w-8,Y+2,5,5,SUN); b.px(X+3,Y+5,8,2,CLOUD); b.px(X+6,Y+3,6,2,CLOUD)
    b.px(X+3,Y+h-8,6,8,BLDG); b.px(X+w-10,Y+h-6,7,6,BLDG2)
    b.px(X+w//2-7,Y+h-6,5,6,TREED); b.px(X+w//2-9,Y+h-10,8,5,TREE)
    b.px(X+w//2-1,Y,1,h,FRAME); b.px(X,Y+h//2,w,1,FRAME)
    b.px(X-3,Y+h+1,w+6,2,SILL)

def shelves(b,X,Y):
    cups=[(217,83,79),(98,158,200),(110,180,120),(240,190,90),(198,156,224)]
    for i in range(2):
        yy=Y+i*9
        b.px(X,yy,30,1,SHELF); b.px(X,yy+1,30,1,SHELFD)
        for j in range(5):
            cx=X+1+j*6; c=cups[(i*5+j)%5]; b.px(cx,yy-4,4,4,c); b.px(cx,yy-4,4,1,(255,255,255))
    b.px(X+22,Y-5,8,5,LEAF); b.px(X+24,Y-2,4,3,POT)

def hang(b,X):
    b.px(X+2,0,1,5,(120,98,72)); b.px(X-1,5,8,3,POT); b.px(X-1,5,8,1,(216,114,66))
    b.px(X,8,1,4,VINE); b.px(X+2,8,1,5,VINE); b.px(X+4,8,1,3,VINE); b.px(X+6,8,1,4,VINE)
    b.px(X+1,11,1,1,LEAFL); b.px(X+5,12,1,1,LEAFL)

def clock(b,X,Y):
    b.px(X,Y,12,12,CLOCKF); b.px(X+1,Y+1,10,10,CLOCKB)
    b.px(X+6,Y+2,1,4,CLOCKH); b.px(X+6,Y+6,3,1,CLOCKH)
    pts=[(6,2),(9,6),(6,9),(3,6)][(b_step//5)%4]; b.px(X+pts[0],Y+pts[1],1,1,(208,80,80))

def picframe(b,X,Y,kind):
    b.px(X,Y,12,10,PIC); b.px(X+1,Y+1,10,8,PICB)
    if kind==0:
        b.px(X+3,Y+3,2,1,(80,70,60)); b.px(X+7,Y+3,2,1,(80,70,60)); b.px(X+4,Y+6,4,1,(208,120,120))
    else:
        b.px(X+3,Y+5,6,3,(120,180,120)); b.px(X+5,Y+3,2,2,(110,160,240))

def bunting(b):
    b.px(0,4,W,1,(120,108,86)); cols=[F1,F2,F3,F4,F5]; i=0
    for fx in range(2,W-7,15):
        c=cols[i%5]; i+=1; b.px(fx,5,7,1,c); b.px(fx+1,6,5,1,c); b.px(fx+2,7,3,1,c); b.px(fx+3,8,1,1,c)

def sign(b):
    X=(W-36)//2; b.px(X,0,36,10,SIGN); b.px(X,0,36,1,SIGNL); b.px(X,9,36,1,(62,38,15)); b.px(X+1,1,34,1,(116,70,34))
    b.px(X+8,4,4,2,SIGNT); b.px(X+7,2,1,1,SIGNT); b.px(X+9,1,1,1,SIGNT); b.px(X+12,1,1,1,SIGNT); b.px(X+15,2,1,1,SIGNT)
    b.px(X+19,3,5,4,CREAM); b.px(X+24,4,1,2,CREAM); b.px(X+20,2,1,1,STEAM)
    b.px(X+28,2,2,2,F1); b.px(X+31,2,2,2,F1); b.px(X+28,4,5,1,F1); b.px(X+29,5,3,1,F1); b.px(X+30,6,1,1,F1)

def station(b):
    Y=COUNTER_Y
    b.px(2,Y-13,15,13,MACH); b.px(2,Y-13,15,1,(232,110,110)); b.px(2,Y-13,1,13,(232,110,110))
    b.px(4,Y-10,10,4,CHROME); b.px(5,Y-9,8,2,(14,28,22)); b.px(6,Y-8,2,1,(120,200,150))
    b.px(8,Y-4,2,3,(150,156,164)); b.px(7,Y-1,4,1,(150,156,164))
    b.px(13,Y-12,3,2,(255,231,154) if (b_step%20<10) else (200,160,60))
    if (b_step//5)%2==0: b.px(6,Y-15,1,2,STEAM)

def cafe_back(b):
    b.band(0,16,WALL[0]); b.band(16,28,WALL[1]); b.band(28,COUNTER_Y,WALL[2])
    bunting(b); sign(b)
    window(b,3,11,26,18)
    shelves(b,99,12)
    clock(b,34,3)
    picframe(b,86,4,0)
    hang(b,70)
    station(b)
    b.px(0,COUNTER_Y-1,W,2,COUNTERT)

def layout(n):
    if n<=0: return []
    xs,xe=26,120
    if n==1: return [((xs+xe)//2,COUNTER_Y)]
    return [(int(xs+(xe-xs)*i/(n-1)),COUNTER_Y) for i in range(n)]

def workstation(b,cx,P,busy,tool,hat,selected):
    pose="sleep"
    if busy>0: pose="read" if tool in ("Read","WebSearch") else "type"
    oy=COUNTER_Y-23
    cat(b,cx-10,oy,P,pose,b_step)
    item(b,cx-10,oy,hat)
    if selected:
        b.px(cx-2,oy-9,5,1,SELC); b.px(cx-1,oy-8,3,1,SELC); b.px(cx,oy-7,1,1,SELC)
    if pose!="read": laptop(b,cx-7,COUNTER_Y-1,tool)
    b.px(cx+8,COUNTER_Y-5,3,4,MUG); b.px(cx+8,COUNTER_Y-5,3,1,(235,110,106))
    if busy>0 and (b_step//6)%2==0: b.px(cx+9,COUNTER_Y-7,1,1,STEAM)

def counter_front(b, agents, pos, sel, mode, namebuf):
    b.px(0,COUNTER_Y+1,W,H-(COUNTER_Y+1),COUNTER)
    b.px(0,COUNTER_Y+1,W,1,(168,112,66))
    for x in range(0,W,18): b.px(x,COUNTER_Y+2,1,H-(COUNTER_Y+2),COUNTERD)
    b.px(0,H-2,W,2,COUNTERE)
    ny=COUNTER_Y+6
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

# ---------- render: half-block, auto-fit (olcekli cizim) ----------
QUAD={0:" ",8:"\u2598",4:"\u259d",2:"\u2596",1:"\u2597",12:"\u2580",3:"\u2584",10:"\u258c",5:"\u2590",9:"\u259a",6:"\u259e",14:"\u259b",13:"\u259c",11:"\u2599",7:"\u259f",15:"\u2588"}
def _d2(a,b): return (a[0]-b[0])**2+(a[1]-b[1])**2+(a[2]-b[2])**2
def _pick2(ps):
    uniq=[]
    for c in ps:
        if c not in uniq: uniq.append(c)
    if len(uniq)==1: return uniq[0],uniq[0]
    bd=-1; best=(uniq[0],uniq[1])
    for i in range(len(uniq)):
        for j in range(i+1,len(uniq)):
            dd=_d2(uniq[i],uniq[j])
            if dd>bd: bd=dd; best=(uniq[i],uniq[j])
    a,bb=best
    # brighter is foreground for nicer contrast
    if (a[0]+a[1]+a[2])>(bb[0]+bb[1]+bb[2]): a,bb=bb,a
    return a,bb
def render_quadrant(buf):
    cols=buf.w//2; rows=buf.h//2; out=[]
    for cy in range(rows):
        r0=buf.d[cy*2]; r1=buf.d[cy*2+1]; line=[]
        for cx in range(cols):
            x0=cx*2; x1=x0+1
            tl=r0[x0]; tr=r0[x1]; bl=r1[x0]; br=r1[x1]
            if tl==tr==bl==br:
                line.append("\x1b[38;2;%d;%d;%dm\u2588"%tl)
            else:
                bg,fg=_pick2((tl,tr,bl,br)); bits=0
                for p,bv in ((tl,8),(tr,4),(bl,2),(br,1)):
                    if _d2(p,fg)<=_d2(p,bg): bits|=bv
                line.append("\x1b[38;2;%d;%d;%d;48;2;%d;%d;%dm%s"%(fg[0],fg[1],fg[2],bg[0],bg[1],bg[2],QUAD[bits]))
        out.append("".join(line)+"\x1b[0m")
    return out

def _sextchar(v):
    if v==0: return " "
    if v==63: return "\u2588"
    if v==21: return "\u258c"
    if v==42: return "\u2590"
    o=(v-1)-(1 if v>21 else 0)-(1 if v>42 else 0)
    return chr(0x1FB00+o)
def render_sextant(buf):
    cols=buf.w//2; rows=buf.h//3; out=[]
    for cy in range(rows):
        ya=buf.d[cy*3]; yb=buf.d[cy*3+1]; yc=buf.d[cy*3+2]; line=[]
        for cx in range(cols):
            x0=cx*2; x1=x0+1
            p=(ya[x0],ya[x1],yb[x0],yb[x1],yc[x0],yc[x1])
            if p[0]==p[1]==p[2]==p[3]==p[4]==p[5]:
                line.append("\x1b[38;2;%d;%d;%dm\u2588"%p[0])
            else:
                bg,fg=_pick2(p); v=0
                for pp,bv in ((p[0],1),(p[1],2),(p[2],4),(p[3],8),(p[4],16),(p[5],32)):
                    if _d2(pp,fg)<=_d2(pp,bg): v|=bv
                line.append("\x1b[38;2;%d;%d;%d;48;2;%d;%d;%dm%s"%(fg[0],fg[1],fg[2],bg[0],bg[1],bg[2],_sextchar(v)))
        out.append("".join(line)+"\x1b[0m")
    return out

def render_terminal(b):
    HALF="\u2580"; rows=[]
    for ry in range(0,b.h,2):
        top=b.d[ry]; bot=b.d[ry+1] if ry+1<b.h else top; line=[]
        for x in range(b.w):
            tr,tg,tb=top[x]; br,bg,bb=bot[x]
            line.append("\x1b[38;2;%d;%d;%d;48;2;%d;%d;%dm%s"%(tr,tg,tb,br,bg,bb,HALF))
        rows.append("".join(line)+"\x1b[0m")
    return rows

class SC:
    def __init__(s,buf,sc,ox,oy): s.b=buf; s.s=sc; s.ox=ox; s.oy=oy
    def px(s,x,y,w,h,c):
        if c is None: return
        k=s.s; x0=int(x*k+0.5)+s.ox; y0=int(y*k+0.5)+s.oy
        x1=int((x+w)*k+0.5)+s.ox; y1=int((y+h)*k+0.5)+s.oy
        if x1<=x0: x1=x0+1
        if y1<=y0: y1=y0+1
        s.b.px(x0,y0,x1-x0,y1-y0,c)
    def band(s,y0,y1,c): s.px(0,y0,W,y1-y0,c)

def draw_edit_overlay(buf,namebuf,BW,BH):
    txt="AD: "+namebuf
    tw1=text_w(txt); fs=max(2,BW//90)
    fs=min(fs,max(1,(BW-16)//max(1,tw1)))
    cur=(b_step//6)%2==0
    bw=tw1*fs+(2*fs if cur else 0)
    bx=(BW-bw)//2; by=(BH-5*fs)//2; pad=3*fs//2+2
    buf.px(bx-pad,by-pad,bw+2*pad,5*fs+2*pad,(38,28,20))
    buf.px(bx-pad,by-pad,bw+2*pad,2,SELC)
    buf.px(bx-pad,by+5*fs+pad-2,bw+2*pad,2,SELC)
    draw_text_scaled(buf,bx,by,txt,SELC,fs)
    if cur: buf.px(bx+tw1*fs+1,by,2*fs,5*fs,SELC)

BLOCKS="quad"
def _dims(cols,rows):
    if BLOCKS=="sext": return cols*2, rows*3
    if BLOCKS=="half": return cols, rows*2
    return cols*2, rows*2
def build_native(agents,sel,mode,namebuf,cols,rows):
    BW,BH=_dims(cols,rows)
    buf=Buf(BW,BH)
    s=min(BW/float(W), BH/float(H))
    ox=(BW-int(W*s+0.5))//2; oy=(BH-int(H*s+0.5))//2
    cy=max(0,oy+int(COUNTER_Y*s+0.5))
    buf.band(0,cy,WALL[0]); buf.band(cy,BH,COUNTER)
    c=SC(buf,s,ox,oy)
    draw_office(c,agents,sel,mode,namebuf)
    if mode=="name": draw_edit_overlay(buf,namebuf,BW,BH)
    return buf

def render_native(agents,sel,mode,namebuf,cols,rows):
    if cols<8 or rows<4: return "\x1b[H\x1b[2J  pencere cok kucuk"
    buf=build_native(agents,sel,mode,namebuf,cols,rows)
    if BLOCKS=="sext": body=render_sextant(buf)
    elif BLOCKS=="half": body=render_terminal(buf)
    else: body=render_quadrant(buf)
    return "\x1b[H"+"\n".join(body)

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

DSC=[(3,0),(2,1),(3,2),(3,3),(3.5,4),(3,2)]; DTOT=sum(x[0] for x in DSC); DTOOLS=["Edit","Bash","WebSearch","Read","Write"]
def demo_agents(now):
    a=now%DTOT; acc=0; n=0
    for d,nn in DSC:
        acc+=d
        if a<acc: n=nn; break
    return [{"slot":i,"busy":0 if (int(now/1.3+i)%5==0) else 3+(i%3),"tool":None if (int(now/1.3+i)%5==0) else DTOOLS[(i+int(now/1.7))%len(DTOOLS)]} for i in range(n)]

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
    ap.add_argument("--blocks",choices=["half","quad","sext"],default="quad")
    a=ap.parse_args()
    global BLOCKS; BLOCKS=a.blocks
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
            sys.stdout.write(render_native(ags,0,"normal","",W,NEED_ROWS)+"\n")
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
            sz=shutil.get_terminal_size((W,NEED_ROWS)); cols=sz.columns; rows=sz.lines
            sys.stdout.write(render_native(ags,sel,mode,namebuf,cols,rows))
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
