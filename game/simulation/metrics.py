
# tiempos de espera, dinero, enemigos eliminados, etc.


class SimulationMetrics:
    def __init__(self):
        # Métricas generales
        self.wait_times = []
        self.enemies_defeated = 0

        # Economía del jugador
        self.money = 100.0
        self.tower_cost = 50.0
        self.reward_per_enemy = 15.0

        # Límites
        self.min_towers = 1
        self.max_towers = 10

    def summary(self, sim_time: float, towers: int):
        """Muestra los resultados finales."""
        avg_wait = sum(self.wait_times) / len(self.wait_times) if self.wait_times else 0
        print("\n--- RESULTADOS DE SIMULACIÓN ---")
        print(f"Tiempo total simulado: {sim_time:.2f}s")
        print(f"Enemigos eliminados: {self.enemies_defeated}")
        print(f"Torres finales: {towers}")
        print(f"Dinero final: {self.money:.2f}")
        print(f"Tiempo promedio de espera: {avg_wait:.2f}s")
