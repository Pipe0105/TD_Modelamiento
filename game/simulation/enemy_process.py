
# Generiacion de enemigos y atencion de enemigos


import simpy
import random


class EnemyGenerator:

    def __init__(self, env: simpy.Environment, num_towers: int, lambda_rate: float, mu_rate: float, metrics):
        
        self.env = env
        self.server = simpy.Resource(env, capacity=num_towers)
        self.lambda_rate = lambda_rate
        self.mu_rate = mu_rate
        self.metrics = metrics

    def enemy_process(self, enemy_id: int):

        # Proceso de un enemigo: llegada, espera y servicio

        arrival_time = self.env.now
        print(f"[{arrival_time:6.2f}] Enemigo {enemy_id} llega. ")

        with self.server.request() as request:
            yield request
            wait_time = self.env.now - arrival_time
            self.metrics.wait_times.append(wait_time)

            print(f"[{self.env.now:6.2f}] Enemigo {enemy_id} atendido (esperó) {wait_time:.2f}s")

        # Tiempo de servicio exponencial

        service_time = random.expovariate(self.mu_rate)
        yield self.env.timeout(service_time)

        print(f"[{self.env.now:6.2f}] Enemigo {enemy_id} elminado en {service_time:.2f}s ")
        self.metrics.enemies_defeated += 1
        self.metrics.money += self.metrics.reward_per_enemy

    def generate_enemies(self):

        # Generador  de enemigos Exp(λ) 

        enemy_id = 0
        while True:
            yield self.env.timeout(random.expovariate(self.lambda_rate))
            enemy_id += 1
            self.env.process(self.enemy_process(enemy_id))