#!/usr/bin/env python3
from pathlib import Path
import json,csv,statistics
ROOT=Path(__file__).resolve().parents[1]
runs=[p for p in sorted((ROOT/'results').iterdir()) if (p/'events.json').exists() and any(e['kind']=='ALL_TESTS_PASSED' for e in json.loads((p/'events.json').read_text()))]
if not runs:raise SystemExit('Nenhuma campanha concluída com sucesso.')
p=runs[-1];raw=list(csv.DictReader((p/'benchmark.csv').open()));rows=[]
for n in [1000,10000,100000]:
 base=statistics.median(float(r['soma_ms']) for r in raw if int(r['n'])==n and int(r['membros'])==1)
 for m in [1,2,3]:
  rs=[r for r in raw if int(r['n'])==n and int(r['membros'])==m]
  med=lambda k:statistics.median(float(r[k]) for r in rs)
  rows.append(dict(n=n,membros=m,carga_ms=med('carga_ms'),soma_ms=med('soma_ms'),min_ms=min(float(r['soma_ms']) for r in rs),max_ms=max(float(r['soma_ms']) for r in rs),total_ms=med('carga_mais_soma_ms'),speedup=base/med('soma_ms'),eficiencia=base/med('soma_ms')/m))
(ROOT/'docs/summary.json').write_text(json.dumps(dict(run=p.name,rows=rows),indent=2))
s=['# Resultados da soma distribuída','',f'Campanha: {p.name}. Resultado: ALL_TESTS_PASSED.','', '## Desempenho','', 'JVMs separadas em um host Linux/WSL, Java 17.0.19, Hazelcast 5.6.0. Heap máximo 768 MiB por processo e ActiveProcessorCount=2. Uma tarefa por membro. Uma rodada de aquecimento descartada e três medições por combinação (27 medições). Não há atraso artificial. Mediana e intervalo mínimo–máximo abaixo.','', '| N | Membros | Carga ms | Soma ms | Min–máx ms | Carga+soma ms | S(p) | E(p) |','|---:|---:|---:|---:|---:|---:|---:|---:|']
for r in rows:s.append(f"| {r['n']} | {r['membros']} | {r['carga_ms']:.2f} | {r['soma_ms']:.2f} | {r['min_ms']:.2f}–{r['max_ms']:.2f} | {r['total_ms']:.2f} | {r['speedup']:.2f} | {r['eficiencia']:.2f} |")
s+=['','S(p)=T(1)/T(p); E(p)=S(p)/p. A referência de um membro também usa Hazelcast, não é uma execução Java sequencial pura. Carga é medida uma vez por combinação e reutilizada na soma carga+processamento. O tempo de carga inclui limpeza, geração e envio; tempo de soma inclui submissão, execução e recebimento. Inicialização/conexão e validação final ficam fora.','', '## Interpretação','', 'Os resultados são observações deste host e desta campanha curta. Mais membros não garantem proporcionalidade: cada número ainda passa pela abstração IMap; threads, rede local, serialização e memória têm custo. JIT, coleta de lixo e ordem fixa também influenciam. O valor de eficiência acima de 1 para N=10000 com dois membros é uma observação desta campanha: efeitos de aquecimento, caches e variação podem produzir ganho aparente superlinear; não se conclui eficiência física superior a 100%. Não extrapolar para máquinas independentes nem confundir uma soma didática com benchmark de produção.','', '## Correção, falha e expansão','', 'N=0, N=1 e N=10 produziram 0, 1 e 55. N negativo e pedido com N diferente do carregado foram rejeitados. Para 100000 números, o total esperado é 5000050000.','', 'O mesmo processo cliente permaneceu aberto durante queda e expansão. Uma rodada interrompida não é recuperada por partes: a próxima refaz a soma inteira. Recorte real do acompanhamento:', '', '```text']
s += [line for line in (p/'acompanhamento.log').read_text().splitlines() if line.startswith(('VALIDADO','RODADA_INTERROMPIDA','AGUARDANDO'))]
s += ['```','','Eventos registrados:','']
for e in json.loads((p/'events.json').read_text()):
 if e['kind'] in ['FALHA_ABRUPTA','RECUPERACAO_VALIDADA','EXPANSAO_DURANTE_ACOMPANHAMENTO','EXPANSAO_VALIDADA']:
  s.append(f"- {e['time']}: {e['kind']}, cliente PID {e['cliente_pid']}.")
s+=['','## Partições antes e depois','']
for fn in ['17-estado.log','19-estado.log','21-estado.log']:
 s+=['```text',fn,*[x for x in (p/fn).read_text().splitlines() if 'primarias=' in x],'```','']
s+=['## Reprodução e limites','','Executar `python3 scripts/experiments.py` e `python3 scripts/summarize.py`. CSV bruto, logs e environment.json estão na pasta da campanha. Scripts de documentos e compilação LaTeX podem ser executados depois para atualizar os PDFs.','','Testes demonstram falha de processo e recuperação no mesmo host. Não foram testados máquinas remotas, falha total do host, queda do cliente ou split-brain. O exemplo assume entrada imutável e conhecida.']
(ROOT/'docs/RESULTADOS.md').write_text('\n'.join(s)+'\n')
tex=['% Gerado por scripts/summarize.py; valores medidos, em ms.',r'\begin{tabular}{rrrr}',r'\toprule',r'$N$ & 1 membro & 2 membros & 3 membros \\',r'\midrule']
for n in [1000,10000,100000]:
 vals=[r['soma_ms'] for r in rows if r['n']==n]
 tex.append(f'{n:,}'.replace(',','.')+' & '+' & '.join(f'{v:.1f}'.replace('.',',') for v in vals)+r' \\')
tex += [r'\bottomrule',r'\end{tabular}']
(ROOT/'slides/resultados.tex').write_text('\n'.join(tex)+'\n')
print('\n'.join(s[:22]))
