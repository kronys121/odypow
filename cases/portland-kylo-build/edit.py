import os, json, subprocess, sys
B = os.path.dirname(os.path.abspath(__file__))
G = os.path.join(B, 'gfx'); T = os.path.join(B, 'tmp'); os.makedirs(T, exist_ok=True)
PPB = os.path.join(B, '..', 'video', 'ref', 'ppb.mp4')
VO = os.path.join(B, 'vo.mp3')
FPS = 30; SR = 48000
FONT = '/usr/share/fonts/opentype/inter/Inter-Bold.otf'
QUICK = '--quick' in sys.argv

def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode: print(' '.join(cmd)); print(r.stderr[-2000:]); sys.exit(1)

def frames(d): return max(1, round(d * FPS))
ENC = ['-c:v', 'libx264', '-preset', 'ultrafast' if QUICK else 'medium', '-crf', '20', '-pix_fmt', 'yuv420p', '-r', str(FPS)]

def esc(t): return t.replace('\\', '\\\\').replace(':', '\\:').replace("'", "’").replace('%', '\\%')
def caption(text, y='h-150', size=44):
    return (f"drawtext=fontfile={FONT}:text='{esc(text)}':fontsize={size}:fontcolor=white:"
            f"box=1:boxcolor=black@0.65:boxborderw=18:x=(w-text_w)/2:y={y}")
def label(text):
    return (f"drawtext=fontfile={FONT}:text='{esc(text)}':fontsize=30:fontcolor=0xD4A017:"
            f"box=1:boxcolor=black@0.7:boxborderw=14:x=60:y=60")

def v_img(out, name, n, k):
    z = 0.05
    vf = (f"scale=w='trunc(1920*(1+{z}*n/{n})/2)*2':h=-2:eval=frame,crop=1920:1080,setsar=1")
    if k % 2: vf = (f"scale=w='trunc(1920*(1+{z}-{z}*n/{n})/2)*2':h=-2:eval=frame,crop=1920:1080,setsar=1")
    run(['ffmpeg', '-y', '-v', 'error', '-loop', '1', '-framerate', str(FPS), '-i', os.path.join(G, name + '.png'),
         '-vf', vf, '-frames:v', str(n), *ENC, out])

def v_clip(out, ss, n, speed=1.0, extra=None):
    src = n / FPS * speed + 0.5
    vf = f"setpts=(PTS-STARTPTS)/{speed},fps={FPS},scale=1920:1080,setsar=1,tpad=stop_mode=clone:stop_duration=5"
    if extra: vf += ',' + ','.join(extra)
    run(['ffmpeg', '-y', '-v', 'error', '-ss', str(ss), '-t', str(src), '-i', PPB, '-an', '-vf', vf, '-frames:v', str(n), *ENC, out])

def v_black(out, n, extra=None):
    vf = 'null' if not extra else ','.join(extra)
    run(['ffmpeg', '-y', '-v', 'error', '-f', 'lavfi', '-i', f'color=c=0x0B0D10:s=1920x1080:r={FPS}', '-vf', vf, '-frames:v', str(n), *ENC, out])

def a_vo(out, a, b):
    run(['ffmpeg', '-y', '-v', 'error', '-i', VO, '-af', f'atrim={a}:{b},asetpts=N/SR/TB,aresample={SR},apad', '-ac', '2',
         '-t', str(frames(b - a) / FPS), '-c:a', 'pcm_s16le', out])
def a_ppb(out, ss, d, gain_lufs=-17):
    run(['ffmpeg', '-y', '-v', 'error', '-ss', str(ss), '-t', str(d + 0.2), '-i', PPB, '-vn',
         '-af', f'loudnorm=I={gain_lufs}:TP=-2:LRA=11,aresample={SR},afade=t=in:d=0.08,afade=t=out:st={d-0.12}:d=0.12,apad',
         '-ac', '2', '-t', str(frames(d) / FPS), '-c:a', 'pcm_s16le', out])
def a_sil(out, d):
    run(['ffmpeg', '-y', '-v', 'error', '-f', 'lavfi', '-i', f'anullsrc=r={SR}:cl=stereo', '-t', str(frames(d) / FPS), '-c:a', 'pcm_s16le', out])

