// Optional Markdown layout check. TeX remains source text in this QA preview.
const fs=require('node:fs'),path=require('node:path');
const {pathToFileURL}=require('node:url');
const {chromium}=require('playwright');
const root=path.resolve(__dirname,'..'),out=path.join(__dirname,'qa');
(async()=>{
 const {marked}=await import(pathToFileURL(require.resolve('marked')).href);
 const tex=[],esc=s=>s.replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;');
 let md=fs.readFileSync(path.join(root,'1106.md'),'utf8');
 md=md.replace(/\$\$([\s\S]*?)\$\$/g,(_,s)=>{let n=tex.length;tex.push(`<div class="display-math">${esc(s.trim())}</div>`);return `\n\nTEXBLOCK${n}END\n\n`;});
 md=md.replace(/\$([^$\r\n]+)\$/g,(_,s)=>{let n=tex.length;tex.push(`<span class="inline-math">${esc(s)}</span>`);return `TEXINLINE${n}END`;});
 let content=marked.parse(md).replace(/<p>TEXBLOCK(\d+)END<\/p>/g,(_,n)=>tex[n]).replace(/TEXINLINE(\d+)END/g,(_,n)=>tex[n]);
 content=content.replace(/<table>[\s\S]*?<\/table>/g,s=>`<div class="table-wrap">${s}</div>`);
 const html=`<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><base href="${pathToFileURL(root+path.sep).href}"><style>*{box-sizing:border-box}body{max-width:900px;margin:auto;padding:36px;color:#26343b;font:18px/1.9 'Segoe UI','Microsoft YaHei',sans-serif}h2{margin-top:56px}h3{margin-top:38px}a{color:#227d82}img{width:100%;height:auto}table{width:100%;border-collapse:collapse;min-width:620px;font-size:16px}th,td{border-bottom:1px solid #d9dfdf;padding:12px;text-align:left}.table-wrap{overflow:auto}th{background:#f4f7f7}.display-math{padding:16px;background:#f4f7f7;white-space:pre;overflow:auto;font:15px/1.6 Consolas,monospace}.inline-math{font:15px Consolas,monospace;overflow-wrap:anywhere}p>em{font-size:16px;color:#647079}code{overflow-wrap:anywhere}li{margin-bottom:8px}@media(max-width:600px){body{padding:20px;font-size:16px}}</style></head><body>${content}</body></html>`;
 fs.writeFileSync(path.join(out,'handout-layout.html'),html);
 const browser=await chromium.launch({channel:'msedge',headless:true}),page=await browser.newPage({viewport:{width:1100,height:1300}});
 await page.goto(pathToFileURL(path.join(out,'handout-layout.html')).href);await page.evaluate(()=>document.fonts.ready);
 const desktop=await page.evaluate(()=>({tables:document.querySelectorAll('table').length,images:document.images.length,brokenImages:[...document.images].filter(x=>!x.complete||x.naturalWidth===0).length,overflow:document.documentElement.scrollWidth>innerWidth,unrenderedStrong:document.body.innerText.includes('**')}));
 for(const [label,name]of [['9.2','sampling'],['10.3','posttraining'],['8.4','diffusion']]){
  await page.locator('h3').filter({hasText:label}).evaluate(e=>e.scrollIntoView());await page.screenshot({path:path.join(out,`handout-${name}.png`)});
 }
 await page.setViewportSize({width:390,height:844});await page.locator('h3').filter({hasText:'9.2'}).evaluate(e=>e.scrollIntoView());await page.screenshot({path:path.join(out,'handout-mobile.png')});
 const mobile=await page.evaluate(()=>({overflow:document.documentElement.scrollWidth>innerWidth}));
 const passed=desktop.tables===7&&desktop.images===30&&!desktop.brokenImages&&!desktop.overflow&&!desktop.unrenderedStrong&&!mobile.overflow;
 const report={status:passed?'passed':'failed',desktop,mobile,mathCheck:'TeX source preserved; this preview checks Markdown layout, not formula typesetting.'};
 fs.writeFileSync(path.join(out,'handout-layout-validation.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report,null,2));await browser.close();if(!passed)process.exitCode=1;
})().catch(e=>{console.error(e);process.exit(1)});
