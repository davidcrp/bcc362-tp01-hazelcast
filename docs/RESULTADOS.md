# Resultados da soma distribuída

Campanha: 20260918-182626. Resultado: ALL_TESTS_PASSED.

## Desempenho

JVMs separadas em um host Linux/WSL, Java 17.0.19, Hazelcast 5.6.0. Heap máximo 768 MiB por processo e ActiveProcessorCount=2. Uma tarefa por membro. Uma rodada de aquecimento descartada e três medições por combinação (27 medições). Não há atraso artificial. Mediana e intervalo mínimo–máximo abaixo.

| N | Membros | Carga ms | Soma ms | Min–máx ms | Carga+soma ms | S(p) | E(p) |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 1000 | 1 | 112.69 | 104.21 | 88.17–105.53 | 216.90 | 1.00 | 1.00 |
| 1000 | 2 | 303.78 | 68.35 | 65.62–69.50 | 372.13 | 1.52 | 0.76 |
| 1000 | 3 | 214.17 | 40.47 | 39.80–43.01 | 254.64 | 2.58 | 0.86 |
| 10000 | 1 | 101.81 | 692.00 | 682.75–749.69 | 793.81 | 1.00 | 1.00 |
| 10000 | 2 | 160.34 | 347.20 | 333.50–389.60 | 507.54 | 1.99 | 1.00 |
| 10000 | 3 | 133.45 | 290.33 | 274.53–327.71 | 423.78 | 2.38 | 0.79 |
| 100000 | 1 | 227.63 | 6432.57 | 6188.06–7057.56 | 6660.20 | 1.00 | 1.00 |
| 100000 | 2 | 230.23 | 2921.74 | 2700.13–3237.70 | 3151.97 | 2.20 | 1.10 |
| 100000 | 3 | 207.84 | 2537.03 | 2455.89–3014.42 | 2744.88 | 2.54 | 0.85 |

S(p)=T(1)/T(p); E(p)=S(p)/p. A referência de um membro também usa Hazelcast, não é uma execução Java sequencial pura. Carga é medida uma vez por combinação e reutilizada na soma carga+processamento. O tempo de carga inclui limpeza, geração e envio; tempo de soma inclui submissão, execução e recebimento. Inicialização/conexão e validação final ficam fora.

## Interpretação

Os resultados são observações deste host e desta campanha curta. Mais membros não garantem proporcionalidade: cada número ainda passa pela abstração IMap; threads, rede local, serialização e memória têm custo. JIT, coleta de lixo e ordem fixa também influenciam. O valor de eficiência acima de 1 para N=10000 com dois membros é uma observação desta campanha: efeitos de aquecimento, caches e variação podem produzir ganho aparente superlinear; não se conclui eficiência física superior a 100%. Não extrapolar para máquinas independentes nem confundir uma soma didática com benchmark de produção.

## Correção, falha e expansão

N=0, N=1 e N=10 produziram 0, 1 e 55. N negativo e pedido com N diferente do carregado foram rejeitados. Para 100000 números, o total esperado é 5000050000.

O mesmo processo cliente permaneceu aberto durante queda e expansão. Uma rodada interrompida não é recuperada por partes: a próxima refaz a soma inteira. Recorte real do acompanhamento:

```text
VALIDADO n=100000 soma=5000050000 membros=3 ms=2418.80086
RODADA_INTERROMPIDA ExecutionException; próxima rodada refaz a soma inteira
VALIDADO n=100000 soma=5000050000 membros=2 ms=3307.606102
RODADA_INTERROMPIDA IllegalStateException; próxima rodada refaz a soma inteira
VALIDADO n=100000 soma=5000050000 membros=3 ms=2779.31615
```

Eventos registrados:

- 2026-09-18T18:28:16.642033: FALHA_ABRUPTA, cliente PID 49305.
- 2026-09-18T18:28:29.375319: RECUPERACAO_VALIDADA, cliente PID 49305.
- 2026-09-18T18:28:29.393728: EXPANSAO_DURANTE_ACOMPANHAMENTO, cliente PID 49305.
- 2026-09-18T18:28:40.444630: EXPANSAO_VALIDADA, cliente PID 49305.

## Partições antes e depois

```text
17-estado.log
[127.0.0.1]:5701 primarias=91 seguro=true
[127.0.0.1]:5703 primarias=90 seguro=true
[127.0.0.1]:5702 primarias=90 seguro=true
```

```text
19-estado.log
[127.0.0.1]:5701 primarias=136 seguro=true
[127.0.0.1]:5702 primarias=135 seguro=true
```

```text
21-estado.log
[127.0.0.1]:5701 primarias=91 seguro=true
[127.0.0.1]:5704 primarias=90 seguro=true
[127.0.0.1]:5702 primarias=90 seguro=true
```

## Reprodução e limites

Executar `python3 scripts/experiments.py` e `python3 scripts/summarize.py`. CSV bruto, logs e environment.json estão na pasta da campanha. Scripts de documentos e compilação LaTeX podem ser executados depois para atualizar os PDFs.

Testes demonstram falha de processo e recuperação no mesmo host. Não foram testados Docker, máquinas remotas, falha total do host, queda do cliente ou split-brain. O exemplo assume entrada imutável e conhecida.
