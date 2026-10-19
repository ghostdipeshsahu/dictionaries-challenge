/* Dictionaries: The Python Challenge · game UI
   The server owns answers, XP, unlocking, badges, every clock and the proctoring limits (/api/dicts/*).
   This file renders the journey, shows the countdowns, collects answers, reports integrity events,
   and runs learner code in a sandboxed Pyodide worker (never on the server). */
(()=>{
const reduce=matchMedia('(prefers-reduced-motion: reduce)').matches;
const $=(s,r=document)=>r.querySelector(s),$$=(s,r=document)=>[...r.querySelectorAll(s)];
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const view=$('#view'),drawer=$('#drawer'),modal=$('#modal');

const ICON={
  star:'<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="m12 2.5 2.9 6 6.6.8-4.9 4.6 1.3 6.6L12 17.3l-5.9 3.2 1.3-6.6L2.5 9.3l6.6-.8z"/></svg>',
  lock:'<svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" aria-hidden="true"><rect x="5" y="11" width="14" height="10" rx="2.5" fill="currentColor" stroke="none"/><path d="M8 11V8a4 4 0 0 1 8 0v3"/></svg>',
  check:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m5 12.5 4.5 4.5L19 7.5"/></svg>',
  x:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" aria-hidden="true"><path d="M6 6l12 12M18 6 6 18"/></svg>',
  play:'<svg class="i" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M7 4.5v15l13-7.5z"/></svg>',
  back:'<svg class="i" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" aria-hidden="true"><path d="M15 5l-7 7 7 7"/></svg>',
  up:'<svg class="i" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" aria-hidden="true"><path d="M6 15l6-6 6 6"/></svg>',
  down:'<svg class="i" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" aria-hidden="true"><path d="M6 9l6 6 6-6"/></svg>',
  bulb:'<svg class="i" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 2a7 7 0 0 0-4 12.7V17a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1v-2.3A7 7 0 0 0 12 2zm-3 18h6v1a1 1 0 0 1-1 1h-4a1 1 0 0 1-1-1z"/></svg>',
  clock:'<svg class="i" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" aria-hidden="true"><circle cx="12" cy="13" r="8"/><path d="M12 9v4l2.5 2.5M9 2h6"/></svg>',
  shield:'<svg class="i" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 2 4 5v6c0 5 3.4 9.4 8 11 4.6-1.6 8-6 8-11V5zm-1.2 13.6-3.5-3.5 1.4-1.4 2.1 2.1 4.6-4.6 1.4 1.4z"/></svg>',
  eye:'<svg class="i" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" aria-hidden="true"><path d="M2 12s3.6-7 10-7 10 7 10 7-3.6 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/></svg>',
  board:'<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linejoin="round" aria-hidden="true"><path d="M2.5 7.5h9l3 4.5-3 4.5h-9z"/><circle cx="6" cy="12" r="1.2" fill="currentColor" stroke="none"/><rect x="16.5" y="7.5" width="5" height="9" rx="1.5" fill="currentColor" stroke="none"/></svg>',
  trophy:'<svg viewBox="0 0 24 24" width="26" height="26" fill="currentColor" aria-hidden="true"><path d="M7 3h10v2h3v3a4 4 0 0 1-4 4h-.3A5 5 0 0 1 13 14.9V18h3v3H8v-3h3v-3.1A5 5 0 0 1 8.3 12H8a4 4 0 0 1-4-4V5h3zm-1 4v1a2 2 0 0 0 1 1.7V7zm11 0v2.7A2 2 0 0 0 18 8V7z"/></svg>'
};
const BADGE_ICON={
  'board-explorer':'<path d="M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20zm3.5 6.5-2 5-5 2 2-5z"/>',
  'duplicate-detective':'<path d="M8 3h10a2 2 0 0 1 2 2v10h-2V5H8zM4 7h10a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V9a2 2 0 0 1 2-2zm1.6 4.2 1.4-1.4 2 2 2-2 1.4 1.4-2 2 2 2-1.4 1.4-2-2-2 2-1.4-1.4 2-2z"/>',
  'key-keeper':'<path d="M7.5 6.5a5.5 5.5 0 0 1 5.2 3.7H22v3.6h-2V17h-3.4v-3.2h-3.9A5.5 5.5 0 1 1 7.5 6.5zm0 3.4a2.1 2.1 0 1 0 0 4.2 2.1 2.1 0 0 0 0-4.2z"/>',
  'logic-detective':'<path d="M10 3a7 7 0 0 1 5.6 11.2l5.1 5.1-1.4 1.4-5.1-5.1A7 7 0 1 1 10 3zm0 2a5 5 0 1 0 0 10 5 5 0 0 0 0-10z"/>',
  'bug-hunter':'<path d="M9 4l1.4 1.4A4 4 0 0 1 12 5a4 4 0 0 1 1.6.4L15 4l1.4 1.4-1.2 1.2A4 4 0 0 1 16 9h3v2h-3v2h3v2h-3.3A4 4 0 0 1 8.3 15H5v-2h3v-2H5V9h3a4 4 0 0 1 .8-2.4L7.6 5.4z"/>',
  'python-dicts-champion':'<path d="M7 3h10v2h3v3a4 4 0 0 1-4 4h-.3A5 5 0 0 1 13 14.9V18h3v3H8v-3h3v-3.1A5 5 0 0 1 8.3 12H8a4 4 0 0 1-4-4V5h3z"/>',
  'combo-5':'<path d="M12 2c1 4 6 6 6 12a6 6 0 0 1-12 0c0-3 2-5 3-6 0 2 1 3 2 3 0-4-1-6 1-9z"/>',
  'clean-sweep':'<path d="m12 2.5 2.9 6 6.6.8-4.9 4.6 1.3 6.6L12 17.3l-5.9 3.2 1.3-6.6L2.5 9.3l6.6-.8z"/>',
  'sheet-explorer':'<path d="M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20zm3.5 6.5-2 5-5 2 2-5z"/>',
  'copy-maker':'<path d="M8 3h10a2 2 0 0 1 2 2v10h-2V5H8zM4 7h10a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V9a2 2 0 0 1 2-2z"/>',
  'star-packer':'<path d="M4 6h3l-2 12H2zm5 0h12v3H9zm0 5h12v3H9zm0 5h12v3H9z"/>',
  'key-matcher':'<path d="M7.5 6.5a5.5 5.5 0 0 1 5.2 3.7H22v3.6h-2V17h-3.4v-3.2h-3.9A5.5 5.5 0 1 1 7.5 6.5zm0 3.4a2.1 2.1 0 1 0 0 4.2 2.1 2.1 0 0 0 0-4.2z"/>',
  'trip-champion':'<path d="M7 3h10v2h3v3a4 4 0 0 1-4 4h-.3A5 5 0 0 1 13 14.9V18h3v3H8v-3h3v-3.1A5 5 0 0 1 8.3 12H8a4 4 0 0 1-4-4V5h3z"/>',
  'landing-pro':'<path d="M3 4h7v7H3zm11 0h7v7h-7zM3 15h18v5H3zm4.5-4.5 2 3h-4zm11 0 2 3h-4z"/>',
  'board-pro':'<path d="M2 6.5h10.5L16.5 12l-4 5.5H2zm4 4a1.5 1.5 0 1 0 0 3 1.5 1.5 0 0 0 0-3zM18 6.5h4v11h-4z"/>'
};
let CONCEPTS={pairs:'Key-value pairs',creation:'Creating a dictionary',empty:'Empty {} and dict()',unique_keys:'Unique keys',access:'menu[key] takes a key',
  keyerror_get:'KeyError vs get()',membership:'in checks keys',add_change:'Add or change a key',case:'Keys are case-sensitive',delete_len:'del and len()',
  views_methods:'keys(), values(), items()',looping:'Looping over a dictionary',live_views:'Live views vs list() copies',dict_from_pairs:'dict() from pairs',
  hashable_keys:'Keys must be immutable',compare_types:'Dict vs list, tuple, set'};
let TYPE_LABEL={mcq:'Multiple choice',msq:'Multiple select',tf:'True or false',ar:'Assertion and reasoning',fill:'Fill in the blanks',match:'Match the columns',
  order:'Put in order',categorize:'Sort into groups',numeric:'Numeric answer',predict:'Predict the output',debug:'Debug mission',coding:'Coding challenge',board:'Board build'};
const PRAISE={predict:['You read it like Python.','Python agrees.','Exactly what Python prints.'],debug:['Bug squashed.','Sharp debugging.'],coding:['All tests green.','Shipped it.'],
  board:['Board perfect.','Built to spec.'],land:['Every argument in its place.','Landed it.'],_:['Correct.','Spot on.','Nailed it.']};
const pick=a=>a[Math.floor(Math.random()*a.length)];
/* Instructional guidance: the same three-step "how to answer" for each kind of question, shown on the question
   (Your task), on the first-time coach card, and as the "what to do next" line under Check. */
const HOWTO={
  mcq:{steps:['Read the question and any code.','Tap the <b>one</b> answer you think is right.','Press <b>Check</b>.'],wait:'Tap an answer to turn on Check.'},
  predict:{steps:['Read the code line by line, like Python does.','Tap what it prints. A red line means Python stops with an error.','Press <b>Check</b>.'],wait:'Tap what the code prints to turn on Check.'},
  ar:{steps:['Read the Assertion (A) and the Reason (R).','Decide: is each one true? Does R explain A?','Tap one option, then press <b>Check</b>.'],wait:'Tap an option to turn on Check.'},
  msq:{steps:['More than one answer is right.','Tap <b>every</b> correct option. Tap again to unselect.','Press <b>Check</b>.'],wait:'Tap every correct option to turn on Check.'},
  tf:{steps:['Read the statement.','Tap <b>True</b> or <b>False</b>.','Press <b>Check</b>.'],wait:'Tap True or False to turn on Check.'},
  numeric:{steps:['Trace the code and work out the number.','Type the number in the box.','Press <b>Check</b> or Enter.'],wait:'Type a number to turn on Check.'},
  fill:{steps:['Find the highlighted gaps in the code.','Type the missing code into each gap.','Press <b>Check</b>.'],wait:'Fill every gap to turn on Check.'},
  match:{steps:['Tap an item on the left.','Tap its partner on the right. A pair gets the same number.','Match every item, then press <b>Check</b>.'],wait:'Match every item to turn on Check.'},
  order:{steps:['The lines of a program are mixed up.','Move lines with the <b>▲ ▼</b> arrows.','When the program is in order, press <b>Check</b>.'],wait:'Put the lines in order, then press Check.'},
  categorize:{steps:['Read each item.','Tap the group it belongs to.','Sort every item, then press <b>Check</b>.'],wait:'Choose a group for every item to turn on Check.'},
  debug:{steps:['Find the line that goes wrong and <b>tap it in the code</b>.','Choose what goes wrong.','Press <b>Check</b>.'],wait:'Tap a line and choose what goes wrong.'},
  board:{steps:['Read the goal in the yellow box.','Type a key and a value, then press a Python button: add/change or delete.','When the board matches the goal, press <b>Check</b>.'],wait:'Change the board to turn on Check.'},
  land:{steps:['Tap an argument from the call.','Tap the box it lands in, or <b>No box</b> if Python stops.','Place every argument, then press <b>Check</b>.'],wait:'Place every argument to turn on Check.'},
  coding:{steps:['Read the task and the sample tests.','Write your code in the editor.','Press <b>Run samples</b> to test it, then <b>Submit all tests</b>.'],wait:''},
};
const howtoHTML=t=>`<details class="howto"><summary>${ICON.bulb}Your task</summary><ol>${(HOWTO[t]||HOWTO.mcq).steps.map(x=>`<li>${x}</li>`).join('')}</ol></details>`;
/* What a learner has already been shown, per mission and roll number (stored in this browser only). */
const seenKey=k=>API.key(`${(M&&M.ui&&M.ui.id)||'x'}-${(API.user&&API.user.roll_no)||'anon'}-${k}`);
function seen(k){try{return JSON.parse(localStorage.getItem(seenKey(k))||'false')}catch(e){return false}}
function markSeen(k,v){try{localStorage.setItem(seenKey(k),JSON.stringify(v===undefined?true:v))}catch(e){}}
const mins=sec=>{const s=Math.max(0,Math.ceil(sec));return Math.floor(s/60)+':'+String(s%60).padStart(2,'0')};

/* ---------- state ---------- */
let M=null,ST=null,QM={},LVM={},R=null,Q=null,shownXP=0;
const lvIndex=id=>M.levels.findIndex(l=>l.id===id);
const lvState=id=>ST.levels.find(l=>l.id===id);
const qs=id=>ST.questions[id]||{};
const cleared=id=>!!(qs(id).solved||qs(id).revealed||qs(id).timed_out);
const live=()=>!!(ST&&ST.started_at&&!ST.ended_at);
let soundOn=true;try{soundOn=localStorage.getItem('dicts-sound')!=='0'}catch(e){}

/* ---------- sound (short, quiet, optional) ---------- */
let actx=null;
function ac(){if(!actx){try{actx=new (window.AudioContext||window.webkitAudioContext)()}catch(e){}}if(actx&&actx.state==='suspended')actx.resume();return actx}
function tone(f,t,d,type,v){if(!soundOn)return;const c=ac();if(!c)return;try{const o=c.createOscillator(),g=c.createGain(),t0=c.currentTime+t;o.type=type||'sine';o.frequency.setValueAtTime(f,t0);g.gain.setValueAtTime(0,t0);g.gain.linearRampToValueAtTime(v||.08,t0+.012);g.gain.exponentialRampToValueAtTime(.0001,t0+d);o.connect(g).connect(c.destination);o.start(t0);o.stop(t0+d+.05)}catch(e){}}
const sfx={tap(){tone(720,0,.05,'triangle',.035)},good(s){const b=523.25*Math.pow(2,Math.min(s,12)/12);[0,4,7,12].forEach((x,i)=>tone(b*Math.pow(2,x/12),i*.05,.26,'triangle',.08))},
  bad(){tone(220,0,.18,'sine',.09);tone(170,.09,.26,'sine',.07)},combo(){[0,7,12,19].forEach((x,i)=>tone(659*Math.pow(2,x/12),i*.05,.22,'square',.03))},
  win(){[0,4,7,12,16,19,24].forEach((x,i)=>tone(392*Math.pow(2,x/12),i*.08,.45,'triangle',.07))},pass(){tone(880,0,.1,'triangle',.05)},fail(){tone(260,0,.15,'sawtooth',.03)},
  warn(){tone(440,0,.12,'square',.04);tone(440,.18,.12,'square',.04)}};
const soundBtn=$('#soundBtn');
function paintSound(){soundBtn.setAttribute('aria-pressed',soundOn);soundBtn.setAttribute('aria-label',soundOn?'Sound on':'Sound off');$('#waves').style.opacity=soundOn?1:.15}
soundBtn.onclick=()=>{soundOn=!soundOn;try{localStorage.setItem('dicts-sound',soundOn?'1':'0')}catch(e){}paintSound();if(soundOn){ac();sfx.tap()}};
paintSound();

/* ---------- confetti: rare moments only (stage clear, badge, boss) ---------- */
const fxc=$('#fx'),fx=fxc.getContext('2d');let parts=[],fxRun=false,FW=0,FH=0;
function fxSize(){const d=Math.min(2,devicePixelRatio||1);FW=innerWidth;FH=innerHeight;fxc.width=FW*d;fxc.height=FH*d;fx.setTransform(d,0,0,d,0,0)}
fxSize();addEventListener('resize',fxSize);
function palette(){const cs=getComputedStyle(document.documentElement);return ['--gold','--cyan','--blue','--good'].map(v=>cs.getPropertyValue(v).trim()).concat(['#FF7A1A'])}
function burst(x,y,n,power){if(reduce)return;const P=palette();power=power||1;
  for(let i=0;i<n;i++){const a=-Math.PI/2+(Math.random()-.5)*2.2,v=(4+Math.random()*7)*power;parts.push({x,y,vx:Math.cos(a)*v,vy:Math.sin(a)*v,g:.28,s:4+Math.random()*5,r:Math.random()*6,vr:(Math.random()-.5)*.4,c:P[i%P.length],sh:i%3,life:1,dec:.012+Math.random()*.01})}
  if(!fxRun){fxRun=true;requestAnimationFrame(fxLoop)}}
function rain(n){if(reduce)return;const P=palette();for(let i=0;i<n;i++)parts.push({x:Math.random()*FW,y:-20-Math.random()*FH*.4,vx:(Math.random()-.5)*2,vy:2+Math.random()*4,g:.06,s:5+Math.random()*6,r:Math.random()*6,vr:(Math.random()-.5)*.3,c:P[i%P.length],sh:i%3,life:1,dec:.004});if(!fxRun){fxRun=true;requestAnimationFrame(fxLoop)}}
function fxLoop(){fx.clearRect(0,0,FW,FH);
  for(const p of parts){p.vy+=p.g;p.vx*=.99;p.x+=p.vx;p.y+=p.vy;p.r+=p.vr;p.life-=p.dec;fx.save();fx.globalAlpha=Math.max(0,Math.min(1,p.life*1.5));fx.translate(p.x,p.y);fx.rotate(p.r);fx.fillStyle=p.c;
    if(p.sh===0)fx.fillRect(-p.s/2,-p.s/4,p.s,p.s/2);else if(p.sh===1){fx.beginPath();fx.arc(0,0,p.s/2.6,0,6.283);fx.fill()}else{fx.beginPath();fx.moveTo(0,-p.s/2);fx.lineTo(p.s/2,p.s/2);fx.lineTo(-p.s/2,p.s/2);fx.fill()}fx.restore()}
  parts=parts.filter(p=>p.life>0&&p.y<FH+40);if(parts.length)requestAnimationFrame(fxLoop);else{fxRun=false;fx.clearRect(0,0,FW,FH)}}
const centerOf=el=>{const r=el.getBoundingClientRect();return [r.left+r.width/2,r.top+r.height/2]};
// Toasts play one at a time; anything beyond a short backlog is dropped so celebrations never arrive late, on the wrong screen.
let toastQ=Promise.resolve(),toastBacklog=0;
function toast(text,cls){if(toastBacklog>=2&&cls!=='err')return;toastBacklog++;toastQ=toastQ.then(()=>new Promise(res=>{const t=document.createElement('div');t.className='toast '+(cls||'');t.textContent=text;t.setAttribute('role','status');document.body.appendChild(t);setTimeout(()=>{t.remove();toastBacklog--;res()},1500)}))}
function floatXP(from,amount){
  if(!from||!amount)return;const [x,y]=centerOf(from),[tx,ty]=centerOf($('#xpNum'));const f=document.createElement('div');f.className='float';f.textContent='+'+amount+' XP';
  f.style.left=x+'px';f.style.top=y+'px';document.body.appendChild(f);
  if(reduce){f.animate([{opacity:1},{opacity:0}],{duration:700}).onfinish=()=>f.remove();return}
  f.animate([{transform:'translate(-50%,-50%) scale(.8)',opacity:0},{transform:'translate(-50%,-110%) scale(1.1)',opacity:1,offset:.25},{transform:`translate(calc(-50% + ${tx-x}px),calc(-50% + ${ty-y}px)) scale(.5)`,opacity:.2}],{duration:850,easing:'cubic-bezier(.5,0,.3,1)'})
    .onfinish=()=>{f.remove();const s=$('.stat.xp');s.classList.remove('bump');void s.offsetWidth;s.classList.add('bump')};
}

/* ---------- HUD + the 45-minute mission countdown (server time) ---------- */
let missionEnd=null,overHandled=false;
function rollXP(){const el=$('#xpNum'),from=shownXP,to=ST.xp;shownXP=to;if(reduce||from===to){el.textContent=to;return}
  const t0=performance.now()+500;const step=n=>{const p=Math.min(1,Math.max(0,(n-t0)/500));el.textContent=Math.round(from+(to-from)*(1-Math.pow(1-p,3)));if(p<1)requestAnimationFrame(step)};requestAnimationFrame(step)}
function hud(){
  if(!ST)return;$('#xpNum').textContent=shownXP;$('#comboNum').textContent=ST.combo;$('#comboStat').classList.toggle('hot',ST.combo>=3);
  const p=ST.progress;$('#mprog').style.transform=`scaleX(${p.total?p.done/p.total:0})`;
  $('#clock').hidden=!ST.started_at;tickClock();
}
function tickClock(){
  if(!ST||!ST.started_at)return;
  const left=live()&&missionEnd?(missionEnd-Date.now())/1000:0;
  $('#clockNum').textContent=mins(left);
  $('#clock').classList.toggle('low',live()&&left<=300);
  $('#clock').setAttribute('aria-label',`Mission time left: ${mins(left)}`);
  if(live()&&missionEnd&&left<=0&&!overHandled)onMissionOver();
}
setInterval(tickClock,500);

/* ---------- python syntax highlight + code panel ---------- */
function hl(t,blank){
  const re=/(#.*$)|("(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*')|\b(for|in|if|else|elif|not|and|or|is|del|True|False|None)\b|\b(print|set|dict|len|input|type|map|int|str|list|tuple|range|sorted)\b(?=\s*\()|\.([a-z][a-z_]*)(?=\s*\()|\b(\d+(?:\.\d+)?)\b|(___)|([|&^\-=<>+*%]+)/g;
  let out='',last=0,m;
  while((m=re.exec(t))){
    out+=esc(t.slice(last,m.index));
    if(m[1])out+=`<span class="c">${esc(m[1])}</span>`;
    else if(m[2])out+=`<span class="s">${esc(m[2])}</span>`;
    else if(m[3])out+=`<span class="k">${m[3]}</span>`;
    else if(m[4])out+=`<span class="f">${m[4]}</span>`;
    else if(m[5])out+=`.<span class="f m">${m[5]}</span>`;
    else if(m[6])out+=`<span class="n">${m[6]}</span>`;
    else if(m[7])out+=blank?blank():'<span class="slot">&nbsp;?&nbsp;</span>';
    else out+=`<span class="o">${esc(m[8])}</span>`;
    last=re.lastIndex;
  }
  return out+esc(t.slice(last));
}
function linesHTML(code,o){
  o=o||{};let bk=0;const blank=o.blanks?()=>`<input class="blank" data-b="${bk}" aria-label="Blank ${++bk}" autocomplete="off" autocapitalize="off" spellcheck="false" size="9">`:null;
  return code.split('\n').map((raw,i)=>{const n=i+1,t=raw.trim(),ind=raw.match(/^ */)[0].length,tap=o.tap&&t;
    return `<li class="ln${tap?' tappable':''}" data-n="${n}"${tap?` role="button" tabindex="0" aria-pressed="false" aria-label="Line ${n}: ${esc(t)}"`:''}><span class="no">${n}</span><span class="src" style="--d:${Math.floor(ind/4)}">${' '.repeat(ind%4)}${hl(t,blank)}</span><span class="tagz"></span></li>`}).join('');
}
function codePanel(code,o){
  o=o||{};
  return `<div class="code"${o.mode?` data-mode="${o.mode}"`:''}><div class="code-bar"><span class="dots"><i></i><i></i><i></i></span><span>${esc(o.file||'main.py')}</span><span class="vars"></span>${o.run?'<button class="runbtn" type="button">'+ICON.play+'Run it</button>':''}</div>
    <ol class="lines">${linesHTML(code,o)}</ol>${o.run?'<div class="console" hidden><div class="con-head"><span>Output</span><span class="con-state"></span></div><pre class="con-out"></pre></div>':''}</div>`;
}
function tag(l,text,cls){if(l)$('.tagz',l).insertAdjacentHTML('beforeend',`<span class="tag ${cls}">${esc(text)}</span>`)}
function focusLine(panel,n,text){if(!panel||!n)return;const l=panel.querySelector(`.ln[data-n="${n}"]`);if(!l)return;l.classList.add('ran');tag(l,text||'key line','gold')}
function consoleHTML(r){return esc(r.stdout||'')+(r.error?`${r.stdout?'\n':''}<span class="con-err">${esc(r.error.type)}${r.error.line?' on line '+r.error.line:''}: ${esc(r.error.msg)}</span>`:'')+(!r.stdout&&!r.error?'<span class="con-note">Nothing printed.</span>':'')}
function bindRun(panel,code){
  const b=panel&&$('.runbtn',panel);if(!b)return;
  b.onclick=async()=>{const con=$('.console',panel),out=$('.con-out',panel),stt=$('.con-state',panel);con.hidden=false;b.disabled=true;out.textContent='';
    stt.textContent=PYR.ready?'running':'loading Python…';
    const r=await PYR.run(code,'');stt.textContent='real Python';b.disabled=false;out.innerHTML=consoleHTML(r);
    if(r.error&&r.error.line){const l=panel.querySelector(`.ln[data-n="${r.error.line}"]`);if(l){l.classList.add('err');tag(l,r.error.type,'bad')}}};
}

/* ---------- Python runner: Pyodide in a Web Worker, killed on timeout ---------- */
const PYR=(()=>{
  let w=null,boot=null,seq=0;const pending=new Map();let ready=false;
  function start(){
    if(boot)return boot;
    boot=new Promise((res,rej)=>{
      try{w=new Worker('/static/js/py-worker.js')}catch(e){rej(e);return}
      w.onmessage=e=>{const d=e.data;if(d.type==='ready'){ready=true;res()}else if(d.type==='loadError')rej(new Error(d.msg));
        else{const p=pending.get(d.id);if(p){pending.delete(d.id);clearTimeout(p.t);p.res({stdout:d.stdout,error:d.error})}}};
      w.onerror=e=>rej(new Error(e.message||'The Python runner could not start.'));
    });
    boot.catch(()=>{kill()});
    return boot;
  }
  function kill(){if(w)w.terminate();w=null;boot=null;ready=false;pending.forEach(p=>{clearTimeout(p.t);p.res({stdout:'',error:{type:'Stopped',msg:'The run was stopped.'}})});pending.clear()}
  async function run(code,stdin,ms){
    try{await start()}catch(e){return {stdout:'',error:{type:'RunnerUnavailable',msg:'Python could not load in this browser ('+(e.message||'network error')+'). Try again.'}}}
    ms=ms||5000;const id=++seq;
    return new Promise(res=>{const t=setTimeout(()=>{pending.delete(id);kill();res({stdout:'',error:{type:'TimeoutError',msg:`Your code ran for more than ${ms/1000} seconds and was stopped. Look for a loop that never ends, or an input() waiting for a line that does not exist.`}})},ms);
      pending.set(id,{res,t});w.postMessage({id,code,stdin})});
  }
  return {start,run,get ready(){return ready}};
})();
const preloadPython=()=>{const go=()=>PYR.start().catch(()=>{});'requestIdleCallback' in window?requestIdleCallback(go,{timeout:3000}):setTimeout(go,1500)};

/* ---------- output comparison for local sample runs (the server re-checks everything) ---------- */
const outLines=s=>{const a=String(s||'').replace(/\r\n/g,'\n').split('\n').map(x=>x.replace(/\s+$/,''));while(a.length&&!a[a.length-1])a.pop();return a};
function sameOutput(got,exp,mode){const g=outLines(got),e=outLines(exp);
  if(mode==='lines')return JSON.stringify([...g].sort())===JSON.stringify([...e].sort());
  return g.length===e.length&&e.every((el,i)=>g[i].trim()===el.trim())}

/* ---------- API helpers ---------- */
async function api(method,path,body){return API.call(method,'/dicts'+path,body)}
function adopt(state){const first=!ST;ST=state;if(first)shownXP=ST.xp;
  missionEnd=(live()&&ST.remaining!=null)?Date.now()+ST.remaining*1000:null;hud();}
function netError(e){
  if(e&&e.message==='signed-out'){renderLogin('Your session ended. Sign in again to continue.');return}
  if(e&&e.message==='mission-over'){onMissionOver();return}
  // fetch() throws TypeError when the network is down; API.call throws Error(detail) for HTTP errors.
  toast(e instanceof TypeError?'Could not reach the server. Your answer was not saved.':(e&&e.message)||'Something went wrong. Try again.','err');
}
/* ---------- teacher resume: an ended mission (tab switches / time) can be reopened from the dashboard ---------- */
let resumeTimer=null;
function watchResume(){clearInterval(resumeTimer);resumeTimer=setInterval(()=>{if(!document.hidden)checkResume(false)},5000)}
async function checkResume(byHand){
  const b=$('#checkResume');if(byHand&&b){b.disabled=true;b.textContent='Checking…'}
  let m;try{m=await api('GET','/mission')}catch(e){if(b){b.disabled=false;b.textContent='Check again'}return}
  if(m.state.ended_at){
    if(m.state.ended_reason==='complete'||!['time','proctor'].includes(m.state.ended_reason))clearInterval(resumeTimer);
    if(b){b.disabled=false;b.textContent='Check again'}if(byHand)toast('Not resumed yet. Ask your teacher.','err');return}
  clearInterval(resumeTimer);resumeTimer=null;overHandled=false;
  await loadMission();sfx.win();toast('Your teacher resumed your mission','rank');
}
async function onMissionOver(){
  if(overHandled)return;overHandled=true;stopQTimer();closeDrawer();
  try{const m=await api('GET','/mission');adopt(m.state)}catch(e){}
  renderSummary();
}

/* ---------- modal (rules, proctoring warnings) ---------- */
function openModal(html,onClose){
  modal.innerHTML=`<div class="gin">${html}</div>`;modal.onclose=()=>{onClose&&onClose()};
  if(!modal.open)modal.showModal();
}
modal.addEventListener('cancel',e=>{if(modal.dataset.locked)e.preventDefault()});

function showRules(onAccept){
  const r=M.rules;modal.dataset.locked='';
  openModal(`<div class="ghead"><h2 id="modalTitle">${ICON.shield} Mission rules</h2></div>
    <ul class="rules-list">
      <li>${ICON.clock}<span>You have <b>${r.mission_minutes} minutes</b> for the whole mission. The clock starts when you press Start and keeps running even if you leave.</span></li>
      <li>${ICON.clock}<span>Every question has its <b>own countdown</b>. When it reaches zero you see the answer and an explanation, and the question closes.</span></li>
      <li>${ICON.eye}<span><b>Stay on this tab.</b> Leaving it or switching windows is recorded. ${r.max_tab_switches?`After <b>${r.max_tab_switches}</b> switches your mission ends.`:''}</span></li>
      <li>${ICON.shield}<span><b>Copy, paste and right-click are turned off.</b> Open the mission in one tab only.</span></li>
      <li>${ICON.bulb}<span><b>Hints are allowed</b> and point you to the concept. The solution opens after ${r.reveal_after} wrong tries.</span></li>
    </ul>
    <label class="agree"><input type="checkbox" id="agree"> I have read the rules and I am ready.</label>
    <div class="power-row"><button class="btn primary" id="rulesGo" type="button" disabled>${ICON.play}Start the ${r.mission_minutes}-minute mission</button><button class="btn ghost" id="rulesNo" type="button">Not yet</button></div>`);
  $('#agree',modal).onchange=e=>{$('#rulesGo',modal).disabled=!e.target.checked};
  $('#rulesNo',modal).onclick=()=>modal.close();
  $('#rulesGo',modal).onclick=async()=>{const b=$('#rulesGo',modal);b.disabled=true;
    try{const res=await api('POST','/start',{accept_rules:true});adopt(res.state);overHandled=false;modal.close();preloadPython();onAccept()}catch(e){b.disabled=false;netError(e)}};
}

/* ---------- proctoring: tab/window switches, copy/paste, a second tab ---------- */
const PROC={away:null,last:{}};
function report(type,extra){
  if(!live())return Promise.resolve(null);
  return api('POST','/proctor',Object.assign({type,qid:Q&&Q.q?Q.q.id:null},extra||{})).then(r=>{adopt(r.state);return r}).catch(()=>null);
}
function goAway(){if(live()&&!PROC.away)PROC.away=Date.now()}
async function comeBack(){
  if(!PROC.away)return;const ms=Date.now()-PROC.away;PROC.away=null;
  if(ms<800||!live())return;                       // ignore a flicker
  const r=await report('tab_switch',{duration_ms:ms});if(!r||!r.counted)return;
  sfx.warn();
  if(r.ended){overHandled=false;return onMissionOver()}
  const left=r.max?r.max-r.tab_switches:null;
  modal.dataset.locked='1';
  openModal(`<div class="ghead"><h2>${ICON.eye} You left the mission tab</h2></div>
    <p class="warnline">This was switch <b>${r.tab_switches}</b>${r.max?` of <b>${r.max}</b>`:''}. It has been recorded for your teacher.</p>
    ${left!==null?`<p class="${left<=1?'warnline bad':''}">${left===1?'<b>One more switch will end your mission.</b>':`${left} more switches will end your mission.`}</p>`:''}
    <p class="muted">The timers kept running while you were away.</p>
    <div class="power-row"><button class="btn primary" id="okBack" type="button">Back to the mission</button></div>`,()=>{modal.dataset.locked=''});
  $('#okBack',modal).onclick=()=>{modal.dataset.locked='';modal.close()};
}
document.addEventListener('visibilitychange',()=>document.hidden?goAway():comeBack());
addEventListener('blur',goAway);addEventListener('focus',comeBack);

let blockToastAt=0;
function blocked(type){
  if(Date.now()-blockToastAt>2500){blockToastAt=Date.now();toast(type==='devtools'?'Developer tools are not allowed during the mission':'Copy and paste are turned off during the mission','err')}
  if(Date.now()-(PROC.last[type]||0)>2000){PROC.last[type]=Date.now();report(type)}
}
const inLogin=t=>t&&t.closest&&t.closest('#loginForm');
['copy','cut','paste'].forEach(t=>document.addEventListener(t,e=>{if(inLogin(e.target))return;e.preventDefault();blocked(t)},true));
document.addEventListener('contextmenu',e=>{e.preventDefault();blocked('contextmenu')},true);
['dragstart','drop'].forEach(t=>document.addEventListener(t,e=>e.preventDefault(),true));
document.addEventListener('keydown',e=>{
  const k=(e.key||'').toLowerCase(),mod=e.ctrlKey||e.metaKey;
  if(e.key==='F12'||(mod&&e.shiftKey&&['i','j','c'].includes(k))||(mod&&k==='u')){e.preventDefault();blocked('devtools');return}
  if(mod&&['c','v','x'].includes(k)&&!inLogin(e.target)){e.preventDefault();blocked(k==='v'?'paste':k==='x'?'cut':'copy')}
},true);

// One tab at a time: a newly opened tab asks whether the mission is already open elsewhere.
const TAB_ID=Math.random().toString(36).slice(2);let dupTab=false,bc=null;
try{bc=new BroadcastChannel(API.key('mission'));bc.onmessage=e=>{const d=e.data||{};if(d.id===TAB_ID)return;if(d.t==='hello')bc.postMessage({t:'here',id:TAB_ID});else if(d.t==='here')dupTab=true};bc.postMessage({t:'hello',id:TAB_ID})}catch(e){}

/* ---------- navigation: back buttons + the browser's own Back button ---------- */
let popping=false;
function mark(s,a){
  if(popping)return;const cur=history.state||{};
  if(cur.s===s&&cur.a===a)return;
  if(!cur.s)history.replaceState({s,a},'');else history.pushState({s,a},'');
}
addEventListener('popstate',e=>{
  const st=e.state||{s:'map'};if(!M||!ST)return;
  if(guide.open)guide.close();if(modal.open&&!modal.dataset.locked)modal.close();
  popping=true;
  try{
    if(st.s==='brief'&&!ST.ended_at)renderBriefing(st.a);
    else if(st.s==='lab')renderLab();
    else if(st.s==='profile')renderProfile();
    else if(st.s==='report')renderSummary();
    else if(st.s==='q'&&!ST.ended_at&&lvState(st.a).unlocked)startLevel(st.a);
    else renderMap();
  }finally{popping=false}
});
function backBar(label,id){return `<div class="backbar"><button class="backbtn" id="${id||'backBtn'}" type="button">${ICON.back}${esc(label||'Back to mission map')}</button></div>`}

/* ---------- class leaderboard (own section only) ---------- */
async function loadLeaderboard(slot){
  const el=$(slot);if(!el)return;
  let d;try{d=await api('GET','/leaderboard')}catch(e){el.innerHTML='<p class="muted">The leaderboard is not available right now.</p>';return}
  if(!$(slot))return;
  const row=r=>`<li class="${r.me?'me':''}"><span class="rk">${r.rank}</span><span class="nm">${esc(r.name)}${r.me?' <small>(you)</small>':''}<small class="lbsub">${r.done}/${r.total} cleared · ${esc(r.status)}</small></span><b>${r.xp}<small> XP</small></b></li>`;
  el.innerHTML=`<h4>Class leaderboard · ${esc(d.section)}</h4>
    <ol class="lb">${d.rows.map(row).join('')||'<li class="empty">No one has started yet. Be the first.</li>'}</ol>
    ${d.me&&!d.rows.some(r=>r.me)?`<p class="lbme">You: rank ${d.me.rank} of ${d.count} · ${d.me.xp} XP</p>`:`<p class="lbme">${d.count} student${d.count===1?'':'s'} in your section</p>`}`;
}

/* ---------- mission map ---------- */
function starsHTML(n,cls){return `<span class="${cls||'stars'}" aria-label="${n} of 3 stars">${[0,1,2].map(i=>`<span class="${i<n?'on':''}">${ICON.star}</span>`).join('')}</span>`}
function badgeHTML(id,earned,small){const b=M.badges[id];return `<div class="badge${earned?' got':''}${small?' sm':''}" title="${esc(b.name)}: ${esc(b.desc)}"><span class="bico"><svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">${BADGE_ICON[id]||''}</svg></span><span><b>${esc(b.name)}</b><small>${esc(b.desc)}</small></span></div>`}
function nextLevel(){return M.levels.find(l=>lvState(l.id).unlocked&&!lvState(l.id).done)}
function renderMap(){
  if(needSurvey())return renderSurvey();
  R=null;Q=null;stopQTimer();closeDrawer();document.title=M.ui.title;
  const nx=nextLevel(),done=ST.levels.filter(l=>l.done).length,ended=!!ST.ended_at;
  const p=ST.progress,pct=p.total?Math.round(p.done/p.total*100):0;
  view.innerHTML=`<section class="home dicts-home">
    <div>
      <div class="hero enter">
        <div class="eyebrow">Mission · ${M.levels.filter(l=>!l.bonus).length} stages · ${p.total} challenges${M.levels.some(l=>l.bonus)?' + bonus':''}</div>
        <h1>${M.ui.hero_h1}</h1>
        <p>${M.ui.hero_p}</p>
        <div class="hero-row">
          ${ended?`<button class="btn gold" id="go" type="button">${ICON.trophy.replace('width="26" height="26"','width="20" height="20"')}See your mission report</button>`
            :ST.core_done?`<button class="btn gold" id="go" type="button">${ICON.play}Play the bonus round</button><button class="btn primary" id="finishBtn" type="button">Finish: see my report</button>`
            :`<button class="btn primary" id="go" type="button">${ICON.play}${ST.started_at?'Continue':'Start mission'}: ${esc(nx?nx.name:'')}</button>`}
          <button class="btn" id="labBtn" type="button">${ICON.board}${esc(M.ui.lab_name)}</button>
        </div>
        <div class="mbar-big" role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-valuenow="${pct}" aria-label="Mission progress"><i style="width:${pct}%"></i><span>${p.done} / ${p.total} challenges · ${ST.levels.filter((x,k)=>x.done&&!M.levels[k].bonus).length} / ${M.levels.filter(l=>!l.bonus).length} stages</span></div>
      </div>
      <div class="map" id="map">
        <svg class="trail" aria-hidden="true"><path class="base"/><path class="done"/></svg>
        ${M.levels.map((l,i)=>{const s=lvState(l.id),open=s.unlocked&&!ended;
          return `<button class="node${s.done?' cleared':''}${!open?' locked':''}${nx&&nx.id===l.id&&!ended?' next':''}${l.id==='BOSS'?' boss':''}${l.bonus?' bonus':''}" type="button" data-l="${l.id}" ${open?'':'aria-disabled="true"'} aria-label="${esc(l.name)}${open?'':' (locked)'}">
            <span class="orb">${!open&&!s.done?ICON.lock:l.bonus?'<svg viewBox="0 0 24 24" width="26" height="26" fill="currentColor" aria-hidden="true"><path d="m12 2.5 2.9 6 6.6.8-4.9 4.6 1.3 6.6L12 17.3l-5.9 3.2 1.3-6.6L2.5 9.3l6.6-.8z"/></svg>':l.id==='BOSS'?ICON.trophy:i===0?ICON.play.replace('class="i"','width="26" height="26"'):i}</span>
            <span><h3>${esc(l.name)}</h3><p>${esc(l.difficulty)} · ${s.total} challenge${s.total>1?'s':''}</p>
              <span class="nmm${s.done?' done':''}"><i style="width:${s.total?Math.round(s.cleared/s.total*100):0}%"></i></span><small class="nmt">${s.done?'Cleared':ended?'Mission over':open?`${s.cleared} / ${s.total} cleared`:l.bonus?'Optional: clear the Final Boss to unlock':'Clear the stage before to unlock'}</small></span>
            ${starsHTML(s.stars)}</button>`}).join('')}
      </div>
    </div>
    <aside class="side">
      <div class="card lbcard" id="lbCard"><h4>Class leaderboard</h4><p class="muted">Loading…</p></div>
      <div class="card"><h4>Badges · ${ST.badges.length} / ${Object.keys(M.badges).length}</h4><div class="badges">${Object.keys(M.badges).map(id=>badgeHTML(id,ST.badges.includes(id),true)).join('')}</div></div>
      <div class="card"><h4>Concept mastery</h4>${conceptBars()}</div>
      <div class="card"><h4>How it works</h4><div class="legend">
        <div>Every question has a <b>countdown</b>. Answer before it ends to earn XP.</div>
        <div>First try, no hint: <b>+20% XP</b>. Fixing a mistake still earns 60%.</div>
        <div>Stuck? <b>Use the hint.</b> It points you to the idea you need, for a small XP cost.</div>
        <div>3+ right in a row builds a <b>combo bonus</b>. A miss resets the combo, never your XP.</div></div></div>
    </aside></section>`;
  $('#go').onclick=()=>{ac();ended?renderSummary():nx&&renderBriefing(nx.id)};
  $('#labBtn').onclick=()=>{ac();renderLab()};
  const fb=$('#finishBtn');if(fb)fb.onclick=finishMission;
  $$('.node[data-l]').forEach(n=>n.onclick=()=>{
    if(ended)return renderSummary();
    const s=lvState(n.dataset.l);if(!s.unlocked){n.classList.remove('shake');void n.offsetWidth;n.classList.add('shake');sfx.bad();toast('Clear the stage before this one first','rank');return}
    ac();renderBriefing(n.dataset.l)});
  drawTrail();hud();window.scrollTo(0,0);mark('map');loadLeaderboard('#lbCard');
}
function conceptBars(){
  const ent=Object.entries(ST.concepts);
  if(!ent.length)return '<p class="muted">Answer a few questions to see where you are strong.</p>';
  return ent.map(([k,v])=>{const p=Math.round(v.c/v.a*100);return `<div class="skill${p>=80?' full':p<50?' weak':''}"><span>${esc(CONCEPTS[k]||k)}</span><b>${p}%</b><span class="bar"><i style="--p:${p}%"></i></span></div>`}).join('')+
    '<p class="muted small">First-attempt accuracy for each idea.</p>';
}
function drawTrail(){
  const map=$('#map');if(!map)return;const nodes=$$('.node',map),m=map.getBoundingClientRect();
  const pts=nodes.map(n=>{const o=$('.orb',n).getBoundingClientRect();return [o.left+o.width/2-m.left,o.top+o.height/2-m.top]});
  const path=a=>a.map((p,i)=>i?`C ${a[i-1][0]} ${(a[i-1][1]+p[1])/2}, ${p[0]} ${(a[i-1][1]+p[1])/2}, ${p[0]} ${p[1]}`:`M ${p[0]} ${p[1]}`).join(' ');
  $('.trail .base',map).setAttribute('d',path(pts));
  const k=ST.levels.findIndex(l=>!l.done);const upto=k<0?pts.length:k+1;
  $('.trail .done',map).setAttribute('d',upto>1?path(pts.slice(0,upto)):'');
}
addEventListener('resize',()=>{if($('#map'))drawTrail()});

/* ---------- stage briefing (the reading material, made interactive) ---------- */
function renderBriefing(id){
  if(ST.ended_at)return renderSummary();
  const l=LVM[id],i=lvIndex(id),s=lvState(id);closeDrawer();stopQTimer();
  const mains=l.main.map(q=>QM[q]),types=[...new Set(mains.map(q=>TYPE_LABEL[q.type]))],secs=mains.reduce((a,q)=>a+q.time,0);
  view.innerHTML=`<section class="power enter brief">
    ${backBar()}
    <div class="eyebrow">${l.bonus?'Bonus round':id==='BOSS'?'Final Boss':id==='L0'?'Mission briefing':'Stage '+i} · ${esc(l.difficulty)}</div>
    <h2>${esc(l.name)}</h2>
    ${id==='L0'?`<div class="story">${M.ui.story}</div>`:''}
    ${l.job?`<div class="jobbox"><h3>Your job</h3><p>${l.job}</p></div>`:''}
    <div class="intel"><h3>${esc(l.intel_title||'Field intel')}</h3><ul>${l.intel.map(t=>`<li>${t}</li>`).join('')}</ul></div>
    ${codePanel(l.demo,{run:true,file:id==='BOSS'?'scenario.py':'intel.py'})}
    <p class="tipline">${ICON.bulb}<span>Stuck on a question? Open its <b>hint</b>. It names the concept and nudges you towards it. The <b>field guide</b> (book icon, top right) has every rule in one place.</span></p>
    <div class="stages"><div><b>${mains.length} challenge${mains.length>1?'s':''}</b><span>${s.cleared} cleared so far</span><small>${types.join(' · ')}</small></div><div><b>Up to ${mins(secs)}</b><span>question countdowns in total</span><small>Each question shows its own timer</small></div></div>
    <div class="power-row"><button class="btn primary" id="begin" type="button">${ICON.play}${s.done?'Replay stage (no new XP)':s.cleared?'Continue stage':'Start stage'}</button><button class="btn ghost" id="toMap" type="button">Mission map</button><span>Keys: 1–9 pick · Enter checks</span></div>
  </section>`;
  bindRun($('.code',view),l.demo);
  $('#toMap').onclick=renderMap;$('#backBtn').onclick=renderMap;
  $('#begin').onclick=()=>{sfx.tap();if(!ST.started_at)return showRules(()=>startLevel(id));startLevel(id)};
  window.scrollTo(0,0);$('#view').focus({preventScroll:true});mark('brief',id);
}
function startLevel(id){
  const l=LVM[id],s=lvState(id);mark('q',id);
  const queue=s.done?l.main.slice():l.main.filter(q=>!cleared(q));
  R={level:id,mains:l.main,queue,replay:s.done,badges:[],xp0:ST.xp};
  nextQ();
}
function nextQ(){
  closeDrawer();stopQTimer();
  // Finishing the Final Boss also ends the mission: show its celebration screen first, then the report.
  const justFinished=ST.ended_reason==='complete'&&!R.queue.length&&lvState(R.level).done;
  if(ST.ended_at&&!justFinished)return renderSummary();
  if(!R.queue.length)return lvState(R.level).done?renderLevelDone():renderMap();
  renderQuestion(R.queue[0]);
}

/* ---------- per-question countdown (deadline fixed by the server at first open) ---------- */
const QT={end:0,limit:0,iv:null,qid:null,nudged:false,warned:false};
function stopQTimer(){clearInterval(QT.iv);QT.iv=null;QT.qid=null}
function timerHTML(q,replay){
  if(replay||cleared(q.id))return '';
  return `<div class="qtimer" id="qtimer" role="timer" aria-label="Time left for this question"><svg viewBox="0 0 36 36" aria-hidden="true"><circle class="trk" cx="18" cy="18" r="15.5"/><circle class="arc" id="qarc" cx="18" cy="18" r="15.5" pathLength="100"/></svg><b id="qtime">${mins(q.time)}</b></div><span class="sr-only" id="qtimeLive" aria-live="assertive"></span>`;
}
async function startQTimer(q){
  stopQTimer();if(!$('#qtimer'))return;
  let r;try{r=await api('POST','/open',{qid:q.id})}catch(e){return netError(e)}
  if(!Q||Q.q.id!==q.id)return;
  if(r.cleared){$('#qtimer').remove();return}
  Object.assign(QT,{end:Date.now()+r.remaining*1000,limit:r.limit,qid:q.id,nudged:false,warned:false});
  tickQ();QT.iv=setInterval(tickQ,250);
}
function tickQ(){
  if(!Q||Q.q.id!==QT.qid){stopQTimer();return}
  const left=Math.max(0,(QT.end-Date.now())/1000),frac=QT.limit?left/QT.limit:0;
  const t=$('#qtime'),arc=$('#qarc'),box=$('#qtimer');if(!t)return stopQTimer();
  t.textContent=mins(left);arc.style.strokeDashoffset=String(100-frac*100);
  box.classList.toggle('low',left<=10);box.classList.toggle('mid',left>10&&frac<=.5);
  if(!QT.warned&&left<=10&&left>0){QT.warned=true;const lv=$('#qtimeLive');if(lv)lv.textContent='10 seconds left'}
  if(!QT.nudged&&frac<=.5&&!Q.hint&&!Q.done){QT.nudged=true;nudgeHint()}
  if(Q.done){stopQTimer();box.classList.add('stopped');return}
  if(left<=0){stopQTimer();expireQ()}
}
function nudgeHint(){
  const hb=$('#hint');if(!hb||hb.disabled)return;
  hb.classList.add('nudge');
  const slot=$('#hintSlot');if(slot&&!slot.innerHTML)slot.innerHTML=`<p class="nudgeline">${ICON.bulb}<span>Half your time is gone. The <b>hint</b> points you to the concept you need.</span></p>`;
}
async function expireQ(){
  if(!Q||Q.done)return;if(Q.busy){setTimeout(expireQ,300);return}
  Q.done=true;Q.busy=true;
  $$('.qside,.cwork').forEach(x=>x.classList.add('locked'));$$('#check,#hint,#submit,#runS,#revealBtn').forEach(b=>b&&(b.disabled=true));
  let r=null;
  for(let i=0;i<4&&!r;i++){try{r=await api('POST','/expire',{qid:Q.q.id})}catch(e){if(e.message==='mission-over')return onMissionOver();await new Promise(res=>setTimeout(res,800))}}
  Q.busy=false;if(!r)return toast('Could not reach the server.','err');
  adopt(r.state);try{Q.solve(r.solution)}catch(e){}
  if(r.focus)focusLine(Q.panel,r.focus,'the key line');
  $('.segs')&&($('.segs').innerHTML=segsHTML(Q.q.id));
  sfx.bad();celebrateBadges(r.new_badges);openTimeUp(r);
}

/* ---------- question screen ---------- */
function segsHTML(cur){return R.mains.map(id=>{const s=qs(id);return `<i class="${s.solved?(s.wrong?'fixed':'ok'):s.timed_out?'tout':s.revealed?'shown':s.wrong?'redo':''}${id===cur?' cur':''}" title="${esc(QM[id].title)}"></i>`}).join('')}
function qtopHTML(q){
  const l=LVM[R.level];
  return `<div class="qtop"><button class="backbtn sm" id="quit" type="button" aria-label="Back to the mission map (the question timer keeps running)" title="The question timer keeps running">${ICON.back}<span>Map</span></button><span class="where">${esc(l.name)}</span><div class="segs" aria-hidden="true">${segsHTML(q.id)}</div>
    <span class="qcount">${R.mains.indexOf(q.id)+1} / ${R.mains.length}</span>${timerHTML(q,R.replay)}</div>`;
}
function actionsHTML(){
  const st=qs(Q.q.id),can=(st.wrong||0)>=M.rules.reveal_after&&!cleared(Q.q.id);
  return `<button class="btn ghost" id="hint" type="button">${ICON.bulb}Hint</button>${can?'<button class="btn ghost" id="revealBtn" type="button">Show the solution</button>':''}`;
}
function renderQuestion(id){
  const q=QM[id];if(!q)return renderMap();
  if(q.type==='coding')return renderCoding(q);
  const st=qs(id);
  Q={q,sel:null,busy:false,done:false,hint:!!st.hint,wrong:st.wrong||0};
  let left='',solo=false;
  if(q.type==='board')left=`<div>${boardHTML('graded')}</div>`;
  else if(q.type==='fill')left=`<div>${codePanel(q.code,{blanks:true})}</div>`;
  else if(q.code)left=`<div>${codePanel(q.code,{tap:q.type==='debug',mode:q.type==='debug'?'pick':''})}</div>`;
  else if(q.scenario)left=`<div>${codePanel(LVM.BOSS.demo,{file:'scenario.py'})}</div>`;
  else solo=true;
  view.innerHTML=`${qtopHTML(q)}
    <section class="qgrid enter${solo?' solo':''}" data-qid="${esc(q.id)}">
      ${left}
      <div class="qside">
        <span class="qchip">${R.replay?'Replay · no XP · ':''}${TYPE_LABEL[q.type]}${R.replay?'':` · ${q.xp} XP`}</span>
        <h2 class="qtitle" id="qtitle">${esc(q.title)}</h2>
        ${howtoHTML(q.type)}
        <div id="pad"></div>
        <div id="hintSlot" aria-live="polite"></div>
        <div class="actions" id="actions">${actionsHTML()}<button class="btn primary" id="check" type="button" disabled>Check</button></div>
      </div></section>`;
  $('#quit').onclick=renderMap;bindActions();$('#check').onclick=check;
  Q.panel=$('.code',view);
  PADS[q.type](q);
  if(Q.hint)showHint(true);
  window.scrollTo(0,0);
  const first=$('#pad button, #pad input, #pad .ln.tappable, .code .ln.tappable, .board input, .land button');if(first&&!matchMedia('(pointer: coarse)').matches)first.focus({preventScroll:true});
  startQTimer(q);
}
function bindActions(){const hb=$('#hint');if(hb)hb.onclick=()=>showHint();const rb=$('#revealBtn');if(rb)rb.onclick=revealSolution}
function refreshActions(){
  // After a 2nd wrong try, "Show the solution" joins the action bar for the 3rd attempt.
  const a=$('#actions');if(!a||$('#revealBtn'))return;
  if((qs(Q.q.id).wrong||0)>=M.rules.reveal_after&&!Q.done){$('#hint').insertAdjacentHTML('afterend','<button class="btn ghost" id="revealBtn" type="button">Show the solution</button>');bindActions()}
}
const canCheck=v=>{const b=$('#check');if(b)b.disabled=!v||Q.done};
function outHTML(o){
  const lines=o.split('\n'),err=lines[lines.length-1].startsWith('!')?lines.pop().slice(1):null;
  return `<span class="o-wrap">${lines.length?`<pre class="o-out">${esc(lines.join('\n'))}</pre>`:''}${err?`<span class="o-err">${esc(err)}<small>Python stops with an error</small></span>`:''}</span>`;
}
const looksCode=s=>/[(){}\[\]=|&^]|^[a-z_]+\.[a-z_]+/.test(s);

/* each pad defines Q.get() → answer or null, Q.mark(result), Q.reset(), Q.solve(solution) */
function choicePad(q,multi){
  const pad=$('#pad');
  const head=q.type==='ar'?`<div class="arbox"><div><b>Assertion (A)</b><p>${esc(q.assertion)}</p></div><div><b>Reason (R)</b><p>${esc(q.reason)}</p></div></div>`:'';
  const instr=multi?`<div class="instr multi" id="instr"><span class="instr-ico" aria-hidden="true"><i></i><i></i></span><span><b>Select all that apply.</b> More than one answer is correct. Tap every correct option, then press Check.</span><span class="selcount" id="selCount" aria-live="polite">0 selected</span></div>`
    :`<div class="instr"><span class="instr-ico one" aria-hidden="true"><i></i></span><span><b>Choose one answer.</b></span></div>`;
  pad.innerHTML=head+instr+`<div class="opts${multi?' multi':''}" role="${multi?'group':'radiogroup'}" aria-labelledby="qtitle">${q.options.map((o,i)=>`<button class="opt" type="button" role="${multi?'checkbox':'radio'}" aria-checked="false" data-i="${i}"><span class="key">${multi?`<span class="box">${ICON.check}</span>`:i+1}</span>${q.type==='predict'?outHTML(o):`<span class="o-text">${looksCode(o)?`<code class="ocode">${esc(o)}</code>`:esc(o)}</span>`}</button>`).join('')}</div>`;
  const btns=$$('.opt',pad);Q.multi=new Set();
  btns.forEach((b,i)=>b.onclick=()=>{if(Q.done||Q.busy)return;clearMarks();sfx.tap();
    if(multi){Q.multi.has(i)?Q.multi.delete(i):Q.multi.add(i);b.setAttribute('aria-checked',Q.multi.has(i));const n=Q.multi.size;$('#selCount').textContent=n+' selected';$('#instr').classList.toggle('has',n>0);canCheck(n>0)}
    else{Q.sel=i;btns.forEach((x,k)=>x.setAttribute('aria-checked',k===i));canCheck(true)}});
  Q.keyPick=i=>btns[i]&&btns[i].click();
  Q.get=()=>multi?(Q.multi.size?[...Q.multi]:null):Q.sel;
  const clearMarks=()=>btns.forEach(b=>b.classList.remove('is-ok','is-bad','is-bad-soft','dim'));
  Q.reset=clearMarks;
  Q.mark=r=>{if(multi){btns.forEach((b,i)=>{if(Q.multi.has(i))b.classList.add(r.correct?'is-ok':'is-bad-soft')})}else{const b=btns[Q.sel];b.classList.add(r.correct?'is-ok':'is-bad');if(r.correct)btns.forEach((x,i)=>{if(i!==Q.sel)x.classList.add('dim')})}};
  Q.solve=s=>{clearMarks();const ok=multi?s.indexes:[s.index];btns.forEach((b,i)=>{b.classList.add(ok.includes(i)?'is-ok':'dim');if(multi)b.setAttribute('aria-checked',ok.includes(i))})};
}
function padTF(q){
  const pad=$('#pad');
  pad.innerHTML=`<div class="instr"><span class="instr-ico one" aria-hidden="true"><i></i></span><span><b>Is the statement true or false?</b></span></div><div class="yn" role="radiogroup" aria-labelledby="qtitle"><button class="opt" type="button" role="radio" aria-checked="false"><span class="key">1</span><span class="o-big">True</span></button><button class="opt" type="button" role="radio" aria-checked="false"><span class="key">2</span><span class="o-big">False</span></button></div>`;
  const btns=$$('.opt',pad);
  btns.forEach((b,i)=>b.onclick=()=>{if(Q.done||Q.busy)return;Q.reset();sfx.tap();Q.sel=i;btns.forEach((x,k)=>x.setAttribute('aria-checked',k===i));canCheck(true)});
  Q.keyPick=i=>btns[i]&&btns[i].click();
  Q.get=()=>Q.sel===null?null:Q.sel===0;
  Q.reset=()=>btns.forEach(b=>b.classList.remove('is-ok','is-bad','dim'));
  Q.mark=r=>btns[Q.sel].classList.add(r.correct?'is-ok':'is-bad');
  Q.solve=s=>{Q.reset();btns[s.value?0:1].classList.add('is-ok')};
}
function padNumeric(q){
  const pad=$('#pad');
  pad.innerHTML=`<label class="numwrap"><span>Your answer</span><input id="num" type="text" inputmode="decimal" autocomplete="off" placeholder="Type a number" aria-describedby="qtitle"></label><p class="qhelp">Trace the code first. Press Enter to check.</p>`;
  const inp=$('#num');
  inp.oninput=()=>{inp.classList.remove('is-ok','is-bad');canCheck(/^-?\d+(\.\d+)?$/.test(inp.value.trim()))};
  inp.onkeydown=e=>{if(e.key==='Enter'){e.preventDefault();e.stopPropagation();check()}};
  Q.get=()=>/^-?\d+(\.\d+)?$/.test(inp.value.trim())?Number(inp.value.trim()):null;
  Q.reset=()=>inp.classList.remove('is-ok','is-bad');
  Q.mark=r=>{inp.classList.add(r.correct?'is-ok':'is-bad');inp.disabled=!!r.correct};
  Q.solve=s=>{inp.value=s.value;inp.classList.remove('is-bad');inp.classList.add('is-ok');inp.disabled=true};
}
function padFill(q){
  $('#pad').innerHTML=`<p class="qhelp">Type into each highlighted gap in the code. Spelling counts, just like in Python.</p>`;
  const ins=$$('input.blank',Q.panel);
  ins.forEach((inp,k)=>{inp.oninput=()=>{inp.classList.remove('is-ok','is-bad');inp.size=Math.max(4,inp.value.length+1);canCheck(ins.every(x=>x.value.trim()))};
    inp.onkeydown=e=>{if(e.key==='Enter'){e.preventDefault();e.stopPropagation();if(ins[k+1]&&!ins[k+1].value)ins[k+1].focus();else check()}}});
  Q.get=()=>ins.every(x=>x.value.trim())?ins.map(x=>x.value):null;
  Q.reset=()=>ins.forEach(x=>x.classList.remove('is-ok','is-bad'));
  Q.mark=r=>{const per=(r.detail&&r.detail.per_blank)||[];ins.forEach((x,i)=>{x.classList.add(per[i]?'is-ok':'is-bad');if(r.correct)x.disabled=true})};
  Q.solve=s=>ins.forEach((x,i)=>{x.value=s.blanks[i];x.size=Math.max(4,x.value.length+1);x.classList.remove('is-bad');x.classList.add('is-ok');x.disabled=true});
}
function padMatch(q){
  const pad=$('#pad');Q.pairs=q.left.map(()=>null);Q.lsel=0;
  pad.innerHTML=`<p class="qhelp">Pick an item on the left, then its match on the right. Pick a matched item again to change it.</p><div class="mgrid2"><div class="mcol2" id="mL"></div><div class="mcol2" id="mR"></div></div>`;
  const draw=()=>{
    $('#mL').innerHTML=q.left.map((t,i)=>`<button type="button" class="mitem2${Q.lsel===i?' sel':''}${Q.pairs[i]!==null?' paired':''}" data-i="${i}" ${Q.pairs[i]!==null?`data-p="${i%5}"`:''} aria-pressed="${Q.lsel===i}"><code class="ocode">${esc(t)}</code>${Q.pairs[i]!==null?`<span class="pn">${i+1}</span>`:''}</button>`).join('');
    $('#mR').innerHTML=q.right.map((t,j)=>{const li=Q.pairs.indexOf(j);return `<button type="button" class="mitem2${li>=0?' paired':''}" data-j="${j}" ${li>=0?`data-p="${li%5}"`:''}>${li>=0?`<span class="pn">${li+1}</span>`:''}${esc(t)}</button>`}).join('');
    $$('#mL .mitem2').forEach(b=>b.onclick=()=>{if(Q.done)return;Q.reset();Q.lsel=+b.dataset.i;sfx.tap();draw()});
    $$('#mR .mitem2').forEach(b=>b.onclick=()=>{if(Q.done||Q.lsel===null)return;Q.reset();const j=+b.dataset.j,prev=Q.pairs.indexOf(j);if(prev>=0)Q.pairs[prev]=null;Q.pairs[Q.lsel]=j;
      const nx=Q.pairs.findIndex(p=>p===null);Q.lsel=nx<0?null:nx;sfx.tap();draw()});
    canCheck(Q.pairs.every(p=>p!==null));
  };
  draw();
  Q.get=()=>Q.pairs.every(p=>p!==null)?Q.pairs:null;
  Q.reset=()=>$$('#mL .mitem2').forEach(b=>b.classList.remove('is-ok','is-bad'));
  Q.mark=r=>{const per=(r.detail&&r.detail.per_item)||[];$$('#mL .mitem2').forEach((b,i)=>b.classList.add(per[i]?'is-ok':'is-bad'))};
  Q.solve=s=>{Q.pairs=s.mapping.slice();Q.lsel=null;draw();$$('#mL .mitem2').forEach(b=>b.classList.add('is-ok'))};
}
function padOrder(q){
  const pad=$('#pad');Q.order=q.items.map((_,i)=>i);let prevIndex={};
  pad.innerHTML=`<p class="qhelp">Move the lines with the arrow buttons until the program is in the right order.</p><ol class="olist" id="olist"></ol>`;
  const draw=animate=>{
    const first=animate?$$('#olist li').map(li=>li.getBoundingClientRect().top):null;
    $('#olist').innerHTML=Q.order.map((id,k)=>`<li data-id="${id}"><span class="ono">${k+1}</span><code class="ocode">${hl(q.items[id])}</code><span class="omv"><button type="button" data-k="${k}" data-d="-1" aria-label="Move line up" ${k===0?'disabled':''}>${ICON.up}</button><button type="button" data-k="${k}" data-d="1" aria-label="Move line down" ${k===Q.order.length-1?'disabled':''}>${ICON.down}</button></span></li>`).join('');
    $$('#olist button').forEach(b=>b.onclick=()=>{if(Q.done)return;Q.reset();const k=+b.dataset.k,d=+b.dataset.d,j=k+d;[Q.order[k],Q.order[j]]=[Q.order[j],Q.order[k]];sfx.tap();draw(true);
      const nb=$(`#olist li[data-id="${Q.order[j]}"] button[data-d="${d}"]:not(:disabled)`)||$(`#olist li[data-id="${Q.order[j]}"] button:not(:disabled)`);if(nb)nb.focus()});
    if(first&&!reduce)$$('#olist li').forEach(li=>{const old=first[prevIndex[+li.dataset.id]],now=li.getBoundingClientRect().top;if(old!==undefined&&old!==now)li.animate([{transform:`translateY(${old-now}px)`},{transform:'none'}],{duration:200,easing:'cubic-bezier(.23,1,.32,1)'})});
    prevIndex={};Q.order.forEach((id,k)=>prevIndex[id]=k);
  };
  draw();canCheck(true);
  Q.get=()=>Q.order.slice();
  Q.reset=()=>$('#olist').classList.remove('is-ok','is-bad');
  Q.mark=r=>$('#olist').classList.add(r.correct?'is-ok':'is-bad');
  Q.solve=s=>{Q.order=s.mapping.slice();draw();$('#olist').classList.add('is-ok')};
}
function padCategorize(q){
  const pad=$('#pad');Q.cat=q.items.map(()=>null);
  pad.innerHTML=`<p class="qhelp">Choose a group for every item.</p><div class="cats">${q.items.map((it,i)=>`<div class="catrow" data-i="${i}"><code class="ocode">${hl(it)}</code><div class="seg2 catseg" role="radiogroup" aria-label="Group for ${esc(it)}">${q.categories.map((c,k)=>`<button type="button" role="radio" aria-checked="false" data-k="${k}">${esc(c)}</button>`).join('')}</div></div>`).join('')}</div>`;
  $$('.catrow',pad).forEach(row=>{const i=+row.dataset.i;$$('button',row).forEach(b=>b.onclick=()=>{if(Q.done)return;row.classList.remove('is-ok','is-bad');Q.cat[i]=+b.dataset.k;
    $$('button',row).forEach(x=>{x.setAttribute('aria-checked',x===b);x.setAttribute('aria-pressed',x===b)});sfx.tap();canCheck(Q.cat.every(c=>c!==null))})});
  Q.get=()=>Q.cat.every(c=>c!==null)?Q.cat:null;
  Q.reset=()=>$$('.catrow',pad).forEach(r=>r.classList.remove('is-ok','is-bad'));
  Q.mark=r=>{const per=(r.detail&&r.detail.per_item)||[];$$('.catrow',pad).forEach((row,i)=>row.classList.add(per[i]?'is-ok':'is-bad'))};
  Q.solve=s=>$$('.catrow',pad).forEach((row,i)=>{Q.cat[i]=s.mapping[i];$$('button',row).forEach(x=>{const on=+x.dataset.k===s.mapping[i];x.setAttribute('aria-checked',on);x.setAttribute('aria-pressed',on)});row.classList.remove('is-bad');row.classList.add('is-ok')});
}
function padDebug(q){
  const pad=$('#pad');Q.line=null;Q.err=null;
  pad.innerHTML=`<p class="qhelp">Tap the line in the code that the question asks for, then choose what goes wrong. Tap another line to change your pick.</p>
    <div class="target" id="lpick"><small>Faulty line</small>Tap a line in the code</div>
    <div><span class="multi-note muted">What happens?</span><div class="seg2 wide errseg" role="radiogroup" aria-label="Error type">${q.errors.map((e,k)=>`<button type="button" role="radio" aria-checked="false" aria-pressed="false" data-k="${k}">${esc(e)}</button>`).join('')}</div></div>`;
  const upd=()=>{$('#lpick').innerHTML=`<small>Faulty line</small>${Q.line?'Line '+Q.line+' <span class="muted small">· tap another line to change</span>':'Tap a line in the code'}`;canCheck(Q.line&&Q.err!==null)};
  $$('.ln.tappable',Q.panel).forEach(l=>{const pickLine=()=>{if(Q.done)return;Q.reset();Q.line=+l.dataset.n;$$('.ln.tappable',Q.panel).forEach(x=>{x.classList.toggle('picked',x===l);x.setAttribute('aria-pressed',x===l)});sfx.tap();upd()};
    l.onclick=pickLine;l.onkeydown=e=>{if(e.key===' '||e.key==='Enter'){e.preventDefault();e.stopPropagation();pickLine()}}});
  $$('.errseg button',pad).forEach(b=>b.onclick=()=>{if(Q.done)return;Q.reset();Q.err=+b.dataset.k;$$('.errseg button',pad).forEach(x=>{x.setAttribute('aria-pressed',x===b);x.setAttribute('aria-checked',x===b)});sfx.tap();upd()});
  Q.keyPick=i=>{const b=$$('.errseg button',pad)[i];if(b)b.click()};
  Q.get=()=>Q.line&&Q.err!==null?{line:Q.line,error:Q.err}:null;
  Q.reset=()=>{$$('.ln',Q.panel).forEach(l=>{l.classList.remove('mark-ok','mark-bad');$$('.tag',l).forEach(t=>t.remove())});$$('.errseg button',pad).forEach(b=>b.classList.remove('is-ok','is-bad'))};
  Q.mark=r=>{const d=r.detail||{},l=Q.panel.querySelector(`.ln[data-n="${Q.line}"]`);if(l){l.classList.add(d.line_ok?'mark-ok':'mark-bad');tag(l,d.line_ok?'right line':'not this line',d.line_ok?'good':'bad')}
    const b=$$('.errseg button',pad)[Q.err];if(b)b.classList.add(d.error_ok?'is-ok':'is-bad')};
  Q.solve=s=>{Q.reset();const l=Q.panel.querySelector(`.ln[data-n="${s.line}"]`);if(l){l.classList.add('mark-ok');tag(l,'fix this line','good')}const b=$$('.errseg button',pad)[s.error];if(b)b.classList.add('is-ok')};
}
function padBoard(q){
  const pad=$('#pad'),same=rows=>JSON.stringify(rows)===JSON.stringify(q.start);
  pad.innerHTML=`<div class="goal">${q.goal}</div><p class="qhelp">Type a key and a value, then press a Python button on the board. Tap a name tag to load its row. When the board is right, press Check.</p><ul class="checks" id="pgChecks"></ul>`;
  const b=Board($('.board',view),{start:q.start,onChange:()=>{Q.reset();canCheck(!same(b.rows))}});
  Q.get=()=>same(b.rows)?null:{rows:b.rows.map(r=>r.slice())};
  Q.reset=()=>{$('#pgChecks').innerHTML=''};
  Q.mark=r=>{const ch=(r.detail&&r.detail.checks)||[];$('#pgChecks').innerHTML=ch.map(c=>`<li class="${c.ok?'ok':'bad'}">${c.ok?ICON.check:ICON.x}<span>${c.text}</span></li>`).join('');if(r.correct)b.lock()};
  Q.solve=s=>{b.load(s.rows);b.lock();$('#pgChecks').innerHTML=`<li class="ok">${ICON.check}<span>print(menu) gives <code>${esc(s.text)}</code></span></li>`};
}
/* ---------- Where does it land? (graded): tap an argument, then the box it lands in ---------- */
function boxKind(label){return label.startsWith('**')?['dict','dict { }']:label.startsWith('*')?['tuple','tuple ( )']:['named','one value']}
function padLand(q){
  const pad=$('#pad'),n=q.boxes.length;Q.land=q.args.map(()=>null);Q.lsel=0;
  pad.innerHTML=`<p class="qhelp">Tap an argument, then the box it lands in. Use <b>No box</b> if Python stops.</p><div class="land"><div class="lsub">The call's arguments</div><div class="largs" id="largs"></div>
    <div class="lsub">The boxes in the def</div><div class="lboxes" id="lboxes"></div></div>`;
  const draw=()=>{
    $('#largs').innerHTML=q.args.map((a,i)=>`<button type="button" class="lchip${Q.lsel===i?' sel':''}${Q.land[i]!==null?' placed':''}" data-a="${i}" aria-pressed="${Q.lsel===i}"><code>${esc(a)}</code>${Q.land[i]!==null?`<small>→ ${Q.land[i]===n?'no box':esc(q.boxes[Q.land[i]])}</small>`:''}</button>`).join('');
    $('#lboxes').innerHTML=q.boxes.map((b,k)=>{const [cls,desc]=boxKind(b);return `<button type="button" class="lbox ${cls}" data-b="${k}"><span class="lbhead"><code>${esc(b)}</code><small>${desc}</small></span><span class="lin">${Q.land.map((x,i)=>x===k?`<code class="lgot" data-i="${i}">${esc(q.args[i])}</code>`:'').join('')}</span></button>`}).join('')
      +`<button type="button" class="lbox none" data-b="${n}"><span class="lbhead"><b>No box</b><small>Python stops: TypeError</small></span><span class="lin">${Q.land.map((x,i)=>x===n?`<code class="lgot" data-i="${i}">${esc(q.args[i])}</code>`:'').join('')}</span></button>`;
    $$('#largs .lchip').forEach(b=>b.onclick=()=>{if(Q.done)return;Q.reset();Q.lsel=+b.dataset.a;sfx.tap();draw()});
    $$('#lboxes .lbox').forEach(b=>b.onclick=()=>{if(Q.done||Q.lsel===null)return;Q.reset();Q.land[Q.lsel]=+b.dataset.b;
      const nx=Q.land.findIndex(x=>x===null);Q.lsel=nx<0?null:nx;sfx.tap();draw()});
    canCheck(Q.land.every(x=>x!==null));
  };
  draw();
  Q.keyPick=i=>{const b=$$('#largs .lchip')[i];if(b)b.click()};
  Q.get=()=>Q.land.every(x=>x!==null)?Q.land.slice():null;
  Q.reset=()=>$$('#largs .lchip').forEach(b=>b.classList.remove('is-ok','is-bad'));
  Q.mark=r=>{const per=(r.detail&&r.detail.per_item)||[];$$('#largs .lchip').forEach((b,i)=>b.classList.add(per[i]?'is-ok':'is-bad'))};
  Q.solve=s=>{Q.land=s.mapping.slice();Q.lsel=null;draw();$$('#largs .lchip').forEach(b=>b.classList.add('is-ok'))};
}

/* ---------- Trip Lab (free play): Sheets (names and copies) + Calls (where arguments land, in real Python) ---------- */
const TRIP0=[['Teja',1500],['Ravi',800],['Kiran',0]];
function renderTripLab(){
  R=null;Q=null;stopQTimer();closeDrawer();
  view.innerHTML=`<section class="lab enter">${backBar('Back to mission map','quit')}<h2 class="labtitle">${esc(M.ui.lab_name)} <small>free play</small></h2>
    <div class="vnote seg2 labtabs" role="tablist" aria-label="Lab"><button type="button" role="tab" aria-pressed="true" data-tab="sheets">Sheets: names and copies</button><button type="button" role="tab" aria-pressed="false" data-tab="calls">Calls: where arguments land</button></div>
    <div id="labBody"></div></section>`;
  const tabs=$$('.labtabs button');
  tabs.forEach(b=>b.onclick=()=>{tabs.forEach(x=>x.setAttribute('aria-pressed',x===b));sfx.tap();b.dataset.tab==='sheets'?sheetsTab():callsTab()});
  $('#quit').onclick=renderMap;sheetsTab();window.scrollTo(0,0);mark('lab');
}
function sheetsTab(){
  // A tiny model of Python names and objects: names point at sheets; = moves an arrow, copy() makes a sheet.
  let sheets,names,seq,last;
  const reset=()=>{seq=1;sheets={1:TRIP0.map(r=>r.slice())};names={trip:1};last=['trip = {"Teja": 1500, "Ravi": 800, "Kiran": 0}','One sheet, one name.']};
  reset();
  const repr=rows=>rows.length?'{'+rows.map(([k,v])=>`'${k}': ${v}`).join(', ')+'}':'{}';
  const set=(id,k,v)=>{const r=sheets[id].find(x=>x[0]===k);if(r)r[1]=v;else sheets[id].push([k,v])};
  const ACTS=[
    ['backup = trip',()=>{names.backup=names.trip;return 'Only an arrow is added: backup is a second name for the <b>same</b> sheet.'}],
    ['backup = trip.copy()',()=>{sheets[++seq]=sheets[names.trip].map(r=>r.slice());names.backup=seq;return '<b>A second sheet</b> with the same rows. backup points at it.'}],
    ['trip["Kiran"] = 500',()=>{set(names.trip,'Kiran',500);return names.backup===names.trip?'Changed through trip, and backup sees it: one sheet.':'Changed on trip\'s sheet only.'}],
    ['backup["Kiran"] = 2000',()=>{if(!('backup' in names))return null;set(names.backup,'Kiran',2000);return names.backup===names.trip?'Changed through backup, and trip sees it: one sheet.':'Changed on backup\'s sheet only.'}],
    ['trip.clear()',()=>{sheets[names.trip].length=0;return 'The sheet is emptied in place. <b>Every</b> name pointing at it sees {}.'}],
    ['trip = {}',()=>{sheets[++seq]=[];names.trip=seq;return 'trip now points at a <b>new</b> empty sheet. Other names keep the old one.'}],
  ];
  $('#labBody').innerHTML=`<div class="labgrid"><div class="tripsheets card">
      <div class="vops" role="group" aria-label="Run a line">${ACTS.map(([c],i)=>`<button type="button" data-i="${i}"><code>${esc(c)}</code></button>`).join('')}<button type="button" data-i="reset">Start over</button></div>
      <div class="vres"><code class="vexpr" id="tsLine"></code></div><p class="vmsg" id="tsMsg"></p>
      <div class="sheets" id="sheets"></div>
      <div class="tsprint" id="tsPrint"></div></div>
    <div class="card"><h4>Experiments to try</h4><ol class="exp">
      <li>Press <code>backup = trip</code>, then <code>trip["Kiran"] = 500</code>. What does backup show?</li>
      <li>Start over. Press <code>backup = trip.copy()</code>, then change trip. Now?</li>
      <li>Make backup with <code>=</code>, then <code>trip.clear()</code>. Then try it with <code>trip = {}</code> instead.</li>
      <li>Watch <code>id(trip) == id(backup)</code> after each line.</li></ol>
      <p class="muted small">The Lab is free play: nothing here is graded. The mission clock keeps running.</p></div></div>`;
  const draw=()=>{
    $('#tsLine').textContent=last[0];$('#tsMsg').innerHTML=last[1];
    const ids=[...new Set(Object.keys(sheets).map(Number))];
    $('#sheets').innerHTML=ids.map(id=>{const tags=Object.keys(names).filter(n=>names[n]===id);
      return `<div class="sheet${tags.length?'':' orphan'}"><div class="shead">${tags.length?tags.map(t=>`<span class="ntag">${t}</span>`).join(''):'<span class="muted small">no name points here</span>'}<small>dictionary #${id}</small></div>
        <ol class="brows">${sheets[id].map(([k,v])=>`<li class="brow"><span class="btag">${esc(k)}</span><span class="barrow">→</span><span class="bprice">${v}</span></li>`).join('')||'<li class="bempty">empty: <code>{}</code></li>'}</ol></div>`}).join('');
    const has='backup' in names;
    $('#tsPrint').innerHTML=`<div><code>print(trip)</code><code class="out">${esc(repr(sheets[names.trip]))}</code></div>
      <div><code>print(backup)</code><code class="out${has?'':' err'}">${has?esc(repr(sheets[names.backup])):"NameError: name 'backup' is not defined"}</code></div>
      <div><code>id(trip) == id(backup)</code><code class="out${has?'':' err'}">${has?(names.trip===names.backup?'True':'False'):'NameError'}</code></div>`;
  };
  $$('.tripsheets .vops button').forEach(b=>b.onclick=()=>{sfx.tap();
    if(b.dataset.i==='reset'){reset();return draw()}
    const [code,fn]=ACTS[+b.dataset.i],msg=fn();
    last=msg===null?[code,"<span class='bad'>backup does not exist yet: Python would stop with NameError.</span>"]:[code,msg];draw()});
  draw();
}
const CALL_DEFS=[
  {sig:'def split(bill, *friends):',body:'    print(bill, friends)',name:'split',tries:['1200, "Teja", "Ravi", "Kiran"','1200, "Sai"','1200','1200, ["Teja", "Ravi"]','1200, *["Teja", "Ravi"]']},
  {sig:'def mark_paid(**paid):',body:'    print(paid)',name:'mark_paid',tries:['Teja=1500, Ravi=800','','"Teja", 1500','**{"Teja": 1500, "Kiran": 0}']},
  {sig:'def room(name, block):',body:'    print(name, block)',name:'room',tries:['"Teja", "C"','block="C", name="Teja"','**{"block": "C", "name": "Teja"}','**{"student": "Teja", "block": "C"}']},
  {sig:'def student_info(*args, **kwargs):',body:'    print(args, kwargs)',name:'student_info',tries:["'Math', 'Science', 'Rahul', age='15'",'age=15','']},
];
function callsTab(){
  let d=CALL_DEFS[0];
  $('#labBody').innerHTML=`<div class="labgrid"><div class="card calls">
      <div class="seg2 wide calldefs" role="radiogroup" aria-label="Function">${CALL_DEFS.map((c,i)=>`<button type="button" role="radio" aria-pressed="${i===0}" aria-checked="${i===0}" data-i="${i}"><code>${esc(c.sig)}</code></button>`).join('')}</div>
      <div id="callCode"></div>
      <label class="callin"><span>Arguments in the call</span><input id="callArgs" autocomplete="off" autocapitalize="off" spellcheck="false" maxlength="120"></label>
      <div class="vtools" id="callTries"></div>
      <div class="power-row"><button class="btn primary" id="callRun" type="button">${ICON.play}Run the call</button><span class="pystate" id="callPy">Python: loading…</span></div>
      <div id="callOut"></div></div>
    <div class="card"><h4>Experiments to try</h4><ol class="exp">
      <li><code>split</code> with three names, one name, and none. What is friends each time?</li>
      <li><code>split(1200, ["Teja", "Ravi"])</code>, then with a <code>*</code> before the list.</li>
      <li><code>mark_paid</code> with names and amounts, then with plain values.</li>
      <li><code>room(**data)</code> with the keys in any order, then with a key called student.</li></ol>
      <p class="muted small">This runs real Python in your browser. Nothing here is graded.</p></div></div>`;
  const inp=$('#callArgs');
  const show=()=>{$('#callCode').innerHTML=codePanel(`${d.sig}\n${d.body}\n\n${d.name}(${inp.value})`,{file:'call.py'});
    $('#callTries').innerHTML=d.tries.map(t=>`<button class="btn ghost" type="button" data-t="${esc(t)}"><code>${esc(d.name)}(${esc(t)})</code></button>`).join('');
    $$('#callTries button').forEach(b=>b.onclick=()=>{inp.value=b.dataset.t;show();run()})};
  $$('.calldefs button').forEach(b=>b.onclick=()=>{d=CALL_DEFS[+b.dataset.i];$$('.calldefs button').forEach(x=>{x.setAttribute('aria-pressed',x===b);x.setAttribute('aria-checked',x===b)});inp.value=d.tries[0];$('#callOut').innerHTML='';sfx.tap();show()});
  inp.oninput=show;inp.onkeydown=e=>{if(e.key==='Enter'){e.preventDefault();e.stopPropagation();run()}};
  async function run(){
    const args=inp.value,b=$('#callRun');b.disabled=true;$('#callPy').textContent=PYR.ready?'running':'loading Python…';
    // Python's own binder says where each argument lands; then the call itself runs.
    const code=`${d.sig}\n${d.body}\n\nimport inspect as __i\ntry:\n    for __k, __v in __i.signature(${d.name}).bind(${args}).arguments.items():\n        print("@@" + __k + "\\t" + repr(__v))\nexcept TypeError as __e:\n    print("@@!" + str(__e))\nprint("@@--")\n${d.name}(${args})`;
    const r=await PYR.run(code,'');b.disabled=false;$('#callPy').textContent='real Python';$('#callPy').className='pystate ok';
    const lines=(r.stdout||'').split('\n'),landed=[],out=[];let after=false,bindErr=null;
    lines.forEach(l=>{if(l.startsWith('@@--')){after=true;return}if(!after&&l.startsWith('@@!')){bindErr=l.slice(3);return}if(!after&&l.startsWith('@@')){const [k,v]=l.slice(2).split('\t');landed.push([k,v]);return}if(after)out.push(l)});
    const params=[...d.sig.matchAll(/(\*{0,2})(\w+)(?=[,)])/g)].filter(m=>m[2]!==d.name).map(m=>m[1]+m[2]);
    const val=p=>{const f=landed.find(([k])=>k===p.replace(/^\*+/,''));return f?f[1]:p.startsWith('**')?'{}':p.startsWith('*')?'()':'—'};
    $('#callOut').innerHTML=r.error&&r.error.type==='SyntaxError'?`<p class="vmsg bad">That is not a valid call: ${esc(r.error.msg)}</p>`
      :`<div class="lboxes result">${params.map(p=>{const [cls,desc]=boxKind(p);return `<div class="lbox ${cls}"><span class="lbhead"><code>${esc(p)}</code><small>${desc}</small></span><span class="lin"><code class="lgot">${esc(bindErr?'—':val(p))}</code></span></div>`}).join('')}</div>
        <div class="vres"><code class="vexpr">Prints</code><span class="veq">→</span><code class="vout${r.error?' err':''}">${r.error?esc(r.error.type+': '+r.error.msg):esc(out.join('\n').replace(/\n+$/,''))||'(nothing)'}</code></div>
        ${bindErr?`<p class="vmsg bad">No box for an argument, so Python stops before the function runs.</p>`:''}`;
    sfx.tap();
  }
  $('#callRun').onclick=run;inp.value=d.tries[0];show();
  PYR.start().then(()=>{const s=$('#callPy');if(s){s.textContent='Python ready';s.className='pystate ok'}}).catch(()=>{const s=$('#callPy');if(s){s.textContent='Python failed to load';s.className='pystate bad'}});
}

const PADS={mcq:q=>choicePad(q,false),predict:q=>choicePad(q,false),ar:q=>choicePad(q,false),msq:q=>choicePad(q,true),tf:padTF,numeric:padNumeric,fill:padFill,
  match:padMatch,order:padOrder,categorize:padCategorize,debug:padDebug,board:padBoard,land:padLand};

/* ---------- hints, checking, feedback ---------- */
async function showHint(silent){
  if(!Q||Q.done)return;
  const hb=$('#hint');if(hb){hb.disabled=true;hb.classList.remove('nudge')}
  try{const r=await api('POST','/hint',{qid:Q.q.id});Q.hint=true;
    $('#hintSlot').innerHTML=`<div class="hintbox"><span class="hconcept">${ICON.bulb}Concept: <b>${esc(CONCEPTS[r.concept]||r.concept)}</b></span>${r.hints.map((h,i)=>`<p><b>Hint${r.hints.length>1?' '+(i+1):''}:</b> ${h}</p>`).join('')}
      <button class="linkbtn" type="button" id="hGuide">Review this concept in the field guide</button>${silent?'':'<small>Hints lower this challenge\'s XP a little. Understanding the idea is worth more.</small>'}</div>`;
    $('#hGuide').onclick=openGuide;
    if(hb){hb.disabled=!r.more;hb.innerHTML=ICON.bulb+(r.more?'Another hint':'Hint')}
    if(!silent)sfx.tap();
  }catch(e){if(hb)hb.disabled=false;netError(e)}
}
async function check(){
  if(!Q||Q.busy||Q.done)return;const ans=Q.get();if(ans===null||ans===undefined)return;
  Q.busy=true;const cb=$('#check');cb.disabled=true;cb.classList.add('busy');$('.qside').classList.add('locked');
  let r;
  try{r=await api('POST','/answer',{qid:Q.q.id,answer:ans})}
  catch(e){Q.busy=false;cb.disabled=false;cb.classList.remove('busy');$('.qside').classList.remove('locked');return netError(e)}
  Q.busy=false;cb.classList.remove('busy');$('.qside').classList.remove('locked');
  if(r.timed_out){Q.done=true;stopQTimer();adopt(r.state);try{Q.solve(r.solution)}catch(e){}return openTimeUp(r)}
  afterResult(r,cb);
}
function afterResult(r,fromEl){
  adopt(r.state);
  try{Q.mark(r)}catch(e){}
  $('.segs')&&($('.segs').innerHTML=segsHTML(Q.q.id));
  if(r.correct){
    Q.done=true;stopQTimer();$('#qtimer')?.classList.add('stopped');$$('#check,#hint,#revealBtn').forEach(b=>b.disabled=true);
    sfx.good(r.combo);
    if(r.xp){floatXP(fromEl,r.xp);rollXP()}
    if(r.focus)focusLine(Q.panel,r.focus,'the key line');
    if([3,5,8].includes(r.combo))toast(`Combo ×${r.combo}!`);
  }else{
    Q.wrong++;sfx.bad();refreshActions();
    const g=$('.qgrid')||$('.cgrid');if(g&&!reduce){g.classList.remove('shake');void g.offsetWidth;g.classList.add('shake')}
  }
  celebrateBadges(r.new_badges);
  openFeedback(r);
}
function celebrateBadges(list){
  (list||[]).forEach(id=>{const b=M.badges[id];if(!b)return;if(R)R.badges.push(id);toast('Badge: '+b.name,'rank');sfx.win();burst(innerWidth/2,innerHeight*.3,70,1.2)});
}
function wrongMessage(r){
  const d=r.detail||{},t=Q.q.type;
  if(d.why_wrong)return d.why_wrong;
  if(t==='msq')return `Close. ${d.missing?`You missed ${d.missing} correct option${d.missing>1?'s':''}`:''}${d.missing&&d.extra?' and ':''}${d.extra?`${d.extra} of your picks ${d.extra>1?'are':'is'} not correct`:''}. Remember: <b>select every</b> correct option.`;
  if(t==='match'||t==='categorize')return `${d.right_count} of ${(d.per_item||[]).length} are right. Look again at the ones marked red.`;
  if(t==='order')return `${d.right_count} of ${Q.q.items.length} lines are in the right place. Ask: which line needs another line to exist first?`;
  if(t==='debug')return d.line_ok?'You found the right line, but that is not what goes wrong there.':d.error_ok?'Right error type, but look again at which line causes it.':'Trace the code one line at a time. Where does it first go wrong?';
  if(t==='fill')return 'One or more gaps are not right yet. They are marked red in the code.';
  if(t==='board')return 'The board is not right yet. The red rows show what is off. A changed key keeps its place; a new key goes to the end.';
  if(t==='tf')return 'Not quite. Test the statement on a tiny board of two items.';
  if(t==='numeric')return 'Not that number. Write the board down after each line, then count.';
  if(t==='coding'){const tests=d.tests||[],pass=tests.filter(x=>x.passed).length,f=tests.find(x=>!x.passed);
    return `${pass} of ${tests.length} tests passed.${f?` ${f.hidden?'A hidden test':'A sample test'} failed${f.note?` (${esc(f.note)})`:''}.`:''}${f&&f.error?` Your code raised <code>${esc(f.error)}</code>.`:''}`}
  return 'Not quite. Trace it once more.';
}
function openFeedback(r){
  const ok=r.correct,q=Q.q,parts=r.xp_parts||{};
  const xpLine=ok?(r.already_solved?'<span class="muted">Already cleared · no extra XP</span>':
    `<span>+${r.xp} XP</span>${parts.clean?`<span class="chipx">+${parts.clean} first try</span>`:''}${parts.combo?`<span class="chipx combo">+${parts.combo} combo</span>`:''}${qs(q.id).wrong?'<span class="chipx">comeback</span>':''}${Q.hint?'<span class="chipx mute">hint used</span>':''}`):'';
  const canRun=q.code&&['predict','numeric','debug','fill'].includes(q.type);
  const wrongs=r.wrong_count||0,hintUsed=Q.hint||r.hint_used;
  const nextStep=r.can_reveal?`You have tried ${wrongs} times. Have one more go, or open the solution to learn how it works.`
    :hintUsed?'Your XP is safe. Read the hint again and have another go.':'<b>Open the hint.</b> It names the concept behind this question and points you in the right direction.';
  drawer.className='drawer '+(ok?'ok':'bad');
  drawer.innerHTML=`<div class="dr-in">
    <div class="dr-head"><span class="dr-icon">${ok?ICON.check:ICON.x}</span><div><h3>${ok?esc(pick(PRAISE[q.type]||PRAISE._)):'Not quite. Here is the catch.'}</h3>${ok?`<div class="dr-xp">${xpLine}</div>`:''}</div></div>
    <div class="dr-body">${ok?`<p>${r.explain||''}</p>${r.trap?`<div class="trap"><b>The trap</b><p>${r.trap}</p></div>`:''}`
      :`<p class="miscon">${wrongMessage(r)}</p><p class="nextstep">${ICON.bulb}<span>${nextStep}</span></p>`}</div>
    <div class="dr-act">${ok?`<button class="btn good" id="cont" type="button">${contLabel()}</button>${canRun?`<button class="btn ghost" id="runReal" type="button">${ICON.play}Run it in real Python</button>`:''}`
      :`${!hintUsed?`<button class="btn gold" id="dhint" type="button">${ICON.bulb}Show the hint</button>`:''}<button class="btn ${hintUsed?'badc':''}" id="retry" type="button">Try again</button>${r.can_reveal?'<button class="btn ghost" id="reveal" type="button">Show the solution</button>':''}`}</div></div>`;
  requestAnimationFrame(()=>drawer.classList.add('open'));
  const on=(id,fn)=>{const b=$('#'+id);if(b)b.onclick=fn};
  on('cont',()=>{sfx.tap();advance()});
  on('runReal',runReal);
  on('retry',()=>{closeDrawer();Q.reset();const f=$('#pad button,#pad input,.blank,#editor');if(f)f.focus()});
  on('dhint',()=>{closeDrawer();Q.reset();showHint()});
  on('reveal',revealSolution);
  setTimeout(()=>{const c=$('#cont')||$('#dhint')||$('#retry');if(c)c.focus({preventScroll:true})},80);
}
function solutionHTML(sol){
  const t=Q.q.type;
  if(sol.solution)return `<pre class="solcode">${esc(sol.solution)}</pre>`;
  if(t==='predict'&&sol.text)return `<div class="dr-ans"><b>Answer</b>${outHTML(sol.text)}</div>`;
  if(sol.text)return `<div class="dr-ans"><b>Answer</b><span>${esc(sol.text)}</span></div>`;
  if(sol.texts)return `<div class="dr-ans"><b>Answers</b><span>${sol.texts.map(x=>`<code>${esc(x)}</code>`).join(' · ')}</span></div>`;
  if(sol.error_text)return `<div class="dr-ans"><b>Answer</b><span>Line ${sol.line} · ${esc(sol.error_text)}</span></div>`;
  if(sol.value!==undefined)return `<div class="dr-ans"><b>Answer</b><span>${esc(String(sol.value===true?'True':sol.value===false?'False':sol.value))}</span></div>`;
  if(sol.blanks)return `<div class="dr-ans"><b>Answer</b><span>${sol.blanks.map(b=>`<code>${esc(b)}</code>`).join(' · ')}</span></div>`;
  return '<p class="muted">The correct answer is now marked on the question.</p>';
}
function openTimeUp(r){
  drawer.className='drawer bad shown timeup';
  drawer.innerHTML=`<div class="dr-in"><div class="dr-head"><span class="dr-icon">${ICON.clock.replace('class="i"','')}</span><div><h3>Time's up for this question</h3><div class="dr-xp"><span class="muted">No XP this time, but here is how it works, so you are ready for the next one.</span></div></div></div>
    <div class="dr-body">${solutionHTML(r.solution||{})}<p>${r.explain||''}</p>${r.trap?`<div class="trap"><b>The trap</b><p>${r.trap}</p></div>`:''}</div>
    <div class="dr-act"><button class="btn" id="cont" type="button">${contLabel()}</button>${Q.q.type==='coding'?'<button class="btn ghost" id="loadSol" type="button">Load the solution to try it</button>':''}</div></div>`;
  requestAnimationFrame(()=>drawer.classList.add('open'));
  $('#cont').onclick=advance;bindLoadSol(r.solution);
  setTimeout(()=>$('#cont').focus({preventScroll:true}),80);
}
async function runReal(){
  const q=Q.q;let code=q.code;
  if(q.type==='fill'){const ins=$$('input.blank',Q.panel);code=code.split('___').reduce((a,part,i)=>a+(ins[i-1]?ins[i-1].value:'')+part)}
  const panel=Q.panel;if(!$('.console',panel))panel.insertAdjacentHTML('beforeend','<div class="console"><div class="con-head"><span>Output</span><span class="con-state"></span></div><pre class="con-out"></pre></div>');
  const con=$('.console',panel),out=$('.con-out',panel),stt=$('.con-state',panel);con.hidden=false;out.textContent='';stt.textContent=PYR.ready?'running':'loading Python…';
  const b=$('#runReal');if(b)b.disabled=true;
  const r=await PYR.run(code,'');stt.textContent='real Python';if(b)b.disabled=false;
  out.innerHTML=consoleHTML(r);
  if(!matchMedia('(min-width: 981px)').matches)panel.scrollIntoView({behavior:reduce?'auto':'smooth',block:'center'});
}
async function revealSolution(){
  let r;try{r=await api('POST','/reveal',{qid:Q.q.id})}catch(e){return netError(e)}
  adopt(r.state);Q.done=true;Q.revealed=true;stopQTimer();$('#qtimer')?.classList.add('stopped');try{Q.solve(r.solution)}catch(e){}
  $('.segs')&&($('.segs').innerHTML=segsHTML(Q.q.id));$$('#check,#hint,#revealBtn').forEach(b=>b&&(b.disabled=true));
  celebrateBadges(r.new_badges);
  drawer.className='drawer bad shown';
  drawer.innerHTML=`<div class="dr-in"><div class="dr-head"><span class="dr-icon">${ICON.bulb.replace('class="i"','')}</span><div><h3>Here is how it works</h3><div class="dr-xp"><span class="muted">Solution shown · no XP for this one, but the stage still counts it as cleared</span></div></div></div>
    <div class="dr-body">${solutionHTML(r.solution||{})}<p>${r.explain}</p>${r.trap?`<div class="trap"><b>The trap</b><p>${r.trap}</p></div>`:''}</div>
    <div class="dr-act"><button class="btn" id="cont" type="button">${contLabel()}</button>${Q.q.type==='coding'?'<button class="btn ghost" id="loadSol" type="button">Load into editor and try it</button>':''}</div></div>`;
  requestAnimationFrame(()=>drawer.classList.add('open'));
  $('#cont').onclick=advance;bindLoadSol(r.solution);
  setTimeout(()=>$('#cont').focus({preventScroll:true}),80);
}
function bindLoadSol(sol){
  const ls=$('#loadSol');if(!ls||!sol||!sol.solution)return;
  // The question is closed, but the learner can still run the reference solution against every test (no XP).
  ls.onclick=()=>{const ta=$('#editor');if(!ta)return;ta.value=sol.solution;ta.dispatchEvent(new Event('input'));Q.revealed=true;
    $$('.cwork').forEach(x=>x.classList.remove('locked'));const s=$('#submit');if(s){s.disabled=!PYR.ready;s.textContent='Run all tests (practice)'}const rs=$('#runS');if(rs)rs.disabled=!PYR.ready;
    if(!$('#nextAfter')){$('#actions').insertAdjacentHTML('beforeend','<button class="btn good" id="nextAfter" type="button">Continue to the next challenge</button>');$('#nextAfter').onclick=advance}
    closeDrawer();ta.focus()};
}
function advance(){
  if(!R)return renderMap();
  const id=Q.q.id;R.queue=R.queue.filter(x=>x!==id);
  nextQ();
}
function closeDrawer(){drawer.classList.remove('open')}
const contLabel=()=>'Continue';

/* ---------- coding challenge ---------- */
function renderCoding(q){
  const ch=q.challenge,st=qs(q.id);let draft=null;try{draft=localStorage.getItem(API.key('draft-'+q.id))}catch(e){}
  Q={q,done:false,busy:false,revealed:false,hint:!!st.hint,wrong:st.wrong||0,reset(){},mark(){},solve(){}};
  const samples=ch.tests.filter(t=>!t.hidden),hidden=ch.tests.filter(t=>t.hidden).length;
  view.innerHTML=`${qtopHTML(q)}
  <section class="cgrid enter" data-qid="${esc(q.id)}">
    <div class="cprob">
      <span class="qchip boss">${R.replay?'Replay · no XP · ':''}Coding milestone${R.replay?'':` · ${q.xp} XP`}</span>
      <h2 class="qtitle" id="qtitle">${esc(ch.title)}</h2>
      ${howtoHTML('coding')}
      <p class="stmt">${ch.statement}</p>
      <dl class="io"><dt>Input</dt><dd>${ch.input_fmt}</dd><dt>Output</dt><dd>${ch.output_fmt}</dd></dl>
      <h4 class="sub">Sample tests</h4>
      <div class="samples">${samples.map(t=>`<div class="sample"><div><small>Input</small><pre>${esc(t.stdin)||'<i>(empty line)</i>'}</pre></div><div><small>Expected output</small><pre>${esc(t.expected)}</pre></div></div>`).join('')}</div>
      <p class="muted small">${hidden} hidden edge-case test${hidden>1?'s':''} also run when you submit. Output is checked exactly, line by line: dictionaries keep insertion order, so the order you print in matters. Paste is turned off: type your solution.</p>
      <div id="hintSlot" aria-live="polite"></div>
    </div>
    <div class="cwork">
      <div class="code editor"><div class="code-bar"><span class="dots"><i></i><i></i><i></i></span><span>main.py</span><span class="pystate" id="pystate">Python: loading…</span></div>
        <div class="ed"><pre class="gutter" id="gutter" aria-hidden="true"></pre><textarea id="editor" spellcheck="false" autocapitalize="off" autocomplete="off" aria-label="Code editor. Tab indents, Control+Enter runs the samples." wrap="off"></textarea></div>
        <div class="console"><div class="con-head"><span>Output</span><span class="con-state" id="cstate"></span></div><pre class="con-out" id="cout"><span class="con-note">Run your code to see its output here.</span></pre></div></div>
      <div class="actions" id="actions">${actionsHTML()}<button class="btn ghost" id="resetCode" type="button">Reset code</button><button class="btn" id="runS" type="button" disabled>${ICON.play}Run samples</button><button class="btn primary" id="submit" type="button" disabled>Submit all tests</button></div>
      <div class="tests" id="ctests"><h5><span>Tests</span><span id="tscore">0 / ${ch.tests.length}</span></h5>${ch.tests.map((t,i)=>`<div class="test" data-i="${i}"><span class="st"></span><span>${t.hidden?`Hidden test ${i+1-samples.length}`:`Sample ${i+1}`}</span><span class="exp">${t.hidden?'runs on submit':esc(t.stdin.replace(/\n/g,' / '))||'(empty)'}</span></div>`).join('')}</div>
    </div>
  </section>`;
  const ta=$('#editor'),gut=$('#gutter');
  ta.value=draft||ch.starter;
  const sync=()=>{const n=ta.value.split('\n').length;gut.textContent=Array.from({length:n},(_,i)=>i+1).join('\n');gut.scrollTop=ta.scrollTop;try{localStorage.setItem(API.key('draft-'+q.id),ta.value)}catch(e){}};
  ta.oninput=sync;ta.onscroll=()=>{gut.scrollTop=ta.scrollTop};sync();
  ta.onkeydown=e=>{
    if(e.key==='Tab'&&!e.shiftKey){e.preventDefault();ta.setRangeText('    ',ta.selectionStart,ta.selectionEnd,'end');sync()}
    else if(e.key==='Enter'&&(e.ctrlKey||e.metaKey)){e.preventDefault();runSamples()}
    else if(e.key==='Enter'){const s=ta.selectionStart,line=ta.value.slice(0,s).split('\n').pop(),ind=line.match(/^ */)[0]+(/:\s*$/.test(line)?'    ':'');e.preventDefault();ta.setRangeText('\n'+ind,s,ta.selectionEnd,'end');sync()}
    e.stopPropagation();
  };
  $('#quit').onclick=renderMap;bindActions();
  $('#resetCode').onclick=()=>{ta.value=ch.starter;sync();ta.focus()};
  $('#runS').onclick=runSamples;$('#submit').onclick=submitCode;
  if(Q.hint)showHint(true);
  const pys=$('#pystate');
  const bootPy=()=>{pys.textContent='Python: loading…';pys.className='pystate';
    PYR.start().then(()=>{if(!$('#pystate'))return;pys.textContent='Python ready';pys.className='pystate ok';$('#runS').disabled=false;$('#submit').disabled=Q.done&&!Q.revealed})
      .catch(()=>{if(!$('#pystate'))return;pys.innerHTML='Python failed to load <button type="button" class="linkbtn" id="pyRetry">Retry</button>';pys.className='pystate bad';
        $('#cout').innerHTML=`<span class="con-err">The in-browser Python runner could not load.</span>\n<span class="con-note">Check the connection to the app, then press Retry.</span>`;
        $('#pyRetry').onclick=bootPy})};
  bootPy();
  window.scrollTo(0,0);
  startQTimer(q);
}
function showOut(r,label){const out=$('#cout');if(out)out.innerHTML=(label?`<span class="con-note">${esc(label)}</span>\n`:'')+consoleHTML(r)}
function setRow(i,state,extra){const row=$(`#ctests .test[data-i="${i}"]`);if(!row)return;row.classList.remove('pass','fail','run');if(state)row.classList.add(state);
  $('.st',row).innerHTML=state==='pass'?ICON.check:state==='fail'?ICON.x:'';const g=$('.got',row);if(g)g.remove();if(extra)$('.exp',row).insertAdjacentHTML('beforeend',`<span class="got${state==='pass'?' note':''}">${extra}</span>`)}
async function runSamples(){
  if(!Q||Q.busy)return;const ch=Q.q.challenge,code=$('#editor').value;Q.busy=true;$('#runS').disabled=true;$('#cstate').textContent='running samples';
  let first=null;
  for(let i=0;i<ch.tests.length;i++){const t=ch.tests[i];if(t.hidden)continue;setRow(i,'run');
    const r=await PYR.run(code,t.stdin);if(!first)first=r;const ok=!r.error&&sameOutput(r.stdout,t.expected,ch.compare);
    setRow(i,ok?'pass':'fail',ok?'':r.error?esc(r.error.type):'printed: '+esc(outLines(r.stdout).join(' / ')||'nothing'));ok?sfx.pass():sfx.fail();if(r.error&&r.error.type==='RunnerUnavailable')break}
  showOut(first||{stdout:'',error:null},'Sample 1 output:');$('#cstate').textContent='sample check (not graded)';
  Q.busy=false;$('#runS').disabled=false;
}
async function submitCode(){
  if(!Q||Q.busy||(Q.done&&!Q.revealed))return;const ch=Q.q.challenge,code=$('#editor').value,btn=$('#submit');
  Q.busy=true;btn.disabled=true;$('#runS').disabled=true;btn.classList.add('busy');
  const outputs=[];let first=null;
  const unlock=()=>{Q.busy=false;btn.disabled=false;btn.classList.remove('busy');$('#runS').disabled=false};
  for(let i=0;i<ch.tests.length;i++){setRow(i,'run');$('#cstate').textContent=`running test ${i+1} of ${ch.tests.length}`;
    const r=await PYR.run(code,ch.tests[i].stdin);if(r.error&&r.error.type==='RunnerUnavailable'){showOut(r);unlock();setRow(i,'');return}
    if(!first)first=r;outputs.push({stdout:r.stdout||'',error:r.error||null})}
  if(Q.revealed){
    // Practice run after the question closed: check locally against the sample tests, no XP, nothing sent.
    ch.tests.forEach((t,i)=>{if(t.hidden){setRow(i,'',`<span class="muted">checked on submit only</span>`);return}const ok=!outputs[i].error&&sameOutput(outputs[i].stdout,t.expected,ch.compare);setRow(i,ok?'pass':'fail')});
    $('#cstate').textContent='practice run (no XP)';showOut(first||{stdout:'',error:null},'Sample 1 output:');unlock();return;
  }
  let res;
  try{res=await API.call('POST','/dicts/answer',{qid:Q.q.id,answer:{outputs},code:code.slice(0,8000)})}
  catch(e){unlock();ch.tests.forEach((_,i)=>setRow(i,''));return netError(e)}
  Q.busy=false;btn.classList.remove('busy');$('#runS').disabled=false;
  if(res.timed_out){Q.done=true;stopQTimer();adopt(res.state);ch.tests.forEach((_,i)=>setRow(i,''));return openTimeUp(res)}
  const tests=(res.detail&&res.detail.tests)||[];let pass=0;
  for(let i=0;i<tests.length;i++){const t=tests[i];if(t.passed)pass++;setRow(i,t.passed?'pass':'fail',[t.note?esc(t.note):'',t.error?esc(t.error):''].filter(Boolean).join(' · '));
    if(!reduce)await new Promise(r=>setTimeout(r,90));t.passed?sfx.pass():sfx.fail()}
  $('#tscore').textContent=`${pass} / ${tests.length}`;$('#cstate').textContent='graded on the server';
  showOut(first||{stdout:'',error:null},'Sample 1 output:');
  if(!res.correct)btn.disabled=false;
  afterResult(res,btn);
}

/* ---------- canteen board: Board build (graded) + Dict Lab (free play) ---------- */
// One row per pair: a name tag (key) and a price card (value). No index numbers anywhere: rows are found by name.
const DECK_BOARD=[['tea',12],['coffee',15],['samosa',15],['puff',20],['maggi',30]];
const pyStr=v=>typeof v==='number'?String(v):`'${String(v).replace(/\\/g,'\\\\').replace(/'/g,"\\'")}'`;
const fmtDict=rows=>rows.length?'{'+rows.map(([k,v])=>`${pyStr(k)}: ${v}`).join(', ')+'}':'{}';
let boardSeq=0;
function boardHTML(mode){
  const k=++boardSeq,lab=mode==='lab';
  return `<div class="board${lab?' lab':''}" data-k="${k}">
    <div class="bhead"><span class="bname">menu</span><span class="bcount" aria-live="polite"></span></div>
    <ol class="brows" aria-label="The canteen price board"></ol>
    <div class="vin bin">
      <label><span>Key · name</span><input data-f="k" placeholder="e.g. samosa" maxlength="16" autocomplete="off" autocapitalize="off" spellcheck="false"></label>
      <label><span>Value · price</span><input data-f="v" placeholder="e.g. 15" maxlength="4" inputmode="numeric" autocomplete="off"></label>
    </div>
    <div class="vops bops" role="group" aria-label="Change the board">
      <button type="button" data-a="set"><code>menu[key] = value</code></button>
      <button type="button" data-a="del"><code>del menu[key]</code></button>
      <button type="button" data-a="reset">Start over</button>
    </div>
    <div class="vres bpy" aria-live="polite"><code class="vexpr bline">menu</code><span class="veq">→</span><code class="vout bres"></code></div>
    <div class="vres bout"><code class="vexpr">print(menu)</code><span class="veq">→</span><code class="vout bprint"></code></div>
    <p class="vmsg" aria-live="polite"></p>
    ${lab?`<div class="blab">
      <h5 class="sub">Look up a key</h5>
      <div class="vin bin one"><label><span>Key to look up</span><input data-f="q" placeholder="e.g. dosa, Tea or 15" maxlength="16" autocomplete="off" autocapitalize="off" spellcheck="false"></label></div>
      <div class="vops" role="group" aria-label="Look up">
        <button type="button" data-l="br"><code>menu[key]</code></button><button type="button" data-l="get"><code>menu.get(key)</code></button><button type="button" data-l="in"><code>key in menu</code></button>
      </div>
      <h5 class="sub">Views: live or a copy?</h5>
      <div class="vnote seg2" role="radiogroup" aria-label="View method">${['keys','values','items'].map((m,i)=>`<button type="button" role="radio" aria-checked="${i===0}" aria-pressed="${i===0}" data-m="${m}">${m}()</button>`).join('')}</div>
      <div class="bviews">
        <div><small class="bvl">view = menu.keys() · live</small><code class="bview"></code></div>
        <div><small class="bpl">photo = list(menu.keys()) · copy</small><code class="bphoto">not taken yet</code></div>
      </div>
      <div class="vtools"><button class="btn ghost" type="button" data-t="photo">Take a list() copy</button><button class="btn ghost" type="button" data-t="dup">Write tea twice</button><button class="btn ghost" type="button" data-t="clear">Start from {}</button></div>
    </div>`:''}
  </div>`;
}
function Board(root,opts){
  opts=opts||{};let locked=false,method='keys',photo=null;const start=(opts.start||[]).map(r=>r.slice());
  const self={rows:start.map(r=>r.slice())};
  const has=k=>self.rows.findIndex(r=>r[0]===k);
  const kIn=$('[data-f="k"]',root),vIn=$('[data-f="v"]',root),qIn=$('[data-f="q"]',root);
  // what the learner typed into a lookup box: digits are a number key (15), anything else a string key ('dosa')
  const tok=s=>{s=String(s).trim();const m=s.match(/^(['"])(.*)\1$/);if(m)return m[2];return /^-?\d{1,6}$/.test(s)?Number(s):s};
  function msg(t,cls){const m=$('.vmsg',root);m.innerHTML=t;m.className='vmsg'+(cls?' '+cls:'')}
  function py(line,res,err){$('.bline',root).textContent=line;const o=$('.bres',root);o.textContent=res;o.classList.toggle('err',!!err)}
  const view=()=>method==='keys'?`dict_keys([${self.rows.map(r=>pyStr(r[0])).join(', ')}])`:method==='values'?`dict_values([${self.rows.map(r=>r[1]).join(', ')}])`:`dict_items([${self.rows.map(r=>`(${pyStr(r[0])}, ${r[1]})`).join(', ')}])`;
  const snap=()=>method==='keys'?`[${self.rows.map(r=>pyStr(r[0])).join(', ')}]`:method==='values'?`[${self.rows.map(r=>r[1]).join(', ')}]`:`[${self.rows.map(r=>`(${pyStr(r[0])}, ${r[1]})`).join(', ')}]`;
  function paint(flash){
    $('.brows',root).innerHTML=self.rows.map(([k,v])=>`<li class="brow${flash&&flash.k===k?' '+flash.c:''}"><button type="button" class="btag" data-k="${esc(k)}" aria-label="Load ${esc(pyStr(k))} into the boxes">${esc(k)}</button><span class="barrow" aria-hidden="true">→</span><span class="bprice">${v}</span>${locked?'':`<button type="button" class="bdel" data-k="${esc(k)}" aria-label="del menu[${esc(pyStr(k))}]">${ICON.x}</button>`}</li>`).join('')
      ||'<li class="bempty">The board is empty: <code>{}</code></li>';
    $('.bcount',root).textContent=`len(menu) = ${self.rows.length}`;
    $('.bprint',root).textContent=fmtDict(self.rows);
    if(opts.lab){$('.bview',root).textContent=view();$('.bvl',root).textContent=`view = menu.${method}() · live`}
    $$('.btag',root).forEach(b=>b.onclick=()=>{if(locked)return;const i=has(b.dataset.k);kIn.value=self.rows[i][0];vIn.value=self.rows[i][1];sfx.tap();vIn.focus()});
    $$('.bdel',root).forEach(b=>b.onclick=()=>{kIn.value=b.dataset.k;del()});
  }
  const changed=()=>opts.onChange&&opts.onChange();
  function set(){
    if(locked)return;const k=kIn.value.trim().replace(/^(['"])(.*)\1$/,'$2'),v=vIn.value.trim();
    if(!k){msg('Type a key (the name) first.','warn');kIn.focus();return}
    if(!/^[A-Za-z][A-Za-z0-9_ ]{0,15}$/.test(k)){msg('Names on this board start with a letter: letters, digits and spaces only.','warn');return}
    if(!/^\d{1,4}$/.test(v)){msg('Type a whole-number price for the value.','warn');vIn.focus();return}
    const n=Number(v),i=has(k),line=`menu[${pyStr(k)}] = ${n}`;
    if(i>=0){const old=self.rows[i][1];self.rows[i][1]=n;py(line,fmtDict(self.rows));
      msg(old===n?`${esc(pyStr(k))} already costs ${n}. Same key, same value: nothing changes.`:`${esc(pyStr(k))} is already a key, so its value changes <b>in place</b> (${old} → ${n}). No second row.`);paint({k,c:'chg'})}
    else{if(self.rows.length>=10){msg('This board holds 10 rows for the demo.','warn');return}
      const twin=self.rows.find(r=>r[0].toLowerCase()===k.toLowerCase());
      self.rows.push([k,n]);py(line,fmtDict(self.rows));
      msg(twin?`${esc(pyStr(k))} is a <b>new key</b>: keys are case-sensitive, so ${esc(pyStr(twin[0]))} and ${esc(pyStr(k))} are two rows.`:`New key: the pair goes on at the <b>end</b> of the board.`);paint({k,c:'new'})}
    sfx.tap();kIn.value='';vIn.value='';kIn.focus();changed();
  }
  function del(){
    if(locked)return;const k=kIn.value.trim().replace(/^(['"])(.*)\1$/,'$2');if(!k){msg('Type the key to delete, or tap its ✕.','warn');kIn.focus();return}
    const i=has(k),line=`del menu[${pyStr(k)}]`;
    if(i<0){py(line,`KeyError: ${pyStr(k)}`,true);msg(`${esc(pyStr(k))} is not a key, so <code>del</code> raises <b>KeyError</b> and Python stops. The board does not change.`,'bad');sfx.bad();return}
    self.rows.splice(i,1);py(line,fmtDict(self.rows));msg(`The whole pair is gone. If ${esc(pyStr(k))} is added again, it goes to the end.`);
    sfx.tap();kIn.value='';vIn.value='';paint();changed();
  }
  function look(kind){
    const raw=qIn.value;if(!raw.trim()){msg('Type a key to look up.','warn');qIn.focus();return}
    const k=tok(raw),i=typeof k==='string'?has(k):-1,isVal=self.rows.some(r=>r[1]===k);
    if(kind==='br'){if(i>=0){py(`menu[${pyStr(k)}]`,String(self.rows[i][1]));msg('Found by its key.')}else{py(`menu[${pyStr(k)}]`,`KeyError: ${pyStr(k)}`,true);msg(`Square brackets with a missing key raise <b>KeyError</b> and the program <b>stops</b>.${typeof k==='number'?' Brackets hold a key, never a position.':''}`,'bad');sfx.bad();return}}
    else if(kind==='get'){py(`menu.get(${pyStr(k)})`,i>=0?String(self.rows[i][1]):'None');msg(i>=0?'Found by its key.':'<code>get()</code> gives <b>None</b> for a missing key, and the program carries on.')}
    else{py(`${pyStr(k)} in menu`,i>=0?'True':'False');msg(i>=0?'<code>in</code> found the key.':isVal?`${esc(pyStr(k))} is a <b>value</b> on the board, but <code>in</code> checks <b>keys only</b>.`:'<code>in</code> checks the keys. This one is not on the board.')}
    sfx.tap();
  }
  $$('[data-a]',root).forEach(b=>b.onclick=()=>{const a=b.dataset.a;if(a==='set')set();else if(a==='del')del();else if(!locked){self.rows=start.map(r=>r.slice());py('menu',fmtDict(self.rows));msg('Back to the starting board.');sfx.tap();paint();changed()}});
  [kIn,vIn].forEach(inp=>inp.onkeydown=e=>{if(e.key==='Enter'){e.preventDefault();e.stopPropagation();if(inp===kIn&&!vIn.value)vIn.focus();else set()}});
  if(opts.lab){
    qIn.onkeydown=e=>{if(e.key==='Enter'){e.preventDefault();e.stopPropagation();look('get')}};
    $$('[data-l]',root).forEach(b=>b.onclick=()=>look(b.dataset.l));
    $$('[data-m]',root).forEach(b=>b.onclick=()=>{method=b.dataset.m;$$('[data-m]',root).forEach(x=>{x.setAttribute('aria-checked',x===b);x.setAttribute('aria-pressed',x===b)});
      photo=null;$('.bphoto',root).textContent='not taken yet';$('.bpl',root).textContent=`photo = list(menu.${method}()) · copy`;sfx.tap();paint()});
    $$('[data-t]',root).forEach(b=>b.onclick=()=>{const t=b.dataset.t;sfx.tap();
      if(t==='photo'){photo=snap();$('.bphoto',root).textContent=photo;$('.bpl',root).textContent=`photo = list(menu.${method}()) · copy`;msg('Copy taken. Now change the board and watch which one follows.')}
      else if(t==='dup'){self.rows=[['tea',14],['coffee',15]];py('menu = {"tea": 12, "coffee": 15, "tea": 14}',fmtDict(self.rows));msg('No error. A key can appear only once: the <b>last value wins</b> (14) and tea keeps its <b>first position</b>.');paint()}
      else{self.rows=[];py('menu = {}',"{}");msg('<code>{}</code> is an empty <b>dictionary</b>, not a set. <code>dict()</code> makes one too.');paint()}});
  }
  self.lock=()=>{locked=true;root.classList.add('locked');$$('input,[data-a],.bdel',root).forEach(x=>x.disabled=true);paint()};
  self.load=rows=>{self.rows=rows.map(r=>r.slice());py('menu',fmtDict(self.rows));paint()};
  py('menu',fmtDict(self.rows));paint();
  return self;
}
/* ---------- Python Lab: free play in real Python, for missions without a visual lab (UI lab: "py") ---------- */
function renderPyLab(){
  R=null;Q=null;stopQTimer();closeDrawer();
  const tips=M.ui.lab_tips||[];let code=M.ui.lab_starter||'';try{code=localStorage.getItem(API.key('lab-code'))??code}catch(e){}
  view.innerHTML=`<section class="lab enter">${backBar('Back to mission map','quit')}<h2 class="labtitle">${esc(M.ui.lab_name)} <small>free play</small></h2>
    <div class="labgrid"><div class="code editor"><div class="code-bar"><span class="dots"><i></i><i></i><i></i></span><span>lab.py</span><span class="pystate">${PYR.ready?'real Python':'Python loads on the first run'}</span></div>
      <div class="ed"><pre class="gutter" id="plGut" aria-hidden="true"></pre><textarea id="plCode" spellcheck="false" autocapitalize="off" autocomplete="off" wrap="off" aria-label="Lab code. Tab indents, Control+Enter runs."></textarea></div>
      <div class="plbar"><button class="btn primary" id="plRun" type="button">${ICON.play}Run</button><button class="btn ghost" id="plReset" type="button">Start again</button>
        <label class="plin"><span>Input for input(), one line each</span><textarea id="plIn" rows="2" spellcheck="false"></textarea></label></div>
      <div class="console"><div class="con-head"><span>Output</span><span class="con-state" id="plState"></span></div><pre class="con-out" id="plOut"><span class="con-note">Press Run to see what Python prints.</span></pre></div></div>
    <div class="card"><h4>Experiments to try</h4>${tips.length?`<ol class="exp">${tips.map(t=>`<li>${t}</li>`).join('')}</ol>`:'<p class="muted">Change the code, press Run, and check your guess.</p>'}
      <p class="muted small">The Lab is free play: nothing here is graded. The mission clock keeps running.</p></div></div></section>`;
  const ta=$('#plCode'),gut=$('#plGut');ta.value=code;
  const sync=()=>{gut.textContent=Array.from({length:ta.value.split('\n').length},(_,i)=>i+1).join('\n');gut.scrollTop=ta.scrollTop;try{localStorage.setItem(API.key('lab-code'),ta.value)}catch(e){}};
  const run=async()=>{const b=$('#plRun');b.disabled=true;$('#plState').textContent=PYR.ready?'running':'loading Python…';
    const r=await PYR.run(ta.value,$('#plIn').value);if(!$('#plOut'))return;
    $('#plState').textContent='real Python';$('#plOut').innerHTML=consoleHTML(r);b.disabled=false};
  ta.oninput=sync;ta.onscroll=()=>{gut.scrollTop=ta.scrollTop};sync();
  ta.onkeydown=e=>{
    if(e.key==='Tab'&&!e.shiftKey){e.preventDefault();ta.setRangeText('    ',ta.selectionStart,ta.selectionEnd,'end');sync()}
    else if(e.key==='Enter'&&(e.ctrlKey||e.metaKey)){e.preventDefault();run()}
    else if(e.key==='Enter'){const st=ta.selectionStart,line=ta.value.slice(0,st).split('\n').pop(),ind=line.match(/^ */)[0]+(/:\s*$/.test(line)?'    ':'');e.preventDefault();ta.setRangeText('\n'+ind,st,ta.selectionEnd,'end');sync()}
    e.stopPropagation();
  };
  $('#plRun').onclick=run;
  $('#plReset').onclick=()=>{ta.value=M.ui.lab_starter||'';sync();$('#plOut').innerHTML='<span class="con-note">Press Run to see what Python prints.</span>'};
  $('#quit').onclick=renderMap;window.scrollTo(0,0);mark('lab');preloadPython();
}
function renderLab(){
  if(needSurvey())return renderSurvey();
  if(M.ui.lab==='trip')return renderTripLab();
  if(M.ui.lab==='py')return renderPyLab();
  R=null;Q=null;stopQTimer();closeDrawer();
  view.innerHTML=`<section class="lab enter">${backBar('Back to mission map','quit')}<h2 class="labtitle">Dict Lab <small>free play</small></h2>
    <div class="labgrid"><div>${boardHTML('lab')}</div>
    <div class="card"><h4>Experiments to try</h4><ol class="exp">
      <li>Give <code>tea</code> a new price. Does a second tea row appear?</li>
      <li>Add <code>Tea</code> with a capital T. Same key, or a new row?</li>
      <li>Look up <code>dosa</code> with <code>menu[key]</code>, then with <code>get()</code>. What is different?</li>
      <li>Ask <code>15 in menu</code>. Two items cost 15, so why is it False?</li>
      <li>Take a <code>list()</code> copy, then add a row. Which one changes: the view or the copy?</li>
      <li>Delete <code>coffee</code>, then add it back. Where does it go now?</li>
      <li>Press <b>Write tea twice</b>. Which value wins, and where does tea stay?</li></ol>
      <p class="muted small">The Lab is free play: nothing here is graded. The mission clock keeps running.</p></div></div></section>`;
  Board($('.board',view),{start:DECK_BOARD,lab:true});
  $('#quit').onclick=renderMap;window.scrollTo(0,0);mark('lab');
}


/* ---------- stage complete + mission report ---------- */
function renderLevelDone(){
  const l=LVM[R.level],s=lvState(R.level),i=lvIndex(R.level),next=M.levels[i+1],gained=ST.xp-R.xp0;
  const boss=R.level==='BOSS',bonusLv=l.bonus,offerBonus=boss&&next&&next.bonus&&live();
  view.innerHTML=`<section class="done">
    ${backBar()}
    <div class="eyebrow">${boss?'Final Boss defeated':esc(l.name)+' cleared'}</div>
    <h2>${boss?esc(M.ui.boss_win):bonusLv?'Bonus round cleared!':'Stage clear!'}</h2>
    ${offerBonus?`<p class="bonusline">${ICON.trophy.replace('width="26" height="26"','width="20" height="20"')}<span><b>Mission complete.</b> You finished early, so a <b>bonus round</b> is open: ${next.main.length} quick questions, about ${Math.round(next.main.reduce((a,q)=>a+QM[q].time,0)/60)} minutes, for extra XP and a badge.</span></p>`:''}
    ${starsHTML(s.stars,'bigstars')}
    <div class="tally"><div><b>+${gained}</b><span>XP this run</span></div><div><b>${s.first_try}/${s.total}</b><span>First try</span></div><div><b>${s.timed_out}</b><span>Timed out</span></div></div>
    ${R.badges.length?`<div class="badges newb">${[...new Set(R.badges)].map(id=>badgeHTML(id,true)).join('')}</div>`:''}
    <p class="muted">${s.stars<3?'Answer every challenge right on the first try for 3 stars.':'Flawless stage. Every challenge right on the first try.'}</p>
    <div class="hero-row" style="justify-content:center">
      ${offerBonus?`<button class="btn gold" id="nextL" type="button">${ICON.play}Play the bonus round</button><button class="btn primary" id="finishBtn" type="button">Finish: see my report</button>`
        :boss||bonusLv?`<button class="btn gold" id="nextL" type="button">${needSurvey()?'Last step: quick feedback':'See your mission report'}</button>`:next?`<button class="btn primary" id="nextL" type="button">${ICON.play}Next: ${esc(next.name)}</button>`:''}
      <button class="btn ghost" id="toMap" type="button">Mission map</button></div></section>`;
  sfx.win();rain(boss?220:s.stars*50);setTimeout(()=>burst(innerWidth/2,innerHeight*.35,boss?140:90,1.3),400);
  const nb=$('#nextL');if(nb)nb.onclick=()=>offerBonus?renderBriefing(next.id):(boss||bonusLv)?renderSummary():renderBriefing(next.id);
  const fb=$('#finishBtn');if(fb)fb.onclick=finishMission;
  $('#toMap').onclick=renderMap;$('#backBtn').onclick=renderMap;window.scrollTo(0,0);mark('done',R.level);
}
/* Every required stage is cleared: end the mission now instead of playing the bonus round. */
async function finishMission(){
  const b=$('#finishBtn');if(b)b.disabled=true;
  try{const r=await api('POST','/finish');adopt(r.state);overHandled=true;renderSummary()}catch(e){if(b)b.disabled=false;netError(e)}
}
/* ---------- end-of-mission feedback ----------
   Opens by itself when the mission ends (time, tab switches, Final Boss / bonus cleared, or Finish) and must be sent
   before the report. Five short steps about the practice only: name, roll number, section, university and contact
   come from the sign-in. A draft is kept in this browser so a reload does not lose answers. */
const needSurvey=()=>!!(ST&&ST.ended_at&&!ST.feedback_done);
const ENJOY=[['😴','Not at all'],['😕','Not much'],['🙂','It was okay'],['😄','Liked it'],['🤩','Loved it']];
const CONF=['Not confident','A little','Getting there','Confident','Very confident'];
const DIFF=[['easy','🥱','Too easy'],['right','👌','Just right'],['hard','🥵','Too hard']];
const PACE=[['spare','🏖️','Time to spare'],['enough','⏱️','Just enough'],['more','🏃','Needed more time']];
const TECH=[['no','✅','No problems'],['small','⚠️','Yes, small ones'],['blocked','🧱','Yes, it blocked me']];
let SV=null;
const svKey=()=>API.key('survey2:'+(API.user?API.user.roll_no:''));
function svSave(){try{localStorage.setItem(svKey(),JSON.stringify(SV))}catch(e){}}
function svLoad(){let d=null;try{d=JSON.parse(localStorage.getItem(svKey())||'null')}catch(e){}
  SV=Object.assign({step:0,enjoy:0,toughest:'',favourite:'',aim:'tomato',difficulty:'',pace:'',confidence:0,helped:[],tech:'',improve:''},d&&typeof d==='object'?d:{});
  SV.step=Math.min(Math.max(0,SV.step|0),4);if(!Array.isArray(SV.helped))SV.helped=[];
  const ids=coreStages().map(l=>l.id);if(!ids.includes(SV.toughest))SV.toughest='';if(!ids.includes(SV.favourite))SV.favourite=''}
const SPLAT='<svg viewBox="0 0 60 60" aria-hidden="true"><path d="M30 6c4 0 5 7 9 8s9-4 11 0-3 8-1 12 9 5 7 10-9 2-11 6 2 10-3 12-7-5-12-5-8 7-12 4 0-9-3-12-10-2-11-7 6-7 7-11-5-8-2-11 8 1 11-2 1-8 5-8z"/><circle cx="52" cy="48" r="3"/><circle cx="8" cy="20" r="2.5"/><circle cx="48" cy="8" r="2"/></svg>';
const coreStages=()=>M.levels.filter(l=>!l.bonus);
const stageTag=(l,i)=>l.id==='BOSS'?'Final Boss':l.id==='L0'?'Briefing':'Stage '+i;
const stageName=id=>{const l=coreStages().find(x=>x.id===id);return l?l.name:''};
/* one 3-option row of big cards, saved to SV[field] */
function optsHTML(field,list,label){return `<div class="bigopts three" role="radiogroup" aria-label="${label}" data-f="${field}">${list.map(([k,e,l])=>`<button type="button" role="radio" class="bigopt${SV[field]===k?' on':''}" aria-checked="${SV[field]===k}" data-k="${k}"><span class="be">${e}</span><b>${l}</b></button>`).join('')}</div>`}
function bindOpts(field){const bs=$$(`.bigopts[data-f="${field}"] .bigopt`);bs.forEach(b=>b.onclick=()=>{SV[field]=b.dataset.k;svSave();bs.forEach(x=>{const on=x===b;x.classList.toggle('on',on);x.setAttribute('aria-checked',on)});sfx.tap()})}
function stageCardsHTML(){return coreStages().map((l,i)=>{const t=SV.toughest===l.id,f=SV.favourite===l.id;
  return `<button type="button" class="stcard${t?' tough':''}${f?' fav':''}" data-l="${l.id}" aria-label="${esc(stageTag(l,i)+': '+l.name)}${t?', toughest':''}${f?', favourite':''}">
    <small>${stageTag(l,i)}</small><b>${esc(l.name)}</b>${t?`<span class="stsplat">${SPLAT}</span>`:''}${f?'<span class="ststar" aria-hidden="true">⭐</span>':''}
    <span class="sttags">${t?'<em class="t">🍅 Toughest</em>':''}${f?'<em class="f">⭐ Favourite</em>':''}</span></button>`}).join('')}
const SV_STEPS=[
  {need:'Tap a face.',ok:()=>SV.enjoy>0,
   html:()=>`<h3 class="svq">How much did you enjoy the practice?</h3>
    <div class="bigface" id="bigFace" aria-hidden="true">${SV.enjoy?ENJOY[SV.enjoy-1][0]:'🤔'}</div><p class="facelab" id="faceLab">${SV.enjoy?ENJOY[SV.enjoy-1][1]:'Tap a face'}</p>
    <div class="faces" role="radiogroup" aria-label="How much you enjoyed it, 1 to 5">${ENJOY.map(([e,l],k)=>`<button type="button" role="radio" class="face${SV.enjoy===k+1?' on':''}" aria-checked="${SV.enjoy===k+1}" aria-label="${k+1}: ${l}" data-v="${k+1}"><span>${e}</span><small>${k+1}</small></button>`).join('')}</div>
    <div class="scaleends"><span>Not at all</span><span>Loved it</span></div>`,
   bind:()=>$$('.face').forEach(b=>b.onclick=()=>{const v=+b.dataset.v;SV.enjoy=v;svSave();
     $$('.face').forEach(x=>{const on=+x.dataset.v===v;x.classList.toggle('on',on);x.setAttribute('aria-checked',on)});
     const f=$('#bigFace');f.textContent=ENJOY[v-1][0];f.classList.remove('pop');void f.offsetWidth;f.classList.add('pop');$('#faceLab').textContent=ENJOY[v-1][1];
     tone(300+v*90,0,.12,'triangle',.06);if(v===5){const r=f.getBoundingClientRect();burst(r.left+r.width/2,r.top+r.height/2,50,1)}})},
  {need:'Splat the toughest stage with a tomato and give your favourite a star.',ok:()=>!!SV.toughest&&!!SV.favourite,
   html:()=>`<h3 class="svq">Which stage was the toughest? Which was your favourite?</h3>
    <p class="svsub">Pick what to throw, then tap a stage. Splat the <b>toughest</b> with a tomato 🍅 and give your <b>favourite</b> a star ⭐. It can be the same stage.</p>
    <div class="aim" role="radiogroup" aria-label="What to throw">
      <button type="button" role="radio" class="aimbtn tomato${SV.aim==='tomato'?' on':''}" aria-checked="${SV.aim==='tomato'}" data-a="tomato"><span class="ae">🍅</span><span><b>Toughest stage</b><small id="aimT">${esc(stageName(SV.toughest))||'Not picked yet'}</small></span></button>
      <button type="button" role="radio" class="aimbtn star${SV.aim==='star'?' on':''}" aria-checked="${SV.aim==='star'}" data-a="star"><span class="ae">⭐</span><span><b>Favourite stage</b><small id="aimF">${esc(stageName(SV.favourite))||'Not picked yet'}</small></span></button></div>
    <div class="stgrid" id="stgrid">${stageCardsHTML()}</div>`,
   bind:bindStageThrow},
  {need:'Pick the difficulty and how the time was.',ok:()=>!!SV.difficulty&&!!SV.pace,
   html:()=>`<h3 class="svq">The difficulty was…</h3>${optsHTML('difficulty',DIFF,'Difficulty')}
    <h3 class="svq">How was the ${Math.round(ST.mission_seconds/60)}-minute clock?</h3>${optsHTML('pace',PACE,'Time')}`,
   bind:()=>{bindOpts('difficulty');bindOpts('pace')}},
  {need:'Tap a confidence bar and pick at least one thing that helped.',ok:()=>SV.confidence>0&&SV.helped.length>0,
   html:()=>`<h3 class="svq">How confident are you with ${esc(M.feedback.topic)} now?</h3>
    <div class="meter" role="radiogroup" aria-label="Confidence, 1 to 5">${[1,2,3,4,5].map(v=>`<button type="button" role="radio" class="mbar${v<=SV.confidence?' on':''}" aria-checked="${v===SV.confidence}" aria-label="${v}: ${CONF[v-1]}" data-v="${v}" style="--h:${28+v*18}px;--c:var(--c${v})"><span>${v}</span></button>`).join('')}</div>
    <p class="facelab" id="confLab">${SV.confidence?CONF[SV.confidence-1]+' '+'💪'.repeat(Math.max(0,SV.confidence-2)):'Tap a bar'}</p>
    <div class="scaleends"><span>Not confident</span><span>Very confident</span></div>
    <h3 class="svq">What helped you learn the most?</h3><p class="svsub">Pick as many as you like.</p>
    <div class="chips">${M.feedback.helped.map(h=>{const on=SV.helped.includes(h.key);return `<button type="button" class="chip${on?' on':''}" aria-pressed="${on}" data-k="${h.key}"><span>${h.emoji}</span>${esc(h.label)}</button>`}).join('')}</div>`,
   bind:()=>{
     $$('.mbar').forEach(b=>b.onclick=()=>{const v=+b.dataset.v;SV.confidence=v;svSave();
       $$('.mbar').forEach(x=>{const n=+x.dataset.v;x.classList.toggle('on',n<=v);x.setAttribute('aria-checked',n===v)});
       $('#confLab').textContent=CONF[v-1]+' '+'💪'.repeat(Math.max(0,v-2));tone(260+v*110,0,.12,'triangle',.06)});
     $$('.chip').forEach(b=>b.onclick=()=>{const k=b.dataset.k,on=!SV.helped.includes(k);
       SV.helped=on?[...SV.helped,k]:SV.helped.filter(x=>x!==k);svSave();b.classList.toggle('on',on);b.setAttribute('aria-pressed',on);
       if(on){b.classList.remove('pop');void b.offsetWidth;b.classList.add('pop');tone(660,0,.08,'triangle',.05)}})}},
  {need:'Tell us about technical problems.',ok:()=>!!SV.tech,
   html:()=>`<h3 class="svq">Did you face any technical problems?</h3>${optsHTML('tech',TECH,'Technical problems')}
    <label class="svf"><span>One thing we should improve (optional)</span><textarea id="svImp" maxlength="600" rows="3" placeholder="What would make the next practice better?">${esc(SV.improve)}</textarea></label>`,
   bind:()=>{bindOpts('tech');$('#svImp').oninput=e=>{SV.improve=e.target.value;svSave()}}},
];
function renderSurvey(){
  R=null;Q=null;stopQTimer();closeDrawer();if(guide.open)guide.close();
  if(!SV)svLoad();
  const i=SV.step,st=SV_STEPS[i],last=i===SV_STEPS.length-1,reason=ST.ended_reason;
  const head=reason==='time'?`<div class="endbanner time">${ICON.clock}<div><b>Time's up! Your progress is saved.</b><p>Every answer you checked is saved on the server. One last step: a quick feedback (about 2 minutes), then your report.</p></div></div>`
    :reason==='proctor'?`<div class="endbanner proctor">${ICON.eye}<div><b>Mission ended: you left the mission tab ${ST.proctor.tab_switches} times.</b><p>Your work is saved. One last step: a quick feedback, then your report.</p></div></div>`
    :`<div class="endbanner done">${ICON.trophy.replace('width="26" height="26"','width="22" height="22"')}<div><b>Mission complete! Brilliant work.</b><p>One last step: a quick feedback (about 2 minutes), then your report.</p></div></div>`;
  view.innerHTML=`<section class="survey enter">
    ${i===0?head:''}
    <div class="svtop"><div class="eyebrow">Your feedback · ${i+1} of ${SV_STEPS.length}</div><div class="svdots" aria-hidden="true">${SV_STEPS.map((x,k)=>`<i class="${k<i?'done':k===i?'cur':''}"></i>`).join('')}</div></div>
    <div class="card svcard">${st.html()}</div>
    <p class="lgerr" id="svErr" role="alert"></p>
    <div class="power-row svnav">${i?`<button class="btn ghost" id="svBack" type="button">${ICON.back}Back</button>`:''}<button class="btn ${last?'gold':'primary'}" id="svNext" type="button">${last?'Send feedback and see my report':'Next'}</button></div>
  </section>`;
  st.bind();
  $('.svcard').addEventListener('click',()=>{if(st.ok())$('#svErr').textContent=''});
  $('.svcard').addEventListener('input',()=>{if(st.ok())$('#svErr').textContent=''});
  if(i)$('#svBack').onclick=()=>{SV.step--;svSave();renderSurvey();window.scrollTo(0,0)};
  $('#svNext').onclick=()=>{
    if(!st.ok()){const e=$('#svErr');e.textContent=st.need;const c=$('.svcard');c.classList.remove('nope');void c.offsetWidth;c.classList.add('nope');sfx.tap();return}
    if(last)return sendSurvey();
    SV.step++;svSave();sfx.tap();renderSurvey();window.scrollTo(0,0)};
  window.scrollTo(0,0);mark('survey');
  if((reason==='time'||reason==='proctor')&&!resumeTimer)watchResume();
}
/* Toughest / favourite stage: pick a tomato or a star, tap a stage card, and it flies there. */
function bindStageThrow(){
  const grid=$('#stgrid');
  function aim(a){SV.aim=a;svSave();$$('.aimbtn').forEach(b=>{const on=b.dataset.a===a;b.classList.toggle('on',on);b.setAttribute('aria-checked',on)})}
  function paint(id,kind){grid.innerHTML=stageCardsHTML();bindCards();
    $('#aimT').textContent=stageName(SV.toughest)||'Not picked yet';$('#aimF').textContent=stageName(SV.favourite)||'Not picked yet';
    const c=grid.querySelector(`.stcard[data-l="${id}"]`);if(!c)return;c.classList.add(kind==='tomato'?'hitnew':'starnew');
    if(kind==='tomato'){tone(130,0,.22,'square',.06);tone(90,.05,.25,'sawtooth',.04)}
    else{tone(880,0,.12,'sine',.06);tone(1175,.08,.16,'sine',.06);const r=c.getBoundingClientRect();burst(r.left+r.width/2,r.top+r.height/2,26,.8)}}
  function land(kind,id){
    if(!grid.isConnected)return;   // the learner moved on before this throw landed
    if(kind==='tomato')SV.toughest=id;else SV.favourite=id;svSave();paint(id,kind);
    if(kind==='tomato'&&!SV.favourite)aim('star');else if(kind==='star'&&!SV.toughest)aim('tomato');
  }
  function fire(card){
    const kind=SV.aim,id=card.dataset.l;
    if(reduce)return land(kind,id);
    const from=$(`.aimbtn[data-a="${kind}"] .ae`).getBoundingClientRect(),to=card.getBoundingClientRect();
    const x0=from.left+from.width/2,y0=from.top+from.height/2,x1=to.left+to.width/2,y1=to.top+to.height/2;
    const p=document.createElement('span');p.className='proj';p.textContent=kind==='star'?'⭐':'🍅';document.body.appendChild(p);
    const spin=kind==='star'?360:540,midY=Math.min(y0,y1)-110;
    p.animate([{transform:`translate(${x0}px,${y0}px) rotate(0) scale(.8)`},{transform:`translate(${(x0+x1)/2}px,${midY}px) rotate(${spin/2}deg) scale(1.3)`},{transform:`translate(${x1}px,${y1}px) rotate(${spin}deg) scale(1)`}],
      {duration:520,easing:'cubic-bezier(.3,.1,.4,1)'}).onfinish=()=>{p.remove();land(kind,id)};
    sfx.tap();
  }
  function bindCards(){$$('.stcard',grid).forEach(c=>c.onclick=()=>fire(c))}
  $$('.aimbtn').forEach(b=>b.onclick=()=>{aim(b.dataset.a);sfx.tap()});
  bindCards();
}
async function sendSurvey(){
  const b=$('#svNext');b.disabled=true;b.classList.add('busy');
  const body={enjoy:SV.enjoy,toughest:SV.toughest,favourite:SV.favourite,difficulty:SV.difficulty,pace:SV.pace,
    confidence:SV.confidence,helped:SV.helped,tech:SV.tech,improve:SV.improve.trim()};
  try{const r=await api('POST','/feedback',body);adopt(r.state)}
  catch(e){b.disabled=false;b.classList.remove('busy');
    if(e&&e.message==='signed-out')return netError(e);
    if(e&&/opens when your mission ends/.test(e.message)){SV=null;return loadMission()}   // the teacher resumed the mission meanwhile
    $('#svErr').textContent=e instanceof TypeError?'Could not reach the server. Check the connection and press Send again.':(e&&e.message)||'Something went wrong. Try again.';return}
  try{localStorage.removeItem(svKey())}catch(e){}
  SV=null;
  view.innerHTML=`<section class="power enter thanks"><div class="thx" aria-hidden="true">🎉</div><h2>Thank you!</h2><p class="loginlead">Your feedback is in. Here comes your report…</p></section>`;
  sfx.win();rain(180);setTimeout(()=>burst(innerWidth/2,innerHeight*.35,120,1.2),200);
  setTimeout(renderSummary,reduce?300:1700);
}
async function renderSummary(){
  if(needSurvey())return renderSurvey();
  R=null;Q=null;stopQTimer();closeDrawer();
  let rev={items:[]};try{rev=await api('GET','/review')}catch(e){}
  const ent=Object.values(ST.questions),firstTry=ent.filter(v=>v.solved&&!v.wrong).length,attempted=ent.filter(v=>v.solved||v.revealed||v.timed_out).length;
  const timedOut=ent.filter(v=>v.timed_out).length,weak=Object.entries(ST.concepts).filter(([k,v])=>v.c/v.a<.7);
  const reason=ST.ended_reason,p=ST.progress,pr=ST.proctor;
  const unfinished=ST.levels.filter(l=>!l.done).map(l=>LVM[l.id].name);
  const banner=reason==='time'?`<div class="endbanner time">${ICON.clock}<div><b>Time's up. ${(m=>m===1?'The 1 minute is':`The ${m} minutes are`)(Math.round(ST.mission_seconds/60))} over.</b><p>You cleared <b>${p.done} of ${p.total}</b> challenges and earned <b>${ST.xp} XP</b>.${unfinished.length?` Still to do: ${unfinished.map(esc).join(', ')}.`:''} The review below shows exactly what to study next.</p></div></div>`
    :reason==='proctor'?`<div class="endbanner proctor">${ICON.eye}<div><b>Mission ended: you left the mission tab ${pr.tab_switches} times.</b><p>The limit was ${pr.max_tab_switches}. Your work up to that point is saved and your teacher can see it. You cleared <b>${p.done} of ${p.total}</b> challenges.</p></div></div>`
    :reason==='complete'?`<div class="endbanner done">${ICON.trophy.replace('width="26" height="26"','width="22" height="22"')}<div><b>Mission complete. Every stage cleared.</b><p>Look at the concept bars and the review to lock in what you learned.</p></div></div>`:'';
  view.innerHTML=`<section class="report enter">
    ${backBar()}
    <div class="eyebrow">Mission report</div>
    <h2>${reason==='complete'?esc(M.ui.champion):reason?'Mission over':'Mission in progress'}</h2>
    ${banner}
    <div class="tally four"><div><b>${ST.xp}</b><span>Total XP</span></div><div><b>${attempted?Math.round(firstTry/attempted*100):0}%</b><span>First-try accuracy</span></div><div><b>${mins(ST.used_seconds)}</b><span>Time used / ${Math.round(ST.mission_seconds/60)}m</span></div><div><b>${p.done}/${p.total}</b><span>Challenges cleared</span></div></div>
    <div class="tally four small"><div><b>${ST.best_combo}</b><span>Best combo</span></div><div><b>${timedOut}</b><span>Timed out</span></div><div><b>${pr.tab_switches}</b><span>Tab switches</span></div><div><b>${pr.copy_paste}</b><span>Copy/paste tries</span></div></div>
    ${reason==='time'||reason==='proctor'?`<div class="resumewait" id="resumeWait"><span class="rwdot" aria-hidden="true"></span><div><b>Your teacher can resume your mission from where you stopped.</b><p>Your XP, cleared challenges and the time you had left are kept. This page checks every few seconds and continues by itself.</p></div><button class="btn" id="checkResume" type="button">Check again</button></div>`
      :reason?'<p class="muted small attempt-note">Each student gets one attempt at the mission. If you need another attempt, ask your teacher.</p>':''}
    <div class="repgrid">
      <div class="card lbcard" id="lbReport"><h4>Class leaderboard</h4><p class="muted">Loading…</p></div>
      <div class="card"><h4>Badges · ${ST.badges.length} / ${Object.keys(M.badges).length}</h4><div class="badges">${Object.keys(M.badges).map(id=>badgeHTML(id,ST.badges.includes(id))).join('')}</div></div>
      <div class="card"><h4>Concept mastery</h4>${conceptBars()}${weak.length?`<p class="small"><b>Study next:</b> ${weak.map(([k])=>esc(CONCEPTS[k]||k)).join(', ')}. The field guide covers each one.</p>`:''}</div>
    </div>
    <div class="card"><h4>Learn from your mistakes · ${rev.items.length}</h4>${rev.items.length?`<div class="review">${rev.items.map(it=>`<details><summary><span class="rlvl">${esc(LVM[it.level].name)}</span>${esc(it.title)}<small>${it.timed_out?'time ran out':it.revealed?'solution viewed':it.wrong+' wrong attempt'+(it.wrong>1?'s':'')+' then solved'}</small></summary><p>${it.explain}</p>${it.trap?`<div class="trap"><b>The trap</b><p>${it.trap}</p></div>`:''}</details>`).join('')}</div>`:'<p class="muted">No mistakes to review. Impressive.</p>'}</div>
    <div class="hero-row" style="justify-content:center"><button class="btn primary" id="toMap" type="button">Mission map</button><button class="btn" id="lab" type="button">Open the ${esc(M.ui.lab_name)}</button><button class="btn ghost" id="guide2" type="button">Field guide</button></div>
  </section>`;
  $('#toMap').onclick=renderMap;$('#backBtn').onclick=renderMap;$('#lab').onclick=renderLab;$('#guide2').onclick=openGuide;window.scrollTo(0,0);
  mark('report');loadLeaderboard('#lbReport');
  if(reason==='time'||reason==='proctor'){$('#checkResume').onclick=()=>checkResume(true);watchResume()}
  if(reason==='complete'){rain(120)}
}

/* ---------- field guide (cheatsheet + comparison table) ---------- */
const guide=$('#guide');
function openGuide(){
  guide.innerHTML=`<div class="gin"><div class="ghead"><h2 id="guideTitle">${esc(M.ui.guide_title)}</h2><button class="iconbtn" id="gclose" type="button" aria-label="Close the field guide">${ICON.x}</button></div>
    ${M.ui.guide_html}
  </div>`;
  $('#gclose',guide).onclick=()=>guide.close();
  guide.showModal();
}
$('#guideBtn').onclick=openGuide;
guide.addEventListener('click',e=>{if(e.target===guide)guide.close()});

/* ---------- keyboard ---------- */
document.addEventListener('keydown',e=>{
  if(guide.open||modal.open||e.ctrlKey||e.metaKey||e.altKey)return;
  const tag=(e.target.tagName||'').toLowerCase();if(tag==='input'||tag==='textarea')return;
  if(drawer.classList.contains('open')&&e.key==='Enter'&&e.target===document.body){const c=$('#cont')||$('#retry');if(c){e.preventDefault();c.click()}return}
  if(!Q||Q.done||drawer.classList.contains('open'))return;
  if(/^[1-9]$/.test(e.key)&&Q.keyPick){Q.keyPick(+e.key-1);return}
  if(e.key==='Enter'&&tag!=='button'&&$('#check')&&!$('#check').disabled){e.preventDefault();check()}
});

/* ---------- sign-in + boot ---------- */
let CLASS_CODE=false;
function renderLogin(msg){
  closeDrawer();stopQTimer();R=null;Q=null;
  view.innerHTML=`<section class="power enter login">
    <div class="eyebrow">Dictionaries: The Python Challenge</div>
    <h2>Join the mission</h2>
    <p class="loginlead">Sign in with your class details. Use your own roll number: it can be signed in on <b>one device at a time</b>, and each student gets <b>one attempt</b> at the mission.</p>
    <form id="loginForm" class="loginf" novalidate>
      <label>Your name<input id="lgName" autocomplete="name" maxlength="60" required></label>
      <label>Roll number<input id="lgRoll" autocomplete="off" maxlength="30" required></label>
      <label>Section<input id="lgSec" autocomplete="off" maxlength="40" placeholder="For example S-001" required></label>
      <label>University name<input id="lgUni" autocomplete="organization" maxlength="120" placeholder="Your university" required></label>
      <label>Contact no.<input id="lgPhone" type="tel" inputmode="tel" autocomplete="tel" maxlength="16" placeholder="10-digit mobile number" required></label>
      ${CLASS_CODE?'<label>Class code<input id="lgCode" autocomplete="off" maxlength="40" required></label>':''}
      <p class="lgerr" id="lgErr" role="alert">${msg?esc(msg):''}</p>
      <div class="power-row"><button class="btn primary" type="submit">${ICON.play}Continue</button></div>
    </form></section>`;
  $('#loginForm').onsubmit=async e=>{e.preventDefault();const n=$('#lgName').value.trim(),r=$('#lgRoll').value.trim(),s=$('#lgSec').value.trim(),uni=$('#lgUni').value.trim(),ph=$('#lgPhone').value.trim(),c=CLASS_CODE?$('#lgCode').value.trim():null;
    if(!n||!r||!s||!uni||!ph||(CLASS_CODE&&!c)){$('#lgErr').textContent=!s?'Type your section, for example S-001.':!uni?'Type your university name.':!ph?'Type your 10-digit mobile number.':'Fill in every field to join.';return}
    if(!/^(\+?91|0)?[6-9]\d{9}$/.test(ph.replace(/[\s-]/g,''))){$('#lgErr').textContent='Type a 10-digit mobile number.';return}
    const b=$('#loginForm button[type=submit]');b.disabled=true;$('#lgErr').textContent='';
    try{await API.login(n,r,s,uni,ph,c);ac();paintUser();await loadMission()}catch(err){$('#lgErr').textContent=err.message==='signed-out'?'Please sign in again.':err.message;b.disabled=false}};
  paintUser();window.scrollTo(0,0);
}
function paintUser(){const c=$('#userChip'),u=API.user;c.hidden=!u;if(u){c.innerHTML=`<b>${esc(u.name)}</b><small>${esc(u.section)} · profile</small>`;c.setAttribute('aria-label','Open your profile')}}
$('#userChip').onclick=()=>{if(M&&ST)renderProfile()};

/* ---------- profile ---------- */
async function renderProfile(){
  if(needSurvey())return renderSurvey();
  R=null;Q=null;stopQTimer();closeDrawer();
  const u=API.user||{},p=ST.progress,stages=ST.levels.filter(l=>l.done).length,reason=ST.ended_reason;
  const status=reason==='complete'?'Completed':reason==='time'?'Time ran out':reason==='proctor'?'Ended: tab switches':ST.started_at?'In progress':'Not started';
  const initials=String(u.name||'?').trim().split(/\s+/).map(w=>w[0]).slice(0,2).join('').toUpperCase();
  view.innerHTML=`<section class="profile enter">
    ${backBar()}
    <div class="pcard">
      <span class="avatar" aria-hidden="true">${esc(initials)}</span>
      <div><h2>${esc(u.name)}</h2><p class="pmeta"><span>Roll no <b>${esc(u.roll_no)}</b></span><span>Section <b>${esc(u.section)}</b></span>${u.university?`<span>University <b>${esc(u.university)}</b></span>`:''}<span class="pstatus ${reason||''}">${esc(status)}</span></p></div>
    </div>
    <div class="tally four"><div><b id="pRank">–</b><span>Rank in ${esc(u.section)}</span></div><div><b>${ST.xp}</b><span>XP</span></div><div><b>${p.done}/${p.total}</b><span>Challenges cleared</span></div><div><b>${stages}/${M.levels.length}</b><span>Stages cleared</span></div></div>
    <div class="tally four small"><div><b>${ST.badges.length}/${Object.keys(M.badges).length}</b><span>Badges</span></div><div><b>${ST.best_combo}</b><span>Best combo</span></div>
      <div><b>${ST.started_at?mins(live()&&missionEnd?(missionEnd-Date.now())/1000:0):'45:00'}</b><span>Time left</span></div><div><b>${ST.proctor.tab_switches}/${ST.proctor.max_tab_switches||'∞'}</b><span>Tab switches</span></div></div>
    <div class="repgrid">
      <div class="card"><h4>Your attempt</h4><div class="legend">
        <div>Each student gets <b>one attempt</b> at the mission. ${reason?'Yours is finished. Ask your teacher if you need another.':ST.started_at?'Yours is running now: the clock does not stop while you are on this page.':'It starts when you accept the rules in the first stage.'}</div>
        <div>Your roll number can be signed in on <b>one device at a time</b>.</div></div>
        <div class="power-row" style="margin-top:12px">${reason?'<button class="btn" id="pReport" type="button">See your mission report</button>':''}<button class="btn ghost" id="pOut" type="button">Sign out</button></div>
        <p class="muted small" id="pOutNote" hidden></p></div>
      <div class="card"><h4>Concept mastery</h4>${conceptBars()}</div>
    </div>
  </section>`;
  $('#backBtn').onclick=renderMap;const pr=$('#pReport');if(pr)pr.onclick=renderSummary;
  const out=$('#pOut');out.onclick=async()=>{
    if(live()&&!out.dataset.armed){out.dataset.armed='1';out.textContent='Tap again to sign out';const n=$('#pOutNote');n.hidden=false;n.textContent='Signing out does not pause your 45-minute clock.';return}
    await API.logout();M=null;ST=null;stopQTimer();renderLogin()};
  window.scrollTo(0,0);mark('profile');
  try{const d=await api('GET','/leaderboard');const r=$('#pRank');if(r&&d.me)r.textContent=`${d.me.rank} / ${d.count}`}catch(e){}
}
$('#homeBtn').onclick=()=>{if(M&&ST)renderMap()};
function paintBrand(short,title){const b=$('#homeBtn span');if(b&&short)b.textContent=short;if(title)document.title=title}
async function loadMission(){
  const m=await api('GET','/mission');M=m;M.badges=m.badges;QM={};LVM={};
  if(m.concepts)CONCEPTS=m.concepts;if(m.type_labels)TYPE_LABEL=m.type_labels;paintBrand(m.ui.short,m.ui.title);
  m.levels.forEach(l=>{LVM[l.id]=l;l.questions.forEach(q=>QM[q.id]=q)});
  ST=null;adopt(m.state);
  if(live())preloadPython();
  if(ST.ended_at)return renderSummary();
  renderMap();
}
function renderOffline(){
  view.innerHTML=`<section class="power enter"><div class="eyebrow">Connection needed</div><h2>The mission server is not reachable</h2>
    <p class="loginlead">Answers and timers in this mission are checked on the server, so it needs a connection. Check that the app is running, then try again.</p>
    <div class="power-row"><button class="btn primary" id="again" type="button">Try again</button></div></section>`;
  $('#again').onclick=boot;
}
function renderDupTab(){
  view.innerHTML=`<section class="power enter"><div class="eyebrow">One tab only</div><h2>The mission is already open in another tab</h2>
    <p class="loginlead">Continue in that tab. Opening the mission twice is not allowed and has been recorded.</p>
    <div class="power-row"><button class="btn primary" id="again" type="button">I closed the other tab · reload</button></div></section>`;
  $('#again').onclick=()=>location.reload();
}
// Heartbeat: keeps this device's claim on the roll number (one device per roll number at a time).
setInterval(()=>{
  if(!API.signedIn||!M)return;
  API.call('POST','/ping').catch(e=>{if(e.message==='signed-out'){stopQTimer();M=null;ST=null;renderLogin('You were signed out. Your teacher released this roll number, or it was signed in somewhere else.')}});
},30000);
async function boot(){
  await new Promise(r=>setTimeout(r,350));          // give an already-open tab time to answer
  const r=await API.boot();CLASS_CODE=!!r.classCode;if(r.short)paintBrand(r.short,r.title);
  if(!r.online)return renderOffline();
  if(r.needsLogin&&!dupTab)return renderLogin();
  paintUser();
  if(dupTab){try{const m=await api('GET','/mission');ST=m.state;await report('multi_tab')}catch(e){}return renderDupTab()}
  try{await loadMission()}catch(e){e.message==='signed-out'?renderLogin():renderOffline()}
}
boot();
})();
