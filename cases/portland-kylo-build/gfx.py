import os, re, html, subprocess
from PIL import Image, ImageDraw, ImageFont, ImageFilter

B = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(B, 'gfx'); os.makedirs(OUT, exist_ok=True)
SRC = os.path.join(B, '..', 'video', 'src')
MEMO = os.path.join(B, '..', 'dl', 'memo.pdf')
W, H = 1920, 1080
BG = (11, 13, 16); FG = (232, 230, 227); DIM = (140, 140, 140)
AMBER = (212, 160, 23); RED = (192, 57, 43); BLUE = (70, 130, 200); GRID = (36, 40, 46)
FD = '/usr/share/fonts/opentype/inter/'
def F(sz, w='SemiBold', disp=False):
    return ImageFont.truetype(FD + ('InterDisplay-' if disp else 'Inter-') + w + '.otf', sz)
MONO = lambda sz: ImageFont.truetype('/usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-Regular.ttf', sz) if os.path.exists('/usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-Regular.ttf') else F(sz, 'Medium')

def canvas():
    im = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(im)
    # subtle vignette grid
    for x in range(0, W, 120): d.line([(x, 0), (x, H)], fill=(16, 18, 22))
    for y in range(0, H, 120): d.line([(0, y), (W, y)], fill=(16, 18, 22))
    return im, d

def wrap(d, text, font, maxw):
    words, lines, cur = text.split(), [], ''
    for w in words:
        t = (cur + ' ' + w).strip()
        if d.textlength(t, font=font) <= maxw: cur = t
        else: lines.append(cur); cur = w
    if cur: lines.append(cur)
    return lines

def save(im, name):
    p = os.path.join(OUT, name + '.png'); im.save(p); return p

def kicker(d, x, y, text, color=AMBER):
    d.rectangle([x, y + 6, x + 8, y + 34], fill=color)
    d.text((x + 24, y), text.upper(), font=F(30, 'Bold'), fill=color)

def card(name, kick, title, lines=(), color=AMBER):
    im, d = canvas()
    x = 180; y = 330 - 30 * len(lines)
    kicker(d, x, y, kick, color); y += 70
    for ln in wrap(d, title, F(84, 'Bold', True), 1560):
        d.text((x, y), ln, font=F(84, 'Bold', True), fill=FG); y += 100
    y += 30
    for ln in lines:
        hi = ln.startswith('!'); ln = ln.lstrip('!')
        for l2 in wrap(d, ln, F(42, 'Medium'), 1560):
            d.text((x, y), l2, font=F(42, 'Medium'), fill=FG if hi else DIM); y += 58
        y += 10
    return save(im, name)

def quote(name, who, text, src):
    im, d = canvas()
    d.text((160, 170), '“', font=F(260, 'Bold', True), fill=AMBER)
    y = 360
    for ln in wrap(d, text, F(64, 'Medium', True), 1540):
        d.text((180, y), ln, font=F(64, 'Medium', True), fill=FG); y += 84
    y += 40
    d.text((180, y), who, font=F(40, 'Bold'), fill=AMBER)
    d.text((180, y + 56), src, font=F(30, 'Medium'), fill=DIM)
    return save(im, name)

def title():
    im, d = canvas()
    t1 = '90 SECONDS'; t2 = 'IN PORTLAND'
    f = F(170, 'Black', True) if os.path.exists(FD + 'InterDisplay-Black.otf') else F(170, 'Bold', True)
    for i, t in enumerate([t1, t2]):
        w = d.textlength(t, font=f); d.text(((W - w) / 2, 330 + i * 190), t, font=f, fill=FG if i == 0 else AMBER)
    s = 'SEPTEMBER 24, 2026  ·  SE PORTLAND, OREGON'
    w = d.textlength(s, font=F(34, 'Medium')); d.text(((W - w) / 2, 740), s, font=F(34, 'Medium'), fill=DIM)
    return save(im, 'title')

