import sys
import pandas as pd
import os
import numpy as np

#Call Arguments
fileName = sys.argv[1]
valStart = sys.argv[2]
valStop = sys.argv[3]

def parser(fileName, valSet, final_fileName):
    # Step 1: Read and Prep File
    # 1a) Delete 1st 25 Lines and last 8 lines
    step1 = pd.read_csv(fileName, skiprows=25, skipfooter=8, names=["step1"], engine='python')
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
    step3 = pd.read_csv("step2.csv", engine='python')
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
    table.to_csv("pivot/"+fileName, index=False)
    #Final Result Creation
    final_result = pd.read_csv("result/"+final_fileName, engine='python')
    final_result["s"+str(valSet)]=""
    final_result[beneficial_arrName]=table[beneficial_arrName]
    final_result[detrimental_arrName]=table[detrimental_arrName]
    final_result[fitness_arrName]=table[fitness_arrName]
    final_result.to_csv("result/"+final_fileName, index=False)

# Create Simulation CSV File
genList = [int(i) for i in list(range(0,2001))]
genDf = pd.DataFrame({"Generation":genList})
for x in range(1, 8):
    genDf[str(x)] = ''
genDf.to_csv("result/"+fileName+"_data.csv", index=False)
# Call Functions 
for x in range(int(valStart), int(valStop)+1):
    print("Processing "+fileName+"."+ str(x) +".csv")
    parser(fileName+"."+ str(x) +".csv", str(x), fileName+"_data.csv")

print("Pivot Tables Completed")