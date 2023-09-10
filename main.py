import pandas as pd
import streamlit as st
import numpy as np

def comparison(a,b,profile):
    weights = profile[0]
    q = profile[1]
    p = profile[2]
    v = profile[3]
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
    st.text('made entirely by nikos diaourtas in seven days in his house in chania')


st.title("Dynamic Table App")

# Get user input for the number of rows and columns
num_cols = st.slider('how many cruteria does you problem have', min_value=0, max_value=20, value=1, step=1, key="cols")
num_rows = st.slider("Enter the number of alternatives:", min_value=0, max_value=20, value=0, step=1, key="rows")

# Create a 2D list to store table data
table_data = []

for k in range(num_rows+1):
    row = []
    for j in range(num_cols+1):
        if k == 0 and j != 0:
            cell_value = "criterion_no."+str(j)
        elif k>=1 and j==0:
            cell_value = "alternative "+str(k)
        elif k==0 and j==0:
            cell_value = "*"
        else:
            cell_value = 0
        row.append(cell_value)
    table_data.append(row)

df = pd.DataFrame(table_data[1:], columns=table_data[0]) 

st.write("Enter your data:")
data = st.data_editor(df)

profiles_count = st.slider('how many profiles does you problem have', min_value=1, max_value=num_cols-1, value=1, step=1, key="profiles")
profiles = []
profiles_table = [[''],['w'],['q(b)'],['p(b)'],['v(b)'],['g(b)']]
for i in range(6):
    for z in range(num_cols):
        if i==0:
            profiles_table[i].append("criterion_no."+str(z))
        else:
            profiles_table[i].append(0)
profiles_df = pd.DataFrame(profiles_table[1:], columns=profiles_table[0])

for i in range(profiles_count):
    st.title("profile no "+str(i+1)+":")
    dt_ed = st.data_editor(profiles_df,key=i)
    profiles.append(dt_ed)

l_value = st.number_input('please enter the lamda value',min_value=0.0,max_value=1.0,value=0.7)
pessimicity = st.selectbox('Do you want to run the optimistic method or the pessimistic',('optimistic','pessimistic'))

submited = st.button(label="Submit all tables", type='primary')


if submited:
    s_greek=[0,0]
    final_results = [[],[]]
    unfinished = False
    for i in range(num_rows):
        for j in range(profiles_count):
            profiles_list = profiles[j].values.tolist()
            s_greek[0] = comparison(data.iloc[i][1:],profiles_list[4][1:],[row[1:] for row in profiles_list[:4]])
            s_greek[1] = comparison(profiles_list[4][1:],data.iloc[i][1:],[row[1:] for row in profiles_list[:4]])
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

    st.table(final_results)
    