# ---------- map ----------
PINE, OAK, STARK = 300, 560, 830
X97, X98, X99 = 640, 960, 1300
def street_map(stage):
    im, d = canvas()
    for y, n in [(PINE, 'SE PINE ST'), (OAK, 'SE OAK ST'), (STARK, 'SE STARK ST')]:
        d.rectangle([0, y - 14, W, y + 14], fill=GRID); d.text((40, y - 52), n, font=F(26, 'Bold'), fill=DIM)
    for x, n in [(X97, 'SE 97TH AVE'), (X98, ''), (X99, 'SE 99TH AVE')]:
        d.rectangle([x - (14 if n else 6), 0, x + (14 if n else 6), H], fill=GRID)
        if n:
            tmp = Image.new('RGBA', (300, 40), (0, 0, 0, 0)); ImageDraw.Draw(tmp).text((0, 0), n, font=F(26, 'Bold'), fill=DIM)
            tmp = tmp.rotate(90, expand=True); im.paste(tmp, (x - 56, 900), tmp)
    # buildings
    d.rectangle([1340, 340, 1620, 500], outline=BLUE, width=4); d.text((1360, 360), 'MONTAVILLA\nMOTEL', font=F(28, 'Bold'), fill=BLUE)
    d.rectangle([680, 600, 1000, 790], outline=AMBER, width=4); d.text((700, 620), 'CHESTNUT TREE INN\n(PARKING LOT)', font=F(26, 'Bold'), fill=AMBER)
    d.text((1580, 40), 'NOT TO SCALE', font=F(22, 'Bold'), fill=(70, 70, 70))
    d.polygon([(1840, 120), (1825, 160), (1855, 160)], fill=DIM); d.text((1832, 166), 'N', font=F(24, 'Bold'), fill=DIM)
    def path(pts, col, w=10, dash=False):
        for a, b in zip(pts, pts[1:]):
            if not dash: d.line([a, b], fill=col, width=w)
            else:
                import math
                L = math.dist(a, b); n = int(L // 30)
                for i in range(0, n, 2):
                    p1 = (a[0] + (b[0] - a[0]) * i / n, a[1] + (b[1] - a[1]) * i / n)
                    p2 = (a[0] + (b[0] - a[0]) * (i + 1) / n, a[1] + (b[1] - a[1]) * (i + 1) / n)
                    d.line([p1, p2], fill=col, width=w)
    def dot(p, col, label=None, dx=20, dy=-50):
        d.ellipse([p[0] - 16, p[1] - 16, p[0] + 16, p[1] + 16], fill=col, outline=BG, width=4)
        if label:
            f = F(28, 'Bold'); tw = d.textlength(label, font=f)
            d.rectangle([p[0] + dx - 10, p[1] + dy - 6, p[0] + dx + tw + 10, p[1] + dy + 38], fill=BG)
            d.text((p[0] + dx, p[1] + dy), label, font=f, fill=col)
    if stage >= 1:
        path([(1460, PINE), (760, PINE)], RED)
        dot((1460, PINE), RED, '1:48 PM  CONTACT', -120, -64)
    if stage >= 2:
        path([(760, PINE + 40), (1220, PINE + 40)], AMBER, 6, dash=True)
        dot((760, PINE), AMBER, 'CARJACK ATTEMPT', -40, 40)
        dot((X99, PINE), BLUE, 'K9 UNIT BLOCKS ROAD', 20, -64)
        path([(1200, PINE - 30), (X97, PINE - 30)], RED, 6)
    if stage >= 3:
        path([(X97, PINE), (X97, 690), (820, 690)], RED)
        path([(X97 + 40, STARK), (X97 + 40, 720)], BLUE, 6, dash=True)
        dot((X97 + 40, 760), BLUE, 'OFC. FENDER', 30, 10)
        dot((X97, 400), BLUE, 'K9 KYLO SENT', -300, -20)
        dot((820, 690), RED)
    if stage >= 4:
        d.rectangle([X97 - 34, 460, X97 - 8, 500], fill=AMBER)
        f = F(28, 'Bold'); d.rectangle([230, 458, 590, 502], fill=BG)
        d.text((240, 462), 'MAGAZINE FOUND HERE', font=f, fill=AMBER)
        d.line([(590, 480), (X97 - 36, 480)], fill=AMBER, width=3)
    return save(im, f'map{stage}')

def lot():
    im, d = canvas()
    d.rectangle([300, 120, 1620, 260], fill=(40, 46, 56)); d.text((330, 150), 'MOTEL BUILDING', font=F(30, 'Bold'), fill=DIM)
    d.rectangle([300, 260, 1620, 980], outline=(50, 50, 50), width=3)
    for x in range(380, 1600, 160): d.line([(x, 860), (x, 980)], fill=(90, 80, 30), width=4)
    c = (960, 360); k = (960, 300); fe = (960, 360 + 21 * 22); ab = (960 + 15 * 22, 360)
    dp = [(420, 620), (440, 720)]
    d.line([c, fe], fill=(90, 90, 90), width=3); d.line([c, ab], fill=(90, 90, 90), width=3); d.line([fe, ab], fill=(60, 60, 60), width=2)
    for p in dp: d.line([c, p], fill=(70, 70, 70), width=2)
    def tag(p, t, col, dx=30, dy=-18):
        d.ellipse([p[0] - 20, p[1] - 20, p[0] + 20, p[1] + 20], fill=col, outline=BG, width=4)
        d.text((p[0] + dx, p[1] + dy), t, font=F(30, 'Bold'), fill=col)
    tag(k, 'K9 KYLO (holding backpack)', AMBER, 34, -40)
    tag(c, 'CAMPBELL (on ground)', RED, -400, -10)
    tag(fe, 'OFC. FENDER  ·  ~21 FT', BLUE)
    tag(ab, 'OFC. ABLES  ·  ~15 FT', BLUE, 34, -10)
    tag(dp[0], 'DEPUTY DIAZ', BLUE, -10, -64); tag(dp[1], 'DEP. U.S. MARSHAL PFENNING', BLUE, -10, 30)
    d.text((140, 860), 'FROM SE 97TH AVE →\n35–40 FT', font=F(28, 'Bold'), fill=DIM)
    d.text((1660, 1000), 'NOT TO SCALE', font=F(22, 'Bold'), fill=(70, 70, 70))
    d.text((1260, 520), 'No cover.\nOfficers in the open.', font=F(34, 'Medium'), fill=FG)
    return save(im, 'lot')

def shots():
    im, d = canvas()
    kicker(d, 180, 150, 'Rounds fired · per DA memo')
    rows = [('Officer Jerry Ables (PPB)', 4), ('Officer Kameron Fender (PPB)', 5), ('Deputy Christian Diaz (Clackamas Co.)', 3), ('Dep. U.S. Marshal Aaron Pfenning', 1)]
    y = 260
    for n, c in rows:
        d.text((180, y), n, font=F(44, 'Medium'), fill=FG)
        for i in range(c): d.rectangle([1080 + i * 54, y + 6, 1110 + i * 54, y + 50], fill=AMBER)
        d.text((1400, y), str(c), font=F(48, 'Bold'), fill=AMBER); y += 110
    d.line([(180, y), (1500, y)], fill=(60, 60, 60), width=2)
    d.text((180, y + 30), 'TOTAL', font=F(44, 'Bold'), fill=FG); d.text((1400, y + 24), '13', font=F(60, 'Bold'), fill=AMBER)
    d.text((180, y + 120), 'About 10 rounds struck Campbell. K9 Kylo was also hit.', font=F(40, 'Medium'), fill=DIM)
    return save(im, 'shots')

def photo_card(name, src, kick, title, lines=(), box=None):
    im, d = canvas()
    ph = Image.open(src).convert('RGB')
    ph.thumbnail((820, 900))
    im.paste(ph, (1880 - ph.width, (H - ph.height) // 2))
    x = 120; y = 300
    kicker(d, x, y, kick); y += 70
    for ln in wrap(d, title, F(72, 'Bold', True), 860): d.text((x, y), ln, font=F(72, 'Bold', True), fill=FG); y += 86
    y += 24
    for ln in lines:
        for l2 in wrap(d, ln, F(38, 'Medium'), 860): d.text((x, y), l2, font=F(38, 'Medium'), fill=DIM); y += 52
        y += 8
    return save(im, name)

# ---------- memo excerpts ----------
def memo_words():
    raw = subprocess.run(['pdftotext', '-bbox', MEMO, '-'], capture_output=True, text=True).stdout
    out, page = [], -1
    for line in raw.split('\n'):
        if '<page ' in line: page += 1
        m = re.search(r'xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">(.*)</word>', line)
        if m: out.append((page, *map(float, m.groups()[:4]), html.unescape(m.group(5))))
    return out
MW = None
def norm(s): return re.sub(r'[^a-z0-9]', '', s.lower())
def memo(name, phrase, ctx_lines=2):
    global MW
    MW = MW or memo_words()
    toks = [norm(t) for t in phrase.split() if norm(t)]
    seq = [norm(w[5]) for w in MW]
    for i in range(len(seq)):
        if seq[i:i + len(toks)] == toks: break
    else: raise ValueError(phrase)
    hit = MW[i:i + len(toks)]; page = hit[0][0]
    dpi = 220; sc = dpi / 72
    pp = os.path.join(OUT, f'memo_p{page}.png')
    if not os.path.exists(pp):
        subprocess.run(['pdftoppm', '-r', str(dpi), '-f', str(page + 1), '-l', str(page + 1), '-png', '-singlefile', MEMO, pp[:-4]], check=True)
    pg = Image.open(pp).convert('RGB')
    hl = Image.new('RGBA', pg.size, (0, 0, 0, 0)); hd = ImageDraw.Draw(hl)
    for w in hit: hd.rectangle([w[1] * sc - 4, w[2] * sc - 2, w[3] * sc + 4, w[4] * sc + 4], fill=(255, 210, 40, 110))
    pg = Image.alpha_composite(pg.convert('RGBA'), hl).convert('RGB')
    y0 = min(w[2] for w in hit) * sc; y1 = max(w[4] for w in hit) * sc
    lines = []
    for w in sorted([w for w in MW if w[0] == page], key=lambda w: w[2]):
        if lines and abs(w[2] - lines[-1][0]) < 3: lines[-1][1] = max(lines[-1][1], w[4])
        else: lines.append([w[2], w[4]])
    li = lambda y: min(range(len(lines)), key=lambda k: abs(lines[k][0] - y))
    i0 = max(0, li(hit[0][2]) - ctx_lines); i1 = min(len(lines) - 1, li(hit[-1][2]) + ctx_lines)
    top = lines[i0][0] * sc - 2; bot = lines[i1][1] * sc + 4
    xl = min(w[1] for w in MW if w[0] == page) * sc - 6; xr = max(w[3] for w in MW if w[0] == page) * sc + 6
    from PIL import ImageOps
    crop = ImageOps.expand(pg.crop((int(xl), int(top), int(xr), int(bot))), border=40, fill='white')
    im, d = canvas()
    scale = min(1640 / crop.width, 760 / crop.height); crop = crop.resize((int(crop.width * scale), int(crop.height * scale)), Image.LANCZOS)
    sh = Image.new('RGBA', (crop.width + 60, crop.height + 60), (0, 0, 0, 0)); ImageDraw.Draw(sh).rectangle([30, 30, crop.width + 30, crop.height + 30], fill=(0, 0, 0, 180))
    sh = sh.filter(ImageFilter.GaussianBlur(18))
    px = (W - crop.width) // 2; py = 200 + (760 - crop.height) // 2
    im.paste(sh, (px - 20, py - 10), sh); im.paste(crop, (px, py))
    kicker(d, 140, 80, 'Multnomah County DA · Prosecution Decline Memo · Oct 8, 2026')
    return save(im, name)

if __name__ == '__main__':
    title()
    for s in range(5): street_map(s)
    lot(); shots()
    card('victim', 'Gresham, Oregon · Sept 24, 2026 · ~7:00 a.m.', 'Jeff Thompson, 60', ['Found dead during a welfare check, 17900 block of SE Market St.', 'Apparent gunshot wound to the head.'])
    card('leads', 'East County Major Crimes Team', 'Two early leads', ['!1.  Thompson’s car is missing from the driveway.', '!2.  Sept 23, evening: a witness saw someone go inside with Thompson. Surveillance video shows his car leaving soon after.'])
    card('alpr', 'Automatic License Plate Reader', 'PLATE OF INTEREST', ['Alert from a camera on a private commercial vehicle.', '!Hit: near the Montavilla Motel, SE 99th Ave & SE Pine St, Portland.'], BLUE)
    card('suspect', 'Identified', 'Eddie Brandon Todd Campbell, 39', ['Outstanding warrant: post-prison supervision violation, weapons offense.', 'Suspect in the killing of Jeff Thompson. Never charged or tried.'], RED)
    card('taskforce', 'U.S. Marshals Service', 'Pacific Northwest Violent Offender Task Force', ['Federal marshals and local officers, including Portland Police.', '!Officer Jerry Ables · PPB K9 Unit · 21 years · partner: K9 Kylo'], BLUE)
    card('fender', 'Task force member', 'Officer Kameron Fender', ['Portland Police Bureau · K9 Unit · 17 years'], BLUE)
    card('dead', 'SE Stark St · ~1:59 p.m.', 'Campbell pronounced dead at the scene', ['Patrol officers began aid within a minute. Paramedics arrived in about five minutes.'], RED)
    card('nibin', 'NIBIN · ATF correlation review', '“Presumptive significant link”', ['Casing from Campbell’s .22 vs. casings from Jeff Thompson’s house in Gresham.', '!Pending confirmation by the Oregon State Police Crime Lab.'], BLUE)
    card('tox', 'Autopsy · preliminary toxicology', 'THC · methamphetamine · alcohol')
    card('da', 'October 8, 2026 · Multnomah County DA Nathan Vasquez', 'Justified under Oregon law. No charges.', ['!No grand jury: “no material facts in dispute.”', 'Evidence: multiple body cameras, aerial video, surveillance video, independent witnesses.'])
    card('pending', 'Still open', 'What happens next', ['!Police Review Board', '!Chief’s ruling on whether the shooting followed bureau policy', '!Oregon State Police Crime Lab confirmation on the gun', 'Officers Ables and Fender: standard administrative leave.'])
    card('end', 'Sources in the description', 'DA memo · PPB footage · news reports', ['Body camera footage: Portland Police Bureau. Used for commentary and news reporting.'])
    quote('q_kanal', 'Sameer Kanal, Portland City Councilor', 'Incomplete footage which goes beyond objective documentation of an incident undermines trust in both local law enforcement and the City broadly.', 'via KATU')
    quote('q_day', 'Bob Day, Portland Police Chief (paraphrased)', 'Releasing video without context may leave viewers \u201Cwithout important information needed to understand what they are seeing.\u201D', 'via KATU')
    photo_card('kylo', os.path.join(SRC, 'kylo.jpg'), 'Portland Police K9', 'Kylo', ['German shepherd. About six years of service, 139 captures.', 'September 24 was scheduled to be his last shift.'])
    photo_card('kylo2', os.path.join(SRC, 'kylo.jpg'), 'End of watch · Sept 24, 2026', 'K9 Kylo', ['Struck by police gunfire. Euthanized on veterinarians’ advice.', 'His body, draped in a U.S. flag, was escorted to the Oregon Humane Society.'])
    photo_card('gun', os.path.join(SRC, 'gun.jpg'), '.22-caliber Jennings', 'No magazine. Empty chamber.', ['One live round on the ground next to Campbell. More loose in his pocket.', 'Photo: Portland Police Bureau'])
    memo('m_diffperson', 'a different person than detectives initially thought, but who also had an outstanding warrant for his arrest')
    memo('m_surv', 'detectives observed Mr. Thompson’s missing vehicle leaving the area on surveillance video')
    memo('m_backpack', 'likely by his backpack')
    memo('m_bothhands', 'He then holds it with both hands appearing to point it directly in Officer Fender’s direction before transferring it to his left hand.')
    memo('m_empty', 'found the magazine missing and the chamber of the firearm empty')
    memo('m_grandjury', 'this investigation will not be presented to the grand jury as there are no material facts in dispute')
    memo('m_kylo', 'This remains true even with Kylo being in danger of being hit')
    memo('m_90s', 'occurred in approximately a minute and a half')
    print(sorted(os.listdir(OUT)))
