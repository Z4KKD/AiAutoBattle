import numpy as np
import pickle

ACTIONS = ["attack","defend","heal","power"]

class Agent:
    """Simple linear policy agent.
    Policy: score = features (vector) @ weights matrix (features x actions) + bias (actions)
    """
    def __init__(self, weights=None, bias=None):
        self.n_features = 5
        self.n_actions = len(ACTIONS)
        if weights is None:
            # small random init
            self.weights = np.random.randn(self.n_features, self.n_actions) * 0.5
        else:
            self.weights = weights.copy()
        if bias is None:
            self.bias = np.zeros(self.n_actions)
        else:
            self.bias = bias.copy()

    def act(self, features):
        """features: array-like length n_features -> returns action string"""
        f = np.asarray(features, dtype=float)
        scores = f @ self.weights + self.bias
        idx = int(np.argmax(scores))
        return ACTIONS[idx]

    def get_params(self):
        return self.weights, self.bias

    @classmethod
    def from_params(cls, weights, bias):
        return cls(weights=np.array(weights), bias=np.array(bias))

    def mutate(self, rate=0.1, scale=0.2):
        mask = np.random.rand(*self.weights.shape) < rate
        self.weights += mask * (np.random.randn(*self.weights.shape) * scale)
        maskb = np.random.rand(*self.bias.shape) < rate
        self.bias += maskb * (np.random.randn(*self.bias.shape) * scale)

    @staticmethod
    def crossover(a, b, mix_rate=0.5):
        w1, b1 = a.get_params()
        w2, b2 = b.get_params()
        mask = np.random.rand(*w1.shape) < mix_rate
        w = np.where(mask, w1, w2)
        mb = np.random.rand(*b1.shape) < mix_rate
        bias = np.where(mb, b1, b2)
        return Agent(weights=w, bias=bias)

    def save(self, path):
        with open(path, "wb") as f:
            pickle.dump(self.get_params(), f)

    @staticmethod
    def load(path):
        with open(path, "rb") as f:
            w,b = pickle.load(f)
        return Agent.from_params(w,b)
