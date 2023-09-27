import pandas as pd
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# Η συνάρτηση comparison() συγκρινει μια εναλλακτική a με ένα profile b και επιστρεφει το σ(a,b) 
# a = g(a) , b = g(b), profile = [q,p,v], weights = k, desc_list = indexes of descending criteria
def comparison(a,b,profile,weights,desc_list):
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
    #start of the comparison 

    #Υπολογισμός δείκτη ολικής συμφωνίας c_big
    c_small = []
    for i in range(len(a)):
        if i in desc_list:
            if a[i] >= b[i] + p[i]:
                c_small.append(0)
            elif a[i] > b[i] + q[i]:
                c_small.append(1)
            else:
                c_small.append((b[i]-a[i]+p[i])/(p[i]-q[i]))
        else:
            if a[i] <= b[i] - p[i]:
                c_small.append(0)
            elif a[i] > b[i] - q[i]:
                c_small.append(1)
            else:
                c_small.append((a[i]-b[i]+p[i])/(p[i]-q[i]))
    
    c_big = np.dot(np.array(c_small),np.array(weights))/sum(weights)

    #Υπολογισμος δείκτη μερικής ασυμφωνίας d_small
    d_small=[]
    s_greek = 1
    for i in range(len(a)):
        if i in desc_list:
            if a[i] < b[i] + p[i]:
                d_small.append(0)
            elif a[i] > b[i] + v[i]:
                d_small.append(1)
                s_greek = 0
            else:
                d_small.append((a[i]-b[i]-p[i])/(v[i]-p[i]))
        else:
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
    st.title('ELECTRE TRI IMPLEMENTATION')


# input for the number of rows and columns
num_cols = st.slider('how many cruteria does you problem have', min_value=0, max_value=20, value=1, step=1, key="cols")
num_rows = st.slider("Enter the number of alternatives:", min_value=0, max_value=20, value=0, step=1, key="rows")

# Create a 2D list to store table data
table_data = []

# Create the main table
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

# Display the main table to get input
df = pd.DataFrame(table_data[1:], columns=table_data[0]) 
st.write("Enter your data:")
data = st.data_editor(df)

# Input about which are the descending criteria
col_descend1, col_descend2 = st.columns([0.7,0.3])
desc_list = []
col_descend1.write("Specify the criteria that have descending value of preference (e.g. price):")
for j in range(num_cols):
    desc_list.append(col_descend2.toggle(label="criterion_no."+str(j+1)))
desc_arr = np.where(np.array(desc_list)==True)
desc_list = desc_arr[0].tolist()

st.divider()

# Get the number of profiles. profiles_table[] is used to create a profile table , profiles[] stores every profile table
profiles_count = st.slider('how many profiles does you problem have', min_value=1, max_value=max(num_rows-1,2), value=1, step=1, key="profiles")
profiles = []
profiles_table = [[''],['q(b)'],['p(b)'],['v(b)'],['g(b)']]
# create empty table for a profile
for i in range(5):
    for z in range(num_cols):
        if i==0:
            profiles_table[i].append("criterion_no."+str(z+1))
        else:
            profiles_table[i].append(0.0)
profiles_df = pd.DataFrame(profiles_table[1:], columns=profiles_table[0])

# Display profiles tables to get input
for i in range(profiles_count):
    st.title("profile no "+str(i+1)+":")
    dt_ed = st.data_editor(profiles_df,key=i)
    profiles.append(dt_ed)

l_value = st.number_input('please enter the lamda value',min_value=0.0,max_value=1.0,value=0.7)
pessimicity = st.selectbox('Do you want to run the optimistic method or the pessimistic',('pessimistic','optimistic'))

submited = st.button(label="Submit all tables", type='primary')


if submited:
    #s_greek[0] stores σ(a,b) , s_greek[1] stores σ(b,a).
    #final_results[0] stores the index of the alternative and final_results[1] stores the class it is assigned to
    s_greek=[0,0]
    final_results = [[],[]]
    unfinished = False
    #Every alternative is compared with every profile
    for i in range(1,num_rows+1):
        for j in range(profiles_count):
            profiles_list = profiles[j].values.tolist()
            s_greek[0] = comparison(data.iloc[i][1:],profiles_list[3][1:],[row[1:] for row in profiles_list[:3]],data.iloc[0][1:],desc_list)
            s_greek[1] = comparison(profiles_list[3][1:],data.iloc[i][1:],[row[1:] for row in profiles_list[:3]],data.iloc[0][1:],desc_list)
            #Break if invalid input
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
            
            #The programm requires the profiles to be ordered. If the alternative reaches a profile that is better, 
            #it gets asigned to the according class
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

        #Create the data for the plot
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

        # set width and draw horizontal lines
        plt.figure().set_figwidth(12)
        for y1 in y:
            plt.hlines(y1,0,(max_val*1.2),colors='grey',linewidth=0.5)
        # Plot the lines
        for i in range(len(x)):
            plt.plot(x[i], y,linewidth=0.6,color='black')

        # Fill the area between lines
        for i in range(len(x)):
            plt.fill_between(x[i], y,num_cols-1,  color='grey', alpha=(0.4))

        #final_results gets converted to classes[] which has the following structure
        #classes=[['alternative1','alternative3'],['alternative2','alternative4']] in this example there are 2 classes
        #class 1 contains alternatives 1 and 3, and class 2 contains alternatives 2 and 4
        final_results = np.array(final_results)
        classes = []
        for i in range(profiles_count+1):
            classes.append(np.where(final_results[1]==i)[0])

        # Display the classes side by side
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











