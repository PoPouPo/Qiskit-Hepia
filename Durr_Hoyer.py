import numpy as np
import matplotlib.pyplot as plt
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile
from qiskit_aer import AerSimulator
from qiskit.circuit.library import GroverOperator
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)

# Définition du tableau de valeurs
valeurs = np.array([
    542, 127, 896, 341, 675, 234, 789, 456, 912, 88,
    301, 654, 23, 498, 765, 321, 987, 156, 432, 678,
    99, 543, 876, 210, 345, 789, 123, 456, 901, 234,
    567, 890, 12, 345, 678, 901, 234, 567, 890, 123,
    456, 789, 234, 567, 890, 123, 456, 789, 234, 567,
    890, 123, 456, 789, 234, 567, 890, 123, 456, 789,
    234, 567, 890, 123, 456, 789, 234, 567, 890, 123,
    456, 789, 234, 567, 890, 123, 456, 789, 234, 567,
    890, 123, 456, 789, 234, 567, 890, 123, 456, 789,
    234, 567, 890, 123, 456, 789, 234, 567, 890, 11
])
if len(valeurs) == 0:
    raise ValueError("Le tableau de valeurs ne peut pas être vide.")

n_qubits = int(np.ceil(np.log2(len(valeurs))))

def create_oracle(valeurs, threshold, n_qubits):
    """Oracle qui marque les indices où valeurs[i] < threshold."""
    oracle = QuantumCircuit(n_qubits, name="oracle")
    
    for i in range(len(valeurs)):
        if valeurs[i] < threshold:
            bin_i = format(i, f'0{n_qubits}b')
            
            # Appliquer X sur les bits à 0
            for j, bit in enumerate(reversed(bin_i)):
                if bit == '0':
                    oracle.x(j)
            
            # Phase flip sur l'état cible
            if n_qubits == 1:
                oracle.z(0)
            elif n_qubits == 2:
                oracle.cz(0, 1)
            else:
                # Multi-controlled Z gate
                oracle.h(n_qubits - 1)
                oracle.mcx(list(range(n_qubits - 1)), n_qubits - 1)
                oracle.h(n_qubits - 1)
            
            # Annuler les X
            for j, bit in enumerate(reversed(bin_i)):
                if bit == '0':
                    oracle.x(j)
    
    return oracle

def run_grover(valeurs, threshold, n_qubits, num_iterations):
    """Exécute l'algorithme de Grover."""
    qr = QuantumRegister(n_qubits, 'q')
    cr = ClassicalRegister(n_qubits, 'c')
    circuit = QuantumCircuit(qr, cr)
    
    # Superposition uniforme
    circuit.h(qr)
    
    # Oracle
    oracle = create_oracle(valeurs, threshold, n_qubits)
    
    # Opérateur de Grover avec transpilation
    try:
        grover_op = GroverOperator(oracle)
        for _ in range(num_iterations):
            circuit.append(grover_op, qr)
        
        # CLEF : Transpiler le circuit avant exécution
        simulator = AerSimulator()
        transpiled_circuit = transpile(circuit, simulator)
        transpiled_circuit.measure(qr, cr)
        
        # Exécution
        job = simulator.run(transpiled_circuit, shots=1)
        result = job.result()
        counts = result.get_counts()
        
        measured_index = int(list(counts.keys())[0], 2)
        return measured_index if measured_index < len(valeurs) else np.random.randint(0, len(valeurs))
        
    except Exception as e:
        print(f"Erreur : {e}")
        return np.random.randint(0, len(valeurs))

# Algorithme principal
x_best = np.random.randint(0, len(valeurs))
history_indices = [x_best]
history_valeurs = [valeurs[x_best]]

max_iterations = 10
optimal_grover_iterations = max(1, int(np.ceil(np.pi / 4 * np.sqrt(len(valeurs)))))

print(f"Démarrage avec indice {x_best}, valeur {valeurs[x_best]}")

for i in range(max_iterations):
    threshold = valeurs[x_best]
    new_index = run_grover(valeurs, threshold, n_qubits, optimal_grover_iterations)
    
    print(f"Itération {i+1}: nouvel indice={new_index}, valeur={valeurs[new_index]}")
    
    if valeurs[new_index] < valeurs[x_best]:
        x_best = new_index
        history_indices.append(x_best)
        history_valeurs.append(valeurs[x_best])
    else:
        print(f"Arrêt après {i+1} itérations. Minimum trouvé : valeur={valeurs[x_best]} à l'indice={x_best}")
        break

# Vérification
min_index = np.argmin(valeurs)
print(f"\nVérification : Minimum réel = {valeurs[min_index]} à l'indice {min_index}")
print(f"Chemin parcouru : {history_indices}")

# Visualisations
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

# Évolution des indices
ax1.plot(range(len(history_indices)), history_indices, marker='o', color='purple', linewidth=2, markersize=8)
ax1.axhline(y=min_index, color='green', linestyle='--', linewidth=2, label=f'Minimum global (indice {min_index})')
ax1.set_title("Évolution de l'indice du minimum", fontsize=14, fontweight='bold')
ax1.set_xlabel("Itération", fontsize=12)
ax1.set_ylabel("Indice", fontsize=12)
ax1.grid(alpha=0.3)
ax1.legend()

# Évolution des valeurs
ax2.plot(range(len(history_valeurs)), history_valeurs, marker='o', color='blue', linewidth=2, markersize=8)
ax2.axhline(y=valeurs[min_index], color='red', linestyle='--', linewidth=2, label=f'Valeur minimale ({valeurs[min_index]})')
ax2.set_title("Évolution de la valeur du minimum", fontsize=14, fontweight='bold')
ax2.set_xlabel("Itération", fontsize=12)
ax2.set_ylabel("Valeur", fontsize=12)
ax2.grid(alpha=0.3)
ax2.legend()

plt.tight_layout()
plt.show()
