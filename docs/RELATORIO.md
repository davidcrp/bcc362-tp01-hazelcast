# UFOP — BCC362 — Sistemas Distribuídos
# TP01: primeiro contato com Hazelcast

**Aplicação:** soma distribuída dos números de 1 até N.
**Integrantes:** preencher nomes e matrículas (até três).
**Versões:** Java 17 e Hazelcast 5.6.0, fixada para reproduzir o trabalho.

## 1. Proposta e relação com o enunciado

A proposta é implementar um exemplo básico já encontrado no site do framework e utilizá-lo para entender distribuição de dados e execução em cluster. Hazelcast está na lista de frameworks do enunciado. Aplicam-se os itens de descrição, arquitetura, aplicação e perguntas; a exigência específica de instalação de middleware com VMs/orquestradores não se aplica como obrigação dessa modalidade.

O ponto de partida é o exemplo SumTask da documentação oficial de Java Executor Service [1]. Cada membro soma os valores das chaves que lhe pertencem, e um cliente soma as respostas. O algoritmo foi mantido simples. Configuração, inspeção, benchmark e acompanhamento são recursos de apoio à demonstração, separados da classe SomaTask.

## 2. Para que serve o Hazelcast?

Hazelcast oferece armazenamento e processamento distribuídos em memória. Neste trabalho usamos IMap, um mapa chave–valor distribuído, e IExecutorService, que envia tarefas Java para os membros. Isso permite trabalhar com dados compartilhados e executar cálculo em mais de um processo. [1,2]

Aplicações possíveis incluem cache, sessões, contadores e estatísticas operacionais. Casos comerciais relatados pelo fornecedor incluem British Gas/Hive em IoT e BNP Paribas Bank Polska em serviços bancários. O caso Hive cita um cluster de 20 nós; o caso bancário relata 84 mil requisições por segundo em produção. São relatos do fornecedor, não medições do nosso trabalho nem garantia do desempenho atual desses sistemas. [4,5]

Não é uma solução que elimina os custos de rede, memória ou coordenação. Backup em RAM não é persistência em disco. Também não é necessário usar um cluster para calcular uma soma pequena: este problema foi escolhido para aprendizado, e não para alegar que a distribuição é a melhor forma de somar uma sequência conhecida.

### Maior aplicação e quantidade de máquinas

Não foi localizada evidência suficiente para apontar a maior implantação mundial ou seu tamanho atual. O caso comercial Hive fornece um exemplo de 20 nós. Separadamente, um benchmark histórico do fornecedor usando Jet 4.3 relata 45 nós EC2, 720 vCPUs, 1 bilhão de eventos por segundo e latência p99 de 26 ms. Benchmark não é aplicação comercial nem prova de recorde mundial. Esses números não descrevem a capacidade do exemplo de soma. Nós também não devem ser confundidos automaticamente com máquinas físicas. [4,6]

## 3. Como funciona internamente?

O cliente se conecta ao cluster, escreve números no mapa e pede o cálculo. Os membros armazenam partições e executam tarefas. Cada chave é associada a uma partição por hash; uma tabela indica o membro proprietário. A configuração mantém as 271 partições padrão e uma cópia síncrona dos dados em outro membro quando possível. [2,3]

Há participação distribuída dos membros, mas existem funções de coordenação, como as relacionadas à tabela de partições. Não se deve afirmar que não existe nenhuma coordenação interna. A aplicação também tem um cliente central para reunir as respostas; sua queda interrompe o cálculo em andamento. [3]

| Camada | Responsabilidade neste trabalho |
|---|---|
| Aplicação | Carregar 1..N, pedir a soma, juntar respostas e conferir |
| Serviços Hazelcast | IMap armazena dados; IExecutorService executa SomaTask |
| Gestão do cluster | Descoberta TCP, membros, detecção de saída e migração de partições |
| Infraestrutura | JVM, threads, RAM, serialização e comunicação TCP |

Uma cópia em outro membro permite recuperar os dados quando um membro cai, desde que a cópia exista e esteja sincronizada. Com um único membro não há redundância em outro membro. Ao entrar ou sair um membro, os dados são redistribuídos. Os experimentos esperam as cópias ficarem seguras antes da falha. [2]

## 4. Algoritmo escolhido e origem

A soma é uma redução: vários valores são combinados em um resultado. É útil como base para totais e estatísticas. A operação é associativa para os valores inteiros utilizados, então podemos somar partes e depois juntar as parcelas. O exemplo implementado adapta SumTask da seção “Implementing a Callable Task” da documentação oficial. Não usamos a API histórica MapReduce nem um pipeline Jet. [1]

A sequência é simples: o cliente grava números de 1 até N; cada membro percorre suas chaves primárias locais; uma tarefa retorna a soma local; o cliente recebe uma parcela de cada membro e calcula o total. A fórmula N(N+1)/2 serve somente para validar o cálculo distribuído.

As adaptações são nomes em português, chaves Integer e valores Long, combinação das parciais no cliente, entrada determinística e comandos de demonstração. Long é necessário porque a soma até 100000 excede o limite de Integer.

### Exemplo didático

