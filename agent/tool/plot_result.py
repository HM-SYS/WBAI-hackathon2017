import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--task-file', '-t', default='task_result.log')
parser.add_argument('--episode-file', '-e', default='episode_result.log')

args = parser.parse_args()

task_file = args.task_file
episode_file = args.episode_file
df_task = pd.read_csv('../log/'+task_file)
df_episode = pd.read_csv('../log/'+episode_file)
# plot task result
labels = df_task.index
label_name = []
for l in labels:
    label_name.append('task' + str(l+1))
ax = df_task.ix[:, 1:].plot.bar(stacked=True)
ax.set_xticklabels(label_name)
plt.savefig('total_task_result.jpg')

# plot episode result
tasks = set(df_episode['task'])
for i in tasks:
    df_task = df_episode[df_episode.task == i].copy()
    fig, ax1 = plt.subplots()
    s = df_task.episode
    ax1.plot(s, df_task['step'], color='r', label='step')
    ax1.set_xlabel('number of episodes')
    ax1.set_ylabel('number of steps')
    ax2 = ax1.twinx()
    ax2.plot(s, df_task['time'], color='g', label='time')
    ax2.set_ylabel('elapsed times')
    file_name = 'task' + str(i) + '.jpg'
    h1, l1 = ax1.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax1.legend(h1+h2, l1+l2, loc=2)
    plt.savefig(file_name)
