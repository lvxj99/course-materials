// Original 28-by-28 pen strokes. No image datasets, models or downloaded artwork are used.
'use strict';
const {C,blend,rng,normal,num}=require('./drawing.cjs');
const N=28;
const pens={
  2:[[5,8,9,1,22,2,21,9],[21,9,21,14,10,18,5,23],[5,23,11,21,19,24,23,21]],
  3:[[6,6,12,2,21,3,21,8],[21,8,21,12,16,13,12,14],
     [12,14,21,12,24,17,19,22],[19,22,15,26,8,25,5,21]],
};
function digit(kind=2,variant=0){
  const curve=[];
  for(const [x0,y0,x1,y1,x2,y2,x3,y3] of pens[kind]){
    for(let k=0;k<=42;k++){
      const t=k/42,s=1-t;
      const x=s**3*x0+3*s*s*t*x1+3*s*t*t*x2+t**3*x3;
      const y=s**3*y0+3*s*s*t*y1+3*s*t*t*y2+t**3*y3;
      curve.push([x+variant*(.4+(14-y)*.075),y+variant*.51*Math.sin(x/5)]);
    }
  }
  return Array.from({length:N*N},(_,i)=>{
    const x=(i%N)+.5,y=Math.floor(i/N)+.5;
    const d=Math.sqrt(curve.reduce((v,[a,b])=>Math.min(v,(a-x)**2+(b-y)**2),Infinity));
    const radius=1.45+.3*Math.sin((x+y)*.22)+.12*variant;
    return Math.max(0,Math.min(1,.5+(radius-d)*1.2));
  });
}
function tile(f,x,y,side,pixels,{n=N,background='#f1f4ef',ink='#29424a',border=true}={}){
  const levels=32,paths=Array.from({length:levels},()=>[]);
  for(let j=0;j<n;j++){
    let i=0;
    while(i<n){
      const at=k=>Math.max(0,Math.min(levels-1,Math.round(pixels[j*n+k]*(levels-1))));
      const bin=at(i),start=i++;
      while(i<n&&at(i)===bin)i++;
      if(bin)paths[bin].push('M'+start+' '+j+'h'+(i-start)+'v1h-'+(i-start)+'z');
    }
  }
  f.rect(x,y,side,side,background);
  f.raw('<g transform="translate('+num(x)+' '+num(y)+') scale('+num(side/n)+')" shape-rendering="crispEdges">');
  paths.forEach((data,i)=>{if(data.length)f.raw('<path d="'+data.join('')+'" fill="'+blend(background,ink,i/(levels-1))+'"/>');});
  f.raw('</g>');
  if(border)f.rect(x,y,side,side,'none','#a6b7b5',1);
}
function cropPatch(pixels,index){
  const r=Math.floor(index/4),c=index%4;
  return Array.from({length:49},(_,i)=>pixels[(r*7+Math.floor(i/7))*N+c*7+i%7]);
}
function corrupt(pixels,seed){
  const random=rng(seed);
  return pixels.map(v=>random()<.16?Number(random()>.44):Math.max(0,Math.min(1,v+.16*normal(random))));
}

// A two-glyph data distribution lets us sample the actual reverse conditional analytically.
// a and b are adjacent cumulative alphas. The forward kernel has alpha=a/b.
function diffusionSamples(){
  const fromInk=glyph=>glyph.map(v=>2*v-1),toInk=glyph=>glyph.map(v=>Math.max(0,Math.min(1,(v+1)/2)));
  const templates=[fromInk(digit(2)),fromInk(digit(3))],abar=[1,.78,.45,.16,.002];
  const forward=[templates[0]],r1=rng(35453);
  for(let i=1;i<abar.length;i++){
    const alpha=abar[i]/abar[i-1];
    forward.push(forward.at(-1).map(v=>Math.sqrt(alpha)*v+Math.sqrt(1-alpha)*normal(r1)));
  }
  const reverse=new Array(abar.length),r2=rng(8053);
  reverse[4]=Array.from({length:N*N},()=>normal(r2));
  for(let i=4;i>0;i--){
    const a=abar[i],b=abar[i-1],alpha=a/b,xt=reverse[i];
    const logp=templates.map(x0=>-xt.reduce((s,v,k)=>s+(v-Math.sqrt(a)*x0[k])**2,0)/(2*(1-a)));
    const p0=1/(1+Math.exp(logp[1]-logp[0]));
    const x0=templates[r2()<p0?0:1],c0=Math.sqrt(b)*(1-alpha)/(1-a),ct=Math.sqrt(alpha)*(1-b)/(1-a);
    const sd=Math.sqrt((1-b)*(1-alpha)/(1-a));
    reverse[i-1]=xt.map((v,k)=>c0*x0[k]+ct*v+sd*normal(r2));
  }
  return {forward:forward.map(toInk),reverse:reverse.map(toInk)};
}
module.exports={digit,tile,cropPatch,corrupt,diffusionSamples};
