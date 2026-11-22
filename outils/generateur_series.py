import asyncio, os
from playwright.async_api import async_playwright
OUT=os.environ.get("OUT", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "sortie"))
CSS="""
*{margin:0;padding:0;box-sizing:border-box}
:root{--navy:#17457d;--blue:#2f78c4;--orange:#e8681a;--ink:#1d2a3a;--grey:#8a96a6}
body{background:#ccc}
.s{width:1080px;height:1350px;position:relative;overflow:hidden;font-family:'Fira Sans',sans-serif;color:var(--ink);background:#e9ebee}
.tex{position:absolute;inset:0;filter:url(#noise);opacity:.55}
.grid{position:absolute;inset:40px;border:2px solid #b9c0ca;background-image:linear-gradient(#d3d8df 1.5px,transparent 1.5px),linear-gradient(90deg,#d3d8df 1.5px,transparent 1.5px);background-size:250px 250px;background-position:-2px -2px}
.lab{position:absolute;left:90px;top:95px;font-weight:800;font-size:34px;letter-spacing:3px;padding:10px 22px;color:#fff;background:var(--navy)}
.lab.p{background:var(--orange)}
h1{position:absolute;left:90px;right:90px;top:170px;font-weight:700;color:var(--navy);font-size:68px;line-height:1.06}
h1 em{font-style:normal;color:var(--orange)}
h1 small{display:block;font-size:32px;font-weight:500;color:var(--orange);margin-top:22px}
.ill{position:absolute;left:90px;width:900px}
.box{position:absolute;left:90px;right:90px;background:rgba(245,247,250,.88);border:3px solid var(--navy);padding:20px 28px;font-size:30px;line-height:1.28}
.box b{color:var(--navy)}
.box.o{border-color:var(--orange);background:rgba(252,238,226,.92)}
.box.o b{color:var(--orange)}
.box:before,.box:after{content:"";position:absolute;width:50px;height:50px;border:5px solid var(--navy)}
.box:before{top:-15px;left:-15px;border-right:none;border-bottom:none}
.box:after{bottom:-15px;right:-15px;border-left:none;border-top:none}
.box.o:before,.box.o:after{border-color:var(--orange)}
.stack{position:absolute;left:90px;right:90px;display:flex;flex-direction:column;gap:36px}
.stack .box{position:relative;left:auto;right:auto}
.wm{position:absolute;right:80px;bottom:62px;font-size:26px;font-weight:600;color:var(--navy)}
.pg{position:absolute;left:80px;bottom:62px;font-size:26px;font-weight:700;color:var(--grey)}
.swipe{position:absolute;left:0;right:0;bottom:115px;text-align:center;font-size:28px;font-weight:700;color:var(--orange)}
svg text{font-family:'Fira Sans'}
"""
DEFS="""<svg width="0" height="0" style="position:absolute"><filter id="noise"><feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="3" seed="4"/><feColorMatrix values="0 0 0 0 .55  0 0 0 0 .57  0 0 0 0 .6  0 0 0 .35 0"/></filter><defs>
<g id="sun"><circle r="46" fill="none" stroke="#e8681a" stroke-width="7"/><g stroke="#e8681a" stroke-width="7" stroke-linecap="round"><line x1="0" y1="-68" x2="0" y2="-90"/><line x1="0" y1="68" x2="0" y2="90"/><line x1="-68" y1="0" x2="-90" y2="0"/><line x1="68" y1="0" x2="90" y2="0"/><line x1="48" y1="48" x2="64" y2="64"/><line x1="-48" y1="-48" x2="-64" y2="-64"/><line x1="48" y1="-48" x2="64" y2="-64"/><line x1="-48" y1="48" x2="-64" y2="64"/></g></g>
<g id="drop"><path d="M0 -34 C14 -14 24 0 24 12 A24 24 0 0 1 -24 12 C-24 0 -14 -14 0 -34Z" fill="#2f78c4"/></g>
<pattern id="conc" width="40" height="40" patternUnits="userSpaceOnUse"><rect width="40" height="40" fill="#9aa3ae"/><circle cx="8" cy="10" r="3" fill="#7d8792"/><circle cx="28" cy="24" r="4" fill="#858f9a"/><circle cx="18" cy="34" r="2" fill="#6f7984"/></pattern>
<pattern id="soil" width="30" height="30" patternUnits="userSpaceOnUse"><rect width="30" height="30" fill="#b8a48a"/><circle cx="7" cy="8" r="2.5" fill="#9b8669"/><circle cx="21" cy="19" r="3" fill="#a48f72"/></pattern>
<pattern id="block" width="120" height="60" patternUnits="userSpaceOnUse"><rect width="120" height="60" fill="#c3cad3"/><rect x="2" y="2" width="116" height="56" fill="#cfd5dc" stroke="#9aa4b0" stroke-width="3"/></pattern>
<marker id="ar" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10z" fill="#e8681a"/></marker>
<marker id="arb" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10z" fill="#2f78c4"/></marker>
<marker id="arn" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10z" fill="#17457d"/></marker>
</defs></svg>"""
WM='<div class="wm">Wilfried · Plans &amp; Construction</div>'

