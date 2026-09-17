/* Native WebGL ray-marched sculpture. No external 3D library or model download. */
'use strict';
(() => {
  const canvas=document.getElementById('brand-canvas'),stage=document.getElementById('art-stage');
  if(!canvas||!stage)return;
  const gl=canvas.getContext('webgl',{alpha:true,antialias:false,powerPreference:'low-power'});
  if(!gl)return; // CSS 3D sculpture remains visible.
  const vertex=`attribute vec2 aPosition;void main(){gl_Position=vec4(aPosition,0.,1.);}`;
  const fragment=`precision highp float;
    uniform vec2 uResolution;uniform vec2 uPointer;uniform float uTime;
    mat2 rotation(float a){float c=cos(a),s=sin(a);return mat2(c,-s,s,c);}
    float torus(vec3 p,vec2 t){return length(vec2(length(p.xz)-t.x,p.y))-t.y;}
    vec2 scene(vec3 p){
      p.xz=rotation(uTime*.16+uPointer.x*.7+.3)*p.xz;
      p.yz=rotation(.35+uPointer.y*.45)*p.yz;
      vec3 a=p;a.xy=rotation(.85)*a.xy;
      float d=torus(a,vec2(.94,.25));float m=1.;
      vec3 b=p-vec3(.13,.04,0.);b.yz=rotation(1.55)*b.yz;b.xy=rotation(-.65)*b.xy;
      float d2=torus(b,vec2(.80,.20));if(d2<d){d=d2;m=2.;}
      vec3 c=p;c.xy=rotation(-.6)*c.xy;c.yz=rotation(.7)*c.yz;
      float d3=torus(c,vec2(1.02,.14));if(d3<d){d=d3;m=3.;}
      return vec2(d,m);
    }
    vec3 normal(vec3 p){vec2 e=vec2(.002,0.);return normalize(vec3(scene(p+e.xyy).x-scene(p-e.xyy).x,scene(p+e.yxy).x-scene(p-e.yxy).x,scene(p+e.yyx).x-scene(p-e.yyx).x));}
    float ao(vec3 p,vec3 n){float occ=0.;float sca=1.;for(int i=1;i<=4;i++){float h=.07*float(i);occ+=(h-scene(p+n*h).x)*sca;sca*=.6;}return clamp(1.-occ*1.8,.25,1.);}
    void main(){
      vec2 uv=(gl_FragCoord.xy-.5*uResolution)/min(uResolution.x,uResolution.y);
      vec3 ro=vec3(0.,.12,4.7),rd=normalize(vec3(uv*3.1,-4.5));float t=0.;vec2 hit=vec2(0.);
      for(int i=0;i<72;i++){hit=scene(ro+rd*t);if(hit.x<.002||t>8.)break;t+=hit.x*.78;}
      if(t>8.){gl_FragColor=vec4(0.);return;}
      vec3 p=ro+rd*t;if(scene(p).x>.015){gl_FragColor=vec4(0.);return;}
      vec3 n=normal(p),l=normalize(vec3(-3.,5.,4.)),v=normalize(ro-p),h=normalize(l+v);
      vec3 col=hit.y<1.5?vec3(.48,.55,.33):(hit.y<2.5?vec3(.74,.34,.20):vec3(.76,.65,.43));
      float diffuse=max(dot(n,l),0.);float spec=pow(max(dot(n,h),0.),48.);float rim=pow(1.-max(dot(n,v),0.),3.);
      col*=.38+.64*diffuse;col*=ao(p,n);col+=vec3(1.,.93,.79)*spec*.45+vec3(.9,.92,.73)*rim*.15;
      col=pow(col,vec3(.85));gl_FragColor=vec4(col,1.);
    }`;
  function shader(type,source){const s=gl.createShader(type);gl.shaderSource(s,source);gl.compileShader(s);if(!gl.getShaderParameter(s,gl.COMPILE_STATUS)){gl.deleteShader(s);return null;}return s;}
  const vs=shader(gl.VERTEX_SHADER,vertex),fs=shader(gl.FRAGMENT_SHADER,fragment);
  if(!vs||!fs)return;
  const program=gl.createProgram();gl.attachShader(program,vs);gl.attachShader(program,fs);gl.linkProgram(program);
  if(!gl.getProgramParameter(program,gl.LINK_STATUS))return;
  gl.useProgram(program);const buffer=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,buffer);
  gl.bufferData(gl.ARRAY_BUFFER,new Float32Array([-1,-1,1,-1,-1,1,-1,1,1,-1,1,1]),gl.STATIC_DRAW);
  const a=gl.getAttribLocation(program,'aPosition');gl.enableVertexAttribArray(a);gl.vertexAttribPointer(a,2,gl.FLOAT,false,0,0);
  const resolution=gl.getUniformLocation(program,'uResolution'),pointer=gl.getUniformLocation(program,'uPointer'),time=gl.getUniformLocation(program,'uTime');
  let target=[0,0],current=[0,0],elapsed=0,last=0,frame=0,visible=true,lost=false;
  let paused=window.portfolioMotionPaused?window.portfolioMotionPaused():matchMedia('(prefers-reduced-motion: reduce)').matches;
  function resize(){const r=stage.getBoundingClientRect(),dpr=Math.min(devicePixelRatio||1,1.35);canvas.width=Math.min(Math.round(r.width*dpr),760);canvas.height=Math.min(Math.round(r.height*dpr),760);gl.viewport(0,0,canvas.width,canvas.height);draw();}
  function draw(){if(lost)return;gl.uniform2f(resolution,canvas.width,canvas.height);gl.uniform2f(pointer,current[0],current[1]);gl.uniform1f(time,elapsed);gl.drawArrays(gl.TRIANGLES,0,6);}
  function tick(now){frame=0;if(paused||!visible||document.hidden||lost){last=0;return;}if(now-last>32){elapsed+=last?Math.min((now-last)/1000,.06):0;last=now;current=current.map((v,i)=>v+(target[i]-v)*.08);draw();}frame=requestAnimationFrame(tick);}
  function resume(){if(!frame&&!paused&&visible&&!document.hidden&&!lost)frame=requestAnimationFrame(tick);}
  stage.addEventListener('pointermove',event=>{if(paused)return;const r=stage.getBoundingClientRect();target=[(event.clientX-r.left)/r.width-.5,(event.clientY-r.top)/r.height-.5];});
  stage.addEventListener('pointerleave',()=>{target=[0,0];});
  window.addEventListener('portfolio-motion',event=>{paused=event.detail.paused;if(paused){cancelAnimationFrame(frame);frame=0;last=0;}else resume();});
  document.addEventListener('visibilitychange',resume);
  if('IntersectionObserver'in window)new IntersectionObserver(entries=>{visible=entries[0].isIntersecting;resume();},{threshold:.01}).observe(stage);
  if('ResizeObserver'in window)new ResizeObserver(resize).observe(stage);else addEventListener('resize',resize);
  canvas.addEventListener('webglcontextlost',event=>{event.preventDefault();lost=true;cancelAnimationFrame(frame);frame=0;stage.classList.remove('webgl-ready');});
  // After context loss, the animated CSS object remains the stable fallback.
  resize();stage.classList.add('webgl-ready');resume();
})();
