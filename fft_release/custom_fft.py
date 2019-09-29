import numpy as np


def custom_dft(input_signal):
    x = np.asarray(input_signal, dtype=float)
    N = x.shape[0]
    result = np.zeros(N, dtype=complex)
    for i in range(N):
        z = np.zeros(2)
        for j in range(N):
            p = 2 * np.pi * j * i / N
            z[0] += x[j] * np.cos(p)
            z[1] -= x[j] * np.sin(p)
        result[i] = z[0] + z[1] * 1j

    return result


def custom_fft(input_signal):
    x = np.asarray(input_signal, dtype=float)
    N = x.shape[0]

    if np.log2(N) % 1 > 0:
        N_old = N
        x_old = x
        while np.log2(N) % 1 > 0:
            N -= 1

        x = np.zeros(N)
        for i in range(N):
            x[i] = x_old[i]
        x = custom_fft(x)

    N_min = min(N, 32)

    n = np.arange(N_min)
    k = n[:, None]
    M = np.exp(-2j * np.pi * n * k / N_min)
    X = np.dot(M, x.reshape((N_min, -1)))

    # build-up each level of the recursive calculation all at once
    while X.shape[0] < N:
        X_even = X[:, : int(X.shape[1] / 2)]
        X_odd = X[:, int(X.shape[1] / 2):]
        factor = np.exp(-1j * np.pi * np.arange(X.shape[0])
                        / X.shape[0])[:, None]
        X = np.vstack([X_even + factor * X_odd,
                       X_even - factor * X_odd])

    return X.ravel()
