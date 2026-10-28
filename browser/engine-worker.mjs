import {loadPyodide} from './pyodide/pyodide.mjs';
const runtime=(async()=>{
  const python=await loadPyodide({indexURL:new URL('./pyodide/',import.meta.url).href});
  python.FS.mkdirTree('/home/pyodide/algotrace');
  for(const file of ['__init__.py','algorithms.py','extra.py']){
    const response=await fetch(new URL(`./python/algotrace/${file}`,import.meta.url));
    if(!response.ok)throw new Error('Python source files are unavailable.');
    python.FS.writeFile(`/home/pyodide/algotrace/${file}`,await response.text(),{encoding:'utf8'});
  }
  python.runPython(`
import sys, json
sys.path.insert(0, '/home/pyodide')
from algotrace.algorithms import run_algorithm, compare_sorts
def browser_dispatch(path, payload):
    if path == '/api/run':
        return run_algorithm(payload.get('algorithm'), payload.get('values'), payload.get('target'))
    if path == '/api/compare':
        return {'results': compare_sorts(payload.get('values'))}
    raise ValueError('Unsupported operation.')
`);
  self.postMessage({type:'ready'});return python;
})();
let queue=Promise.resolve();
self.onmessage=({data})=>{queue=queue.then(async()=>{
  try{
    const python=await runtime;
    python.globals.set('_browser_path',data.path);
    python.globals.set('_browser_payload',JSON.stringify(data.payload));
    const result=JSON.parse(python.runPython("json.dumps(browser_dispatch(_browser_path,json.loads(_browser_payload)),ensure_ascii=False)"));
    self.postMessage({id:data.id,result});
  }catch(error){self.postMessage({id:data.id,error:String(error.message||error)});}
});};