# ---------------- timeline ----------------
# VO chunk: (vo_start, vo_end, [(abs_vo_time, kind, arg...)])
CH = [
 (0.0, 35.3, [(0, 'img', 'kylo'), (16.2, 'clip', 141.5, 0.95), (27.9, 'black')]),
 ('title', 4.0),
 (35.3, 234.35, [(35.3, 'clip', 55.5, 1.0, 'GRESHAM, OREGON · SEPT 24, 2026 · ~7:00 A.M.'), (46.6, 'img', 'victim'), (56.96, 'img', 'leads'),
                 (77.9, 'img', 'm_surv'), (83.0, 'clip', 66.5, 1.0, '17900 BLOCK OF SE MARKET ST'), (90.78, 'img', 'alpr'),
                 (104.38, 'clip', 82.0, 1.0, 'SE 99TH AVE & SE PINE ST, PORTLAND'), (123.26, 'img', 'suspect'), (136.03, 'img', 'm_diffperson'),
                 (150.15, 'img', 'taskforce'), (169.71, 'img', 'kylo'), (177.39, 'img', 'map1'),
                 (199.52, 'clip', 111.0, 1.0, 'PPB AIR VIDEO'), (211.6, 'img', 'map2')]),
 ('block', 439.5, 454.0, 'PPB AIR VIDEO · ORIGINAL AUDIO', [(448.0, 451.2, '“Guy’s jumping in a car. I don’t know if he carjacked a car, dude.”'), (452.0, 453.6, '“What is going on?”')]),
 (234.35, 263.3, [(234.35, 'img', 'map2'), (242.48, 'img', 'map3')]),
 ('block', 139.6, 152.6, 'OFFICER ABLES · BODY CAMERA', [(140.0, 152.6, 'K9 Kylo released')]),
 (263.3, 347.05, [(263.3, 'img', 'fender'), (277.67, 'clip', 152.8, 0.75, 'MOTEL SURVEILLANCE VIDEO'), (286.0, 'img', 'm_backpack'),
                  (294.3, 'img', 'lot'), (320.62, 'clip', 176.0, 1.0, 'PPB HIGHLIGHT: FIREARM'), (328.68, 'img', 'm_bothhands'),
                  (338.2, 'clip', 181.0, 1.0, 'PPB HIGHLIGHT: FIREARM')]),
 ('block', 209.3, 221.8, 'OFFICERS FENDER (L) AND ABLES (R) · BODY CAMERAS',
  [(209.6, 212.3, '“Get on the ground! Get on the ground!”'), (213.1, 215.6, '“Get your hands out!”'),
   (216.9, 218.2, '“Hands out to your side!”'), (219.0, 221.8, '“Drop the gun! Drop the gun!”')]),
 ('gap', 1.2),
 (347.05, 374.75, [(347.05, 'img', 'shots'), (363.32, 'black')]),
 ('block', 224.7, 226.3, None, [(224.7, 226.3, '“Ah, no!”')], 'black'),
 ('gap', 0.8),
 (374.75, 649.874, [(374.75, 'img', 'dead'), (392.04, 'img', 'kylo2'), (416.11, 'clip', 275.0, 0.45, 'PPB'), (424.27, 'img', 'gun'),
                    (436.27, 'img', 'map4'), (452.11, 'img', 'm_empty'), (469.05, 'img', 'nibin'), (485.45, 'img', 'tox'),
                    (492.49, 'img', 'da'), (510.17, 'img', 'm_grandjury'), (522.32, 'img', 'm_kylo'),
                    (543.6, 'clip', 0.0, 1.0, 'PPB VIDEO RELEASE · OCT 8, 2026'), (559.36, 'img', 'q_kanal'), (579.52, 'img', 'q_day'),
                    (595.48, 'clip', 467.5, 1.0, 'MOTEL SURVEILLANCE VIDEO'), (605.08, 'img', 'pending'), (628.89, 'img', 'kylo'),
                    (636.49, 'img', 'end')]),
 ('tail', 2.5, 'end'),
]

vparts, aparts, srt_map, out_t, k = [], [], [], 0.0, 0
def add(v, a, d):
    global out_t
    vparts.append(v); aparts.append(a); out_t += frames(d) / FPS

