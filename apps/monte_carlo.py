import streamlit as st
import numpy as np
import matplotlib.pyplot as plt


def app():
    st.title('Monte Carlo Simulation')
    # st.write(st.session_state.close_data)
    st.write("This is the Monte Carlo for selected stock")
    close_data = st.session_state['close_data']
    log_ret = np.log(close_data/close_data.shift(1))

    num_ports = 20000

    all_weights = np.zeros((num_ports, len(close_data.columns)))
    ret_arr = np.zeros(num_ports)
    vol_arr = np.zeros(num_ports)
    sharpe_arr = np.zeros(num_ports)

    for ind in range(num_ports):

        # Create Random Weights
        weights = np.array(np.random.random(len(close_data.columns)))

        # Rebalance Weights
        weights = weights / np.sum(weights)

        # Save Weights
        all_weights[ind, :] = weights

        # Expected Return
        ret_arr[ind] = np.sum((log_ret.mean() * weights) * 252)

        # Expected Variance
        vol_arr[ind] = np.sqrt(
            np.dot(weights.T, np.dot(log_ret.cov() * 252, weights)))

        # Sharpe Ratio
        sharpe_arr[ind] = ret_arr[ind]/vol_arr[ind]

    # Get the maximum value of sharpe ratio obtained from all the runs
    sharpe_arr.max()

    # Find the index location of the max sharpe value generated
    sharpe_arr.argmax()
    # st.write(sharpe_arr.argmax())

    max_sr_ret = ret_arr[sharpe_arr.argmax()]
    max_sr_vol = vol_arr[sharpe_arr.argmax()]
    fig = plt.figure(figsize=(16, 8))
    plt.scatter(vol_arr, ret_arr, c=sharpe_arr, cmap='plasma')
    plt.colorbar(label='Sharpe Ratio')
    plt.xlabel('Volatility')
    plt.ylabel('Return')
    # Add red dot for max SR
    plt.scatter(max_sr_vol, max_sr_ret, c='red', s=50, edgecolors='black')
    st.pyplot(fig)
    st.write("The highest return generated is " +
             str(round(max_sr_ret, 4)*100)+"%")
    st.write("The highest Sharpe Ratio generated is " +
             str(round(sharpe_arr.max(),4)))
    st.write("The proportion you should invest for the selected stocks are")

    weights = list(all_weights[sharpe_arr.argmax()])
    cols = list(close_data)
    dict1 = {cols[i]: weights[i] for i in range(len(cols))}
    st.write(dict1)
