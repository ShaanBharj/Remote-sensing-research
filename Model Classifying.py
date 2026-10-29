    # -*- coding: utf-8 -*-

    
import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt
import statsmodels.formula.api as smf
    
global Lin
global Quad
global Ins

sig = []
Linear = []
Quadratic = []
Insig = []
def RegressionModel(path):
        global Lin, Quad, Ins
    
        
        df = pd.read_csv(path)
        df = df.dropna()
        
        print("Number of observations " + str(len(df)) + path)
    
        
        df['logQ'] = np.log(df['Discharge']+1)
        df['logRWE'] = np.log(df['RWE']+1)
        

        linear = smf.ols(
            'logRWE ~ logQ',
            data=df
        ).fit()
        

        quadratic = smf.ols(
            'logRWE ~ logQ + I(logQ**2)',
            data=df
        ).fit()
        

        if quadratic.aic < linear.aic:
            best = quadratic
            best_name = "Quadratic"
        else:
            best = linear
            best_name = "Linear"
        
        print(f"\nBest model according to AIC: {best_name}")
        

        if best_name == "Linear":
        
            significant = best.pvalues["logQ"] < 0.05
            if significant == True:
                path = path[17:24]
                temp = {"path": path}
                Linear.append(temp)
                Lin += 1
        
        else:
        
            significant = best.pvalues["I(logQ ** 2)"] < 0.05
            if significant == True:
                path = path[17:24]
                temp = {"path": path}
                Quadratic.append(temp)
                Quad += 1
        
        if significant:
            classification = best_name
        else:
            classification = "No significant relationship"
            Ins += 1
            path = path[17:24]
            print(path)
            temp = {"path": path}
            Insig.append(temp)
        
        print("\nClassification")
        print(classification)
        
        print("\nR² =", round(best.rsquared,4))
        print("Adjusted R² =", round(best.rsquared_adj,4))
        
        print("\nRegression summary")
        print(best.summary())
        

        plt.figure(figsize=(7,5))
        
        plt.scatter(
            df["logQ"],
            df["logRWE"],
            alpha=0.7,
            color="steelblue"
        )
        
        Q = np.linspace(
            df["logQ"].min(),
            df["logQ"].max(),
            300
        )
        
        #logQ = np.log(Q+1)
        
        
        
        pred = best.predict(
            pd.DataFrame({"logQ":Q})
        )
        
        plt.plot(
            Q,
            #np.exp(pred),
            pred,
            color="red",
            linewidth=3
        )
        
        
        plt.xlabel("Log Of Discharge")
        plt.ylabel("Log Of Relative Water Extent (RWE)")
        plt.title(classification + f"\n$R^2$={best.rsquared:.3f}")


        plt.xticks([0, 1, 2, 3, 4,5,6,7])
        plt.yticks([0.0, 0.1, 0.2, 0.3, 0.4, 0.5,0.6,0.7]) 
        
        plt.tight_layout()
        plt.show()
        
        return classification
    
Lin = 0
Quad = 0
Ins = 0
for e in os.scandir("./data/FinalData/"):
    if e.is_file():
        RegressionModel("./data/FinalData/" + (e.name))
            
print(Lin + Quad + Ins,Lin, Quad, Ins)
df = pd.DataFrame(Linear)
df.drop_duplicates().to_csv("./data/Linear.csv", index=False)
df = pd.DataFrame(Quadratic)
df.drop_duplicates().to_csv("./data/Quadratic.csv", index=False)
df = pd.DataFrame(Insig)
df.drop_duplicates().to_csv("./data/Insignificant.csv", index=False)