#!/usr/bin/env python

# Copyright 2021 Mehdi Koşaca, Ezgi Karaca
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import shutil

class StatisticalAnalyze():
    def __init__(self,pdb_file,chain,algorithm,pssm,cut_off,iqr):
        self.pdb_file = pdb_file
        self.pdb = self.pdb_file[:-4]
        self.chain = chain
        self.algorithm = algorithm
        self.Scores_File = pd.read_table("{}_chain_{}_proton_scores".format(self.pdb,self.chain), sep = " ")
        self.pssm = pssm
        self.cut_off = float(cut_off)
        self.iqr = float(iqr)
        self.Positive_Outliers = open("{}_chain_{}_depleting_mutations".format(self.pdb,self.chain), "w")
        self.Negative_Outliers = open("{}_chain_{}_enriching_mutations".format(self.pdb,self.chain), "w")
        self.Stability_Depletings = open("{}_chain_{}_stabilizing_depleting_mutations".format(self.pdb,self.chain), "w")
        self.Stability_Enrichings = open("{}_chain_{}_stabilizing_enriching_mutations".format(self.pdb,self.chain), "w")
        self.heatmap_df = open("heatmap_df","w")
        print("Positions Mutations {}_WT_Scores Stability_WT_Scores {}_Mutant_Scores Stability_Mutant_Scores DDG_{}_Scores DDG_Stability_Scores".format(self.algorithm,self.algorithm,self.algorithm), file = self.Positive_Outliers)
        print("Positions Mutations {}_WT_Scores Stability_WT_Scores {}_Mutant_Scores Stability_Mutant_Scores DDG_{}_Scores DDG_Stability_Scores".format(self.algorithm,self.algorithm,self.algorithm), file = self.Negative_Outliers)
        print("Positions Mutations {}_WT_Scores Stability_WT_Scores {}_Mutant_Scores Stability_Mutant_Scores DDG_{}_Scores DDG_Stability_Scores".format(self.algorithm,self.algorithm,self.algorithm), file = self.Stability_Depletings)
        print("Positions Mutations {}_WT_Scores Stability_WT_Scores {}_Mutant_Scores Stability_Mutant_Scores DDG_{}_Scores DDG_Stability_Scores".format(self.algorithm,self.algorithm,self.algorithm), file = self.Stability_Enrichings)
        print("Positions Mutations DDG_{}_Scores".format(self.algorithm),file=self.heatmap_df)

    def BoxPlot(self):
        DDG_Scores = list(self.Scores_File["DDG_{}_Scores".format(self.algorithm)])
        q1 = np.quantile(DDG_Scores,0.25)
        q3 = np.quantile(DDG_Scores, 0.75)
        IQR = float(q3 - q1)
        upperfence = q3 + (self.iqr * IQR)
        lowerfence = q1 - (self.iqr * IQR)
        for i in DDG_Scores:
            if i < lowerfence:
                self.negative_outlier = q1 - (self.iqr * IQR)
                break
            else:
                self.negative_outlier = min(DDG_Scores)
        
        for i in DDG_Scores:
            if i > upperfence:
                self.positive_outlier = (q3 + self.iqr * IQR)
                break
            else:
                self.positive_outlier = max(DDG_Scores)
        boxplot = go.Figure()
        boxplot.add_trace(go.Box(y=[DDG_Scores],boxpoints="outliers",hovertemplate='<b>ΔΔG Score</b>: %{y}<extra></extra>'))
        boxplot.update_traces(q1=[np.quantile(DDG_Scores,0.25)], 
            median=[np.quantile(DDG_Scores,0.50)],
            q3=[np.quantile(DDG_Scores,0.75)],
            lowerfence=[self.negative_outlier],
            upperfence=[self.positive_outlier])
        boxplot.update_layout(title="<b>Distribution of {} ΔΔG Scores</b>".format(self.algorithm),
            title_x=0.5,
            yaxis={"title": '<b>{} ΔΔG Scores</b>'.format(self.algorithm)},
            template="plotly_white",
            font=dict(family='Times New Roman', size=20, color='black'))
        boxplot.update_yaxes(tickprefix="<b>",ticksuffix ="</b><br>")
        boxplot.write_image("{}_chain_{}_boxplot.png".format(self.pdb,self.chain), format = "png")
        boxplot.write_image("{}_chain_{}_boxplot.svg".format(self.pdb,self.chain))
        shutil.move("{}_chain_{}_boxplot.png".format(self.pdb,self.chain), "{}_chain_{}_{}_output".format(self.pdb,self.chain,self.algorithm))
        shutil.move("{}_chain_{}_boxplot.svg".format(self.pdb,self.chain), "{}_chain_{}_{}_output".format(self.pdb,self.chain,self.algorithm))
        PositionSpecificBP = px.box(self.Scores_File, x="Positions", y="DDG_{}_Scores".format(self.algorithm),color="Positions",hover_data=["Mutations"],template="plotly_white")
        PositionSpecificBP.update_layout(title="<b>Position Specific Distribution of {} ΔΔG Scores</b>".format(self.algorithm),
            title_x=0.5,
            xaxis={"title": '<b>Positions</b>'},
            yaxis={"title": '<b>ΔΔG {} Scores</b>'.format(self.algorithm)},
            xaxis_nticks=len(self.Scores_File["Positions"]))
        PositionSpecificBP.update_xaxes(tickprefix="<b>",ticksuffix ="</b><br>")
        PositionSpecificBP.update_yaxes(tickprefix="<b>",ticksuffix ="</b><br>")
        PositionSpecificBP.write_image("{}_chain_{}_PositionSpecificBoxPlot.png".format(self.pdb,self.chain), format = "png")
        PositionSpecificBP.write_image("{}_chain_{}_PositionSpecificBoxPlot.svg".format(self.pdb,self.chain))
        shutil.move("{}_chain_{}_PositionSpecificBoxPlot.png".format(self.pdb,self.chain), "{}_chain_{}_{}_output".format(self.pdb,self.chain,self.algorithm))
        shutil.move("{}_chain_{}_PositionSpecificBoxPlot.svg".format(self.pdb,self.chain), "{}_chain_{}_{}_output".format(self.pdb,self.chain,self.algorithm))
       
    def HeatMap(self):
        try:
            heatmap = pd.read_table("heatmap_df",sep = " ")
            mid = float(0 - heatmap["DDG_{}_Scores".format(self.algorithm)].min() / (heatmap["DDG_{}_Scores".format(self.algorithm)].max() - heatmap["DDG_{}_Scores".format(self.algorithm)].min()))
            colorscale = [[0, 'rgba(0, 102, 170, 255)'],
            [mid, 'rgba(255, 255, 255, 0.85)'],
            [1, 'rgba(214, 39, 40, 0.85)']]
            fig = go.Figure(go.Heatmap(colorbar={"title": " <b>{} ΔΔG Scores</b>".format(self.algorithm)},
                z=self.Scores_File["DDG_{}_Scores".format(self.algorithm)],
                x=self.Scores_File["Mutations"],
                y=self.Scores_File["Positions"],
                colorscale=colorscale,
                zmin=self.negative_outlier,
                zmax=self.positive_outlier,
                hovertemplate='Mutation: %{x}<br>Position: %{y}<br>ΔΔG: %{z}<extra></extra>'))
            fig.update_layout(title="<b>Heatmap for chain {} of {}</b>".format(self.chain,self.pdb),
                title_x=0.5,
                yaxis={"title": '<b>Positions</b>'},
                xaxis={"title": '<b>Mutations</b>'},
                yaxis_nticks=len(self.Scores_File["Positions"]),
                width=800, height=800)
            fig.update_xaxes(tickprefix="<b>",ticksuffix="</b><br>")
            fig.write_image("{}_chain_{}_heatmap.png".format(self.pdb,self.chain), format = "png")
            fig.write_image("{}_chain_{}_heatmap.svg".format(self.pdb,self.chain))
            shutil.move("{}_chain_{}_heatmap.png".format(self.pdb,self.chain), "{}_chain_{}_{}_output".format(self.pdb,self.chain,self.algorithm))
            shutil.move("{}_chain_{}_heatmap.svg".format(self.pdb,self.chain), "{}_chain_{}_{}_output".format(self.pdb,self.chain,self.algorithm))
        except:
            pass
        
    def Detect_Outliers(self): #detect positive and negative outliers by IQR rule.
        Q1 = np.quantile(self.Scores_File["DDG_{}_Scores".format(self.algorithm)], 0.25)
        Q3 = np.quantile(self.Scores_File["DDG_{}_Scores".format(self.algorithm  )], 0.75)
        IQR = Q3 - Q1
        Upper_Bound = Q3 + (self.iqr*IQR)
        Lower_Bound = Q1 - (self.iqr*IQR)
        for i in range(0, len(self.Scores_File)):
            if self.Scores_File.iloc[i]["DDG_{}_Scores".format(self.algorithm)] >= Upper_Bound:
                print(self.Scores_File.iloc[i]["Positions"],self.Scores_File.iloc[i]["Mutations"],self.Scores_File.iloc[i]["{}_WT_Scores".format(self.algorithm)],self.Scores_File.iloc[i]["Stability_WT_Scores"],self.Scores_File.iloc[i]["{}_Mutant_Scores".format(self.algorithm)],self.Scores_File.iloc[i]["Stability_Mutant_Scores"],self.Scores_File.iloc[i]["DDG_{}_Scores".format(self.algorithm)],self.Scores_File.iloc[i]["DDG_Stability_Scores"], file = self.Positive_Outliers)
            elif self.Scores_File.iloc[i]["DDG_{}_Scores".format(self.algorithm)] <= Lower_Bound:
                print(self.Scores_File.iloc[i]["Positions"],self.Scores_File.iloc[i]["Mutations"],self.Scores_File.iloc[i]["{}_WT_Scores".format(self.algorithm)],self.Scores_File.iloc[i]["Stability_WT_Scores"],self.Scores_File.iloc[i]["{}_Mutant_Scores".format(self.algorithm)],self.Scores_File.iloc[i]["Stability_Mutant_Scores"],self.Scores_File.iloc[i]["DDG_{}_Scores".format(self.algorithm)],self.Scores_File.iloc[i]["DDG_Stability_Scores"], file = self.Negative_Outliers)
            else:
                print(self.Scores_File.iloc[i]["Positions"],self.Scores_File.iloc[i]["Mutations"],self.Scores_File.iloc[i]["DDG_{}_Scores".format(self.algorithm)], file=self.heatmap_df)
        self.Positive_Outliers.close()
        self.Negative_Outliers.close()
        self.heatmap_df.close()
    
    def Stability_Filter(self): #filtering mutations by stabilizing energies
        self.depleting_mutations = pd.read_table("{}_chain_{}_depleting_mutations".format(self.pdb,self.chain), sep = " ")
        self.enriching_mutations = pd.read_table("{}_chain_{}_enriching_mutations".format(self.pdb,self.chain), sep = " ")
        for i in range(0, len(self.depleting_mutations)):
            if self.depleting_mutations.iloc[i]["DDG_Stability_Scores"] < 0:
                print(self.depleting_mutations.iloc[i]["Positions"],self.depleting_mutations.iloc[i]["Mutations"],self.depleting_mutations.iloc[i]["{}_WT_Scores".format(self.algorithm)],self.depleting_mutations.iloc[i]["Stability_WT_Scores"],self.depleting_mutations.iloc[i]["{}_Mutant_Scores".format(self.algorithm)],self.depleting_mutations.iloc[i]["Stability_Mutant_Scores"],self.depleting_mutations.iloc[i]["DDG_{}_Scores".format(self.algorithm)],self.depleting_mutations.iloc[i]["DDG_Stability_Scores"], file = self.Stability_Depletings)
        for i in range(0, len(self.enriching_mutations)):
            if self.enriching_mutations.iloc[i]["DDG_Stability_Scores"] < 0:
                print(self.enriching_mutations.iloc[i]["Positions"],self.enriching_mutations.iloc[i]["Mutations"],self.enriching_mutations.iloc[i]["{}_WT_Scores".format(self.algorithm)],self.enriching_mutations.iloc[i]["Stability_WT_Scores"],self.enriching_mutations.iloc[i]["{}_Mutant_Scores".format(self.algorithm)],self.enriching_mutations.iloc[i]["Stability_Mutant_Scores"],self.enriching_mutations.iloc[i]["DDG_{}_Scores".format(self.algorithm)],self.enriching_mutations.iloc[i]["DDG_Stability_Scores"], file = self.Stability_Enrichings)
        self.Stability_Enrichings.close()
        self.Stability_Depletings.close()
        shutil.move("{}_chain_{}_stabilizing_depleting_mutations".format(self.pdb,self.chain), "{}_chain_{}_{}_output".format(self.pdb,self.chain,self.algorithm))
        shutil.move("{}_chain_{}_stabilizing_enriching_mutations".format(self.pdb,self.chain), "{}_chain_{}_{}_output".format(self.pdb,self.chain,self.algorithm))
        shutil.move("{}_chain_{}_depleting_mutations".format(self.pdb,self.chain), "{}_chain_{}_{}_output".format(self.pdb,self.chain,self.algorithm))
        shutil.move("{}_chain_{}_enriching_mutations".format(self.pdb,self.chain), "{}_chain_{}_{}_output".format(self.pdb,self.chain,self.algorithm))

    def PSSM_Filter(self): #filtering mutations by PSSM rule.
        pssm_df = pd.read_csv("{}".format(self.pssm),sep = ",")
        PSSM_Depletings = open("{}_chain_{}_pssm_depleting".format(self.pdb,self.chain),"w")
        PSSM_Enrichings = open("{}_chain_{}_pssm_enriching".format(self.pdb,self.chain),"w")
        print("Positions Mutations {}_WT_Scores {}_Mutant_Scores DDG_{}_Scores DDG_Stability_Scores PSSM_wt PSSM_mut PSSM_diff".format(self.algorithm,self.algorithm,self.algorithm), file = PSSM_Depletings)
        print("Positions Mutations {}_WT_Scores {}_Mutant_Scores DDG_{}_Scores DDG_Stability_Scores PSSM_wt PSSM_mut PSSM_diff".format(self.algorithm,self.algorithm,self.algorithm), file = PSSM_Enrichings)
        position = []
        with open("{}".format(self.pdb_file),"r") as structure:
            for line in structure:
                if line[:4] == "ATOM":
                    if line[21] == self.chain:
                        psp = line[22:26]
                        position.append(int(psp))
        sequence_numbers = np.unique(position) #collect sequence numbers of related chain ID
        pssm_df["sequence_numbers"] = sequence_numbers #add sequence numbers to pssm file
        for i in range(0,len(self.depleting_mutations)):
            mutant_aa = self.depleting_mutations["Mutations"][i]
            wt_aa = self.depleting_mutations["Positions"][i][0]
            seq_number = int(self.depleting_mutations["Positions"][i][1:])
            for j in range(0,len(pssm_df)):
                if pssm_df["sequence_numbers"][j] == seq_number:
                    pssm_wt = pssm_df[wt_aa][j]
                    pssm_mut = pssm_df[mutant_aa][j]
                    pssm_diff = pssm_mut - pssm_wt
                    if ((pssm_diff <= 0) and (self.depleting_mutations.iloc[i]["DDG_Stability_Scores"] < 0)):
                        print(self.depleting_mutations.iloc[i]["Positions"],self.depleting_mutations.iloc[i]["Mutations"],self.depleting_mutations.iloc[i]["{}_WT_Scores".format(self.algorithm)],self.depleting_mutations.iloc[i]["{}_Mutant_Scores".format(self.algorithm)],self.depleting_mutations.iloc[i]["DDG_{}_Scores".format(self.algorithm)],self.depleting_mutations.iloc[i]["DDG_Stability_Scores"],pssm_wt,pssm_mut,pssm_diff, file = PSSM_Depletings)
        PSSM_Depletings.close()
        for i in range(0,len(self.enriching_mutations)):
            mutant_aa = self.enriching_mutations["Mutations"][i][-1:]
            wt_aa = self.enriching_mutations["Positions"][i][0]
            seq_number = int(self.enriching_mutations["Positions"][i][1:])
            for j in range(0,len(pssm_df)):
                if pssm_df["sequence_numbers"][j] == seq_number:
                    pssm_wt = pssm_df[wt_aa][j]
                    pssm_mut = pssm_df[mutant_aa][j]
                    pssm_diff = pssm_mut - pssm_wt
                    if ((pssm_diff) > 0 and (self.enriching_mutations.iloc[i]["DDG_Stability_Scores"] < 0)):
                        print(self.enriching_mutations.iloc[i]["Positions"],self.enriching_mutations.iloc[i]["Mutations"],self.enriching_mutations.iloc[i]["{}_WT_Scores".format(self.algorithm)],self.enriching_mutations.iloc[i]["{}_Mutant_Scores".format(self.algorithm)],self.enriching_mutations.iloc[i]["DDG_{}_Scores".format(self.algorithm)],self.enriching_mutations.iloc[i]["DDG_Stability_Scores"],pssm_wt,pssm_mut,pssm_diff, file = PSSM_Enrichings)
        PSSM_Enrichings.close()
        shutil.move("{}_chain_{}_pssm_depleting".format(self.pdb,self.chain), "{}_chain_{}_{}_output".format(self.pdb,self.chain,self.algorithm))
        shutil.move("{}_chain_{}_pssm_enriching".format(self.pdb,self.chain), "{}_chain_{}_{}_output".format(self.pdb,self.chain,self.algorithm))
        shutil.move(self.pssm, "{}_chain_{}_{}_output".format(self.pdb,self.chain,self.algorithm))

def main_DO(pdb_file,chain,algorithm,pssm,cut_off,iqr):
    c = StatisticalAnalyze(pdb_file,chain,algorithm,pssm,cut_off,iqr)
    c.BoxPlot()
    c.Detect_Outliers()
    c.HeatMap()
    c.Stability_Filter()
    if pssm != "":
        c.PSSM_Filter()