def slide(i,n,body,swipe=False):
    return f'<div class="s"><div class="tex"></div><div class="grid"></div>{body}<div class="pg">{i} / {n}</div>{WM}{"<div class=swipe>Glisse pour la solution →</div>" if swipe else ""}</div>'

SERIES={}
# ---------- A : CURE ----------
SERIES["cure"]=[
f'''<div class="lab p">PROBLÈME</div><h1>Ta dalle fissure<br>au <em>soleil</em> ?<small>La cause est souvent dans les 7 jours après le coulage</small></h1>
<svg class="ill" style="top:564px;left:216px" width="648" height="446" viewBox="0 0 900 620">
 <use href="#sun" x="760" y="110"/>
 <g stroke="#2f78c4" stroke-width="6" stroke-dasharray="14 10" fill="none"><path d="M200 330 C190 280 215 250 200 200"/><path d="M400 330 C390 280 415 250 400 200"/><path d="M600 330 C590 280 615 250 600 200"/></g>
 <g fill="#2f78c4"><path d="M188 210 L200 180 L212 210Z"/><path d="M388 210 L400 180 L412 210Z"/><path d="M588 210 L600 180 L612 210Z"/></g>
 <rect x="30" y="350" width="840" height="190" fill="url(#conc)" stroke="#17457d" stroke-width="6"/>
 <line x1="70" y1="480" x2="830" y2="480" stroke="#17457d" stroke-width="10" stroke-linecap="round"/>
 <g fill="#17457d"><circle cx="110" cy="480" r="14"/><circle cx="300" cy="480" r="14"/><circle cx="490" cy="480" r="14"/><circle cx="680" cy="480" r="14"/><circle cx="800" cy="480" r="14"/></g>
 <g stroke="#e8681a" stroke-width="8" fill="none" stroke-linejoin="round"><path d="M260 352 L274 384 L260 410 L278 436"/><path d="M520 352 L506 380 L524 402"/><path d="M710 352 L726 386 L714 416"/></g>
 <text x="30" y="595" font-size="32" font-weight="600" fill="#17457d">Coupe d'une dalle en béton armé</text>
</svg>''',
f'''<div class="lab">LE MÉCANISME</div><h1>Le béton ne sèche pas,<br>il <em>durcit avec l'eau</em></h1>
<svg class="ill" style="top:438px;left:216px" width="648" height="345" viewBox="0 0 900 480">
 <g font-size="36" font-weight="700" fill="#17457d" text-anchor="middle">
  <rect x="10" y="90" width="230" height="230" fill="#f4f6f9" stroke="#17457d" stroke-width="5"/>
  <g fill="#8d97a3"><circle cx="70" cy="160" r="17"/><circle cx="125" cy="205" r="21"/><circle cx="180" cy="150" r="15"/><circle cx="90" cy="260" r="19"/><circle cx="185" cy="250" r="17"/></g>
  <text x="125" y="380">Ciment</text>
  <text x="290" y="225" font-size="76" fill="#e8681a">+</text>
  <rect x="340" y="90" width="230" height="230" fill="#f4f6f9" stroke="#17457d" stroke-width="5"/>
  <use href="#drop" x="410" y="195"/><use href="#drop" x="500" y="170"/><use href="#drop" x="465" y="270"/>
  <text x="455" y="380">Eau</text>
  <line x1="595" y1="205" x2="665" y2="205" stroke="#e8681a" stroke-width="9" marker-end="url(#ar)"/>
  <rect x="690" y="90" width="210" height="230" fill="url(#conc)" stroke="#17457d" stroke-width="5"/>
  <text x="795" y="380">Béton dur</text>
 </g>
</svg>
<div class="box" style="top:844px"><b>L'hydratation :</b> le ciment réagit avec l'eau et forme des cristaux qui collent le sable et le gravier. La réaction dure des jours. <b>Sans eau, elle s'arrête.</b></div>''',
f'''<div class="lab p">LE RISQUE</div><h1>L'eau s'évapore<br><em>trop vite</em></h1>
<div class="box" style="top:368px;font-size:30px"><b>Soleil + vent sec :</b> la surface perd son eau avant que le ciment ait fini de réagir.</div>
<svg class="ill" style="top:592px;left:216px" width="648" height="374" viewBox="0 0 900 520">
 <use href="#sun" x="110" y="100"/>
 <g stroke="#2f78c4" stroke-width="5" stroke-dasharray="12 9" fill="none"><path d="M330 230 C320 190 345 160 330 120"/><path d="M500 230 C490 190 515 160 500 120"/><path d="M670 230 C660 190 685 160 670 120"/></g>
 <rect x="20" y="250" width="860" height="210" fill="url(#conc)" stroke="#17457d" stroke-width="6"/>
 <rect x="20" y="250" width="860" height="50" fill="#e8681a" opacity=".35"/>
 <g stroke="#e8681a" stroke-width="8" fill="none" stroke-linejoin="round"><path d="M150 252 L168 290 L150 322 L172 352"/><path d="M380 252 L362 292 L384 322"/><path d="M560 252 L578 284 L560 318 L585 340"/><path d="M760 252 L742 288 L762 312"/></g>
 <text x="880" y="505" font-size="30" font-weight="600" fill="#17457d" text-anchor="end">En orange : la surface asséchée</text>
</svg>
<div class="box o" style="top:997px;font-size:30px"><b>Résultat :</b> fissures de retrait en surface et béton moins résistant, définitivement.</div>''',
f'''<div class="lab">LA SOLUTION</div><h1>Garder le béton<br><em>humide 7&nbsp;jours</em></h1>
<svg class="ill" style="top:382px;left:216px" width="648" height="165" viewBox="0 0 900 230">
 <line x1="40" y1="150" x2="860" y2="150" stroke="#17457d" stroke-width="6"/>
 <g font-size="32" font-weight="700" fill="#17457d" text-anchor="middle">
 ''' + "".join(f'<circle cx="{60+130*k}" cy="150" r="16" fill="{"#e8681a" if k==6 else "#17457d"}"/><use href="#drop" x="{60+130*k}" y="80"/><text x="{60+130*k}" y="212" fill="{"#e8681a" if k==6 else "#17457d"}">J{k+1}</text>' for k in range(7)) + '''
 </g></svg>
<div class="stack" style="top:606px">
 <div class="box"><b>1. Arroser</b> la dalle et les poteaux matin et soir, sans laisser la surface blanchir.</div>
 <div class="box"><b>2. Couvrir</b> avec une bâche, des sacs vides mouillés ou du sable humide.</div>
 <div class="box o"><b>3. Couler aux heures fraîches :</b> tôt le matin ou en fin d'après-midi, jamais en plein midi.</div>
</div>''',
f'''<div class="lab">À RETENIR</div><h1>La solidité se joue<br><em>après</em> le coulage</h1>
<svg class="ill" style="top:424px;left:216px" width="648" height="403" viewBox="0 0 900 560">
 <g stroke="#17457d" stroke-width="7" fill="none" stroke-linecap="round">
  <line x1="450" y1="80" x2="450" y2="450"/><path d="M350 500 L550 500 L520 450 L380 450Z" fill="#f4f6f9"/>
  <line x1="150" y1="120" x2="750" y2="120"/><circle cx="450" cy="120" r="22" fill="#f4f6f9"/>
  <path d="M150 120 L90 320 M150 120 L210 320 M750 120 L690 320 M750 120 L810 320" stroke-width="4"/>
  <path d="M70 320 Q150 370 230 320Z" fill="#f4f6f9"/><path d="M670 320 Q750 370 830 320Z" fill="#f4f6f9"/>
 </g>
 <use href="#drop" x="150" y="275"/>
 <g transform="translate(750 262) scale(.55)"><use href="#sun"/></g>
 <text x="150" y="420" font-size="38" font-weight="700" fill="#2f78c4" text-anchor="middle">Eau</text>
 <text x="750" y="420" font-size="38" font-weight="700" fill="#e8681a" text-anchor="middle">Chaleur</text>
</svg>
<div class="box" style="top:865px;text-align:center;font-size:33px">Sous notre climat, <b>7 jours d'arrosage</b> valent mieux que des sacs de ciment en plus.</div>
<div class="box o" style="top:1061px;left:180px;right:180px;text-align:center;font-size:30px;padding:20px"><b>Partage à ton maçon</b></div>''']

