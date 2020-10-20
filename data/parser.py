import sys
import pandas as pd
import os
import numpy as np

# Step 0: Get File name
fileName = sys.argv[1]
valSet = sys.argv[2]
# fileName = "test.csv"
# valSet = 22
# Step 1: Read and Prep File
# 1a) Delete 1st 25 Lines and last 8 lines
step1 = pd.read_csv(fileName, skiprows=25, skipfooter=8, names=["step1"])
step1.to_csv("step1.csv", index=False)

# 1b) Delete Delimiter Lines
skip_words = ["Generation", "Population size after elimination"]
with open("step1.csv") as oldfile, open("step2_temp.csv", "w") as newfile:
    for line in oldfile:
        if not any(skipWord in line for skipWord in skip_words):
            newfile.write(line)

with open("step2_temp.csv") as infile, open("step2.csv", "w") as outfile:
    for line in infile:
        outfile.write(line.replace(" | ", "|"))

os.remove("step1.csv")
os.remove("step2_temp.csv")

# Step 2: Convert to Data Frame
step3 = pd.read_csv("step2.csv")
step3.dropna(inplace=True)
temp = step3["step1"].str.split("|", n=4, expand=True)
step3["Generation"] = temp[0]
step3["Beneficial"] = temp[2]
step3["Detrimental"] = temp[3]
step3["Fitness"] = temp[4]
step3.drop(columns=["step1"], inplace=True)
os.remove("step2.csv")

# Step 4: Pivot Table

# 4a): Convert to arrays
gen_arr = [int(i) for i in step3["Generation"].tolist()]
beneficial_arr = [int(i) for i in step3["Beneficial"].tolist()]
detrimental_arr = [int(i) for i in step3["Detrimental"].tolist()]
fitness_arr = [float(i) for i in step3["Fitness"].tolist()]

# 4b) Sort as Table and Assign Column Names
beneficial_arrName = "S" + str(valSet) + " Beneficial"
detrimental_arrName = "S" + str(valSet) + " Detrimental"
fitness_arrName = "S" + str(valSet) + " Fitness"
df = pd.DataFrame(
    {
        "Generation": gen_arr,
        beneficial_arrName: beneficial_arr,
        detrimental_arrName: detrimental_arr,
        fitness_arrName: fitness_arr
    }
)
table = pd.pivot_table(
    df,
    index=["Generation"],
    values=[beneficial_arrName, detrimental_arrName, fitness_arrName],
    aggfunc={beneficial_arrName: np.mean, detrimental_arrName: np.mean, fitness_arrName: np.mean},
)
table.to_csv("pivot/"+sys.argv[1])

# 5 Create new CSV
# genList = [int(i) for i in list(range(1, 2000))]
# genDf = pd.DataFrame({"Generation": genList})
# genDf[""] = ""