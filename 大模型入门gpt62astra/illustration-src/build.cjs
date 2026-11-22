// Rebuild from the course directory with Node.js and Playwright:
//   node illustration-src/build.cjs
//   node illustration-src/build.cjs --verify-handout    (also requires marked)
// A local Microsoft Edge, Google Chrome or Playwright Chromium can render the figures.
'use strict';
const fs=require('node:fs');
const path=require('node:path');
const {chromium}=require('playwright');
const root=path.resolve(__dirname,'..');
const modules=['./transformer.cjs','./generation.cjs','./language.cjs','./systems.cjs'];

function figurePaths(markdown) {
  const refs=new Map();
  for(const m of markdown.matchAll(/^!\[[^\]\r\n]*\]\((images\/(\d+)_[-a-z0-9]+\.png)\)/gm)) {
    const id=Number(m[2]);
    if(refs.has(id)) throw new Error('Duplicate figure '+id);
    refs.set(id,m[1]);
  }
  return refs;
}

// This function runs in the renderer. Font metrics here include the actual CJK fallback.
function inspectLabels(){
  const svg=document.querySelector('svg'),v=svg.viewBox.baseVal,issues=[];
  const labels=Array.from(svg.querySelectorAll('text'),el=>{
    const {x,y,width,height}=el.getBBox();
    const value=el.textContent;
    if(x<0||y<0||x+width>v.width+.2||y+height>v.height+.2)
      issues.push('outside page: '+value);
    if(el.dataset.limit&&width>Number(el.dataset.limit)+1)
      issues.push('too wide: '+value+' ('+Math.round(width)+' > '+el.dataset.limit+')');
    return {x,y,width,height,value};
  });
  for(let i=0;i<labels.length;i++) for(let j=i+1;j<labels.length;j++){
    const a=labels[i],b=labels[j];
    const w=Math.min(a.x+a.width,b.x+b.width)-Math.max(a.x,b.x);
    const h=Math.min(a.y+a.height,b.y+b.height)-Math.max(a.y,b.y);
    if(w>1.5&&h>Math.min(a.height,b.height)*.21) issues.push('overlap: '+a.value+' / '+b.value);
  }
  return issues;
}

async function run(){
  const args=process.argv.slice(2);
  const option=name=>args.includes(name)?args[args.indexOf(name)+1]:undefined;
  const chosen=option('--ids')?.split(',').map(Number);
  const vectorDir=option('--svg-dir')||path.join(__dirname,'svg');
  const markdown=fs.readFileSync(path.join(root,'1106.md'),'utf8');
  const refs=figurePaths(markdown);
  const figures=modules.flatMap(m=>require(m)).map(make=>make());
  if(new Set(figures.map(f=>f.id)).size!==figures.length) throw new Error('Duplicate drawing ID');
  if(!chosen&&figures.length!==refs.size) throw new Error('Missing drawing for a Markdown reference');
  const render=chosen?figures.filter(f=>chosen.includes(f.id)):figures;
  if(chosen&&render.length!==chosen.length)throw new Error('Unknown figure ID');
  fs.mkdirSync(path.join(root,'images'),{recursive:true});
  fs.mkdirSync(vectorDir,{recursive:true});
  const edge=path.join(process.env['ProgramFiles(x86)']||'','Microsoft','Edge','Application','msedge.exe');
  const chrome=path.join(process.env.ProgramFiles||'','Google','Chrome','Application','chrome.exe');
  const binary=process.env.FIGURE_BROWSER||[edge,chrome].find(p=>fs.existsSync(p));
  const browser=await chromium.launch({headless:true,executablePath:binary});
  const issues=[];
  try {
    const page=await browser.newPage({viewport:{width:1000,height:550},deviceScaleFactor:2});
    await page.route(/^https?:/,route=>route.abort());
    for(const f of render){
      const relative=refs.get(f.id);
      if(!relative) throw new Error('No Markdown image for '+f.id);
      const svg=f.svg(),target=path.join(root,relative);
      fs.writeFileSync(path.join(vectorDir,path.basename(target,'.png')+'.svg'),svg);
      await page.setViewportSize({width:1000,height:f.height});
      await page.setContent('<meta charset="utf-8"><style>html,body{margin:0}svg{display:block}</style>'+svg);
      await page.evaluate(()=>document.fonts.ready);
      const findings=await page.evaluate(inspectLabels);
      if(findings.length)issues.push([f.id,findings]);
      const bitmap=await page.screenshot({type:'png',animations:'disabled'});
      if(bitmap.readUInt32BE(16)!==2000||bitmap.readUInt32BE(20)!==2*f.height) throw new Error('Incorrect raster size');
      fs.writeFileSync(target,bitmap);
    }
    if(args.includes('--verify-handout'))await require('./handout-check.cjs')(browser,root,markdown,figures,refs);
  } finally {await browser.close();}
  console.log(render.length+' PNGs rendered at 2x. '+issues.length+' figures with label findings.');
  if(issues.length){console.log(JSON.stringify(issues,null,2));process.exitCode=1;}
}
if(require.main===module)run().catch(e=>{console.error(e);process.exitCode=1;});
module.exports={figurePaths};
