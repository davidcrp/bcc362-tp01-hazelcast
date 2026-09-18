import com.hazelcast.config.*;
import com.hazelcast.core.*;
import java.util.Arrays;
import java.util.concurrent.CountDownLatch;

/** Configuração do laboratório. Comece a leitura do algoritmo em SomaTask.java. */
public class Main {
    static final String CLUSTER = System.getenv().getOrDefault("HZ_CLUSTER", "tp01-soma");
    static final String SEEDS = System.getenv().getOrDefault("HZ_MEMBERS", "127.0.0.1:5701,127.0.0.1:5702,127.0.0.1:5703,127.0.0.1:5704");

    static void membro(int porta) throws Exception {
        Config config = new Config();
        config.setClusterName(CLUSTER);
        config.getNetworkConfig().setPort(porta).setPortAutoIncrement(false);
        var join = config.getNetworkConfig().getJoin();
        join.getMulticastConfig().setEnabled(false);
        join.getAutoDetectionConfig().setEnabled(false);
        join.getTcpIpConfig().setEnabled(true).setMembers(Arrays.asList(SEEDS.split(",")));
        String bind = System.getenv("HZ_BIND");
        if (bind != null) config.getNetworkConfig().getInterfaces().setEnabled(true).addInterface(bind);
        config.addMapConfig(new MapConfig("numeros").setBackupCount(1));
        config.addExecutorConfig(new ExecutorConfig("soma").setPoolSize(2));
        // Limites para executar várias JVMs em um computador pessoal.
        config.setProperty("hazelcast.operation.thread.count", "2");
        config.setProperty("hazelcast.operation.generic.thread.count", "2");
        config.setProperty("hazelcast.io.input.thread.count", "1");
        config.setProperty("hazelcast.io.output.thread.count", "1");
        config.setProperty("hazelcast.heartbeat.interval.seconds", "1");
        config.setProperty("hazelcast.max.no.heartbeat.seconds", "10");
        config.getJetConfig().setEnabled(false);
        HazelcastInstance hz = Hazelcast.newHazelcastInstance(config);
        Runtime.getRuntime().addShutdownHook(new Thread(hz::shutdown));
        System.out.println("MEMBRO_PRONTO porta=" + porta);
        new CountDownLatch(1).await();
    }

    public static void main(String[] args) throws Exception {
        java.util.logging.Logger.getLogger("com.hazelcast").setLevel(java.util.logging.Level.WARNING);
        if (args.length == 0) {
            System.out.println("Comandos: membro PORTA | carregar N | somar N | acompanhar N [RODADAS] | pronto MEMBROS | estado | benchmark CSV");
            return;
        }
        if (args[0].equals("membro")) membro(Integer.parseInt(args[1]));
        else Cliente.executar(args);
    }
}
