package br.edu.ufop;

import com.hazelcast.client.HazelcastClient;
import com.hazelcast.client.config.ClientConfig;
import com.hazelcast.core.HazelcastInstance;
import com.hazelcast.map.IMap;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.TimeUnit;

public class Cliente {
    // 1. Coloca os números de 1 até N no mapa distribuído.
    static void carregar(HazelcastInstance hz, int n) {
        if (n < 0) throw new IllegalArgumentException("N deve ser não negativo");
        IMap<Integer, Long> mapa = hz.getMap("numeros");
        mapa.clear(); // Uma entrada de cada vez; não carregar durante uma soma.
        Map<Integer, Long> entrada = new HashMap<>();
        for (int i = 1; i <= n; i++) entrada.put(i, (long) i);
        mapa.putAll(entrada);
        System.out.println("CARREGADO n=" + n);
    }

    // 2. Executa uma SomaTask em cada membro e soma as respostas.
    static double somar(HazelcastInstance hz, int n) throws Exception {
        if (n < 0) throw new IllegalArgumentException("N deve ser não negativo");
        var membrosAntes = new HashSet<>(hz.getCluster().getMembers());
        long inicio = System.nanoTime();
        System.out.println("SOMA_INICIADA membros=" + membrosAntes.size());
        var respostas = hz.getExecutorService("soma").submitToAllMembers(new SomaTask());
        long total = 0;
        Map<String, Long> parciais = new TreeMap<>();
        try {
            for (var resposta : respostas.entrySet()) {
                long parcial = resposta.getValue().get(30, TimeUnit.SECONDS);
                total += parcial;
                parciais.put(resposta.getKey().getAddress().toString(), parcial);
            }
        } finally {
            // Cancela pendências caso uma tarefa falhe. Não há reenvio por bloco.
            for (var futura : respostas.values()) if (!futura.isDone()) futura.cancel(true);
        }
        double ms = (System.nanoTime() - inicio) / 1_000_000.0;
        long esperado = (long) n * (n + 1L) / 2;
        // O exemplo usa dados imutáveis e conhecidos: mudança/inconsistência é rejeitada.
        if (!membrosAntes.equals(new HashSet<>(hz.getCluster().getMembers())) || total != esperado)
            throw new IllegalStateException("Cluster mudou ou soma divergiu; repita após estabilizar.");
        System.out.println("PARCIAIS " + parciais);
        System.out.println("VALIDADO n=" + n + " soma=" + total + " membros=" + membrosAntes.size() + " ms=" + ms);
        return ms;
    }

    // Daqui em diante: comandos de apoio à apresentação, separados da lógica acima.
    static boolean estado(HazelcastInstance hz, boolean mostrar) throws Exception {
        boolean seguro = true;
        var respostas = hz.getExecutorService("soma").submitToAllMembers(new EstadoTask());
        for (var entrada : respostas.entrySet()) {
            String texto = entrada.getValue().get(15, TimeUnit.SECONDS);
            seguro &= texto.endsWith("seguro=true");
            if (mostrar) System.out.println(entrada.getKey().getAddress() + " " + texto);
        }
        return seguro;
    }

    static void pronto(HazelcastInstance hz, int membros) throws Exception {
        long fim = System.nanoTime() + TimeUnit.SECONDS.toNanos(90);
        while (System.nanoTime() < fim) {
            try {
                if (hz.getCluster().getMembers().size() == membros && estado(hz, false)
                    && hz.getCluster().getMembers().size() == membros) {
                    System.out.println("PRONTO membros=" + membros); return;
                }
            } catch (Exception e) { /* Aguarda a mudança de topologia terminar. */ }
            Thread.sleep(500);
        }
        throw new IllegalStateException("Cluster não ficou pronto em 90 s");
    }

    static void benchmark(HazelcastInstance hz, String arquivo) throws Exception {
        Path path = Path.of(arquivo);
        if (path.getParent() != null) Files.createDirectories(path.getParent());
        boolean novo = !Files.exists(path);
        try (var out = Files.newBufferedWriter(path, StandardOpenOption.CREATE, StandardOpenOption.APPEND)) {
            if (novo) out.write("membros,n,repeticao,carga_ms,soma_ms,carga_mais_soma_ms\n");
            int membros = hz.getCluster().getMembers().size();
            for (int n : new int[]{1000, 10000, 100000}) {
                long inicio = System.nanoTime(); carregar(hz, n);
                double carga = (System.nanoTime() - inicio) / 1e6;
                pronto(hz, membros);
                somar(hz, n); // Aquecimento, não entra no CSV.
                for (int rep = 1; rep <= 3; rep++) {
                    double soma = somar(hz, n);
                    out.write(String.format(Locale.ROOT, "%d,%d,%d,%.3f,%.3f,%.3f%n", membros,n,rep,carga,soma,carga+soma));
                    out.flush();
                }
            }
        }
    }

    static void executar(String[] args) throws Exception {
        ClientConfig config = new ClientConfig(); config.setClusterName(Main.CLUSTER);
        config.getNetworkConfig().addAddress(Main.SEEDS.split(","));
        config.getConnectionStrategyConfig().getConnectionRetryConfig().setClusterConnectTimeoutMillis(30_000);
        HazelcastInstance hz = HazelcastClient.newHazelcastClient(config);
        try {
            switch (args[0]) {
                case "carregar" -> carregar(hz, Integer.parseInt(args[1]));
                case "somar" -> somar(hz, Integer.parseInt(args[1]));
                case "estado" -> estado(hz, true);
                case "pronto" -> pronto(hz, Integer.parseInt(args[1]));
                case "benchmark" -> benchmark(hz, args[1]);
                case "acompanhar" -> {
                    int n = Integer.parseInt(args[1]);
                    int rodadas = args.length > 2 ? Integer.parseInt(args[2]) : 60;
                    for (int i = 0; i < rodadas; i++) {
                        try {
                            if (estado(hz, false)) somar(hz, n);
                            else System.out.println("AGUARDANDO reorganização das partições");
                        } catch (Exception e) {
                            System.out.println("RODADA_INTERROMPIDA " + e.getClass().getSimpleName() + "; próxima rodada refaz a soma inteira");
                        }
                        Thread.sleep(2000);
                    }
                }
                default -> throw new IllegalArgumentException("Comando desconhecido: " + args[0]);
            }
        } finally { hz.shutdown(); }
    }
}
