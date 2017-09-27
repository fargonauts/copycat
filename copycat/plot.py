import matplotlib.pyplot as plt; plt.rcdefaults()
import numpy as np
import matplotlib.pyplot as plt
 

def plot_answers(answers):
    answers = sorted(answers.items(), key=lambda kv : kv[1]['count'])
    objects = [t[0] + ' (temp:{})'.format(t[1]['avgtemp']) for t in answers]
    yvalues = [t[1]['count'] for t in answers]

    y_pos = np.arange(len(objects))
     
    plt.bar(y_pos, yvalues, align='center', alpha=0.5)
    plt.xticks(y_pos, objects)
    plt.ylabel('Count')
    plt.title('Answers')
    plt.show()
   
