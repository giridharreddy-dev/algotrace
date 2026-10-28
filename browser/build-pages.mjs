import {mkdir,readFile,writeFile,copyFile,cp,access} from 'node:fs/promises';
import {spawnSync} from 'node:child_process';
const output='dist-browser';
await mkdir(`${output}/python/algotrace`,{recursive:true});
for(const file of ['__init__.py','algorithms.py','extra.py'])await copyFile(`algotrace/${file}`,`${output}/python/algotrace/${file}`);
await cp('node_modules/pyodide',`${output}/pyodide`,{recursive:true});
await copyFile('LICENSE',`${output}/LICENSE`);
await copyFile('algotrace/web/style.css',`${output}/style.css`);
await copyFile('algotrace/web/learning.mjs',`${output}/learning.mjs`);
for(const file of ['browser-api.mjs','engine-worker.mjs'])await copyFile(`browser/${file}`,`${output}/${file}`);
let html=await readFile('algotrace/web/index.html','utf8');
html=html.replaceAll('href="/','href="./').replaceAll('src="/','src="./')
 .replace('An offline Python algorithm lab.','A browser-based Python algorithm lab.')
 .replace('Runs on your machine','Python in your browser')
 .replace('Python · No external dependencies','WebAssembly · first run loads the Python runtime');
html=html.replace('Offline · Python standard library · v2.1','Browser edition · Python via WebAssembly · v2.1');
await writeFile(`${output}/index.html`,html);
let app=await readFile('algotrace/web/app.js','utf8');
const original=/async function request\(path, payload\) \{[\s\S]*?\n\}/;
if(!original.test(app))throw new Error('The browser request adapter needs review after upstream changes.');
app="import {browserRequest} from './browser-api.mjs';\n"+app.replace(original,'async function request(path,payload) { return browserRequest(path,payload); }')
 .replace("fetch('/api/catalog')","fetch('./catalog.json')")
 .replace('Check that the Python server is running, then refresh.','Refresh this page and check the deployment assets.')
 .replace('Server unavailable','App unavailable');
await writeFile(`${output}/app.js`,app);
const python=process.env.PYTHON||(process.platform==='win32'?'python':'python3');
const result=spawnSync(python,['-c','import json; from dataclasses import asdict; from algotrace.algorithms import CATALOG; print(json.dumps({k:asdict(v) for k,v in CATALOG.items()},ensure_ascii=False))'],{encoding:'utf8'});
if(result.status!==0)throw new Error(result.stderr||'Could not generate the algorithm catalogue.');
const catalogue=JSON.parse(result.stdout);if(Object.keys(catalogue).length!==32)throw new Error('Review the expected algorithm catalogue.');
await writeFile(`${output}/catalog.json`,JSON.stringify(catalogue));
await writeFile(`${output}/.nojekyll`,'');
await access(`${output}/pyodide/pyodide.mjs`);
await access(`${output}/pyodide/pyodide.asm.wasm`);
console.log('Built 32-algorithm browser edition with the original Python implementation and a self-hosted Pyodide runtime.');