Para N=10, os valores são 1 a 10 e a soma é 55. Se três membros tivessem parcelas 12, 15 e 28, o cliente calcularia 12+15+28=55. Essa divisão é apenas ilustrativa: as parcelas reais dependem do hash e da distribuição do cluster.

### Desafios e limites

O trabalho aritmético total é O(N), e a combinação de p parciais é O(p). Entretanto, cada consulta ao mapa tem custos adicionais, mesmo para uma chave local; serialização, invocação, agendamento e coordenação impedem tratar O(N/p) como previsão exata de tempo. A carga guarda N pares e uma cópia adicional quando há membros suficientes. O cliente materializa a entrada e o conjunto de chaves de cada membro também usa memória.

O conjunto deve permanecer imutável durante a soma. localKeySet não é uma fotografia transacional durante migração: uma rodada pode falhar ou contar de forma inconsistente se a topologia mudar. A aplicação verifica a composição do cluster antes/depois e a resposta conhecida; rejeita uma rodada divergente. Isso não oferece garantia universal de integridade para quaisquer dados: conjuntos distintos podem ter a mesma soma.

## 5. Falha e expansão de maneira simples

O mapa tem um backup síncrono. Isso protege os dados contra a perda de um membro em um cluster previamente seguro, não todos os tipos de falha. O executor convencional pode perder uma tarefa em andamento. O exemplo não implementa recuperação por partes ou persistência de tarefas.

O modo acompanhar mantém o mesmo cliente aberto e realiza novas somas. Se uma rodada falhar, ele informa o problema; depois da reorganização, uma rodada seguinte refaz a soma inteira. A classe SomaTask apenas lê dados, então repetir a operação não incrementa algum total compartilhado. Não afirmamos execução exatamente uma vez nem continuidade sem pausa.

Na expansão, um novo membro se conecta pelas seeds, recebe partições e passa a participar das rodadas seguintes. O cliente de acompanhamento não precisa ser reiniciado. Tarefas em andamento não são magicamente transferidas para o novo membro.

Não há persistência, TLS, autenticação ou proteção de split-brain configurados no laboratório. Perda completa do host, falha de dois membros antes da recomposição e queda do cliente não são cobertas. JVMs locais compartilham o domínio de falha físico; para proteção contra queda de máquina é necessário separar membros e cópias em máquinas apropriadas.

## 6. Experimentos e validação

A execução usa JVMs separadas em um host Linux/WSL, Java 17, heap máximo de 768 MiB por processo e ActiveProcessorCount=2. Isso demonstra comunicação distribuída por TCP, mas não é uma medição de três máquinas independentes.

A suíte testa N=0, N=1 e N=10, rejeição de N negativo e de N incompatível com os dados. Depois mede 1000, 10000 e 100000 números com 1, 2 e 3 membros. Para cada combinação, uma soma aquece o ambiente e três somas são registradas: 27 medições. A carga é medida uma vez por combinação e também reportada separadamente.

Finalmente, um único cliente de acompanhamento fica ativo enquanto o processo do membro 5703 é encerrado abruptamente e o membro 5704 é iniciado. Os logs devem comprovar a volta a respostas válidas com dois e depois três membros, com o mesmo PID de cliente. Os detalhes numéricos e o resultado efetivo constam em RESULTADOS.md, incorporado à versão PDF.

O tempo de soma inclui submissão, cálculo e espera das respostas, além da linha de início impressa; não inclui a conferência final nem a impressão das parciais. O tempo de carga inclui limpeza do mapa anterior, criação do mapa Java, envio e a mensagem de carga. Inicialização e conexão ficam fora. Não é um benchmark de produção: poucas repetições, ordem fixa, hardware compartilhado e tempo de aquecimento podem influenciar os resultados.

Aceleração S(p)=T(1)/T(p) compara a mesma entrada com um e p membros. Eficiência E(p)=S(p)/p. Não foi criado um benchmark sequencial separado: o caso de um membro continua sendo Hazelcast, e não deve ser chamado de execução Java sequencial pura. Aumento de N com p fixo mostra crescimento do input; aumentar p com N fixo avalia escalabilidade forte.

## 7. Organização e apresentação

SomaTask.java contém a tarefa; Cliente.java contém carga e redução, seguidas de comandos de apoio; Main.java configura os membros; EstadoTask.java consulta o estado do cluster. O guia explica a execução manual, a automação e o que fazer se precisar instalar Java/WSL. Docker e máquinas remotas são alternativas preparadas, não declaradas como executadas.

Os slides foram refeitos em LaTeX/Beamer. Há fonte editável, PDF e notas de fala. A apresentação reserva cerca de cinco minutos para tecnologia, cinco para arquitetura e cinco para a aplicação/demonstração. Em seguida há dez minutos para perguntas. O questionário concreto não foi fornecido no PDF; as perguntas de preparação são apenas estudo.

## Referências

A numeração [1–8] é detalhada em REFERENCIAS.md, incluída ao final do PDF. O código do exemplo é pequeno o suficiente para ser apresentado e explicado, sem exigir estudar a automação de testes como parte do algoritmo.
