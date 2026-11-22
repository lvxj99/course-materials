"""Self-contained numerical companion. Python 3.9+, standard library only.

These are exact toy MDP/bandit computations, not LLM training benchmarks.
Running this script regenerates lab-data.json deterministically.
"""
import json
import math
from pathlib import Path


def sigmoid(z):
    return 1.0 / (1.0 + math.exp(-z))


def close(a, b, tol=1e-9):
    assert abs(a - b) < tol, (a, b)


def finite_difference(f, x, h=1e-5):
    return (f(x + h) - f(x - h)) / (2 * h)


def clipped_objective(ratio, advantage, epsilon=0.2):
    clipped = min(1 + epsilon, max(1 - epsilon, ratio))
    return min(ratio * advantage, clipped * advantage)


def group_advantages(rewards, epsilon=1e-12):
    mean = sum(rewards) / len(rewards)
    std = math.sqrt(sum((r - mean) ** 2 for r in rewards) / len(rewards))
    return [(r - mean) / (std + epsilon) for r in rewards]


def main():
    checks = []
    gamma = 0.9
    exact_v0 = (-1 + gamma * 0.8 * 8) / (1 - gamma * 0.2)
    values = [0.0, 0.0]
    history = [[0, *values]]
    for step in range(1, 81):
        v0, v1 = values
        values = [max(2.0, -1 + gamma * (0.8 * v1 + 0.2 * v0)),
                  max(8.0, -1 + gamma * v1)]
        history.append([step, *values])
    close(values[0], exact_v0)
    close(values[1], 8.0)
    close(history[2][1], 5.12)
    close(history[3][1], 5.6816)
    checks.append('Value iteration converges to analytic Bellman solution')
    td_target = -1 + 0.9 * 6
    close(3 + 0.2 * (td_target - 3), 3.28)
    checks.append('TD target and one-step update')

    # Forward TD(0) passes on a deterministic a -> b -> c -> terminal chain.
    chain_rewards = [0.0, 0.0, 1.0]
    chain_values = [0.0, 0.0, 0.0, 0.0]
    chain_history = []
    for _ in range(3):
        for t in range(3):
            chain_values[t] = chain_rewards[t] + gamma * chain_values[t + 1]
        chain_history.append(chain_values[:3])
    expected_chain = [[0, 0, 1], [0, 0.9, 1], [0.81, 0.9, 1]]
    for actual, expected in zip(chain_history, expected_chain):
        for a, b in zip(actual, expected):
            close(a, b)
    mc_chain = [sum(gamma ** (k-t) * chain_rewards[k] for k in range(t, 3)) for t in range(3)]
    for a, b in zip(mc_chain, expected_chain[-1]):
        close(a, b)
    close(1 - (1 - 0.2) ** 5, 0.67232)
    close(0.25 * (0.4 / 0.25), 0.4)
    close(0.5 + (1 - 0.5) / 3, 2 / 3)
    close(-1 + 0.9 * 8, 6.2)
    close(-1 + 0.1 * 6.8, -0.32)
    state_value = 0.5 * 2 + 0.5 * 8
    close(state_value, 5)
    close(0.5 * (2 - state_value) + 0.5 * (8 - state_value), 0)
    close(3 + 0.2 * (-1 + 0.9 * 2 - 3), 2.56)
    close(3 + 0.2 * (-1 + 0.9 * 6 - 3), 3.28)
    close(math.log(0.03 / 0.01) - math.log(0.02 / 0.01), 0.405465108108164)
    close(1 - 0.7 ** 4, 0.7599)
    close((1 / 2 / 10) / (1 / 2 / 100), 10)
    assert [int(2 * z + 3 == 7) for z in [2, 5, 2, 1]] == [1, 0, 1, 0]
    checks.append('Worked examples: reward propagation, repeated sampling, importance weighting')

    p = 0.3
    theta = math.log(p / (1 - p))
    pg = p * (1 - p)
    close(finite_difference(sigmoid, theta), pg)
    no_base = [0.7, 0.0]
    with_base = [0.49, 0.09]
    expectation = lambda xs: p * xs[0] + (1 - p) * xs[1]
    variance = lambda xs: expectation([(x - expectation(xs)) ** 2 for x in xs])
    close(expectation(no_base), pg)
    close(expectation(with_base), pg)
    close(variance(no_base), 0.1029)
    close(variance(with_base), 0.0336)
    checks.append('Policy gradient matches finite difference; baseline preserves mean')

    rewards = [0.0, 0.0, 1.0]
    vs = [0.4, 0.5, 0.6, 0.0]
    delta = [rewards[t] + vs[t + 1] - vs[t] for t in range(3)]
    gae = [0.0] * 3
    acc = 0.0
    for t in reversed(range(3)):
        acc = delta[t] + 0.9 * acc
        gae[t] = acc
    for a, b in zip(gae, [0.514, 0.46, 0.4]):
        close(a, b)
    for t in range(3):
        close(sum(delta[t:]), 1 - vs[t])
    checks.append('GAE recursion and lambda=1 telescoping identity')

    close(clipped_objective(1.5, 2), 2.4)
    close(clipped_objective(0.5, -2), -1.6)
    close(clipped_objective(1.5, -2), -3)
    close(finite_difference(lambda r: clipped_objective(r, 1), 1.5), 0)
    close(finite_difference(lambda r: clipped_objective(r, -1), 0.5), 0)
    close(finite_difference(lambda r: clipped_objective(r, -1), 1.5), -1)
    checks.append('PPO clipping values and positive/negative gradient directions')

    beta, margin = 0.5, 0.4
    loss_fn = lambda d: math.log1p(math.exp(-beta * d))
    dpo_loss = loss_fn(margin)
    close(dpo_loss, 0.5981388693815918)
    close(finite_difference(loss_fn, margin), -beta * sigmoid(-beta * margin))
    advantage = group_advantages([1, 0, 1, 0])
    for a, b in zip(advantage, [1, -1, 1, -1]):
        close(a, b)
    assert group_advantages([0, 0, 0, 0]) == [0, 0, 0, 0]
    checks.append('DPO margin, derivative, and GRPO population-standardized rewards')

    # Enumerate every outcome of an iid Bernoulli group (G=4).
    G = 4
    mean_grad, loo_grad = 0.0, 0.0
    for bits in range(2 ** G):
        r = [(bits >> i) & 1 for i in range(G)]
        prob = math.prod(p if v else 1 - p for v in r)
        baseline = sum(r) / G
        mean_grad += prob * sum((r[i] - baseline) * (r[i] - p) for i in range(G)) / G
        loo_grad += prob * sum((r[i] - (sum(r) - r[i]) / (G - 1)) * (r[i] - p) for i in range(G)) / G
    close(mean_grad, (G - 1) / G * pg)
    close(loo_grad, pg)
    checks.append('Group-mean self-inclusion factor and leave-one-out baseline')

    # Exact KL-regularized bandit, reference Bernoulli(0.5).
    theta = 0.0
    trace = []
    def objective(z):
        prob = sigmoid(z)
        kl = prob * math.log(2 * prob) + (1 - prob) * math.log(2 * (1 - prob))
        return prob - beta * kl
    for step in range(2001):
        prob = sigmoid(theta)
        grad = prob * (1 - prob) * (1 - beta * theta)
        if step in [0, 10, 100]:
            close(finite_difference(objective, theta), grad)
        if step % 5 == 0:
            trace.append([step, prob, objective(theta)])
        theta += 0.2 * grad
    optimum = sigmoid(1 / beta)
    close(trace[-1][1], optimum, 1e-6)
    assert all(b[2] >= a[2] - 1e-12 for a, b in zip(trace, trace[1:]))
    checks.append('Exact KL bandit gradient; numerical convergence to analytic optimum')

    result = {
        'status': 'passed', 'checks': checks,
        'mdp': {'gamma': gamma, 'value_iteration': history, 'exact_v0': exact_v0, 'exact_v1': 8},
        'td_propagation': {'gamma': gamma, 'alpha': 1, 'rewards': chain_rewards,
                           'mc': mc_chain, 'td_passes': chain_history},
        'policy_gradient': {'p': p, 'gradient': pg, 'variance_no_baseline': variance(no_base),
                            'variance_with_baseline': variance(with_base)},
        'gae': {'rewards': rewards, 'values': vs, 'delta': delta, 'lambda': 0.9, 'advantages': gae},
        'dpo': {'beta': beta, 'margin': margin, 'loss': dpo_loss, 'preference_probability': sigmoid(beta * margin)},
        'grpo': {'rewards': [1, 0, 1, 0], 'advantages': advantage, 'std_convention': 'population'},
        'bandit': {'beta': beta, 'optimum': optimum, 'trace': trace,
                   'beta_curve': [[b / 100, sigmoid(1 / (b / 100))] for b in range(10, 201, 2)]},
    }
    destination = Path(__file__).with_name('lab-data.json')
    destination.write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(json.dumps({'status': result['status'], 'checks_passed': len(checks),
                      'V_star_s0': exact_v0, 'bandit_P_A': trace[-1][1],
                      'bandit_analytic': optimum, 'data': str(destination)}, indent=2))


if __name__ == '__main__':
    main()
