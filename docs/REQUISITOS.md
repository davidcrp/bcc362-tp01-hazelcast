# Correspondência com o enunciado

| Requisito | Atendimento na versão básica |
|---|---|
| Exemplo simples do site do framework | SomaTask, documentação oficial Hazelcast; adaptação identificada |
| Grupo de até três integrantes | Campo para nomes e matrículas no relatório e LaTeX; preencher |
| Item 1: usos, limites e mercado (~5 min) | Relatório §2 e primeiro bloco dos slides |
| Item 1: maior aplicação e quantidade de máquinas | Ausência de recorde comprovado explicitada; caso comercial 20 nós e benchmark 45 nós com fontes |
| Item 2: arquitetura e camadas (~5 min) | Relatório §3 e segundo bloco dos slides |
| Item 3: instalação de middleware | Não obrigatório na opção framework; guia de instalação local e alternativas adicionais |
| Item 4: origem, conceitos e aplicação | Soma distribuída / redução, SumTask oficial, código comentado e explicação introdutória |
| Item 4: execução em cluster | Processos Java independentes conectados por TCP; logs e somas parciais |
| Item 4: inputs maiores | 1000, 10000 e 100000 números; 1, 2 e 3 membros; 27 medições |
| Item 4: queda abrupta | Processo membro encerrado sem shutdown; backup; nova rodada refaz toda a soma |
| Item 4: expansão sem reiniciar aplicação | Mesmo cliente acompanha saída e entrada de membro; pode haver pausa/rodada descartada |
| Item 5: responder questionários (~10 min) | Preparação com perguntas; questionário específico não incluído no enunciado |
| Apresentação fundamental | Fonte LaTeX/Beamer + PDF + notas e roteiro |

Consulte RESULTADOS.md para saber exatamente o que foi executado e aprovado. Resultados usam JVMs no mesmo host. Docker, máquinas remotas e falha completa de host não foram testados. Os integrantes ainda precisam se identificar, ensaiar e realizar a apresentação no workshop.
