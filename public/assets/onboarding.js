'use strict';
const steps = ['Basic profile','Professional links','Import sources','Documents','Review extraction','Professional positioning','Website preferences','Review & publish'];
let step = 0;
function render() {
  document.getElementById('step').textContent = `Step ${step+1} of 8`;
  document.getElementById('progress').style.width = `${(step+1)/8*100}%`;
  document.getElementById('step-title').textContent = steps[step];
  document.getElementById('back').disabled = !step;
  document.getElementById('next').textContent = step === 7 ? 'Finish setup' : 'Skip for now';
}
document.getElementById('back').onclick = () => {step=Math.max(0,step-1);render();};
document.getElementById('next').onclick = () => {step=Math.min(7,step+1);render();};
