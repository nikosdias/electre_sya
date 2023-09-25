import pandas as pd
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

def comparison(a,b,profile,weights):
    q = profile[0]
    p = profile[1]
    v = profile[2]
    #checking valid data
    err = np.all(np.array(b)>0)
    if err == False:
        return -100
    err = np.all(np.array(weights)>0)
    if err == False:
        return -100
    subtract = [x - y for x, y in zip(p, q)]
    err = np.all(np.array(subtract)>0)
    if err == False:
        return -100
    subtract = [x - y for x, y in zip(v, p)]
    err = np.all(np.array(subtract)>0)
    if err == False:
        return -100
    #start of the comparison function
    c_small = []
    for i in range(len(a)):
        if a[i] <= b[i] - p[i]:
            c_small.append(0)
        elif a[i] > b[i] - q[i]:
            c_small.append(1)
        else:
            c_small.append((a[i]-b[i]+p[i])/(p[i]-q[i]))
    c_big = np.dot(np.array(c_small),np.array(weights))/sum(weights)

    d_small=[]
    s_greek = 1
    for i in range(len(a)):
        if a[i] > b[i] - p[i]:
            d_small.append(0)
        elif a[i] <= b[i] - v[i]:
            d_small.append(1)
            s_greek = 0
        else:
            d_small.append((b[i]-a[i]-p[i])/(v[i]-p[i]))
    for i in range(len(a)):
        if s_greek!=0 and d_small[i]>c_big:
            s_greek *= (1-d_small[i])/(1-c_big)
    if s_greek!=0 and s_greek!=1:
        s_greek *= c_big
    return s_greek

header = st.container()
dataset = st.container()

with header:
    st.title('electre tri implementation')


# Get user input for the number of rows and columns
num_cols = st.slider('how many cruteria does you problem have', min_value=0, max_value=20, value=1, step=1, key="cols")
num_rows = st.slider("Enter the number of alternatives:", min_value=0, max_value=20, value=0, step=1, key="rows")

# Create a 2D list to store table data
table_data = []

for k in range(num_rows+2):
    row = []
    for j in range(num_cols+1):
        if k == 0 and j != 0:
            cell_value = "criterion_no."+str(j)
        elif k==1 and j==0:
            cell_value = "weights" 
        elif k>=2 and j==0:
            cell_value = "alternative "+str(k-1)
        elif k==0 and j==0:
            cell_value = "*"
        else:
            cell_value = 0.0
        row.append(cell_value)
    table_data.append(row)

df = pd.DataFrame(table_data[1:], columns=table_data[0]) 

st.write("Enter your data:")
data = st.data_editor(df)

profiles_count = st.slider('how many profiles does you problem have', min_value=1, max_value=max(num_rows-1,2), value=1, step=1, key="profiles")
profiles = []
profiles_table = [[''],['q(b)'],['p(b)'],['v(b)'],['g(b)']]
for i in range(5):
    for z in range(num_cols):
        if i==0:
            profiles_table[i].append("criterion_no."+str(z+1))
        else:
            profiles_table[i].append(0.0)
profiles_df = pd.DataFrame(profiles_table[1:], columns=profiles_table[0])

for i in range(profiles_count):
    st.title("profile no "+str(i+1)+":")
    dt_ed = st.data_editor(profiles_df,key=i)
    profiles.append(dt_ed)

l_value = st.number_input('please enter the lamda value',min_value=0.0,max_value=1.0,value=0.7)
pessimicity = st.selectbox('Do you want to run the optimistic method or the pessimistic',('pessimistic','optimistic'))

submited = st.button(label="Submit all tables", type='primary')


if submited:
    s_greek=[0,0]
    final_results = [[],[]]
    unfinished = False
    for i in range(1,num_rows+1):
        for j in range(profiles_count):
            profiles_list = profiles[j].values.tolist()
            s_greek[0] = comparison(data.iloc[i][1:],profiles_list[3][1:],[row[1:] for row in profiles_list[:3]],data.iloc[0][1:])
            s_greek[1] = comparison(profiles_list[3][1:],data.iloc[i][1:],[row[1:] for row in profiles_list[:3]],data.iloc[0][1:])
            if s_greek[0]==(-100) or s_greek[1]==-100:
                unfinished = True
                break
            #the following code determines the dominance relation and stores it in the variable comparison_result
            #the variable value translates to the following dominance relationships {0: b>a , 1: a>b, 2: a|b, -1: aRb}
            if s_greek[0]>=l_value:
                if s_greek[1]>=l_value:
                    comparison_result = 2
                else:
                    comparison_result = 1
            elif s_greek[1]>=l_value:
                comparison_result = 0
            else:
                comparison_result=-1
            
            if (pessimicity == 'optimistic' and comparison_result == 0) or (pessimicity == 'pessimistic' and comparison_result != 1):
                final_results[0].append(i)
                final_results[1].append(j)
                break
            if j == profiles_count-1:
                final_results[0].append(i)
                final_results[1].append(j+1)

    if unfinished:
        st.write('Your data was invalid')
    else:
        y, end_line = [0],[0]
        x = [[0] for abc in range(profiles_count)]
        for p in range(num_cols):
            y.append(p)
        for k in range(profiles_count):
            profiles_list = profiles[k].values.tolist()
            x[k].extend(profiles_list[3][1:])
        max_val = max(x[profiles_count-1])
        end_line.extend([max_val*1.2]*num_cols)
        x.append(end_line)

        # Create a figure and axis
        plt.figure().set_figwidth(12)
        for y1 in y:
            plt.hlines(y1,0,(max_val*1.2),colors='grey',linewidth=0.5)
        # Plot the line
        for i in range(len(x)):
            plt.plot(x[i], y,linewidth=0.6,color='black')

        # Fill the area between the vertical lines
        for i in range(len(x)):
            plt.fill_between(x[i], y,num_cols-1,  color='grey', alpha=(0.4))


        final_results = np.array(final_results)
        classes = []
        for i in range(profiles_count+1):
            classes.append(np.where(final_results[1]==i)[0])

        cols = st.columns((2*profiles_count)+1)

        counter = profiles_count+1
        for cl in classes:
            cols[2*(profiles_count-counter+1)].header('Class ' + str(counter)+':')
            final_classes = []
            for c in cl:
                final_classes.append(data.iloc[c+1][0])
            cols[2*(profiles_count-counter+1)].table(final_classes)
            if counter!=1:
                cols[2*(profiles_count-counter+1)+1].header("<")
            counter -= 1
        # Show the plot
        st.pyplot(plt)











