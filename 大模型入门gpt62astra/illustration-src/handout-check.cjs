'use strict';
const fs=require('node:fs');
const path=require('node:path');
const {pathToFileURL}=require('node:url');

// Verify the PNGs through a Markdown renderer and the browser's normal image loader.
// Routes are served entirely from this course folder; no web server or network is needed.
module.exports=async function checkHandout(browser,root,markdown,figures,refs){
  const {marked}=await import(pathToFileURL(require.resolve('marked')).href);
  const html='<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><style>'+
    '*{box-sizing:border-box}body{margin:0;color:#192d38;font:17px/1.85 "Segoe UI","Microsoft YaHei",sans-serif}'+
    'main{max-width:860px;padding:20px 22px;margin:auto}img{display:block;max-width:100%;height:auto}'+
    'p{overflow-wrap:anywhere}pre{overflow:auto}p:has(>img){margin:1.4em 0 .4em}p:has(>img)+p{margin:.4em 0 1.5em;color:#405660}'+
    '</style><main>'+marked.parse(markdown)+'</main></html>';
  const relativePaths=new Set(refs.values());
  const host='http://course-figures.test',page=await browser.newPage();
  const issues=[];
  await page.route('**/*',route=>{
    const url=new URL(route.request().url()),file=decodeURIComponent(url.pathname.slice(1));
    if(url.origin!==host)return route.abort();
    if(file==='1106.html')return route.fulfill({contentType:'text/html; charset=utf-8',body:html});
    if(relativePaths.has(file))return route.fulfill({contentType:'image/png',path:path.join(root,file)});
    return route.fulfill({status:404,body:''});
  });
  try{
    await page.goto(host+'/1106.html');
    await page.locator('img').evaluateAll(nodes=>Promise.all(nodes.map(img=>img.decode())));
    for(const width of [940,390]){
      await page.setViewportSize({width,height:820});
      const loads=await page.locator('img').evaluateAll(images=>images.map(img=>{
        const box=img.getBoundingClientRect(),paragraph=img.closest('p');
        return {src:img.getAttribute('src'),alt:img.alt,w:img.naturalWidth,h:img.naturalHeight,
          fits:box.width>0&&box.x>=0&&box.right<=innerWidth+.2,
          separateParagraph:paragraph?.childNodes.length===1&&!img.closest('li'),
          caption:paragraph?.nextElementSibling?.querySelector('em')?.textContent||''};
      }));
      if(loads.length!==figures.length)issues.push(width+'px: number of images '+loads.length);
      for(let i=0;i<loads.length;i++){
        const item=loads[i],f=figures[i];
        if(!f||item.src!==refs.get(f.id)||!item.alt||item.w!==2000||item.h!==2*f.height||
          !item.fits||!item.separateParagraph||item.caption!=='图 '+f.number+'　'+f.caption)issues.push(width+'px: '+JSON.stringify(item));
      }
      if(process.env.FIGURE_QA_DIR){
        const example=page.locator('img[src*="15_diffusion"]');
        await example.evaluate(el=>window.scrollTo(0,window.scrollY+el.getBoundingClientRect().top-18));
        fs.mkdirSync(process.env.FIGURE_QA_DIR,{recursive:true});
        await page.screenshot({path:path.join(process.env.FIGURE_QA_DIR,'lecture-'+width+'.png')});
      }
    }
  }finally{await page.close();}
  if(issues.length)throw new Error('Markdown rendering: '+issues.join('\n'));
  console.log(figures.length+' figures and captions loaded in reading order at 940px and 390px.');
};
