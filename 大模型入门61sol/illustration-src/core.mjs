export const C={ink:'#26343b',muted:'#647079',rule:'#d9dfdf',paper:'#ffffff',soft:'#f5f7f7',teal:'#227d82',tealLight:'#e4f1f0',orange:'#b76343',orangeLight:'#faeee7',blue:'#4c75a0',blueLight:'#eaf0f8',purple:'#7d6a9b',purpleLight:'#f0edf6'};
export const esc=s=>String(s).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;');
export const n=x=>Number(x.toFixed(3));
export function mix(a,b,t){let aa=a.slice(1).match(/../g).map(v=>parseInt(v,16)),bb=b.slice(1).match(/../g).map(v=>parseInt(v,16));return '#'+aa.map((v,i)=>Math.round(v+(bb[i]-v)*t).toString(16).padStart(2,'0')).join('');}
export function softmax(a,t=1){const m=Math.max(...a);const v=a.map(x=>Math.exp((x-m)/t));const z=v.reduce((x,y)=>x+y,0);return v.map(x=>x/z);}
export function rng(seed=42){return ()=>{seed|=0;seed=seed+0x6D2B79F5|0;let t=Math.imul(seed^seed>>>15,1|seed);t=t+Math.imul(t^t>>>7,61|t)^t;return ((t^t>>>14)>>>0)/4294967296;};}
export function gaussian(r){return Math.sqrt(-2*Math.log(Math.max(1e-12,r())))*Math.cos(2*Math.PI*r());}
export class Fig{
 constructor(id,title,sub,h=560){this.id=id;this.title=title;this.sub=sub;this.h=h;this.a=[];this.text(40,43,`FIG ${String(id).padStart(2,'0')}`,14,C.teal,'start',650);this.text(40,83,title,29,C.ink,'start',650);this.text(40,116,sub,17,C.muted);this.line(40,137,960,137,C.rule,1);}
 add(s){this.a.push(s);return this;}
 text(x,y,s,size=19,fill=C.ink,anchor='start',weight=400,extra=''){if(s==='')return this;return this.add(`<text x="${n(x)}" y="${n(y)}" font-size="${size}" fill="${fill}" text-anchor="${anchor}" font-weight="${weight}" ${extra}>${esc(s)}</text>`);}
 lines(x,y,arr,size=18,fill=C.muted,gap=28,anchor='start'){arr.forEach((s,i)=>this.text(x,y+i*gap,s,size,fill,anchor));return this;}
 rect(x,y,w,h,fill=C.soft,stroke=C.rule,r=6,extra=''){return this.add(`<rect x="${n(x)}" y="${n(y)}" width="${n(w)}" height="${n(h)}" rx="${r}" fill="${fill}" stroke="${stroke}" ${extra}/>`);}
 line(x1,y1,x2,y2,color=C.rule,width=1.5,extra=''){return this.add(`<line x1="${n(x1)}" y1="${n(y1)}" x2="${n(x2)}" y2="${n(y2)}" stroke="${color}" stroke-width="${width}" ${extra}/>`);}
 path(d,color=C.ink,width=1.7,fill='none',extra=''){return this.add(`<path d="${d}" stroke="${color}" stroke-width="${width}" fill="${fill}" stroke-linecap="round" stroke-linejoin="round" ${extra}/>`);}
 arrow(x1,y1,x2,y2,color=C.muted,width=1.7,dash=false){return this.line(x1,y1,x2,y2,color,width,`marker-end="url(#arrow-${color.slice(1)})"${dash?' stroke-dasharray="5 5"':''}`);}
 route(points,color=C.muted,width=1.7,dash=false){return this.path(points.map((p,i)=>`${i?'L':'M'}${n(p[0])},${n(p[1])}`).join(' '),color,width,'none',`marker-end="url(#arrow-${color.slice(1)})"${dash?' stroke-dasharray="5 5"':''}`);}
 circle(x,y,r,fill=C.paper,stroke=C.rule,width=1.5){return this.add(`<circle cx="${n(x)}" cy="${n(y)}" r="${n(r)}" fill="${fill}" stroke="${stroke}" stroke-width="${width}"/>`);}
 box(x,y,w,h,label,fill=C.soft,stroke=C.rule,size=19){this.rect(x,y,w,h,fill,stroke);const ls=Array.isArray(label)?label:[label];ls.forEach((t,i)=>this.text(x+w/2,y+h/2+6+(i-(ls.length-1)/2)*25,t,size,C.ink,'middle'));return this;}
 label(x,y,s,color=C.teal){return this.text(x,y,s,18,color,'start',600);}
 footer(s,s2){this.line(40,this.h-72,960,this.h-72,C.rule,1);this.text(40,this.h-43,s,16,C.muted);if(s2)this.text(40,this.h-18,s2,15,C.muted);return this;}
 matrix(x,y,values,cell=42,{color=C.teal,show=true,highlight=-1,masked=false}={}){values.forEach((row,i)=>row.forEach((v,j)=>{const off=v===null;this.rect(x+j*cell,y+i*cell,cell-3,cell-3,off?'url(#hatch)':mix('#f2f7f7',color,Math.max(0,Math.min(1,v))),C.paper,2);if(show)this.text(x+j*cell+(cell-3)/2,y+i*cell+cell*.61,off?'—':v.toFixed(2),Math.min(16,cell*.27),v>.56?C.paper:C.ink,'middle');}));if(highlight>=0)this.rect(x-4,y+highlight*cell-4,values[0].length*cell+5,cell+5,'none',C.orange,4,'stroke-width="2.5"');return this;}
 tokens(x,y,arr,{w=82,h=40,gap=8,active=-1,color=C.teal}={}){arr.forEach((s,i)=>this.box(x+i*(w+gap),y,w,h,s,i===active?mix(C.paper,color,.12):C.soft,i===active?color:C.rule,18));return this;}
 plot(x,y,w,h,{xmin=0,xmax=1,ymin=0,ymax=1,xticks=[0,.5,1],yticks=[0,.5,1],xlabel='',ylabel=''}={}){const p=(a,b)=>[x+(a-xmin)/(xmax-xmin)*w,y+h-(b-ymin)/(ymax-ymin)*h];yticks.forEach(v=>{const yy=p(0,v)[1];this.line(x,yy,x+w,yy,C.rule,1);this.text(x-12,yy+5,String(v),15,C.muted,'end');});xticks.forEach(v=>{const xx=p(v,0)[0];this.line(xx,y+h,xx,y+h+5,C.muted);this.text(xx,y+h+24,String(v),15,C.muted,'middle');});this.line(x,y,x,y+h,C.muted);this.line(x,y+h,x+w,y+h,C.muted);this.text(x+w/2,y+h+53,xlabel,17,C.muted,'middle');this.text(x,y-17,ylabel,17,C.muted);return p;}
 curve(points,color=C.teal,width=2.5,dash=false){return this.path(points.map((p,i)=>`${i?'L':'M'}${n(p[0])},${n(p[1])}`).join(' '),color,width,'none',dash?'stroke-dasharray="5 5"':'');}
 svg(desc){return `<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="${this.h}" viewBox="0 0 1000 ${this.h}" role="img" aria-labelledby="title desc"><title id="title">${esc(this.title)}</title><desc id="desc">${esc(desc||this.sub)}</desc><defs>${Object.values(C).filter(v=>v.startsWith('#')).map(v=>`<marker id="arrow-${v.slice(1)}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M 1 1 L 9 5 L 1 9 Z" fill="${v}"/></marker>`).join('')}<pattern id="hatch" width="8" height="8" patternUnits="userSpaceOnUse"><rect width="8" height="8" fill="#f4f4f3"/><path d="M-2 2L2-2M0 8L8 0M6 10L10 6" stroke="#d9dedd" stroke-width="1"/></pattern></defs><style>text{font-family:"Segoe UI","Microsoft YaHei","Noto Sans CJK SC",sans-serif}svg{background:#fff}</style><rect width="1000" height="${this.h}" fill="white"/>${this.a.join('\n')}</svg>`;}
}
// An analytic, synthetic grayscale glyph. Pixel values are made by code, not a trained model.
export function glyph(f,x,y,size,{noise=0,seed=4,variant=0,signal=1,grid=16,mask=null,outlines=false,normalized=false}={}){
 const rand=rng(seed),cell=size/grid;
 for(let j=0;j<grid;j++)for(let i=0;i<grid;i++){
  const px=(i+.5)/grid,py=(j+.5)/grid;
  let a=Math.abs(py-.23)<.07&&px>.25&&px<.78;
  let b=Math.abs(px-(.78-.48*(py-.23)/.64+variant*.03))<.065&&py>.23&&py<.87;
  const clean=a||b?.94:.04;
  let v=signal*(normalized?2*clean-1:clean)+noise*gaussian(rand);if(normalized)v=(v+1)/2;v=Math.max(0,Math.min(1,v));
  const mi=Math.floor(j/4)*4+Math.floor(i/4),hidden=mask&&mask.includes(mi);
  f.rect(x+i*cell,y+j*cell,cell+.1,cell+.1,hidden?'#e5e9e9':mix('#f5f7f7',C.ink,v),'none',0);
 }
 if(outlines)for(let j=0;j<4;j++)for(let i=0;i<4;i++)f.rect(x+i*size/4,y+j*size/4,size/4,size/4,'none',C.paper,0);
 f.rect(x,y,size,size,'none',C.rule,2);
}
export const source={transformer:'https://arxiv.org/abs/1706.03762',rope:'https://arxiv.org/abs/2104.09864',mae:'https://arxiv.org/abs/2111.06377',vae:'https://arxiv.org/abs/1312.6114',gan:'https://arxiv.org/abs/1406.2661',ddpm:'https://arxiv.org/abs/2006.11239',sde:'https://arxiv.org/abs/2011.13456',flow:'https://arxiv.org/abs/2210.02747',bpe:'https://arxiv.org/abs/1508.07909',kv:'https://huggingface.co/docs/transformers/main/cache_explanation',moe:'https://arxiv.org/abs/2401.04088',dpo:'https://arxiv.org/abs/2305.18290',rag:'https://arxiv.org/abs/2005.11401',rl:'http://incompleteideas.net/book/the-book-2nd.html'};
export const figures=[];
export function save(f,slug,caption,refs=[],note='概念示意，由代码绘制。'){figures.push({id:f.id,file:`${String(f.id).padStart(2,'0')}_${slug}.svg`,title:f.title,caption,refs,note,svg:f.svg(caption),height:f.h});}
