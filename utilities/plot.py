import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import scipy.stats as st
import jax.numpy as jnp
from sklearn.metrics import brier_score_loss

def plot_actualdata(X, y, x_test, y_test):
    plt.scatter(X, y,color='black', label='Train Data')
    plt.scatter(x_test, y_test,color='red',alpha=0.5,label='Test Data')
    plt.xlabel("$x$", fontsize=16)
    plt.ylabel("$y$", fontsize=16)
    plt.legend(fontsize=16)
    sns.despine()


def calibration_reg(mean,sigma,Y,ax=None):
    n =len(Y)
    mean_train = mean[int(n*1/3):int(n*2/3)]
    sigma_train = sigma[int(n*1/3):int(n*2/3)]
    y_train = Y[int(n*1/3):int(n*2/3)]
    mean_test = jnp.concatenate([mean[:int(n*1/3)],mean[int(n*2/3):]])
    sigma_test  =jnp.concatenate([sigma[:int(n*1/3)],sigma[int(n*2/3):]])
    y_test=jnp.concatenate([Y[:int(n*1/3)],Y[int(n*2/3):]])
    _,_ = calibration_regression(mean_train,sigma_train,y_train,'black','Train',ax)
    _,_ = calibration_regression(mean_test,sigma_test,y_test,'crimson','Test',ax)


def calibration_regression(mean,sigma,Y,color,label,ax=None):
    if ax is None:
      fig,ax = plt.subplots()
    df = pd.DataFrame()
    df['mean']=mean
    df['sigma']=sigma
    df['Y']=Y
    df['z']=(df['Y']-df['mean'])/df['sigma']
    df['perc'] = st.norm.cdf(df['z'])
    k=jnp.arange(0,1.1,.1)
    counts=[]
    df2 = pd.DataFrame()
    df2['Interval'] = k
    df2['Ideal'] = k
    for i in range(0,11):
      l = df[df['perc']<0.5+i*0.05]
      l = l[l['perc']>=0.5-i*0.05]
      counts.append(len(l)/len(df))
    df2['Counts']=counts

    ax.plot(k,counts,color=color,label=label)
    
    ax.plot(k,counts,'o',color=color)
    ax.plot(k,k,'o',color='green')
    ax.set_yticks(k)
    ax.set_xticks(k)
    ax.legend(fontsize=15)
    ax.set_xlabel("decile", fontsize=20)
    ax.set_ylabel("ratio of points", fontsize=20)
    ax.plot(k,k,color='green',label='Ideal')
    sns.despine()
    return df,df2

# change this funtion.
# x_linspace, Y_mean,Y_sigma, X_train,Y_train,X_test,Y_test
def plot_prediction(X,Y,x_stack,y_stack,mean,sigma,title,ax=None,n_points=300):
    if ax==None:
      fig,ax=plt.subplots(1)
    ax.plot(x_stack,mean, color='red',linewidth=3)
    for i_std in range(1,4):
      ax.fill_between(x_stack.reshape(n_points), jnp.array((mean-i_std*sigma)), jnp.array((mean+i_std*sigma)), color='lightsalmon',alpha=2/(3*i_std), label=f'$\mu\pm{i_std}\sigma$')
    ax.scatter(x_stack[:int(n_points/3)], y_stack[:int(n_points/3)],color='crimson',alpha=0.5)
    ax.scatter(X, Y,color='black',alpha=0.7)
    ax.scatter(x_stack[int(n_points*2/3):], y_stack[int(n_points*2/3):],color='crimson',alpha=0.5)
    ax.vlines(min(X),min(min(y_stack),min(mean-3*sigma)),max(max(y_stack),max(mean+3*sigma)),colors='black',linestyles='--')
    ax.vlines(max(X),min(min(y_stack),min(mean-3*sigma)),max(max(y_stack),max(mean+3*sigma)),colors='black',linestyles='--')
    ax.set_xlabel("$x$", fontsize=20)
    ax.set_ylabel("$y$", fontsize=20)
    ax.set_ylim([min(min(y_stack),min(mean-3*sigma)),max(max(y_stack),max(mean+3*sigma))])
    ax.set_xlim([min(x_stack),max(x_stack)])
    ax.set_title(title, fontsize=20)
    ax.legend(fontsize=10)
    sns.despine()


