'use strict';
(() => {
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  const motionButton = document.getElementById('motion-toggle');
  let paused = reduced.matches;
  function setMotion(value) {
    paused = value; document.documentElement.classList.toggle('motion-paused', paused);
    motionButton.setAttribute('aria-pressed', String(paused));
    motionButton.textContent = paused ? 'Enable motion ▷' : 'Pause motion Ⅱ';
    window.dispatchEvent(new CustomEvent('portfolio-motion', {detail:{paused}}));
  }
  window.portfolioMotionPaused = () => paused;
  motionButton.addEventListener('click', () => setMotion(!paused));
  reduced.addEventListener('change', e => setMotion(e.matches)); setMotion(paused);
  const menuButton = document.querySelector('.menu-toggle'), menu = document.getElementById('mobile-menu');
  menuButton.addEventListener('click', () => { menu.hidden = !menu.hidden; menuButton.setAttribute('aria-expanded',String(!menu.hidden)); });
  menu.querySelectorAll('a').forEach(a => a.addEventListener('click', () => {menu.hidden=true;menuButton.setAttribute('aria-expanded','false');}));
  const observer = 'IntersectionObserver' in window ? new IntersectionObserver(entries => entries.forEach(entry => {
    if(entry.isIntersecting) {entry.target.classList.add('visible');observer.unobserve(entry.target);}
  }),{threshold:.06}) : null;
  if(observer && !reduced.matches) document.querySelectorAll('.section-heading,.about-layout,.about-bottom,.capability,.insight-grid article,.timeline article').forEach(el => {el.classList.add('reveal');observer.observe(el);});
  const progress = document.querySelector('.read-progress'); let scrollPending=false;
  function updateProgress() { const total=document.documentElement.scrollHeight-innerHeight; progress.style.width=`${total>0?scrollY/total*100:0}%`;scrollPending=false; }
  addEventListener('scroll',()=>{if(!scrollPending){scrollPending=true;requestAnimationFrame(updateProgress);}}, {passive:true});updateProgress();
  if(matchMedia('(pointer:fine)').matches) document.querySelectorAll('.tilt').forEach(card => {
    card.addEventListener('pointermove',event=>{
      if(paused) return;
      const r=card.getBoundingClientRect();
      card.style.setProperty('--rx',`${-(event.clientY-r.top-r.height/2)/r.height*15}deg`);
      card.style.setProperty('--ry',`${(event.clientX-r.left-r.width/2)/r.width*22}deg`);
    });
    card.addEventListener('pointerleave',()=>{card.style.setProperty('--rx','0deg');card.style.setProperty('--ry','0deg');});
  });
  document.querySelectorAll('[data-filter]').forEach(button=>button.addEventListener('click',()=>{
    document.querySelectorAll('[data-filter]').forEach(b=>{const selected=b===button;b.classList.toggle('active',selected);b.setAttribute('aria-pressed',String(selected));});
    document.querySelectorAll('.project-card').forEach(card=>{card.hidden=button.dataset.filter!=='All work'&&card.dataset.category!==button.dataset.filter;});
  }));
  const projects=JSON.parse(document.getElementById('project-data').textContent), dialog=document.getElementById('project-dialog');
  document.querySelectorAll('[data-project]').forEach(button=>button.addEventListener('click',()=>{
    const project=projects[Number(button.dataset.project)];
    document.getElementById('dialog-title').textContent=project.title;
    document.getElementById('dialog-category').textContent=project.category;
    document.getElementById('dialog-description').textContent=project.description;
    const list=document.getElementById('dialog-scope');list.replaceChildren();
    project.scope.forEach(text=>{const li=document.createElement('li');li.textContent=text;list.append(li);});
    dialog.showModal();
  }));
  document.querySelector('.dialog-close').addEventListener('click',()=>dialog.close());
  dialog.addEventListener('click',event=>{if(event.target===dialog){const r=dialog.getBoundingClientRect();if(event.clientX<r.left||event.clientX>r.right||event.clientY<r.top||event.clientY>r.bottom)dialog.close();}});
  const form=document.getElementById('contact-form'),status=document.getElementById('contact-status');
  form.addEventListener('submit',async event=>{
    event.preventDefault();if(!form.reportValidity())return;
    const button=form.querySelector('button');button.disabled=true;status.hidden=false;status.classList.remove('error');status.textContent='Sending your message…';
    try {
      const controller=new AbortController(), timeout=setTimeout(()=>controller.abort(),15000);
      let response;
      try {response=await fetch(form.action,{method:'POST',body:new FormData(form),headers:{'Accept':'application/json'},signal:controller.signal});}
      finally {clearTimeout(timeout);}
      if(!response.ok)throw new Error('Unable to save');
      status.textContent='Thank you. Your message has been received.';form.reset();
    } catch {status.classList.add('error');status.textContent='Your message could not be saved. Please try again or email falgunichouhan1234@gmail.com.';}
    finally {button.disabled=false;}
  });
})();