# ---------- B : FERS ROUILLES ----------
col=lambda x,y,cov,rust=False: f'''<g transform="translate({x},{y})"><rect width="380" height="380" fill="url(#conc)" stroke="#17457d" stroke-width="6"/>
<rect x="{cov}" y="{cov}" width="{380-2*cov}" height="{380-2*cov}" rx="14" fill="none" stroke="#17457d" stroke-width="8"/>
''' + "".join(f'<circle cx="{cx}" cy="{cy}" r="20" fill="{"#c0561a" if rust else "#17457d"}"/>' for cx,cy in [(cov+24,cov+24),(380-cov-24,cov+24),(cov+24,380-cov-24),(380-cov-24,380-cov-24)]) + '</g>'
SERIES["fers"]=[
f'''<div class="lab p">PROBLÈME</div><h1>Le béton <em>éclate</em><br>et les fers<br>apparaissent ?</h1>
<svg class="ill" style="top:522px;left:216px" width="648" height="504" viewBox="0 0 900 700">
 <rect x="300" y="0" width="300" height="680" fill="url(#conc)" stroke="#17457d" stroke-width="6"/>
 <path d="M300 250 L360 230 L390 280 L370 360 L395 430 L340 470 L300 450Z" fill="#e9ebee" stroke="#17457d" stroke-width="5"/>
 <line x1="335" y1="200" x2="335" y2="500" stroke="#c0561a" stroke-width="22" stroke-linecap="round"/>
 <g fill="#8a3d10" opacity=".7"><circle cx="330" cy="290" r="6"/><circle cx="340" cy="360" r="7"/><circle cx="332" cy="420" r="5"/></g>
 <g stroke="#e8681a" stroke-width="7" fill="none"><path d="M395 280 L440 300 L470 290"/><path d="M395 430 L450 440 L480 470"/></g>
 
 <text x="710" y="240" font-size="34" font-weight="700" fill="#e8681a">Fer rouillé</text>
 <line x1="400" y1="350" x2="700" y2="250" stroke="#17457d" stroke-width="3"/>
 <line x1="380" y1="455" x2="700" y2="520" stroke="#17457d" stroke-width="3"/>
 <text x="710" y="530" font-size="34" font-weight="700" fill="#17457d">Béton éclaté</text>
 <text x="450" y="720" font-size="1" fill="none">.</text>
</svg>''',
f'''<div class="lab p">LA CAUSE</div><h1>Les fers sont <em>trop<br>près</em> de la surface</h1>
<svg class="ill" style="top:438px;left:216px" width="648" height="403" viewBox="0 0 900 560">
 {col(40,40,22,True)}
 {col(480,40,70)}
 <g font-size="34" font-weight="700" text-anchor="middle"><text x="230" y="490" fill="#e8681a">Enrobage trop faible</text><text x="670" y="490" fill="#17457d">Enrobage correct</text></g>
 <line x1="40" y1="455" x2="62" y2="455" stroke="#e8681a" stroke-width="4"/>
 <line x1="480" y1="440" x2="550" y2="440" stroke="#17457d" stroke-width="4" marker-start="url(#arn)" marker-end="url(#arn)"/>
</svg>
<div class="box" style="top:893px"><b>L'enrobage</b>, c'est l'épaisseur de béton entre le fer et l'extérieur. C'est elle qui <b>protège l'acier</b> de l'air et de l'humidité.</div>''',
f'''<div class="lab">LE MÉCANISME</div><h1>La rouille <em>gonfle</em><br>et pousse le béton</h1>
<svg class="ill" style="top:424px;left:216px" width="648" height="403" viewBox="0 0 900 560">
 <g font-size="32" font-weight="700" text-anchor="middle" fill="#17457d">
  <rect x="20" y="80" width="240" height="240" fill="url(#conc)" stroke="#17457d" stroke-width="5"/><circle cx="140" cy="140" r="26" fill="#17457d"/><text x="140" y="380">1. Acier sain</text>
  <line x1="275" y1="200" x2="320" y2="200" stroke="#e8681a" stroke-width="8" marker-end="url(#ar)"/>
  <rect x="330" y="80" width="240" height="240" fill="url(#conc)" stroke="#17457d" stroke-width="5"/><circle cx="450" cy="140" r="38" fill="#c0561a"/><path d="M420 100 L405 82 M480 100 L495 82" stroke="#e8681a" stroke-width="6"/><text x="450" y="380">2. La rouille gonfle</text>
  <line x1="585" y1="200" x2="630" y2="200" stroke="#e8681a" stroke-width="8" marker-end="url(#ar)"/>
  <rect x="640" y="80" width="240" height="240" fill="url(#conc)" stroke="#17457d" stroke-width="5"/><path d="M640 80 L740 80 L720 130 L760 190 L700 210 L640 180Z" fill="#e9ebee" stroke="#17457d" stroke-width="4"/><circle cx="760" cy="140" r="38" fill="#c0561a"/><text x="760" y="380">3. Le béton éclate</text>
 </g>
</svg>
<div class="box o" style="top:816px"><b>Résultat :</b> le fer perd de sa section, la structure s'affaiblit et la réparation coûte bien plus cher que les quelques centimètres de béton économisés.</div>''',
f'''<div class="lab">LA SOLUTION</div><h1>Respecter l'enrobage<br>avec des <em>cales</em></h1>
<svg class="ill" style="top:403px;left:216px" width="648" height="273" viewBox="0 0 900 380">
 <rect x="40" y="40" width="820" height="230" fill="url(#conc)" stroke="#17457d" stroke-width="6"/>
 <line x1="80" y1="190" x2="820" y2="190" stroke="#17457d" stroke-width="16" stroke-linecap="round"/>
 <g fill="#e8681a">''' + "".join(f'<path d="M{x} 270 L{x+40} 270 L{x+30} 205 L{x+10} 205Z"/>' for x in (130,420,710)) + '''</g>
 <line x1="860" y1="198" x2="860" y2="270" stroke="#17457d" stroke-width="4"/>
 <text x="450" y="340" font-size="32" font-weight="700" fill="#e8681a" text-anchor="middle">Cales en béton sous les fers</text>
</svg>
<div class="stack" style="top:718px">
 <div class="box"><b>Poteaux et poutres :</b> en pratique, au moins 2,5 à 3 cm de béton autour des fers.</div>
 <div class="box"><b>Fondations contre la terre :</b> au moins 5 cm, avec un béton de propreté dessous.</div>
 <div class="box o"><b>Jamais de cailloux ou de morceaux de bois</b> comme cales : utilise des cales en béton ou en plastique.</div>
</div>''',
f'''<div class="lab">À RETENIR</div><h1>Quelques centimètres<br>qui sauvent <em>ta maison</em></h1>
<svg class="ill" style="top:438px;left:216px" width="648" height="403" viewBox="0 0 900 560">
 <path d="M450 40 L760 130 L760 300 C760 420 620 500 450 540 C280 500 140 420 140 300 L140 130Z" fill="url(#conc)" stroke="#17457d" stroke-width="8"/>
 <rect x="330" y="200" width="240" height="200" rx="12" fill="none" stroke="#17457d" stroke-width="10"/>
 <g fill="#17457d"><circle cx="355" cy="225" r="18"/><circle cx="545" cy="225" r="18"/><circle cx="355" cy="375" r="18"/><circle cx="545" cy="375" r="18"/></g>
</svg>
<div class="box" style="top:872px;text-align:center;font-size:33px">L'enrobage, c'est le <b>bouclier</b> de tes fers.<br>Vérifie les cales <b>avant</b> chaque coulage.</div>
<div class="box o" style="top:1068px;left:180px;right:180px;text-align:center;font-size:30px;padding:20px"><b>Enregistre ce post</b></div>''']

