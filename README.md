# TP01 — Primeiro contato com Hazelcast

**Aplicação: somar os números de 1 até N usando um cluster Hazelcast.**

Adaptação do exemplo **SumTask**, presente na seção “Implementing a Callable Task” da [documentação oficial do Hazelcast 5.6](https://docs.hazelcast.com/hazelcast/5.6/computing/executor-service). A ideia do exemplo foi preservada: cada membro soma os valores das suas chaves locais. O cliente junta as somas parciais.

Exemplo: para N=10, o resultado é 55. Para N=100.000, é 5.000.050.000. Usamos `long` para o resultado não ultrapassar o limite de `int`.

## Leia nesta ordem

1. `docs/EXPLICACAO_DO_CODIGO.md`: explicação para quem está começando.
2. `docs/GUIA_PASSO_A_PASSO.md` (também em PDF): como compilar, iniciar os membros e executar.
3. `src/main/java/br/edu/ufop/SomaTask.java`: a tarefa de soma, com menos de 30 linhas.
4. `src/main/java/br/edu/ufop/Cliente.java`: os métodos `carregar` e `somar` são o núcleo do cliente; os demais apenas apoiam testes/demonstração.
5. `slides/apresentacao.tex` e `slides/apresentacao.pdf`: apresentação feita em **LaTeX/Beamer**.
6. `docs/RELATORIO.pdf`, `docs/RESULTADOS.md` e `docs/REQUISITOS.md`: fundamentação, evidências e requisitos.

Não é necessário estudar automação de testes, Docker ou detalhes do compilador para entender o algoritmo. A documentação mostra quais trechos foram adaptados e quais são apenas infraestrutura.

## Executar os testes (Ubuntu/WSL)

```bash
cd /mnt/c/Users/mathe/OneDrive/Documentos/ufop/SD/hazelcast-tp01
bash scripts/build.sh
python3 scripts/experiments.py
python3 scripts/summarize.py
```

O guia contém os comandos para fazer a apresentação manualmente. Não rode a suíte automática enquanto houver membros manuais nas portas 5701–5704.

## O que foi simplificado

A versão anterior de contagem de palavras foi substituída: sem tokenização, blocos, janelas de tarefas, histogramas ou recuperação por bloco. Agora são três conceitos: **IMap**, **tarefa Callable** e **IExecutorService**. Em caso de falha, uma nova rodada refaz a soma inteira após a recuperação do cluster; isso é mostrado explicitamente, sem prometer execução exatamente uma vez.

O arquivo anterior foi preservado em `../versoes-anteriores/TP01_WordCount.zip`. Os resultados antigos não são usados no trabalho novo.

## Entrega

Hazelcast está listado como framework no enunciado: itens 1, 2, 4 e 5. VMs com orquestradores não são obrigatórias nessa modalidade. A aplicação foi preparada para testar entradas maiores e observar queda/entrada de membro mantendo o cliente de acompanhamento ativo. Processos locais são JVMs distintas no mesmo host, não máquinas físicas distintas.

Preencha nomes/matrículas (até 3 alunos) em `slides/apresentacao.tex`. As perguntas de preparação não substituem as perguntas efetivas do professor, que não estão anexadas ao enunciado.

## Obter pelo GitHub

```bash
git clone https://github.com/cardosoAM/bcc362-tp01-hazelcast.git
cd bcc362-tp01-hazelcast
bash scripts/build.sh
```

Repositório privado: é necessário ter acesso à conta ou ser colaborador. Os caminhos pessoais dos exemplos do guia devem ser substituídos pela pasta em que você clonou o projeto.

Acesso rápido: [guia](docs/GUIA_PASSO_A_PASSO.pdf), [explicação do código](docs/EXPLICACAO_DO_CODIGO.pdf), [slides PDF](slides/apresentacao.pdf), [fonte LaTeX](slides/apresentacao.tex), [relatório](docs/RELATORIO.pdf) e [enunciado](docs/ENUNCIADO_ORIGINAL.pdf).
