/* Dictionaries · backend client: sign-in, sign-out and authenticated JSON calls. */
/* The session this page belongs to: /<mission>/... (no prefix: the server's default session). */
const BASE=(()=>{const seg=location.pathname.split('/').filter(Boolean)[0]||'';return seg&&seg!=='teacher'&&seg!=='index.html'?'/'+seg:''})();
const API=(()=>{
  // browser storage is per session, so a sign-in, drafts and the feedback draft of one session never leak into another
  const NS='dicts'+(BASE?'-'+BASE.slice(1):''),key=k=>NS+'-'+k;
  const TOKEN_KEY=key('token'),USER_KEY=key('user');
  let token=null,user=null,online=false;
  try{token=localStorage.getItem(TOKEN_KEY);user=JSON.parse(localStorage.getItem(USER_KEY)||'null')}catch(e){}

  async function call(method,path,body,opts){
    const headers={'Content-Type':'application/json'};
    if(token)headers.Authorization='Bearer '+token;
    const res=await fetch(BASE+'/api'+path,Object.assign({method,headers,body:body?JSON.stringify(body):undefined},opts||{}));
    if(res.status===401){forget();throw new Error('signed-out')}
    if(!res.ok){let msg='Request failed ('+res.status+')';try{const j=await res.json();if(j.detail)msg=typeof j.detail==='string'?j.detail:JSON.stringify(j.detail)}catch(e){}throw new Error(msg)}
    return res.status===204?null:res.json();
  }
  function remember(t,u){token=t;user=u;try{localStorage.setItem(TOKEN_KEY,t);localStorage.setItem(USER_KEY,JSON.stringify(u))}catch(e){}}
  function forget(){token=null;user=null;try{localStorage.removeItem(TOKEN_KEY);localStorage.removeItem(USER_KEY)}catch(e){}}

  /* Called once at start-up. Resolves to {online, user, needsLogin, classCode}. */
  async function boot(){
    try{const ctl=new AbortController(),t=setTimeout(()=>ctl.abort(),5000);
      const h=await call('GET','/health',null,{signal:ctl.signal});clearTimeout(t);online=true;
      if(!token)return {online,needsLogin:true,classCode:h.class_code_required};
      const me=await call('GET','/me');user=me.student;return {online,user,classCode:h.class_code_required};
    }catch(e){
      if(e.message==='signed-out')return {online:true,needsLogin:true};
      online=false;return {online:false,user:null};
    }
  }
  async function login(name,roll_no,section,university,contact,class_code){
    const r=await call('POST','/login',{name,roll_no,section,university,contact,class_code:class_code||null});
    remember(r.token,r.student);online=true;return r;
  }
  async function logout(){try{await call('POST','/logout')}catch(e){}forget()}

  return {boot,login,logout,call,key,base:BASE,get user(){return user},get online(){return online},get signedIn(){return !!token}};
})();
