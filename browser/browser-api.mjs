let worker,ready=false,sequence=0;
const pending=new Map();
function startWorker(){
  if(worker)return;
  worker=new Worker(new URL('./engine-worker.mjs',import.meta.url),{type:'module'});
  worker.onmessage=({data})=>{
    if(data.type==='ready'){ready=true;return;}
    const request=pending.get(data.id);if(!request)return;
    clearTimeout(request.timer);pending.delete(data.id);
    if(data.error)request.reject(new Error(data.error));else request.resolve(data.result);
  };
  worker.onerror=()=>{for(const request of pending.values()){clearTimeout(request.timer);request.reject(new Error('Browser Python could not start. Refresh and try again.'));}pending.clear();worker.terminate();worker=null;ready=false;};
}
export function browserRequest(path,payload){
  if(!['/api/run','/api/compare'].includes(path))return Promise.reject(new Error('Unsupported browser operation.'));
  startWorker();if(!ready)document.getElementById('status').textContent='Starting browser Python…';
  return new Promise((resolve,reject)=>{
    const id=++sequence;
    const timer=setTimeout(()=>{pending.delete(id);reject(new Error('Python startup took too long. Refresh and check your connection.'));},120000);
    pending.set(id,{resolve,reject,timer});worker.postMessage({id,path,payload});
  });
}