for ci, c in enumerate(CH):
    tag = f'{ci:02d}'
    if c[0] == 'title':
        v, a = f'{T}/{tag}.mp4', f'{T}/{tag}.wav'; v_img(v, 'title', frames(c[1]), 0); a_sil(a, c[1]); add(v, a, c[1])
    elif c[0] in ('gap',):
        v, a = f'{T}/{tag}.mp4', f'{T}/{tag}.wav'; v_black(v, frames(c[1])); a_sil(a, c[1]); add(v, a, c[1])
    elif c[0] == 'tail':
        v, a = f'{T}/{tag}.mp4', f'{T}/{tag}.wav'; v_img(v, c[2], frames(c[1]), 0); a_sil(a, c[1]); add(v, a, c[1])
    elif c[0] == 'block':
        _, s, e, lab, caps = c[:5]; d = e - s; n = frames(d)
        ex = [label(lab)] if lab else []
        for cs, ce, txt in caps:
            ex.append(caption(txt).replace("y=h-150", f"y=h-150:enable='between(t,{cs - s:.2f},{ce - s:.2f})'"))
        v, a = f'{T}/{tag}.mp4', f'{T}/{tag}.wav'
        if len(c) > 5 and c[5] == 'black': v_black(v, n, ex)
        else: v_clip(v, s, n, 1.0, ex)
        a_ppb(a, s, d); add(v, a, d)
        srt_map.append(('block', out_t - frames(d) / FPS, caps, s))
    else:
        a0, a1, shots = c
        srt_map.append(('vo', out_t, a0, a1))
        a = f'{T}/{tag}.wav'; a_vo(a, a0, a1)
        total = frames(a1 - a0); used = 0; sub = []
        for si, sh in enumerate(shots):
            st = sh[0]; en = shots[si + 1][0] if si + 1 < len(shots) else a1
            n = frames(en - a0) - used if si + 1 < len(shots) else total - used; used += n
            vp = f'{T}/{tag}_{si:02d}.mp4'
            if sh[1] == 'img': v_img(vp, sh[2], n, k); k += 1
            elif sh[1] == 'clip': v_clip(vp, sh[2], n, sh[3], [label(sh[4])] if len(sh) > 4 else None)
            else: v_black(vp, n)
            sub.append(vp)
        lst = f'{T}/{tag}.txt'; open(lst, 'w').write(''.join(f"file '{p}'\n" for p in sub))
        v = f'{T}/{tag}.mp4'; run(['ffmpeg', '-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', v])
        add(v, a, a1 - a0)
    print('done', tag, round(out_t, 2), flush=True)

lst = f'{T}/all.txt'; open(lst, 'w').write(''.join(f"file '{p}'\n" for p in vparts))
run(['ffmpeg', '-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', f'{T}/video.mp4'])
alst = f'{T}/alla.txt'; open(alst, 'w').write(''.join(f"file '{p}'\n" for p in aparts))
run(['ffmpeg', '-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', alst, '-c', 'copy', f'{T}/audio.wav'])
OUTF = os.path.join(B, 'out', 'portland_kylo_rough_cut.mp4'); os.makedirs(os.path.dirname(OUTF), exist_ok=True)
run(['ffmpeg', '-y', '-v', 'error', '-i', f'{T}/video.mp4', '-i', f'{T}/audio.wav', '-map', '0:v', '-map', '1:a',
     '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-ar', str(SR), '-movflags', '+faststart', OUTF])

# ---------------- SRT ----------------
cues = json.load(open(os.path.join(B, 'vo.json')))['cues']
def ts(t):
    ms = int(round(t * 1000)); return f'{ms//3600000:02d}:{ms//60000%60:02d}:{ms//1000%60:02d},{ms%1000:03d}'
items = []
for m in srt_map:
    if m[0] == 'vo':
        _, off, a0, a1 = m
        for cu in cues:
            if a0 <= cu['start'] < a1: items.append((off + cu['start'] - a0, off + min(cu['end'], a1) - a0, cu['text']))
    else:
        _, off, caps, s = m
        for cs, ce, txt in caps: items.append((off + cs - s, off + ce - s, f'[{txt}]'))
items.sort()
with open(os.path.join(B, 'out', 'portland_kylo_rough_cut.en.srt'), 'w') as f:
    for i, (a, b, t) in enumerate(items, 1): f.write(f'{i}\n{ts(a)} --> {ts(b)}\n{t}\n\n')
print('OUT', OUTF, round(out_t, 2))
