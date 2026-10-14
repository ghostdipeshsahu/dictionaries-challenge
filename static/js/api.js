/* Dictionaries · backend client: sign-in, sign-out and authenticated JSON calls. */
const API=(()=>{
  const TOKEN_KEY='dicts-token',USER_KEY='dicts-user';
  let token=null,user=null,online=false;
  try{token=localStorage.getItem(TOKEN_KEY);user=JSON.parse(localStorage.getItem(USER_KEY)||'null')}catch(e){}

  async function call(method,path,body,opts){
    const headers={'Content-Type':'application/json'};
    if(token)headers.Authorization='Bearer '+token;
    const res=await fetch('/api'+path,Object.assign({method,headers,body:body?JSON.stringify(body):undefined},opts||{}));
    if(res.status===401){forget();throw new Error('signed-out')}
    if(!res.ok){let msg='Request failed ('+res.status+')';try{const j=await res.json();if(j.detail)msg=typeof j.detail==='string'?j.detail:JSON.stringify(j.detail)}catch(e){}throw new Error(msg)}
    return res.status===204?null:res.json();
  }
  function remember(t,u){token=t;user=u;try{localStorage.setItem(TOKEN_KEY,t);localStorage.setItem(USER_KEY,JSON.stringify(u))}catch(e){}}
  function forget(){token=null;user=null;try{localStorage.removeItem(TOKEN_KEY);localStorage.removeItem(USER_KEY)}catch(e){}}

  /* Called once at start-up. Resolves to {online, user, needsLogin, classCode, sections}. */
  let sections=[];
  async function boot(){
    try{const ctl=new AbortController(),t=setTimeout(()=>ctl.abort(),5000);
      const h=await call('GET','/health',null,{signal:ctl.signal});clearTimeout(t);online=true;sections=h.sections||[];
      if(!token)return {online,needsLogin:true,classCode:h.class_code_required,sections};
      const me=await call('GET','/me');user=me.student;return {online,user,classCode:h.class_code_required,sections};
    }catch(e){
      if(e.message==='signed-out')return {online:true,needsLogin:true,sections};
      online=false;return {online:false,user:null};
    }
  }
  async function login(name,roll_no,section,class_code){
    const r=await call('POST','/login',{name,roll_no,section,class_code:class_code||null});
    remember(r.token,r.student);online=true;return r;
  }
  async function logout(){try{await call('POST','/logout')}catch(e){}forget()}

  return {boot,login,logout,call,get user(){return user},get online(){return online},get signedIn(){return !!token},get sections(){return sections}};
})();
