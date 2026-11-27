import{M as e,a as t,b as n,j as r,l as i,m as a,o,p as s,r as c,t as l,u,y as d}from"./lang-DAyDo4pq.js";var f=r.about;t(o()),n([...document.querySelectorAll(`[data-emergency]`)]),l(`about.html`),d(),c(`/about`),fetch(e(`data/meta.json`),{cache:`no-cache`}).then(e=>e.json()).then(e=>{document.getElementById(`run`).textContent=u(e.weather_run,{weekday:`long`,day:`numeric`,month:`long`,year:`numeric`}),document.getElementById(`credits`).innerHTML=e.credits.map(e=>`
      <div class="card">
        <p><b>${i(e.name)}</b></p>
        <p>${i(f.credit[e.credit]??e.credit)}</p>
        <p class="tag">${i(f.licence[e.licence]??e.licence)}${e.status===`verified`?``:f.beingChecked}</p>
        ${e.use?`<p class="tag">${i(f.use[e.use]??e.use)}</p>`:``}
      </div>`).join(``)+`
      <div class="card"><p><b>${f.protomapsName}</b></p><p>${f.protomapsCredit}</p></div>`});var p=[...a.map(e=>({name:e.latin,photos:e.photos})),...s.map(e=>({name:e.latin,photos:e.photos}))];document.getElementById(`photo-credits`).innerHTML=p.map(e=>e.photos.map(t=>`
  <li><i>${i(t.taxon??e.name)}</i>: <a href="${i(t.page)}" target="_blank" rel="noopener">${i(t.attribution)}</a></li>`).join(``)).join(``);