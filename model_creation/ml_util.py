import numpy as np
from matplotlib import pyplot as plt
import calculate_evaluations

#default_row "PER", "PER_H", "PRR", "PBR", "DIV_Y",
#  "ACT_Y", "RET_Y", "CAP_Y", "DEBT", "INC_PE",
#  "RET_PE", "YR_change", "RET_change"
def plot_feature_pair(model, i0, i1, r0 = np.linspace(-2,2,16), 
        r1 = np.linspace(-2,2,16), xsize=7, ysize=7, default_row = np.zeros(13)):
    X_grid, Y_grid = np.meshgrid(r0, r1)

    N = X_grid.shape[0] * X_grid.shape[1]
    full_grid = np.empty((N,13))
    for i in range(N):
        full_grid[i] = default_row

    full_grid[:,i0] = X_grid.flatten()
    full_grid[:,i1] = Y_grid.flatten()

    predictions = model.predict(full_grid).reshape(len(r0),len(r1))

    plt.figure(figsize=(xsize, ysize))
    plt.imshow(predictions, extent=[r0[0],r0[-1],r1[-1],r1[0]])
    plt.colorbar()
    plt.xlabel(calculate_evaluations.FEATURE_NAMES[i0])
    plt.ylabel(calculate_evaluations.FEATURE_NAMES[i1])
    plt.show()