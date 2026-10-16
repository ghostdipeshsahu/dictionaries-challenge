/* Dictionaries: The Python Challenge · teacher dashboard (live: server push, 5-second polling fallback) */
(()=>{
const $=(s,r=document)=>r.querySelector(s),$$=(s,r=document)=>[...r.querySelectorAll(s)];
const esc=s=>String(s==null?'':s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const pct=v=>v==null?'–':Math.round(v*100)+'%';
const view=$('#tview'),KEY='dicts-teacher-token';
let CONCEPTS={pairs:'Key-value pairs',creation:'Creating a dictionary',empty:'Empty {} and dict()',unique_keys:'Unique keys',access:'menu[key] takes a key',
  keyerror_get:'KeyError vs get()',membership:'in checks keys',add_change:'Add or change a key',case:'Keys are case-sensitive',delete_len:'del and len()',
  views_methods:'keys(), values(), items()',looping:'Looping over a dictionary',live_views:'Live views vs list() copies',dict_from_pairs:'dict() from pairs',
  hashable_keys:'Keys must be immutable',compare_types:'Dict vs list, tuple, set'};
let TYPES={mcq:'Multiple choice',msq:'Multiple select',tf:'True or false',ar:'Assertion and reasoning',fill:'Fill in the blanks',match:'Match the columns',
  order:'Put in order',categorize:'Sort into groups',numeric:'Numeric answer',predict:'Predict the output',debug:'Debug mission',coding:'Coding challenge',board:'Board build'};
const STATUS_CLS={complete:'hi',time:'mid',proctor:'lo','in progress':'','not started':''};
let BUILD=null,token=null,section='',data=null,sortKey='rank',sortDir=1,filter='',es=null,poll=null,liveMode='',armed=null;
try{token=localStorage.getItem(KEY)}catch(e){}

async function api(path,opts){
  const res=await fetch('/api'+path,Object.assign({headers:{Authorization:'Bearer '+token,'Content-Type':'application/json'}},opts||{}));
  if(res.status===401||res.status===403){signOut();throw new Error('Signed out')}
  if(!res.ok)throw new Error('Request failed ('+res.status+')');
  return res.status===204?null:res;
}
function signOut(){token=null;stopLive();try{localStorage.removeItem(KEY)}catch(e){}$('#tbar').hidden=true;renderLogin()}

function renderLogin(msg){
  view.innerHTML=`<form class="tlogin" id="tl"><h1>Teacher dashboard</h1><p>Every student's progress, score, time and integrity flags for the Dictionaries mission.</p>
    <input type="password" id="pw" placeholder="Teacher password" autocomplete="current-password" required>
    <p class="err" id="err" role="alert">${esc(msg||'')}</p><button class="btn primary" type="submit">Sign in</button>
    <a class="linkback" href="/">Back to the student mission</a></form>`;
  $('#tl').onsubmit=async e=>{e.preventDefault();$('#err').textContent='';
    const r=await fetch('/api/teacher/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({password:$('#pw').value})});
    if(!r.ok){$('#err').textContent='That password is not right.';return}
    token=(await r.json()).token;try{localStorage.setItem(KEY,token)}catch(e){}load()};
  setTimeout(()=>$('#pw').focus(),50);
}

async function load(quiet){
  $('#tbar').hidden=false;
  if(!quiet)view.innerHTML='<section class="dash"><p class="empty">Loading the class…</p></section>';
  try{data=await api('/teacher/dicts'+(section?'?section='+encodeURIComponent(section):'')).then(r=>r.json())}catch(e){return}
  if(checkBuild(data))return;
  missionLabels(data);
  const sel=$('#secSel');sel.innerHTML='<option value="">All sections</option>'+data.sections.map(s=>`<option${s===section?' selected':''}>${esc(s)}</option>`).join('');
  if(quiet&&$('#rows')){tiles();panels();attention();rows();stamp();return}
  render();
  if(!quiet||!es)startLive();
}
/* Live updates: the server pushes the dashboard on every change. If the push channel drops, poll every 5 seconds until it is back. */
function stopLive(){if(es){es.close();es=null}clearInterval(poll);poll=null}
function startPoll(){if(!poll){poll=setInterval(()=>{if(!document.hidden)load(true)},5000)}setLive('poll')}
function startLive(){
  stopLive();
  if(!('EventSource' in window)||(data&&data.push===false))return startPoll();  // push is off on some hosts (Vercel)
  es=new EventSource('/api/teacher/dicts/stream?token='+encodeURIComponent(token)+(section?'&section='+encodeURIComponent(section):''));
  es.onopen=()=>{clearInterval(poll);poll=null;setLive('live')};
  es.onmessage=e=>{let d;try{d=JSON.parse(e.data)}catch(err){return}if(checkBuild(d))return;missionLabels(d);clearInterval(poll);poll=null;data=d;setLive('live');if(!$('#rows'))render();else{tiles();panels();attention();rows();stamp()}};
  es.onerror=()=>startPoll();
}
function setLive(m){liveMode=m;stamp()}
/* Concept and question-type names, and the title, come from the mission this server runs. */
function missionLabels(d){if(d.concept_labels)CONCEPTS=d.concept_labels;if(d.type_labels)TYPES=d.type_labels;
  if(d.short){const b=$('.brand span');if(b)b.textContent=d.short+' · Teacher';document.title=d.short+' · Teacher'}}
/* The server was updated while this page was open: reload so the page has the new buttons, not just new numbers. */
function checkBuild(d){if(!d||!d.build)return false;if(BUILD===null){BUILD=d.build;return false}if(d.build===BUILD)return false;stopLive();location.reload();return true}
function stamp(){const u=$('#updated');if(u)u.innerHTML=`<span class="livedot ${liveMode}"></span>${liveMode==='live'?'Live':liveMode==='poll'?'Live · refreshes every 5 s':'Connecting…'} · updated ${new Date().toLocaleTimeString()}`}
function tiles(){
  const o=data.overview,started=data.students.filter(s=>s.status!=='not started');
  const avgMin=started.length?Math.round(started.reduce((a,s)=>a+s.used_minutes,0)/started.length):0;
  $('#tiles').innerHTML=[[o.students,'Students'],[o.started,'Started'],[o.online,'Online now'],[o.completed,'Completed'],[avgMin+' min','Average time used'],
    [o.avg_done+' / '+data.total_questions,'Average cleared'],[pct(o.accuracy),'Answer accuracy'],[o.flagged,'Integrity flags']].map(([b,s],i)=>`<div class="tile${i===7&&o.flagged?' warn':''}"><b>${b}</b><span>${s}</span></div>`).join('');
}
function panels(){
  const d=data,max=Math.max(1,d.overview.students),col=a=>a<.5?'var(--bad)':a<.75?'var(--gold)':'var(--good)';
  $('#pStages').innerHTML=d.stages.map(s=>`<div class="srow"><span>${esc(s.name)}</span><small>${s.cleared} / ${d.overview.students} cleared</small><span class="sbar${s.cleared===d.overview.students&&s.cleared?' ok':''}"><i style="width:${Math.round(s.cleared/max*100)}%"></i></span></div>`).join('');
  $('#pConcepts').innerHTML=d.concepts.map(c=>`<div class="trow2"><span>${esc(CONCEPTS[c.concept]||c.concept)}</span><span class="tb"><i style="width:${Math.round(c.accuracy*100)}%;background:${col(c.accuracy)}"></i></span><b>${pct(c.accuracy)}</b></div>`).join('')||'<p class="empty">No answers yet.</p>';
  feedback();
  $('#pTypes').innerHTML=d.types.map(t=>`<div class="trow2"><span>${esc(TYPES[t.qtype]||t.qtype)}</span><span class="tb"><i style="width:${Math.round(t.accuracy*100)}%;background:${col(t.accuracy)}"></i></span><b>${pct(t.accuracy)}</b></div>`).join('')||'<p class="empty">No answers yet.</p>';
}
/* End-of-mission feedback: every student fills it in after the mission ends, before seeing the report. */
const FACE=['😴','😕','🙂','😄','🤩'];
function feedback(){
  const f=data.feedback,el=$('#pFb');if(!f||!el)return;
  const wasOpen=!!($('.fball')||{}).open;  // live updates redraw the panel: keep the response table open
  $('#fbCount').textContent=f.count?f.count:'';
  if(!f.count){el.innerHTML=`<p class="empty">Feedback appears here as students finish. Each student fills it in when their mission ends, before they see the report.${f.pending?` ${f.pending} finished student${f.pending>1?'s have':' has'} not sent it yet.`:''}</p>`;return}
  const bars=(list,tot)=>list.map(x=>`<div class="trow2"><span>${esc(x.label)}</span><span class="tb"><i style="width:${tot?Math.round(x.count/tot*100):0}%;background:var(--blue)"></i></span><b>${x.count}</b></div>`).join('');
  const dist=(d,labels)=>`<div class="fbdist">${d.map((c,i)=>`<div><span class="fbcol"><i style="height:${Math.round(c/Math.max(1,...d)*100)}%"></i></span><b>${c}</b><small>${labels[i]}</small></div>`).join('')}</div>`;
  const notes=f.responses.filter(r=>r.improve),top=list=>list.reduce((a,x)=>x.count>a.count?x:a,{count:0});
  el.innerHTML=`<div class="fbtiles">
      <div class="tile"><b>${f.count}${f.ended?' / '+f.ended:''}</b><span>Responses${f.pending?` · ${f.pending} pending`:''}</span></div>
      <div class="tile"><b>${FACE[Math.max(0,Math.round(f.enjoy)-1)]} ${f.enjoy} / 5</b><span>Enjoyed it</span></div>
      <div class="tile"><b>🍅 ${esc(top(f.toughest).label||'–')}</b><span>Toughest stage · ${top(f.toughest).count} vote${top(f.toughest).count===1?'':'s'}</span></div>
      <div class="tile"><b>💪 ${f.confidence} / 5</b><span>Confidence now</span></div></div>
    <div class="fbgrid">
      <div><h3>How much they enjoyed it</h3>${dist(f.enjoy_dist,FACE)}</div>
      <div><h3>Confidence now</h3>${dist(f.confidence_dist,['1','2','3','4','5'])}</div>
      <div><h3>🍅 Toughest stage</h3>${bars(f.toughest,f.count)}</div>
      <div><h3>⭐ Favourite stage</h3>${bars(f.favourite,f.count)}</div>
      <div><h3>Difficulty</h3>${bars(f.difficulty,f.count)}</div>
      <div><h3>Time${f.needed_more_time?` · ${f.needed_more_time} needed more`:''}</h3>${bars(f.pace,f.count)}</div>
      <div><h3>Technical problems</h3>${bars(f.tech,f.count)}</div>
      <div><h3>What helped them learn most</h3>${bars(f.helped,f.count)}</div>
    </div>
    ${notes.length?`<h3>What to improve, in their words · ${notes.length}</h3><ul class="fbnotes">${notes.map(r=>`<li><span class="aname"><b>${esc(r.name)}</b><small>${esc(r.roll_no)} · ${esc(r.section)} · ${FACE[r.enjoy-1]} · 🍅 ${esc(r.toughest_label)}</small></span><div><p>${esc(r.improve)}</p></div></li>`).join('')}</ul>`:''}
    <details class="fball"${wasOpen?' open':''}><summary>All responses (${f.count})</summary><div class="tablewrap"><table><thead><tr><th>Name</th><th>Roll no</th><th>Section</th><th>University</th><th>Contact</th><th>Enjoyed</th><th>Toughest</th><th>Favourite</th><th>Difficulty</th><th>Time</th><th>Confidence</th><th>Helped most</th><th>Tech problems</th><th>Reached</th><th>Sent</th></tr></thead>
      <tbody>${f.responses.map(r=>`<tr><td><b>${esc(r.name)}</b></td><td>${esc(r.roll_no)}</td><td>${esc(r.section)}</td><td>${esc(r.university)}</td><td>${esc(r.contact)}</td><td>${FACE[r.enjoy-1]} ${r.enjoy}</td><td>${esc(r.toughest_label)}</td><td>${esc(r.favourite_label)}</td><td>${esc(r.difficulty_label)}</td><td>${esc(r.pace_label)}</td><td>${r.confidence} / 5</td><td class="fbhelp">${r.helped.map(esc).join('<br>')}</td><td class="${r.tech==='blocked'?'m lo':r.tech==='small'?'m mid':''}">${esc(r.tech_label)}</td><td>${esc(r.reached)}<small>${esc(r.status_label)}</small></td><td>${esc((r.at||'').replace('T',' ').slice(11,16))}</td></tr>`).join('')}</tbody></table></div></details>`;
}
function render(){
  const d=data;
  view.innerHTML=`<section class="dash">
    <div class="dhead2"><div><h1>${d.section?esc(d.section):'All sections'}</h1><p class="sub">${esc(d.title||"")} · ${d.mission_minutes}-minute timed, proctored mission. ${d.max_tab_switches?`A mission ends at ${d.max_tab_switches} tab switches.`:'Tab switches are recorded only.'} <span id="updated"></span></p></div></div>
    ${d.storage==='temporary'?`<div class="endbanner proctor"><b>No database connected: student progress will be lost.</b><p>In Vercel, open this project → Storage → Create Database → Neon (Postgres), connect it to the project, then redeploy.</p></div>`:''}
    <div class="tiles" id="tiles"></div>
    <div class="panel attn" id="attnPanel"><h2>Needs attention <span class="acount" id="attnCount"></span></h2><div id="pAttn"></div></div>
    <div class="cols">
      <div class="panel"><h2>How far the class got</h2><div id="pStages"></div></div>
      <div class="panel"><h2>Hardest ideas first</h2><div id="pConcepts"></div></div>
    </div>
    <div class="panel"><h2>Question types, hardest first</h2><div class="typegrid" id="pTypes"></div></div>
    <div class="panel fb" id="fbPanel"><div class="fbhead"><h2>Student feedback <span class="acount" id="fbCount"></span></h2><button class="nbtn" id="fbExport" type="button">Download feedback CSV</button></div><div id="pFb"></div></div>
    <div class="panel"><h2>Students</h2>
      <div class="tools"><input id="find" type="search" placeholder="Search by name, roll number or university" value="${esc(filter)}"><span class="hint2"><b>Resume</b>: continue an ended mission from exactly where it stopped. Release login: lets a student sign in on another device. Reset mission: erases everything and starts again from zero.</span></div>
      <div class="tablewrap"><table><thead><tr>
        ${[['rank','#'],['name','Name'],['roll_no','Roll no'],['section','Section'],['status','Status'],['current','Now on'],['done','Cleared'],['first_try','First try'],['timed_out','Timed out'],['revealed','Solutions viewed'],['used_minutes','Time used'],['tab_switches','Tab switches'],['copy_paste','Copy/paste'],['weak','Weakest idea'],['last_seen','Last seen']]
          .map(([k,l])=>`<th data-k="${k}"${sortKey===k?` aria-sort="${sortDir>0?'ascending':'descending'}"`:''}>${l}</th>`).join('')}<th>Actions</th>
      </tr></thead><tbody id="rows"></tbody></table></div>
    </div></section>`;
  tiles();panels();attention();stamp();
  $$('th[data-k]').forEach(th=>th.onclick=()=>{const k=th.dataset.k;if(sortKey===k)sortDir=-sortDir;else{sortKey=k;sortDir=['name','roll_no','section','status','weak','rank','current'].includes(k)?1:-1}render()});
  $('#find').oninput=e=>{filter=e.target.value;rows()};
  rows();
}
const weakest=s=>{const w=Object.entries(s.concepts).sort((a,b)=>a[1]-b[1])[0];return w?[CONCEPTS[w[0]]||w[0],w[1]]:null};
function rows(){
  const f=filter.trim().toLowerCase(),max=data.max_tab_switches;
  const STAGE_ORDER=Object.fromEntries(data.stages.map((x,i)=>[x.name,i]));
  const val=(s,k)=>k==='weak'?(weakest(s)||['~'])[0]:k==='current'?(s.current?STAGE_ORDER[s.current.stage]*100+s.current.n:999):s[k]==null?-1:s[k];
  const list=data.students.filter(s=>!f||s.name.toLowerCase().includes(f)||s.roll_no.toLowerCase().includes(f)||(s.university||'').toLowerCase().includes(f))
    .sort((a,b)=>{const x=val(a,sortKey),y=val(b,sortKey);return (typeof x==='string'?x.localeCompare(y):x-y)*sortDir});
  $('#rows').innerHTML=list.map(s=>{const w=weakest(s);
    return `<tr><td>${s.rank}</td><td><b>${esc(s.name)}</b>${s.online?' <span class="dot" title="Signed in right now"></span>':''}${s.university?`<small class="uni">${esc(s.university)}</small>`:''}</td><td>${esc(s.roll_no)}</td><td>${esc(s.section)}</td>
    <td class="m ${STATUS_CLS[s.status]||''}">${esc(s.status_label)}${s.feedback_sent?'<small class="fbsent">feedback sent</small>':''}</td><td class="curcell">${s.current?`<b>${esc(s.current.stage)}${actTag(s)}</b><small title="${esc(s.current.title)}">Q${s.current.n}/${s.current.of} · ${esc(s.current.title)}${s.current.cleared?' (done)':''}</small>`:actTag(s)||'–'}</td><td>${s.done}/${s.total}</td><td>${s.first_try}</td><td>${s.timed_out}</td><td>${s.revealed}</td><td>${s.used_minutes} min</td>
    <td class="${s.tab_switches?(max&&s.tab_switches>=max?'m lo':'m mid'):''}">${s.tab_switches}</td><td class="${s.copy_paste?'m mid':''}">${s.copy_paste}</td>
    <td>${w?esc(w[0])+' · '+Math.round(w[1]*100)+'%':'–'}</td><td>${esc((s.last_seen||'').replace('T',' ').slice(0,16))}</td>
    <td class="acts">${s.can_resume?`<button class="del go" data-a="resume" data-id="${s.id}" type="button">Resume</button>`:''}<button class="del" data-a="release" data-id="${s.id}" type="button"${s.online?'':' disabled'}>Release login</button><button class="del" data-a="reset" data-id="${s.id}" type="button">Reset mission</button><button class="del" data-a="remove" data-id="${s.id}" type="button">Remove</button></td></tr>`}).join('')
    ||`<tr><td colspan="16" class="empty">No students yet. Share the link to the app; students appear here after they sign in.</td></tr>`;
  bindActs();
}
const LABEL={resume:'Tap again: resume',release:'Tap again: sign out',reset:'Tap again: erase and restart',remove:'Tap again: delete student'};
function bindActs(){
  const arm=b=>{b.classList.add('armed');b.textContent=LABEL[b.dataset.a]};
  if(armed){const bs=$$(`#tview .del[data-id="${armed.id}"][data-a="${armed.a}"]`).filter(b=>!b.disabled);if(bs.length&&Date.now()-armed.t<8000)bs.forEach(arm);else armed=null}
  $$('#tview .del').forEach(b=>b.onclick=async()=>{if(!b.classList.contains('armed')){armed={id:b.dataset.id,a:b.dataset.a,t:Date.now()};$$(`#tview .del[data-id="${b.dataset.id}"][data-a="${b.dataset.a}"]`).forEach(arm);return}
    armed=null;const id=b.dataset.id,a=b.dataset.a;b.disabled=true;
    try{if(a==='resume')await api(`/teacher/dicts/${id}/resume`,{method:'POST'});else if(a==='release')await api(`/teacher/students/${id}/release`,{method:'POST'});else if(a==='reset')await api(`/teacher/dicts/${id}/reset`,{method:'POST'});else await api('/teacher/students/'+id,{method:'DELETE'})}catch(e){}
    load(true)});
}
const ago=sec=>sec<60?sec+' s':Math.floor(sec/60)+' min';
function actTag(s){
  if(s.activity==='idle')return ` <span class="atag idle" title="Page open, but no step for ${ago(s.idle_seconds)}">idle ${ago(s.idle_seconds)}</span>`;
  if(s.activity==='offline')return ` <span class="atag off" title="The mission is running but the student's page is not responding">offline</span>`;
  if(s.can_resume)return ` <span class="atag off">${s.status==='proctor'?'ended: tabs':'ended: time'}</span>`;
  return '';
}
/* Students who need the teacher now: stopped moving, dropped off, or had their mission ended. */
function attention(){
  const list=data.students.filter(s=>s.activity==='idle'||s.activity==='offline'||s.can_resume)
    .sort((a,b)=>(b.can_resume-a.can_resume)||(b.idle_seconds-a.idle_seconds));
  $('#attnCount').textContent=list.length?list.length:'';
  $('#attnPanel').classList.toggle('hot',list.length>0);
  const where=s=>s.current?`${esc(s.current.stage)} · Q${s.current.n}/${s.current.of}`:'not on a question';
  const why=s=>s.can_resume?(s.status==='proctor'?`Mission ended: left the tab ${s.tab_switches_now} times`:'Mission ended: time ran out')
    :s.activity==='offline'?'Offline: the page stopped responding':`Not moving for ${ago(s.idle_seconds)}`;
  $('#pAttn').innerHTML=list.length?`<ul class="alist">${list.map(s=>`<li class="${s.can_resume?'end':s.activity}"><span class="aname"><b>${esc(s.name)}</b><small>${esc(s.roll_no)} · ${esc(s.section)}</small></span><span class="awhy">${why(s)}<small>${where(s)}${s.resumes?` · resumed ${s.resumes}×`:''}</small></span>${s.can_resume?`<button class="del go" data-a="resume" data-id="${s.id}" type="button">Resume</button>`:'<span></span>'}</li>`).join('')}</ul>`
    :`<p class="empty">Everyone is moving. Students show up here when they are idle for ${data.idle_minutes} min, go offline, or their mission ends.</p>`;
  bindActs();
}

$('#secSel').onchange=e=>{section=e.target.value;stopLive();load()};
$('#refresh').onclick=()=>load(true);
$('#signout').onclick=signOut;
document.addEventListener('click',async e=>{
  if(!e.target.closest('#fbExport'))return;
  const r=await api('/teacher/dicts/feedback.csv'+(section?'?section='+encodeURIComponent(section):''));const blob=await r.blob();
  const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download=`${(data.short||'mission').toLowerCase().replace(/\s+/g,'-')}-feedback-${(section||'all').toLowerCase().replace(/\s+/g,'-')}.csv`;document.body.appendChild(a);a.click();setTimeout(()=>{URL.revokeObjectURL(a.href);a.remove()},500);
});
$('#export').onclick=async()=>{
  const r=await api('/teacher/dicts/export.csv'+(section?'?section='+encodeURIComponent(section):''));const blob=await r.blob();
  const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download=`${(data.short||'mission').toLowerCase().replace(/\s+/g,'-')}-${(section||'all').toLowerCase().replace(/\s+/g,'-')}.csv`;document.body.appendChild(a);a.click();setTimeout(()=>{URL.revokeObjectURL(a.href);a.remove()},500);
};
token?load():renderLogin();
})();