# ---------- C : HUMIDITE ----------
wall='''<rect x="250" y="40" width="300" height="520" fill="url(#block)" stroke="#17457d" stroke-width="5"/>
 <rect x="200" y="560" width="400" height="140" fill="url(#conc)" stroke="#17457d" stroke-width="5"/>
 <rect x="0" y="560" width="900" height="200" fill="url(#soil)" opacity=".9"/>
 <rect x="200" y="560" width="400" height="140" fill="url(#conc)" stroke="#17457d" stroke-width="5"/>'''
SERIES["humidite"]=[
f'''<div class="lab p">PROBLÈME</div><h1>Le bas de tes murs<br><em>noircit</em> et l'enduit<br>se décolle ?</h1>
<svg class="ill" style="top:564px;left:216px" width="648" height="460" viewBox="0 0 900 640">
 <rect x="60" y="20" width="780" height="520" fill="#efe9dd" stroke="#17457d" stroke-width="6"/>
 <path d="M60 330 C160 300 220 350 320 315 C420 280 480 345 580 310 C680 280 760 335 840 305 L840 540 L60 540Z" fill="#8f8a7c" opacity=".55"/>
 <path d="M220 420 L300 400 L330 440 L280 470 L230 460Z" fill="#cfc6b4" stroke="#17457d" stroke-width="3"/>
 <path d="M560 440 L640 425 L660 470 L590 490Z" fill="#cfc6b4" stroke="#17457d" stroke-width="3"/>
 <g fill="#fff" opacity=".8"><circle cx="420" cy="470" r="5"/><circle cx="440" cy="485" r="4"/><circle cx="700" cy="500" r="5"/><circle cx="150" cy="480" r="4"/></g>
 <rect x="0" y="540" width="900" height="100" fill="url(#soil)"/>
 
</svg>''',
f'''<div class="lab p">LA CAUSE</div><h1>L'eau du sol <em>monte</em><br>dans les murs</h1>
<svg class="ill" style="top:410px;left:216px" width="648" height="561" viewBox="0 0 900 780">
 {wall}
 <path d="M250 560 L250 340 C320 320 380 360 550 330 L550 560Z" fill="#2f78c4" opacity=".28"/>
 <g stroke="#2f78c4" stroke-width="7" marker-end="url(#arb)"><line x1="300" y1="740" x2="300" y2="420"/><line x1="400" y1="740" x2="400" y2="390"/><line x1="500" y1="740" x2="500" y2="420"/></g>
 <text x="600" y="420" font-size="34" font-weight="700" fill="#2f78c4">Zone humide</text>
 <text x="620" y="650" font-size="32" font-weight="700" fill="#17457d">Sol humide</text>
</svg>
<div class="box" style="top:997px;font-size:30px"><b>Les remontées capillaires :</b> les parpaings et le mortier aspirent l'eau du sol comme une éponge.</div>''',
f'''<div class="lab">POURQUOI ÇA ARRIVE</div><h1>Trois erreurs<br><em>à la construction</em></h1>
<div class="stack" style="top:424px">
 <div class="box o"><b>1. Pas de barrière étanche</b> entre la fondation et le premier rang de parpaings.</div>
 <div class="box o"><b>2. L'eau de pluie reste au pied du mur :</b> pas de pente ni de trottoir autour de la maison.</div>
 <div class="box o"><b>3. Les descentes d'eau du toit</b> se vident juste contre les murs.</div>
</div>''',
f'''<div class="lab">LA SOLUTION</div><h1>Couper la route<br><em>de l'eau</em></h1>
<svg class="ill" style="top:382px;left:216px" width="648" height="561" viewBox="0 0 900 780">
 {wall}
 <rect x="250" y="548" width="300" height="16" fill="#e8681a"/>
 <polygon points="550,560 860,600 860,620 550,580" fill="#9aa3ae" stroke="#17457d" stroke-width="4"/>
 <g stroke="#2f78c4" stroke-width="7" marker-end="url(#arb)"><line x1="300" y1="740" x2="300" y2="600"/><line x1="500" y1="740" x2="500" y2="600"/></g>
 <line x1="560" y1="555" x2="640" y2="470" stroke="#e8681a" stroke-width="3"/><text x="650" y="465" font-size="32" font-weight="700" fill="#e8681a">Arase étanche</text>
 <line x1="760" y1="598" x2="760" y2="680" stroke="#17457d" stroke-width="3"/><text x="620" y="715" font-size="30" font-weight="700" fill="#17457d">Trottoir en pente</text>
</svg>
<div class="stack" style="top:956px">
 <div class="box" style="font-size:28px;padding:22px 30px"><b>Arase étanche</b> (mortier hydrofuge ou film) sur la fondation, avant les murs.</div>
 <div class="box" style="font-size:28px;padding:22px 30px"><b>Trottoir en pente</b> et descentes d'eau loin des murs.</div>
</div>''',
f'''<div class="lab">À RETENIR</div><h1>Ça se prévoit<br><em>sur le plan</em></h1>
<div class="box" style="top:424px;font-size:33px">Une maison sans arase étanche peut garder ce problème <b>toute sa vie</b>. Le traiter après coup est bien plus compliqué et plus cher.</div>
<div class="box o" style="top:690px;font-size:33px">Sur mes plans, la coupe montre l'arase, le soubassement et le trottoir. Le maçon sait <b>exactement</b> quoi faire.</div>
<div class="box" style="top:970px;left:150px;right:150px;text-align:center;font-size:31px;padding:22px"><b>Ton projet ? Écris-moi en privé</b></div>''']

def html_for(name):
    sl=SERIES[name]; n=len(sl)
    return "<!DOCTYPE html><html><head><meta charset='utf-8'><style>"+CSS+"</style></head><body>"+DEFS+"".join(slide(i+1,n,b,swipe=(i==0)) for i,b in enumerate(sl))+"</body></html>"

async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path="/usr/bin/google-chrome",args=["--no-sandbox"])
        pg=await b.new_page(viewport={"width":1080,"height":1350})
        for name in SERIES:
            d=f"{OUT}/{name}"; os.makedirs(d,exist_ok=True)
            open(f"{d}/s.html","w").write(html_for(name))
            await pg.goto(f"file://{d}/s.html"); await pg.wait_for_timeout(600)
            for i,e in enumerate(await pg.query_selector_all(".s"),1):
                await e.screenshot(path=f"{d}/{name}_{i}.jpg",type="jpeg",quality=92)
        await b.close()
asyncio.run(main())
