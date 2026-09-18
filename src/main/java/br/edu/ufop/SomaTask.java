package br.edu.ufop;

import com.hazelcast.core.HazelcastInstance;
import com.hazelcast.core.HazelcastInstanceAware;
import com.hazelcast.map.IMap;
import java.io.Serializable;
import java.util.concurrent.Callable;

/** Adaptação do exemplo SumTask da documentação oficial (link no README). */
public class SomaTask implements Callable<Long>, Serializable, HazelcastInstanceAware {
    private static final long serialVersionUID = 1L;
    private transient HazelcastInstance hazelcast;

    public void setHazelcastInstance(HazelcastInstance instancia) {
        this.hazelcast = instancia;
    }

    public Long call() {
        IMap<Integer, Long> numeros = hazelcast.getMap("numeros");
        long soma = 0;
        // Cada membro soma somente as chaves primárias que pertencem a ele.
        for (Integer chave : numeros.localKeySet()) {
            Long valor = numeros.get(chave);
            if (valor == null) throw new IllegalStateException("Dado indisponível; repita a soma.");
            soma += valor;
        }
        return soma;
    }
}
