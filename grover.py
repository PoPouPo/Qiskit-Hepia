# ============================================================
# Algorithme de Grover sur 3 qubits : recherche de l'état |101⟩
# ============================================================
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit.visualization import plot_histogram
import matplotlib.pyplot as plt

# 1. Nombre de qubits
n = 3
grover_circuit = QuantumCircuit(n, n)

# ------------------------------------------------------------
# 2. ÉTAPE D'INITIALISATION : superposition uniforme
# ------------------------------------------------------------
# Application de la porte de Hadamard sur chaque qubit
# Chaque |0⟩ devient (|0⟩ + |1⟩)/√2 → création de 2^n états équiprobables
grover_circuit.h(range(n))

# Barrière pour séparer visuellement les étapes
grover_circuit.barrier()

# ------------------------------------------------------------
# 3. ORACLE : marquage de l'état cible |101⟩
# ------------------------------------------------------------
# L'oracle change la phase de |101⟩ en -|101⟩.
# Pour cela, on utilise des portes X et une porte multi-contrôlée Z.

target = '101'  # État cible (lecture de gauche à droite : q0=1, q1=0, q2=1)

# Étape 3.1 : inverser les qubits correspondant à des '0' dans la cible
for i, bit in enumerate(target):
    if bit == '0':
        grover_circuit.x(i)

# Étape 3.2 : appliquer une porte Z multi-contrôlée (CCZ)
# Méthode : H + MCX + H sur le dernier qubit
grover_circuit.h(n-1)
grover_circuit.mcx(list(range(n-1)), n-1)  # mcx au lieu de mct
grover_circuit.h(n-1)

# Étape 3.3 : restaurer les qubits inversés
for i, bit in enumerate(target):
    if bit == '0':
        grover_circuit.x(i)

grover_circuit.barrier()

# ------------------------------------------------------------
# 4. DIFFUSEUR (U_s) : inversion autour de la moyenne
# ------------------------------------------------------------
# Réflexion de toutes les amplitudes autour de leur moyenne
# pour amplifier la solution marquée.

grover_circuit.h(range(n))
grover_circuit.x(range(n))

grover_circuit.h(n-1)
grover_circuit.mcx(list(range(n-1)), n-1)  # mcx au lieu de mct
grover_circuit.h(n-1)

grover_circuit.x(range(n))
grover_circuit.h(range(n))

grover_circuit.barrier()

# ------------------------------------------------------------
# 5. MESURE FINALE
# ------------------------------------------------------------
grover_circuit.measure(range(n), range(n))

# Visualisation du circuit
print("Circuit quantique de Grover :")
grover_circuit.draw('mpl')
plt.tight_layout()
plt.show()

# ------------------------------------------------------------
# 6. SIMULATION
# ------------------------------------------------------------
# Utilisation de AerSimulator au lieu de Aer.get_backend()
simulator = AerSimulator()

# Transpilation et exécution
compiled = transpile(grover_circuit, simulator)
job = simulator.run(compiled, shots=1024)
result = job.result()
counts = result.get_counts()

# Affichage des résultats
print("\nRésultats de la mesure :")
for state, count in sorted(counts.items(), key=lambda x: x[1], reverse=True):
    print(f"État |{state}⟩ : {count} fois ({count/1024*100:.1f}%)")

# Histogramme
plot_histogram(counts)
plt.title("Résultat de la mesure après 1 itération de Grover\nCible : |101⟩")
plt.tight_layout()
plt.show()

# Vérification du succès
target_reversed = target[::-1]  # Qiskit affiche dans l'ordre inversé (big-endian)
if target_reversed in counts:
    success_rate = counts[target_reversed] / 1024 * 100
    print(f"\n✓ État cible |{target_reversed}⟩ trouvé avec {success_rate:.1f}% de probabilité")
else:
    print("\n✗ État cible non trouvé dans les mesures")
