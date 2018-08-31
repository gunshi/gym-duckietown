import math
import numpy as np
from controllers import Controller


class UARandomExploration(Controller):

    def __init__(self, env, fake_uncertainty=1):
        Controller.__init__(self, env)
        self.uncertainty = fake_uncertainty

    def _do_update(self, dt):
        return self.predict(dt)

    def predict(self, observation):
        return np.random.uniform(0, 1, 2), self.uncertainty

    def learn(self, observations, actions):
        pass

    def save(self):
        print('I didn\'t learn a thing...')

    def reset(self):
        pass