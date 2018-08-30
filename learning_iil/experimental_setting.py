import math
import numpy as np
import tensorflow as tf

from gym_duckietown.envs import DuckietownEnv, DuckiebotEnv
from learning_iil.algorithms import SupervisedLearning
from learning_iil.learners import UANeuralNetworkPolicy, NeuralNetworkPolicy
from learning_iil.teachers import UncertaintyAwarePurePursuitController
from learning_iil.learners.parametrizations.tf import MonteCarloDropoutResnetOneRegression, MonteCarloDropoutResnetOneMixture

SEED = 19048  # generated by Google Random Generator (1 - 50,000)

MAP_NAME = 'udem1'
MAP_STARTING_POSITIONS = [
    [(0.8, 0.0, 1.5), 10.90],
    [(0.8, 0.0, 2.5), 10.90],
    [(1.5, 0.0, 3.5), 12.56],
    [(2.5, 0.0, 3.5), 12.56],
    [(4.1, 0.0, 2.0), 14.14],
    [(2.8, 0.0, 0.8), 15.71],
]

# all with Dataset Aggregation
algorithms = ['supervised', 'dagger', 'aggrevate', 'safe_dagger', 'upms', 'upms-ne', 'upms-sl', 'upms-ne-sl']

# learner's parametrization
parametrization_names = ['resnet_one_regression', 'resnet_one_mixture']
parametrization_classes = [MonteCarloDropoutResnetOneRegression, MonteCarloDropoutResnetOneMixture]

# teacher
teacher_name = 'pure_pursuit'

# optimization
optimization_methods_names = ['adam', 'adagrad', 'rmsprop']
optimization_methods_classes = [tf.train.AdamOptimizer, tf.train.AdagradOptimizer, tf.train.RMSPropOptimizer]
learning_rate = 1e-3

# Task Configuration
HORIZONS = [128, 256, 512, 1024, 2048]
EPISODES = [64, 32, 16, 8, 4]

ITERATIONS = 4  # to 4

SUBMISSION_DIRECTORY = 'icra2019/'


np.random.seed(SEED)


def experimental_entry(algorithm, experiment_iteration, selected_parametrization, selected_horizon, selected_episode,
                       selected_optimization):
    return '{}/{}/{}/h{}e{}/{}_{}/{}_lr_{}/'.format(
        SUBMISSION_DIRECTORY,
        algorithm,
        experiment_iteration,
        HORIZONS[selected_horizon],
        EPISODES[selected_episode],
        teacher_name,
        parametrization_names[selected_parametrization],
        optimization_methods_names[selected_optimization],
        learning_rate
    )


def simulation():
    return DuckietownEnv(
        domain_rand=True,
        max_steps=math.inf,
        map_name=MAP_NAME
    )


def robot():
    return DuckiebotEnv()


def teacher(env):
    return UncertaintyAwarePurePursuitController(
        env=env,
        following_distance=0.3,
        refresh_rate=1 / 30
    )


def task_configuration(iteration):
    return {
        'horizon': HORIZONS[iteration],
        'episodes': EPISODES[iteration]
    }


def optimization_method(index, lr):
    return optimization_methods_classes[index](lr)


def parametrization(iteration, optimization):
    return parametrization_classes[iteration](
        optimization_method(optimization, learning_rate)
    )


def supervised(env, teacher, experiment_iteration, selected_parametrization, selected_optimization, selected_horizon,
               selected_episode):

    initial_position, initial_angle = MAP_STARTING_POSITIONS[experiment_iteration]

    learner = NeuralNetworkPolicy(env=env,
                                  parametrization=parametrization(
                                      iteration=selected_parametrization,
                                      optimization=selected_optimization
                                  ),
                                  storage_location=experimental_entry(
                                      algorithm='supervised',
                                      experiment_iteration=experiment_iteration,
                                      selected_parametrization=selected_parametrization,
                                      selected_horizon=selected_horizon,
                                      selected_episode=selected_episode,
                                      selected_optimization=selected_optimization
                                  ))

    return SupervisedLearning(env=env,
                              teacher=teacher,
                              learner=learner,
                              horizon=HORIZONS[selected_horizon],
                              episodes=EPISODES[selected_episode],
                              starting_position=initial_position,
                              starting_angle=initial_angle)


if __name__ == '__main__':
    environment = simulation()
    for iteration in range(0, ITERATIONS):
        for horizon_iteration in range(0, len(HORIZONS)):
            for parametrization_iteration in range(0, len(parametrization_names)):
                for optimization_iteration in range(0, len(optimization_methods_names)):
                    method = supervised(
                        env=environment,
                        teacher=teacher(environment),
                        experiment_iteration=iteration,
                        selected_parametrization=parametrization_iteration,
                        selected_optimization=optimization_iteration,
                        selected_horizon=horizon_iteration,
                        selected_episode=horizon_iteration
                    )




