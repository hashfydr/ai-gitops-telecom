import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import confusion_matrix
import numpy as np

def plot_multi_user_results(csv_path):
    data = pd.read_csv(csv_path)
    
    # We plot based on the two physical metrics: Loss and Delay
    X = data[['lost_packets', 'delay_sum_ns']]
    y = data['label']
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    model = LogisticRegression()
    model.fit(X_scaled, y)
    y_pred = model.predict(X_scaled)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

    # 1. Decision Boundary Plot (16 Nodes)
    h = .02
    x_min, x_max = X_scaled[:, 0].min() - 1, X_scaled[:, 0].max() + 1
    y_min, y_max = X_scaled[:, 1].min() - 1, X_scaled[:, 1].max() + 1
    xx, yy = np.meshgrid(np.arange(x_min, x_max, h), np.arange(y_min, y_max, h))
    Z = model.predict(np.c_[xx.ravel(), yy.ravel()]).reshape(xx.shape)

    ax1.contourf(xx, yy, Z, alpha=0.2, cmap='RdYlGn_r')
    scatter = sns.scatterplot(x=X_scaled[:, 0], y=X_scaled[:, 1], hue=y, 
                               palette={0: 'green', 1: 'red'}, s=150, edgecolors='k', ax=ax1)
    
    # Label each point with its Flow ID for clarity
    for i, txt in enumerate(data['flow_id']):
        ax1.annotate(f"ID:{txt}", (X_scaled[i, 0], X_scaled[i, 1]), 
                     xytext=(5, 5), textcoords='offset points', fontsize=9)

    ax1.set_title('Samsung PRISM: Multi-User Fault Isolation (16 Nodes)')
    ax1.set_xlabel('Scaled Packet Loss')
    ax1.set_ylabel('Scaled Delay (ns)')
    ax1.legend(title="Status", labels=['Healthy', 'Faulty'])

    # 2. Confusion Matrix
    cm = confusion_matrix(y, y_pred)
    sns.heatmap(cm, annot=True, fmt='d', cmap='Greens', ax=ax2,
                xticklabels=['Pred Healthy', 'Pred Fault'],
                yticklabels=['Actual Healthy', 'Actual Fault'])
    ax2.set_title('Detection Reliability (N=16)')

    plt.tight_layout()
    plt.savefig('results/week1_final_analysis.png')
    print("Final visualization saved to results/week1_final_analysis.png")

if __name__ == "__main__":
    plot_multi_user_results('results/training_data.csv')
