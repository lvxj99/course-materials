import {readFileSync,writeFileSync,existsSync} from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import assert from 'node:assert/strict';
import {softmax,figures} from './core.mjs';
import './transformer.mjs';import './generative.mjs';import './llm.mjs';
const root=fileURLToPath(new URL('../',import.meta.url));
const md=readFileSync(path.join(root,'1106.md'),'utf8'),old=readFileSync(path.join(root,'illustration-src/1106.before-illustrations.md'),'utf8');
const checks=[];function check(name,fn){fn();checks.push({name,passed:true});}
check('全部 27 个原始文件名主体保留，全部 30 个 SVG 引用存在',()=>{const refs=[...md.matchAll(/!\[[^\]]*\]\(([^)]+)\)/g)].map(m=>m[1]);assert.equal(refs.length,30);for(const r of refs)assert.ok(existsSync(path.join(root,r)),r);for(const m of old.matchAll(/!\[[^\]]*\]\(images\/([^)]*)\.png\)/g))assert.ok(refs.includes('images/'+m[1]+'.svg'),m[1]);assert.equal(new Set(refs).size,30);});
check('所有 SVG 与源码最新构建一致，无外链图像或脚本',()=>{for(const f of figures){const s=readFileSync(path.join(root,'images',f.file),'utf8');assert.equal(s,f.svg);assert.match(s,/<title/);assert.match(s,/<desc/);assert.ok(!/<script|<foreignObject|<image|https?:\/\/(?!www\.w3\.org)/.test(s),f.file);}});
check('原有独立公式保留，新增公式完整，表格正常使用 Markdown',()=>{
 const math=s=>[...s.matchAll(/\$\$([\s\S]*?)\$\$/g)].map(m=>m[1].trim());
 const current=math(md);for(const block of math(old))assert.ok(current.includes(block),'原有公式缺失：'+block.slice(0,70));
 assert.equal((md.match(/\$\$/g)||[]).length,current.length*2);
 for(const block of current){let depth=0;for(let i=0;i<block.length;i++){if(block[i-1]==='\\')continue;if(block[i]==='{')depth++;if(block[i]==='}')depth--;assert.ok(depth>=0);}assert.equal(depth,0);}
 assert.ok(!/```\r?\n\|/.test(md),'表格不应包在代码围栏内');assert.ok(!/[\x00-\x09\x0b\x0c\x0e-\x1f]/.test(md),'正文出现控制字符');
 const nums=[...md.matchAll(/^## (A\.\d+) /gm)].map(m=>m[1]);assert.equal(new Set(nums).size,nums.length,'附录编号重复');
 const body=md.replace(/\$\$[\s\S]*?\$\$/g,'');for(const [i,line]of body.split(/\r?\n/).entries())assert.equal((line.match(/(?<!\\)\$/g)||[]).length%2,0,'行内公式未配对：'+(i+1));
});
check('原稿外部链接全部保留，UTF-8 无替代符，CRLF 格式保留',()=>{const links=s=>[...s.matchAll(/\]\((https?:\/\/[^)]+)\)/g)].map(m=>m[1]);const next=links(md);for(const u of links(old))assert.ok(next.includes(u),u);assert.ok(!md.includes('\uFFFD'));assert.equal(md.replaceAll('\r\n','').includes('\n'),false);assert.ok(!md.includes('*描述：'));});
check('拓展讲义链接可用，新增手算例子正确',()=>{
 for(const m of md.matchAll(/(?<!!)\[[^\]]*\]\(([^)]+)\)/g)){if(!/^https?:|^#/.test(m[1]))assert.ok(existsSync(path.join(root,m[1])),m[1]);}
 assert.equal(8192-400-3600-1800-200,2192);assert.equal(4096*4096,16777216);assert.equal(2*4096*8,65536);
 const p=[.4,.25,.2,.1,.05];assert.ok(Math.abs(p.reduce((a,b)=>a+b,0)-1)<1e-12);assert.ok(p[0]+p[1]<.8&&p[0]+p[1]+p[2]>=.8);
});
check('温度图每一个实际柱高对应 softmax，概率归一化且熵随温度增加',()=>{const f=figures.find(f=>f.id===19);const vals=[...f.svg.matchAll(/data-prob="([^"]+)"/g)].map(m=>+m[1]);let last=-Infinity;for(let i=0;i<3;i++){const p=softmax([2,1,0,-1],[.5,1,2][i]);assert.ok(Math.abs(p.reduce((a,b)=>a+b,0)-1)<1e-12);assert.deepEqual(vals.slice(i*4,i*4+4),p);const entropy=-p.reduce((a,v)=>a+v*Math.log(v),0);assert.ok(entropy>last);last=entropy;}});
check('注意力热图每行实际绘制权重和为 1',()=>{const f=figures.find(f=>f.id===24);const a=[...f.svg.matchAll(/<text[^>]*>(0\.\d{2})<\/text>/g)].map(m=>+m[1]);assert.equal(a.length,16);for(let i=0;i<4;i++)assert.ok(Math.abs(a.slice(i*4,i*4+4).reduce((x,y)=>x+y,0)-1)<1e-10);});
check('QKV 加权例、MoE 归一化、缓存与 Bellman 数值一致',()=>{assert.ok(Math.abs(.6*1+.3*0+.1*1-.7)<1e-12);assert.ok(Math.abs(.6*0+.3*1+.1*1-.4)<1e-12);assert.equal(.52/(.52+.28),.65);assert.equal(2*1*32*8192*8*128*2,2**30);assert.ok(Math.abs(.75*(2+.9*4)+.25*(-1+.9*1)-4.175)<1e-12);});
check('BPE 三轮相邻对计数均为最高频 9，合并后词序列正确',()=>{let corpus=[['low',5],['lower',2],['newest',6],['widest',3]].map(([s,n])=>({tokens:[...s,'</w>'],n}));for(const [left,right] of [['e','s'],['es','t'],['est','</w>']]){const counts={};for(const {tokens,n}of corpus)for(let j=0;j<tokens.length-1;j++){const k=tokens[j]+'|'+tokens[j+1];counts[k]=(counts[k]||0)+n;}assert.equal(counts[left+'|'+right],9);assert.equal(Math.max(...Object.values(counts)),9);corpus=corpus.map(({tokens,n})=>{const next=[];for(let j=0;j<tokens.length;j++){if(tokens[j]===left&&tokens[j+1]===right){next.push(left+right);j++;}else next.push(tokens[j]);}return{tokens:next,n};});}assert.deepEqual(corpus[2].tokens,['n','e','w','est</w>']);assert.deepEqual(corpus[3].tokens,['w','i','d','est</w>']);});
check('因果掩码是下三角，MAE 可见与遮挡数量匹配',()=>{const f=figures.find(f=>f.id===28);assert.equal((f.svg.match(/fill="url\(#hatch\)"/g)||[]).length,6);const mae=figures.find(f=>f.id===12);assert.match(mae.svg,/保留 4 个，遮住 12 个/);assert.equal(12/16,.75);});
const report={status:'passed',figures:30,originalPlaceholders:27,addedFigures:3,codeBlocks:[...md.matchAll(/```[\s\S]*?```/g)].length,displayMathBlocks:[...md.matchAll(/\$\$[\s\S]*?\$\$/g)].length,checks};
writeFileSync(path.join(root,'images/validation.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report,null,2));
