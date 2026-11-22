const fs = require('fs');
const path = require('path');
const {pathToFileURL} = require('url');
const dep = 'C:/Users/lvxin/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/';
const sharp = require(dep+'sharp');
const {marked}=require(dep+'marked');
const {chromium}=require(dep+'playwright');
const root=process.cwd();
const title='半导体光刻领域机器学习应用调研报告';
const escape=s=>s.replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;');
(async()=>{
const figures=fs.readdirSync('assets').filter(f=>f.endsWith('.svg')).sort();
for(const file of figures)await sharp('assets/'+file).png().toFile('.work/'+file.replace('.svg','.png'));
const imgs=await Promise.all(figures.map(async(f,i)=>({input:await sharp('assets/'+f).resize({width:600,height:400,fit:'contain',background:'#ffffff'}).png().toBuffer(),left:(i%2)*600,top:Math.floor(i/2)*400})));
await sharp({create:{width:1200,height:1600,channels:3,background:'#e2e8f0'}}).composite(imgs).png().toFile('.work/figures_contact.png');
const md=fs.readFileSync(title+'.md','utf8');
const math=[];
const protectedMd=md.replace(/\$\$[\s\S]*?\$\$|\$[^\n$]+?\$/g,m=>{const key='MATHPLACEHOLDER'+math.length+'END';math.push(m);return key;});
let body=marked.parse(protectedMd,{gfm:true});
body=body.replace(/MATHPLACEHOLDER(\d+)END/g,(_,n)=>escape(math[+n]));
const html=`<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><base href="../"><title>${title}</title><style>
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:#eef2f6;color:#183247;font:17px/1.9 "Microsoft YaHei",sans-serif}main{max-width:1120px;margin:36px auto;background:white;padding:52px 64px 80px;border:1px solid #dbe3ec;border-radius:14px}h1{font-size:36px;line-height:1.5;letter-spacing:-.5px}h2{font-size:28px;margin:54px 0 18px;padding-top:18px;border-top:2px solid #dbe3ec}h3{font-size:22px;margin:32px 0 12px}p{margin:16px 0}a{color:#1d4ed8;text-decoration:none}a:hover{text-decoration:underline}img{display:block;width:100%;height:auto;margin:28px 0 10px;border:1px solid #e1e7ef;border-radius:8px}p:has(>em:only-child){color:#526477;font-size:15px;line-height:1.8}table{display:block;max-width:100%;overflow-x:auto;border-collapse:collapse;font-size:15px;margin:22px 0;line-height:1.7}td,th{padding:11px 13px;border:1px solid #dbe3ec;min-width:90px;vertical-align:top}th{background:#eef4ff;text-align:left}tr:nth-child(even){background:#f8fafc}code{font-size:.9em;background:#f1f5f9;padding:2px 4px;border-radius:3px;overflow-wrap:anywhere}strong{font-weight:650;color:#122b43}mjx-container[display="true"]{overflow-x:auto;overflow-y:hidden;padding:12px 0}li{margin:9px 0}a[id]{scroll-margin-top:24px}@media(max-width:700px){body{font-size:16px}main{padding:24px 20px;margin:0;border:0;border-radius:0}h1{font-size:28px}h2{font-size:24px}h3{font-size:20px}}@media print{body{background:white}main{border:0;padding:0;margin:0;max-width:none}h2,h3{break-after:avoid}img,table,mjx-container{break-inside:avoid}}
</style><script>window.mathErrors=[];window.MathJax={tex:{inlineMath:[['$','$']],displayMath:[['$$','$$']],packages:{'[-]':['autoload','require','noundefined']},formatError:(jax,e)=>{window.mathErrors.push(e.message);return jax.formatError(e)}},svg:{fontCache:'local'},options:{enableMenu:false}};</script><script defer src=".work/tex-svg.js"></script></head><body><main>${body}</main></body></html>`;
fs.writeFileSync('.work/preview.html',html);
const browser=await chromium.launch({channel:'msedge',headless:true});
const page=await browser.newPage({viewport:{width:1440,height:1100},deviceScaleFactor:1});
const errors=[];page.on('pageerror',e=>errors.push(String(e)));
await page.goto(pathToFileURL(path.join(root,'.work/preview.html')).href);
await page.waitForFunction(()=>window.MathJax?.startup?.document);
await page.evaluate(()=>MathJax.startup.promise);
const audit=await page.evaluate(()=>({mathErrors:window.mathErrors,mathCount:document.querySelectorAll('mjx-container').length,mathErrorNodes:document.querySelectorAll('[data-mjx-error]').length,brokenImages:[...document.images].filter(i=>!i.complete||!i.naturalWidth).map(i=>i.src),horizontalOverflow:document.documentElement.scrollWidth>innerWidth}));
await page.screenshot({path:'.work/report_top.png'});
for(const id of ['sec05','sec06','sec07','sec14']){
 await page.locator('#'+id).scrollIntoViewIfNeeded();
 await page.screenshot({path:'.work/report_'+id+'.png'});
}
// Embed figures so the reading version remains usable as one offline HTML file.
const imageData=Object.fromEntries(figures.map(f=>[f,'data:image/svg+xml;base64,'+fs.readFileSync('assets/'+f).toString('base64')]));
await page.evaluate(data=>{for(const im of document.images){const name=decodeURIComponent(im.getAttribute('src').split('/').pop());if(data[name])im.src=data[name];}},imageData);
await page.evaluate(()=>Promise.all([...document.images].map(i=>i.decode())));
// Build an offline reading version with already rendered SVG mathematics.
const rendered=await page.evaluate(()=>{document.querySelectorAll('script,base').forEach(e=>e.remove());return '<!doctype html>\n'+document.documentElement.outerHTML;});
fs.writeFileSync(title+'_阅读版.html',rendered);
await page.setViewportSize({width:390,height:900});
await page.goto(pathToFileURL(path.join(root,title+'_阅读版.html')).href);
await page.screenshot({path:'.work/report_phone.png'});
audit.phoneOverflow=await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth);
audit.readingVersion=await page.evaluate(()=>({mathCount:document.querySelectorAll('mjx-container').length,images:document.images.length,brokenImages:[...document.images].filter(i=>!i.complete||!i.naturalWidth).length,scripts:document.scripts.length,externalAssets:document.querySelectorAll('link[href^="http"],img[src^="http"],script[src^="http"]').length}));
audit.figureCount=figures.length;audit.pageErrors=errors;
fs.writeFileSync('.work/render_validation.json',JSON.stringify(audit,null,2));
console.log(JSON.stringify(audit,null,2));
await browser.close();
if(audit.mathErrors.length||audit.mathErrorNodes||audit.brokenImages.length||errors.length)process.exitCode=1;
})();