def plot_prediction_reg(X_train,Y_train,x_test,y_test,X_linspace,predict_mean,predict_sigma,title,ax=None):
    """
    plots the prediction in 1d case.
    X_train: (n_samples,1) or (n_sample,) X coordinates of the training points
    Y_train: (n_sample,1) or (n_samples,) True Y coordinates of the training points
    X_test: (n_samples,1) or (n_sample,) X coordinates of the given test points
    Y_test: (n_samples,1) or (n_sample,) True Y coordinates of given test points
    X_linspace: (n_points,) X coordinates used for predictions
    predict_mean: (n_points,) mean of predicted values over X_linspace
    predict_sigma: (n_points,) variance of predicted values over X_linspace
    title: title of the plot
    """

    if ax==None:
      fig,ax=plt.subplots(1, figsize=(10,6))
    ax.plot(X_linspace,predict_mean, color='red',linewidth=3)
    for i_std in range(1,4):
      ax.fill_between(
        X_linspace.reshape((-1,)),
        jnp.array((predict_mean-i_std*predict_sigma)),
        jnp.array((predict_mean+i_std*predict_sigma)),
        color='lightsalmon',alpha=2/(3*i_std),
        label=f'$\mu\pm{i_std}\sigma$'
        )
      
    ax.scatter(x_test, y_test,color='crimson',alpha=0.5)
    ax.scatter(X_train, Y_train,color='black',alpha=0.7)
    ax.vlines(min(X_train), min(min(y_test),min(predict_mean-3*predict_sigma)),max(max(y_test),max(predict_mean+3*predict_sigma)),colors='black',linestyles='--')
    ax.vlines(max(X_train), min(min(y_test),min(predict_mean-3*predict_sigma)),max(max(y_test),max(predict_mean+3*predict_sigma)),colors='black',linestyles='--')
    ax.set_xlabel("$x$", fontsize=20)
    ax.set_ylabel("$y$", fontsize=20)
    ax.set_ylim([min(min(y_test),min(predict_mean-3*predict_sigma)),max(max(y_test),max(predict_mean+3*predict_sigma))])
    ax.set_xlim([min(x_test),max(x_test)])
    # ax.set_ylim(-3,3)
    ax.set_title(title, fontsize=20)
    ax.legend(fontsize=10)
    sns.despine()
    
    
    
def plot_binary_class(X_scatters,y_scatters,XX1_grid,XX2_grid,grid_preds_mean,grid_preds_sigma,titles:tuple):
  """
  funtion to binary classificaton outputs

  X: points shape=(n_samples,2)
  y_hat: predictions for X shape=(n_samples,)
  XX1,XX2: grid outputs shape=(n_points,n_points)
  Z: mean of the predictions shape = (n_points,n_points)
  sigma_Z: variance of the predictions shape= (n_points,n_points) 
  titles: tuple with title of the two images. 
  """

  fig, ax = plt.subplots(1, 2, figsize=(20, 6))

  ax[0].set_title(titles[0], fontsize=16)
  ax[0].contourf(XX1_grid, XX2_grid, grid_preds_mean, cmap="coolwarm", alpha=0.8)
  hs = ax[0].scatter(X_scatters.T[0], X_scatters.T[1], c=y_scatters,cmap='bwr')
  # *hs is similar to hs[0],hs[1]
  ax[0].legend(*hs.legend_elements(), fontsize=20)

  ax[1].set_title(titles[1], fontsize=16)
  CS = ax[1].contourf(XX1_grid, XX2_grid, grid_preds_sigma, cmap="viridis", alpha=0.8)
  hs = ax[1].scatter(X_scatters.T[0], X_scatters.T[1], c=y_scatters,cmap='bwr')
  ax[1].legend(*hs.legend_elements(), fontsize=20)
  fig.colorbar(CS,ax=ax[1])
  sns.despine()


def plot_scattter_predictions(x, y_true, y_test, ax=None):
    if ax == None:
      fig, ax = plt.subplots(1,figsize=(10,6))
    hs = ax.scatter(x[:,0], x[:, 1], c = y_test, cmap="seismic")
    ax.set_title(f'Train Brier Loss {brier_score_loss(y_true,y_test)}')
    ax.legend(*hs.legend_elements(), fontsize=16)
    sns.despine()

# def plot_train_test(X_train,X_test,y_pred_train,y_pred_test,y_train,y_test):
#     """
#     predicts using the given model and parameters on training and testing data and plots side by side.
#     X_train: Training points
#     X_test: Testing points
#     y_pred_train: predicted Y labels for training data
#     y_pred_test: predicted Y labels for test data
#     y_train: true y labels of training points
#     y_test: true y labels of testing points
#     """
#     fig,(ax1,ax2) = plt.subplots(1,2,figsize=(10,5))
#     ax1.scatter(X_train[:,0],X_train[:,1],c=y_pred_train,cmap='seismic')
#     ax1.set_title(f'Train Brier Loss {brier_score_loss(y_train,y_pred_train)}')
#     ax2.scatter(X_test[:,0],X_test[:,1],c=y_pred_test,cmap='seismic')
#     ax2.set_title(f'Test Brier Loss {brier_score_loss(y_test,y_pred_test)}')
#     # ax2.set_title(brier_score_loss(y_test,y_pred_test))
#     sns.despine()