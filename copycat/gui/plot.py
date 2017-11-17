import matplotlib.pyplot as plt; plt.rcdefaults()
import numpy as np
import matplotlib.pyplot as plt

def plot_temp(temperature, status):
    status.subplot.clear()
    status.subplot.plot(temperature.history)
    status.subplot.set_ylabel('Temperature')
    status.subplot.set_xlabel('Time')
    status.subplot.set_title('Temperature History')

def plot_answers(answers, status):
    answers = sorted(answers.items(), key=lambda kv : kv[1]['count'])
    objects = [t[0] for t in answers]
    yvalues = [t[1]['count'] for t in answers]

    y_pos = np.arange(len(objects))
     
    status.subplot.clear()
    status.subplot.bar(y_pos, yvalues, align='center', alpha=0.5)
    status.subplot.set_xticks(y_pos)
    status.subplot.set_xticklabels(tuple(objects))
    status.subplot.set_ylabel('Count')
    status.subplot.set_title('Answers')
