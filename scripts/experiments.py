#!/usr/bin/env python3
"""Automação opcional: o aluno pode executar tudo manualmente seguindo o guia."""
import subprocess,pathlib,os,time,json,datetime,platform
ROOT=pathlib.Path(__file__).resolve().parents[1]
OUT=ROOT/'results'/datetime.datetime.now().strftime('%Y%m%d-%H%M%S');OUT.mkdir(parents=True)
ENV=dict(os.environ,HZ_CLUSTER='soma-teste-'+str(os.getpid()),HZ_MEMBERS='127.0.0.1:5701,127.0.0.1:5702,127.0.0.1:5703,127.0.0.1:5704',HZ_BIND='127.0.0.1')
JAVA=['java','-Xms128m','-Xmx768m','-XX:ActiveProcessorCount=2','-cp',str(ROOT/'build/tp01.jar')+os.pathsep+str(ROOT/'lib/*'),'Main']
processes=[];handles=[];events=[];counter=0

def event(kind,**kw):
 e=dict(time=datetime.datetime.now().isoformat(),kind=kind,**kw);events.append(e)
 (OUT/'events.json').write_text(json.dumps(events,indent=2),encoding='utf-8');print(e,flush=True)

def start(port):
 f=open(OUT/f'membro-{port}.log','w');handles.append(f)
 p=subprocess.Popen(JAVA+['membro',str(port)],stdout=f,stderr=subprocess.STDOUT,env=ENV,cwd=ROOT);processes.append(p)
 event('MEMBRO_INICIADO',port=port,pid=p.pid);return p

def run(*args,success=True):
 global counter
 counter+=1;r=subprocess.run(JAVA+list(map(str,args)),capture_output=True,text=True,env=ENV,cwd=ROOT,timeout=300)
 name=f'{counter:02d}-{args[0]}.log';(OUT/name).write_text(r.stdout+'\n'+r.stderr,encoding='utf-8')
 if (r.returncode==0)!=success:raise RuntimeError(f'{args}: {r.stdout}\n{r.stderr}')
 event('COMANDO_OK' if success else 'ERRO_ESPERADO_CONFIRMADO',args=list(args),log=name)
 return r.stdout

def wait_text(path,pattern,start_at=0,timeout=120):
 deadline=time.monotonic()+timeout
 while time.monotonic()<deadline:
  content=path.read_text()
  if pattern in content[start_at:]:return len(content)
  time.sleep(.2)
 raise RuntimeError('Não apareceu '+pattern+' em '+str(path))

try:
 env=dict(platform=platform.platform(),cpu_count=os.cpu_count(),java=subprocess.run(['java','-version'],capture_output=True,text=True).stderr,scope='JVMs separadas em um host; heap máximo 768 MiB; ActiveProcessorCount=2')
 (OUT/'environment.json').write_text(json.dumps(env,indent=2))
 one=start(5701);run('pronto',1)
 for n in [0,1,10]:
  run('carregar',n);r=run('somar',n)
  assert f'soma={n*(n+1)//2} ' in r
 run('somar',11,success=False)
 run('carregar',-1,success=False)
 run('benchmark',str(OUT/'benchmark.csv'))
 two=start(5702);run('pronto',2);run('benchmark',str(OUT/'benchmark.csv'))
 three=start(5703);run('pronto',3);run('benchmark',str(OUT/'benchmark.csv'))
 run('carregar',100000);run('pronto',3);run('estado')
 path=OUT/'acompanhamento.log';f=open(path,'w');handles.append(f)
 watch=subprocess.Popen(JAVA+['acompanhar','100000','120'],stdout=f,stderr=subprocess.STDOUT,env=ENV,cwd=ROOT);processes.append(watch)
 pos=wait_text(path,'VALIDADO n=100000 soma=5000050000 membros=3')
 # Encerra o terceiro membro durante a próxima rodada; o cliente permanece vivo.
 wait_text(path,'SOMA_INICIADA',start_at=pos)
 three.kill();three.wait();event('FALHA_ABRUPTA',port=5703,pid=three.pid,cliente_pid=watch.pid)
 run('pronto',2)
 pos=wait_text(path,'VALIDADO n=100000 soma=5000050000 membros=2')
 assert watch.poll() is None
 run('estado');event('RECUPERACAO_VALIDADA',cliente_pid=watch.pid)
 four=start(5704);event('EXPANSAO_DURANTE_ACOMPANHAMENTO',cliente_pid=watch.pid)
 run('pronto',3)
 wait_text(path,'VALIDADO n=100000 soma=5000050000 membros=3',start_at=pos)
 assert watch.poll() is None
 run('estado');event('EXPANSAO_VALIDADA',cliente_pid=watch.pid)
 watch.terminate();watch.wait(timeout=15)
 event('ALL_TESTS_PASSED')
except Exception as exc:
 event('FAILED',error=str(exc));raise
finally:
 for p in processes:
  if p.poll() is None:p.terminate()
 for p in processes:
  try:p.wait(timeout=20)
  except subprocess.TimeoutExpired:p.kill();p.wait()
 for f in handles:f.close()
 print('Resultados:',OUT,flush=True)
