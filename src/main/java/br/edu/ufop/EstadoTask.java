package br.edu.ufop;

import com.hazelcast.core.*;
import java.io.Serializable;
import java.util.concurrent.Callable;

/** Apoio à demonstração; não faz parte do algoritmo de soma. */
public class EstadoTask implements Callable<String>, Serializable, HazelcastInstanceAware {
    private static final long serialVersionUID = 1L;
    private transient HazelcastInstance hazelcast;
    public void setHazelcastInstance(HazelcastInstance h) { hazelcast = h; }
    public String call() {
        long particoes = hazelcast.getPartitionService().getPartitions().stream()
            .filter(p -> hazelcast.getCluster().getLocalMember().equals(p.getOwner())).count();
        return "primarias=" + particoes + " seguro=" + hazelcast.getPartitionService().isClusterSafe();
    }
}
