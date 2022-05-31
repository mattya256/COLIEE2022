#MakeDataで作成したファイル,ルールベースのシステムの結果をもとに解答を作成する。
#makeExcelは与え荒れれた答えと比較して解答率を出力し、こちらは分析などには使えず結果のみを出力する。

from fileinput import filename
import os
import re
import math
import pickle
import csv
import LegalDataList
import numpy as np



Rule_name = "/Ronbuntest6_20220330_all_2/Ans_Module_Suiron.txt" #TESTH18~R02ルールベース

#KIS1
vername_list = ["R02/Test1_1/","R01/Test1_1/","H30/Test1_1/","H18-H29_ver0_0/"]


Dict = {"H18":["H18"],"H19":["H19"],"H20":["H20"],"H21":["H21"],"H22":["H22"],"H23":["H23"],"H24":["H24"],\
"H25":["H25"],"H26":["H26"],"H27":["H27"],"H28":["H28"],"H29":["H29"],"H30":["H30"],"R01":["R1","R01"],"R02":["R02"],"R03":["R03"]}

# RM_List = ["H30","R01","R02"]
RM_List = []

for line in RM_List:
    del Dict[line]

MethodList = ["Majority","Confidence_max","Confidence_sum"]

Ikiti = -1 #アンサンブルに使用する閾値

ID = "TESTA"

def MakeAnswer():
    Dict_Dict = {"Rule":{},"Majority":{},"Confidence_max":{},"Confidence_sum":{}}
    #Ruleは{問題番号:[解答,モジュール番号]}
    #他は{問題番号:[0の個数,1の個数]}

    for vername in vername_list:
        input_dir = "data/output/Answer_2022/ver" + vername +"/"
        List1 = os.listdir(input_dir)
        for dir1 in List1:
            List2 = os.listdir(input_dir + "/" + dir1 )
            for dir2 in List2:
                List3 = os.listdir(input_dir + "/" + dir1 + "/" + dir2)
                for dir3 in List3:
                    for Method in MethodList:
                        with open(input_dir + dir1 + "/" + dir2 + "/" + dir3 +"/" + Method + ".csv", 'rb') as fp:
                            Dict = (pickle.load(fp))
                            for ProbNum,Ans in Dict.items():
                                AnsN = 0
                                AnsY = 0
                                if Ans == 0:
                                    AnsN = 1
                                else:
                                    AnsY = 1
                                if ProbNum in Dict_Dict[Method]:
                                    Dict_Dict[Method][ProbNum] = [Dict_Dict[Method][ProbNum][0] + AnsN, Dict_Dict[Method][ProbNum][1] + AnsY]
                                else:
                                    Dict_Dict[Method][ProbNum] = [AnsN, AnsY]
                                
                    
    input_dir = open("data/input/Result/ルールベース実行結果/" + Rule_name)
    for line in input_dir:
        line = re.sub("\n","",line).split(",")
        Dict_Dict["Rule"][line[0]] = [int(line[1]),int(line[2])]

    for Method in MethodList:
        OutputStr =""
        for ProbNum,_ in Dict_Dict[Method].items():
            if Dict_Dict["Rule"][ProbNum][1] <= Ikiti:
                if Dict_Dict["Rule"][ProbNum][0] == 0:
                    Answer = "N"
                else:
                    Answer = "Y"
            else:
                if Dict_Dict[Method][ProbNum][0] >= Dict_Dict[Method][ProbNum][1]:
                    Answer = "N"
                else:
                    Answer = "Y"
            if not Dict_Dict[Method][ProbNum][0] == Dict_Dict[Method][ProbNum][1]:
                OutputStr += ProbNum + " " + Answer + " " + ID + "\n"
        Output_dir = "data/output/Answer/ver" + vername_list[0] +"/" + Method
        Output = open(Output_dir,"w")
        Output.write(OutputStr)
        Output.close()

def MakeAnswerList():
    with open("data/output/List/Answer/BeforeAns.csv", 'rb') as fp:
        Dict = pickle.load(fp)
    
    input_dir = "data/output/TestData/ver20220326_9"
    List1 = os.listdir(input_dir)
    for dir1 in List1:
        List2 = os.listdir(input_dir + "/" + dir1 )
        for dir2 in List2:
            List3 = os.listdir(input_dir + "/" + dir1 + "/" + dir2)
            for dir3 in List3:
                filename = os.listdir(input_dir + "/" + dir1 + "/" + dir2 + "/" + dir3)
                file = open(input_dir + "/" + dir1 + "/" + dir2 + "/" + dir3 + "/" + filename[0],'r')
                for line in file.readlines():
                    line = line.split(",")
                    line[3] = re.sub("\n","",line[3])
                    if line[3] in Dict:
                        if line[0] != Dict[line[3]]:
                            print("error29725")
                    else:
                        Dict[line[3]] = line[0]

    os.makedirs("data/output/List/Answer/",exist_ok=True)
    with open("data/output/List/Answer/BeforeAns.csv" ,  'wb') as fp:
        pickle.dump(Dict, fp)
    
    file = open("data/output/List/Answer/BeforeAns_Read.txt" ,'w') 
    for Prob,Ans in Dict.items():
        file.write(re.sub("\n","",Prob) + "," + Ans + "\n")
    file.close()

def CheckAnswer():
    
    with open("data/output/List/Answer/BeforeAns.csv", 'rb') as fp:
        AnswerDict = (pickle.load(fp))
    
    for method in ["Majority","Confidence_max","Confidence_sum"]:
        CheckAnswer_Dict = {}

        for key,val in Dict.items():
            CheckAnswer_Dict[key] = [0,0]

        TrueCount = 0
        FalseCount = 0
        file = open("data/output/Answer/ver" + vername_list[0] + method ,'r') 
        for line in file.readlines():
            line = line.split(" ")
            ProbNum = line[0]
            Key = ""

            check = False
            for key,list in Dict.items():
                for x in list:
                    if  re.match("^"+x,ProbNum):
                        check = True
                        Key = key
            if not check:
                pass
                #print("NOYEAR:",ProbNum)

            if Key == "":
                continue

            if line[1] == "Y":
                Answer = 1
            elif line[1] == "N":
                Answer = 0
            if (int(AnswerDict[ProbNum]) == 0 and Answer == 0) or (int(AnswerDict[ProbNum]) == 1 and Answer == 1):
                TrueCount += 1
                CheckAnswer_Dict[Key] = [CheckAnswer_Dict[Key][0],CheckAnswer_Dict[Key][1] + 1 ]
            elif (int(AnswerDict[ProbNum]) == 1 and Answer == 0) or (int(AnswerDict[ProbNum]) == 0 and Answer == 1):
                FalseCount += 1
                CheckAnswer_Dict[Key] = [CheckAnswer_Dict[Key][0] + 1,CheckAnswer_Dict[Key][1]]

        file.close()
        print("method",method,",正",TrueCount,",負",FalseCount,",率",(TrueCount)/(TrueCount+FalseCount)) 
        for key,value in CheckAnswer_Dict.items():
            if not (value[1]+value[0]) == 0:
                print("key",key,",正",value[1],",負",value[0],",率",(value[1])/(value[1]+value[0]))

if __name__ == "__main__":
    MakeAnswer()
    MakeAnswerList()
    CheckAnswer()

