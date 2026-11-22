// Drawing coordinates are in a 1000-unit-wide page. Text y coordinates are baselines.
'use strict';

const C = {
  ink: '#192d38', muted: '#536670', rule: '#c9d4d5', faint: '#e3e9e8',
  teal: '#146f65', mint: '#e2f1ec', blue: '#35638a', sky: '#e7eff7',
  rust: '#a14b2a', sand: '#f8ebdf', grey: '#eff2f1', white: '#ffffff',
};
const xml = s => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
const num = n => Number(n.toFixed(3));
const pts = points => points.map(([x,y]) => num(x) + ',' + num(y)).join(' ');
const tones = {
  teal: [C.mint,C.teal], blue: [C.sky,C.blue], rust: [C.sand,C.rust],
  grey: [C.grey,C.muted], white: [C.white,C.ink],
};

class Plate {
  constructor(id, number, title, height, takeaway, caption) {
    Object.assign(this,{id,number,title,height,takeaway,caption});
    this.parts = [];
  }
  raw(markup) { this.parts.push(markup); }
  rect(x,y,w,h,fill=C.white,stroke='none',sw=1,r=0) {
    this.raw('<rect x="'+num(x)+'" y="'+num(y)+'" width="'+num(w)+'" height="'+num(h)+'" rx="'+r+'" fill="'+fill+'" stroke="'+stroke+'" stroke-width="'+sw+'"/>');
  }
  circle(x,y,r,fill,stroke='none',sw=1) {
    this.raw('<circle cx="'+num(x)+'" cy="'+num(y)+'" r="'+num(r)+'" fill="'+fill+'" stroke="'+stroke+'" stroke-width="'+sw+'"/>');
  }
  path(d,stroke=C.muted,sw=2,fill='none',dash='') {
    this.raw('<path d="'+d+'" fill="'+fill+'" stroke="'+stroke+'" stroke-width="'+sw+'" stroke-linecap="round" stroke-linejoin="round"'+(dash?' stroke-dasharray="'+dash+'"':'')+'/>');
  }
  poly(points,fill,stroke='none',sw=1) {
    this.raw('<polygon points="'+pts(points)+'" fill="'+fill+'" stroke="'+stroke+'" stroke-width="'+sw+'" stroke-linejoin="round"/>');
  }
  line(x1,y1,x2,y2,c=C.rule,w=1.5,dash='') {
    this.path('M'+num(x1)+' '+num(y1)+' L'+num(x2)+' '+num(y2),c,w,'none',dash);
  }
  wire(points,c=C.muted,w=2,dash='') {
    this.path('M'+points.map(([x,y])=>num(x)+' '+num(y)).join(' L'),c,w,'none',dash);
  }
  arrow(points,c=C.muted,w=2,dash='') {
    const [ex,ey]=points.at(-1), [px,py]=points.at(-2);
    const len=Math.hypot(ex-px,ey-py);
    if (len < .01) throw new Error('Arrow has no direction');
    const ux=(ex-px)/len, uy=(ey-py)/len, size=6+w, half=2.1+w*.65;
    const bx=ex-size*ux, by=ey-size*uy;
    this.wire([...points.slice(0,-1),[bx+ux,by+uy]],c,w,dash);
    this.poly([[ex,ey],[bx-uy*half,by+ux*half],[bx+uy*half,by-ux*half]],c);
  }
  a(x1,y1,x2,y2,c=C.muted,w=2,dash='') {this.arrow([[x1,y1],[x2,y2]],c,w,dash);}
  t(x,y,value,size=18,opt={}) {
    const {anchor='start',color=C.ink,weight=400,limit,italic=false}=opt;
    this.raw('<text x="'+num(x)+'" y="'+num(y)+'" font-size="'+size+'" font-weight="'+weight+'" fill="'+color+'" text-anchor="'+anchor+'"'+(italic?' font-style="italic"':'')+(limit?' data-limit="'+limit+'"':'')+'>'+xml(value)+'</text>');
  }
  mid(x,y,s,size=18,opt={}) {this.t(x,y,s,size,{...opt,anchor:'middle'});}
  end(x,y,s,size=18,opt={}) {this.t(x,y,s,size,{...opt,anchor:'end'});}
  label(x,y,s,color=C.teal) {this.t(x,y,s,20,{weight:650,color});}
  box(x,y,w,h,s,tone='grey',size=18,opt={}) {
    const [fill,ink]=tones[tone];
    this.rect(x,y,w,h,fill,opt.outline?ink:'none',1.3,opt.radius??5);
    this.mid(x+w/2,y+h/2+size*.34,s,size,{weight:opt.weight??600,color:ink,limit:w-7});
  }
  cell(x,y,w,h,s,fill,ink=C.ink,opt={}) {
    this.rect(x,y,w,h,fill,opt.stroke??C.white,opt.sw??1.5,opt.radius??1);
    if(s!==null) this.mid(x+w/2,y+h/2+(opt.size??18)*.34,s,opt.size??18,{color:ink,weight:opt.weight??500,limit:w-4});
  }
  svg() {
    const header=new Plate(), footer=new Plate();
    header.rect(0,0,1000,this.height,C.white);
    header.t(34,45,this.title,31,{weight:700,limit:840});
    header.end(966,43,'图 '+this.number,17,{weight:600,color:C.muted,limit:100});
    header.line(34,65,966,65,C.rule,1.2);
    footer.line(34,this.height-54,966,this.height-54,C.rule,1.2);
    footer.rect(35,this.height-37,4,19,C.teal);
    footer.t(51,this.height-21,this.takeaway,18,{weight:530,limit:914});
    return '<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="'+this.height+'" viewBox="0 0 1000 '+this.height+'" role="img" aria-labelledby="title desc" font-family="Segoe UI, Microsoft YaHei, Noto Sans CJK SC, Cambria Math, sans-serif"><title id="title">'+xml(this.title)+'</title><desc id="desc">'+xml(this.caption)+'</desc>'+header.parts.join('')+this.parts.join('')+footer.parts.join('')+'</svg>';
  }
}

function blend(a,b,t) {
  return '#'+[1,3,5].map(i=>{
    const x=parseInt(a.slice(i,i+2),16),y=parseInt(b.slice(i,i+2),16);
    return Math.round(x+(y-x)*Math.max(0,Math.min(1,t))).toString(16).padStart(2,'0');
  }).join('');
}
function softmax(scores,temp=1) {
  const largest=Math.max(...scores),e=scores.map(s=>Math.exp((s-largest)/temp)),total=e.reduce((a,b)=>a+b);
  return e.map(x=>x/total);
}
function rng(seed) {
  let state=seed>>>0;
  return ()=>{state=(Math.imul(1664525,state)+1013904223)>>>0;return (state+.5)/4294967296;};
}
function normal(random) {return Math.sqrt(-2*Math.log(random()))*Math.cos(2*Math.PI*random());}
function grid(f,x,y,rows,cols,size,style) {
  for(let i=0;i<rows;i++) for(let j=0;j<cols;j++){
    const {fill=C.grey,stroke=C.white,sw=1,s=null,ink=C.ink,font=16}=style(i,j);
    f.cell(x+j*size,y+i*size,size,size,s,fill,ink,{stroke,sw,size:font});
  }
}
function blockVector(f,x,y,values,w,h,accent=C.teal) {
  const step=w/values.length;
  values.forEach((v,i)=>f.rect(x+i*step,y,step-1,h,blend('#edf3f1',accent,.12+.84*v)));
}
module.exports={C,Plate,blend,softmax,rng,normal,grid,blockVector,num,xml};
