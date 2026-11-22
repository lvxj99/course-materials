// Optional browser QA; needs playwright and sharp in NODE_PATH or local node_modules.
const fs=require('node:fs'),path=require('node:path');
const {pathToFileURL}=require('node:url');
const {chromium}=require('playwright');
const sharp=require('sharp');
const root=path.resolve(__dirname,'..'),out=path.join(__dirname,'qa');fs.mkdirSync(out,{recursive:true});
(async()=>{
 const browser=await chromium.launch({channel:'msedge',headless:true});
 const page=await browser.newPage({viewport:{width:1040,height:850},deviceScaleFactor:1});
 const manifest=JSON.parse(fs.readFileSync(path.join(root,'images/manifest.json'),'utf8'));const records=[],errors=[];
 page.on('pageerror',e=>errors.push(e.message));
 for(const f of manifest){
  await page.goto(pathToFileURL(path.join(root,'images',f.file)).href);await page.evaluate(()=>document.fonts.ready);
  const result=await page.evaluate(()=>{const svg=document.querySelector('svg');if(document.querySelector('parsererror'))return {parseError:true};const vb=svg.viewBox.baseVal;
   const texts=[...svg.querySelectorAll('text')].map(t=>{const b=t.getBBox();return {text:t.textContent,x:b.x,y:b.y,w:b.width,h:b.height};});
   const outside=texts.filter(b=>b.x<18||b.y<6||b.x+b.w>vb.width-17||b.y+b.h>vb.height-5);
   const collisions=[];for(let i=0;i<texts.length;i++)for(let j=i+1;j<texts.length;j++){const a=texts[i],b=texts[j];const w=Math.min(a.x+a.w,b.x+b.w)-Math.max(a.x,b.x),h=Math.min(a.y+a.h,b.y+b.h)-Math.max(a.y,b.y);if(w>3&&h>3)collisions.push([a.text,b.text,Math.round(w*h)]);}
   return {outside,collisions,textCount:texts.length,width:vb.width,height:vb.height};});
  await page.locator('svg').screenshot({path:path.join(out,f.file.replace('.svg','.png'))});
  records.push({id:f.id,file:f.file,...result});
 }
 const contact=[];for(let base=0;base<manifest.length;base+=6){const batch=manifest.slice(base,base+6),tiles=[];let top=0;for(let row=0;row<3;row++){const pair=batch.slice(row*2,row*2+2);if(!pair.length)break;const rh=Math.max(...pair.map(f=>Math.round(f.height/2)))+18;for(let c=0;c<pair.length;c++){const b=await sharp(path.join(out,pair[c].file.replace('.svg','.png'))).resize(500).toBuffer();tiles.push({input:b,left:c*500,top});}top+=rh;}
 const dest=path.join(out,`contact-${Math.floor(base/6)+1}.png`);await sharp({create:{width:1000,height:top,channels:3,background:'#e7ecec'}}).composite(tiles).png().toFile(dest);contact.push(dest);
 }
 await page.goto(pathToFileURL(path.join(root,'插图预览.html')).href);await page.evaluate(()=>document.fonts.ready);
 const gallery=await page.evaluate(()=>({figures:document.querySelectorAll('.figure').length,duplicateIds:[...document.querySelectorAll('[id]')].map(x=>x.id).filter((x,i,a)=>a.indexOf(x)!==i),hasHorizontalOverflow:document.documentElement.scrollWidth>innerWidth}));
 await page.locator('#tau').fill('2');await page.locator('#tau').dispatchEvent('input');const temp=await page.locator('#entropy').textContent();
 await page.locator('[data-row="0"]').click();const firstMask=await page.locator('.cell.blocked').count();
 await page.locator('[data-row="3"]').click();const lastMask=await page.locator('.cell.blocked').count();
 await page.locator('[data-filter="Transformer"]').click();const filtered=await page.locator('.figure:not(.hidden)').count();await page.locator('[data-filter="全部"]').click();
 await page.evaluate(()=>scrollTo(0,0));await page.screenshot({path:path.join(out,'gallery-desktop.png')});
 await page.setViewportSize({width:390,height:844});await page.screenshot({path:path.join(out,'gallery-mobile.png')});
 const mobile=await page.evaluate(()=>({pageOverflow:document.documentElement.scrollWidth>innerWidth,svgScrollable:document.querySelector('.canvas').scrollWidth>document.querySelector('.canvas').clientWidth}));
 const issues=records.filter(r=>r.parseError||r.outside.length||r.collisions.length);
 const passed=issues.length===0&&errors.length===0&&gallery.figures===30&&gallery.duplicateIds.length===0&&!gallery.hasHorizontalOverflow&&!mobile.pageOverflow&&firstMask===3&&lastMask===0&&filtered===12&&temp.includes('1.000000');
 const result={status:passed?'passed':'failed',records,gallery,mobile,interactions:{temperature:temp,firstMask,lastMask,filtered},errors,contact};
 fs.writeFileSync(path.join(out,'browser-validation.json'),JSON.stringify(result,null,2));
 console.log(JSON.stringify({status:result.status,figures:records.length,issues,gallery,mobile,interactions:result.interactions,errors,contact},null,2));await browser.close();if(!passed)process.exitCode=1;
})().catch(e=>{console.error(e);process.exit(1)});
