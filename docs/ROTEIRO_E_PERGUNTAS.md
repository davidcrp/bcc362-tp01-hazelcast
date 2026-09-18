# Roteiro e perguntas de preparação

## Organização do tempo

- 0–5 min: slides 1–4, o que é Hazelcast, usos, limites e exemplos de mercado.
- 5–10 min: slides 5–8, membros/cliente, partições, camadas e recuperação.
- 10–15 min: slides 9–13, código simples, resultados e demonstração.
- 15–25 min: perguntas. Todos os integrantes devem participar.

A apresentação .tex contém notas de fala em `\note{...}`. O quadro de referências final é apoio, não exige leitura de todos os links em voz alta.

## Demonstração em até três minutos

Antes: compilar, deixar três membros ativos e N=100000 carregado; abrir os terminais com fonte grande.

1. Mostrar `estado`: três membros e `seguro=true`.
2. Executar `somar 100000`: mostrar parcelas e 5000050000.
3. Iniciar `acompanhar 100000`. Em outro terminal, encerrar apenas o membro 5703 com kill -9.
4. Explicar eventual rodada interrompida e observar resultado correto com dois membros.
5. Iniciar `membro 5704` e observar resultado correto com três, sem reiniciar o cliente.

Use os logs como evidência anterior caso o ambiente de sala falhe; diga que são registros de uma execução anterior. Não execute a campanha completa de benchmark nos cinco minutos.

## Perguntas (preparação, não questionário oficial)

**Por que esse algoritmo é simples?**
Porque ele somente guarda números, soma os valores locais e junta parcelas. Não há tokenização, blocos de texto ou recuperação por bloco.

**De onde veio?**
Do exemplo SumTask da documentação oficial de Java Executor Service do Hazelcast. Mantivemos a iteração por localKeySet e adaptamos tipos e cliente.

**IMap é o mesmo que HashMap?**
A interface lembra um mapa, mas IMap distribui os dados no cluster. O HashMap utilizado para montar a entrada existe apenas na memória do cliente.

**O que é um membro? E cliente?**
Membro guarda partições e executa tarefas. Cliente envia dados e solicita operações; neste trabalho também reúne as respostas.

**O que significa Callable<Long>?**
Uma tarefa que retorna um valor Long quando executada. Serializable permite enviá-la; HazelcastInstanceAware fornece a instância local.

**Por que localKeySet?**
Para que cada membro processe somente as chaves primárias que lhe pertencem, em vez de todos somarem o mapa inteiro.

**O backup seria contado duas vezes?**
Não no cluster estável: as chaves de backup não são tratadas como primárias locais pelo localKeySet.

**O que é Future?**
Um objeto que representa uma resposta em processamento; get espera ela ficar pronta. O exemplo completo usa um prazo por resposta.

**Como validar?**
Para entrada 1..N, comparar com N(N+1)/2. Isso verifica esse cenário conhecido, não prova integridade universal de qualquer conjunto.

**Por que Long?**
A soma até 100000 é 5000050000, maior que o limite de um inteiro de 32 bits.

**Por que não usar só a fórmula?**
Seria melhor para essa sequência específica. Aqui a fórmula é o oráculo de conferência; a finalidade é aprender execução distribuída, cuja estrutura se aplica a outros dados.

**O que acontece durante uma queda?**
O Hazelcast recupera os dados das cópias disponíveis. Uma tarefa pode falhar; o acompanhamento refaz a soma inteira na próxima rodada após estabilização.

**A tarefa executa exatamente uma vez?**
Não é a garantia oferecida. A soma apenas lê; repetir não altera o mapa. Não há contador global sendo incrementado por tentativas repetidas.

**O programa para para adicionar um membro?**
O processo cliente permanece aberto, mas uma rodada pode pausar ou ser rejeitada durante a migração. Novas rodadas usam o cluster atualizado.

**E se o cliente cair?**
O resultado em andamento se perde. Se os membros continuam vivos, outro cliente pode pedir uma soma completa novamente.

**E se o computador inteiro cair?**
As cópias locais em RAM também se perdem. Não há persistência e os membros compartilham o mesmo host nesta demonstração.

**Mais membros sempre melhora o desempenho?**
Não. Rede, agendamento, acesso ao mapa e recursos compartilhados têm custo. O CSV mostra o comportamento observado, sem prometer aceleração linear.

**Qual é o maior cluster mundial?**
Não encontramos evidência pública suficiente. Citamos apenas exemplos quantificados: caso Hive de 20 nós e benchmark Jet de 45 nós, sem confundi-los com um recorde.

**O exemplo resolve split-brain?**
Não. Backup não resolve automaticamente toda partição de rede. Esse cenário e suas políticas não foram configurados/testados.

**O que seria uma evolução?**
Usar agregações prontas do Hazelcast, analisar dados reais e testar hosts independentes. Isso fica como possibilidade futura, preservando o exemplo básico do TP.
