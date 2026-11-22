// Local review preview: render Markdown and every formula, then inspect in Edge.
const fs=require('node:fs'), path=require('node:path');
const {pathToFileURL}=require('node:url');
const mjRoot='C:/Users/lvxin/.vscode/extensions/james-yu.latex-workshop-10.20.0/node_modules/mathjax-full/js';
const {mathjax}=require(path.join(mjRoot,'mathjax.js'));
const {TeX}=require(path.join(mjRoot,'input/tex.js'));
const {SVG}=require(path.join(mjRoot,'output/svg.js'));
const {liteAdaptor}=require(path.join(mjRoot,'adaptors/liteAdaptor.js'));
const {RegisterHTMLHandler}=require(path.join(mjRoot,'handlers/html.js'));
const {AllPackages}=require(path.join(mjRoot,'input/tex/AllPackages.js'));
const {chromium}=require('playwright');
const root=path.resolve(__dirname,'../..');
const adaptor=liteAdaptor();RegisterHTMLHandler(adaptor);
const jax=mathjax.document('',{InputJax:new TeX({packages:AllPackages,formatError:(_,e)=>{throw e}}),OutputJax:new SVG({fontCache:'none'})});
const escape=s=>s.replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;');
const documents=[{key:'1106',file:path.join(root,'1106.md'),sections:['9.2','10.2']},{key:'rl',file:path.join(root,'强化学习拓展/强化学习_从序贯决策到大模型后训练.md'),sections:['6.3','16.3','20.2']}];
(async()=>{
 const {marked}=await import(pathToFileURL(require.resolve('marked')).href);
 const browser=await chromium.launch({channel:'msedge',headless:true});
 const page=await browser.newPage({viewport:{width:1200,height:900},deviceScaleFactor:1});
 const reports=[];
 for(const item of documents){
  const blocks=[],formulas=[],errors=[];
  let text=fs.readFileSync(item.file,'utf8');
  const stash=html=>{const id=`HANDOUTPROTECTED${blocks.length}END`;blocks.push(html);return id};
  text=text.replace(/```[^\n]*\n[\s\S]*?```/g,m=>'\n\n'+stash(marked.parse(m))+'\n\n');
  const render=(src,display)=>{
   try{const svg=adaptor.outerHTML(jax.convert(src,{display,em:16,ex:8,containerWidth:920}));
    if(svg.includes('data-mjx-error'))errors.push({src,error:'MathJax error output'});
    formulas.push({display,source:src});return stash(`<${display?'div':'span'} class="${display?'math-block':'math-inline'}">${svg}</${display?'div':'span'}>`);
   }catch(e){errors.push({src,error:e.message});return stash(`<code>${escape(src)}</code>`)}
  };
  text=text.replace(/\$\$([\s\S]*?)\$\$/g,(_,src)=>'\n\n'+render(src,true)+'\n\n');
  text=text.replace(/(?<!\\)\$([^\n$]+?)(?<!\\)\$/g,(_,src)=>render(src,false));
  let html=marked.parse(text).replace(/HANDOUTPROTECTED(\d+)END/g,(_,i)=>blocks[+i]);
  html=html.replace(/<p>(<div class="math-block">[\s\S]*?<\/div>)<\/p>/g,'$1');
  html=html.replace(/src="([^"#]+)"/g,(all,ref)=>/^https?:/.test(ref)?all:`src="${pathToFileURL(path.resolve(path.dirname(item.file),ref)).href}"`);
  html=`<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>${item.key} · 审阅预览</title><style>body{max-width:920px;margin:55px auto;padding:0 32px;color:#26343b;font:18px/1.85 "Microsoft YaHei",sans-serif}h1,h2,h3{line-height:1.5}h2{margin-top:65px;border-top:1px solid #d9dfdf;padding-top:25px}h3{margin-top:38px}p{margin:18px 0}img{max-width:100%;height:auto}table{border-collapse:collapse;width:100%;font-size:16px;margin:25px 0}td,th{border-bottom:1px solid #d9dfdf;padding:12px 9px;text-align:left}th{background:#f1f6f5}blockquote{border-left:3px solid #227d82;margin:25px 0;padding:1px 22px;color:#52646b}a{color:#227d82}pre{background:#f5f7f7;padding:18px;overflow:auto}code{font-size:.86em}.math-block{overflow-x:auto;margin:26px 0;padding:8px 0;text-align:center}.math-inline mjx-container{display:inline-block;vertical-align:middle}mjx-container[display="true"]{margin:0!important}svg{max-width:100%;height:auto}em{color:#647079;font-size:.93em}</style><article>${html}</article></html>`;
  const output=path.join(__dirname,`preview-${item.key}.html`);fs.writeFileSync(output,html);
  await page.goto(pathToFileURL(output).href);await page.evaluate(()=>Promise.all([...document.images].map(i=>i.decode())));
  const stats=await page.evaluate(()=>({tables:document.querySelectorAll('table').length,images:document.images.length,failedImages:[...document.images].filter(i=>!i.complete||!i.naturalWidth).length,headings:document.querySelectorAll('h2').length,math:document.querySelectorAll('mjx-container').length,overflow:document.documentElement.scrollWidth>innerWidth,visibleBackslashErrors:[...document.querySelectorAll('mjx-merror,[data-mjx-error]')].map(e=>e.textContent)}));
  for(const prefix of item.sections){const heading=page.locator('h3').filter({hasText:new RegExp('^'+prefix.replaceAll('.','\\.')+' ')});if(await heading.count()===1){await heading.scrollIntoViewIfNeeded();await page.evaluate(el=>window.scrollTo(0,el.getBoundingClientRect().top+scrollY-30),await heading.elementHandle());await page.screenshot({path:path.join(__dirname,`preview-${item.key}-${prefix}.png`)});}}
  const report={document:item.file,displayMath:formulas.filter(f=>f.display).length,inlineMath:formulas.filter(f=>!f.display).length,errors,...stats};reports.push(report);
 }
 await browser.close();const status=reports.every(r=>!r.errors.length&&!r.failedImages&&!r.overflow&&!r.visibleBackslashErrors.length)?'passed':'failed';
 fs.writeFileSync(path.join(__dirname,'render-validation.json'),JSON.stringify({status,reports},null,2));console.log(JSON.stringify({status,reports},null,2));if(status!=='passed')process.exitCode=1;
})().catch(e=>{console.error(e);process.exit(1)});
