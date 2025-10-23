
# Economia del jugador

import simpy

class PlayerEconomy:

    def __init__(self, env: simpy.Environment, enemy_gen, metrics):

        self.env = env
        self.enemy_gen = enemy_gen
        self.metrics = metrics
        self.decision_interval = 5 

    def manage(self):

        while True:
            yield self.env.timeout( self.decision_interval)

            if (
                self.metrics.money >= self.metrics.tower_cost
                and self.enemy_gen.server.capacity < self.metrics.max_towers
            ):
                self.add_tower()
                self.metrics.money -= self.metrics.tower_cost
            elif (
                self.metrics.money < self.metrics.tower_cost / 2
                and self.enemy_gen.server.capacity > self.metrics.min_towers
            ):
                self.remove_tower()

            print(
                f"[{self.env.now:6.2f}] Dinero: {self.metrics.money:.2f} | "
                f"Torres: {self.enemy_gen.server.capacity} | "
                f"Enemigos derrotados: {self.metrics.enemies_defeated}"
            )

    def add_tower(self):
        """Agrega una torre creando un nuevo recurso con mayor capacidad."""
        new_capacity = self.enemy_gen.server._capacity + 1
        old_server = self.enemy_gen.server
        self.enemy_gen.server = type(old_server)(self.env, capacity=new_capacity)
        print(f"[{self.env.now:6.2f}] Nueva torre construida. Total: {new_capacity}")

    def remove_tower(self):
        """Vende una torre creando un nuevo recurso con menor capacidad."""
        new_capacity = max(self.enemy_gen.server._capacity - 1, self.metrics.min_towers)
        old_server = self.enemy_gen.server
        self.enemy_gen.server = type(old_server)(self.env, capacity=new_capacity)
        print(f"[{self.env.now:6.2f}] Torre vendida. Total: {new_capacity}")