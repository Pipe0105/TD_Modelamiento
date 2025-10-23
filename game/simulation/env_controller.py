# Entorno de simulación teoria de colas MMC con Simpy

## Cada enemigo representa un cliente que llega al sistema con distribución exponencial (λ).
## Cada torre representa un servidor con tiempo de servicio exponencial (μ).


import simpy
from .enemy_process import EnemyGenerator
from .player_economy import PlayerEconomy
from .metrics import SimulationMetrics

class TowerDefenseEnv:
    def __init__(self, num_towers: int, lambda_rate: float, mu_rate: float):

        self.env = simpy.Environment()
        self.num_towers = num_towers
        self.lambda_rate = lambda_rate
        self.mu_rate = mu_rate

        # inicializador de metricas compartidas

        self.metrics = SimulationMetrics()

        # Procesos Principales

        self.enemy_gen = EnemyGenerator (

            env = self.env,
            num_towers = num_towers,
            lambda_rate = lambda_rate,
            mu_rate = mu_rate,
            metrics = self.metrics
        )

        self.economy = PlayerEconomy (

            env = self.env,
            enemy_gen = self.enemy_gen,
            metrics = self.metrics
        )


    def run (self, sim_time: float):

        # segundos simulados

        print("Iniciando simulacion Tower Defense")

        self.env.process(self.enemy_gen.generate_enemies())
        self.env.process(self.economy.manage())

        self.env.run(until= sim_time)
        self.metrics.summary(self.env.now, self.enemy_gen.server.capacity)


if __name__ == "__main__":

    # ejemplo de prueba

    sim = TowerDefenseEnv ( num_towers=2, lambda_rate=0.9, mu_rate=1.2)
    sim.run(sim_time=60)

        