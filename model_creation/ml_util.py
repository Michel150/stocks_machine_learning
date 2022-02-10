import numpy as np
from matplotlib import pyplot as plt
import calculate_evaluations
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVR
from sklearn.model_selection import train_test_split

#default_row "PER", "PER_H", "PRR", "PBR", "DIV_Y",
#  "ACT_Y", "RET_Y", "CAP_Y", "DEBT", "INC_PE",
#  "RET_PE", "YR_change", "RET_change"
def plot_feature_pair(model, i0, i1, r0 = np.linspace(-2,2,32), 
        r1 = np.linspace(-2,2,32), xsize=7, ysize=7, default_row = np.zeros(13)):
    X_grid, Y_grid = np.meshgrid(r0, r1)

    N = X_grid.shape[0] * X_grid.shape[1]
    full_grid = np.empty((N,13))
    for i in range(N):
        full_grid[i] = default_row

    full_grid[:,i0] = X_grid.flatten()
    full_grid[:,i1] = Y_grid.flatten()

    predictions = model.predict(full_grid).reshape(len(r1),len(r0))

    plt.figure(figsize=(xsize, ysize))
    plt.imshow(predictions, extent=[r0[0],r0[-1],r1[-1],r1[0]])
    plt.colorbar()
    plt.xlabel(calculate_evaluations.FEATURE_NAMES[i0])
    plt.ylabel(calculate_evaluations.FEATURE_NAMES[i1])
    plt.show()

def load_prediction_model():
    dl = calculate_evaluations.data_loader(2002, 2021)
    hrefs, X, y = dl.create_datasets(2004, 2019, past=2, future=2)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.30, random_state=42)
    X_t = StandardScaler().fit_transform(X_train)
    svr = SVR(C=0.1, epsilon=0).fit(X_t, y_train)
    return svr
