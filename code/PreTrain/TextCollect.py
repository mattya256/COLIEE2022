#複数のTextファイルを一つに書き換える

import os
import re
from tabnanny import verbose
from googletrans import Translator
import pandas as pd
import csv

Search_dic = {1:"総合", 2:"最高裁判所" , 3:"高等裁判所" , 4:"下級裁判所" , 5:"行政事件" , 6:"労働事件" , 7:"知的財産"}
Search_int_list = [2,3,4,5,6,7] #上のやつに対応、2なら最高裁判所の結果のみを検索
NengouList = ["平成","令和"]

ver = "20220311_onlyHanrei"

MaxLine = 10000000

UseWiki = False #Wikipediaのデータも使用する。
UseWiki_same_Minpou = True #Wikipediaのデータを民法条文と同じだけ使用する。

#multiNLIの英語の含意関係のデータセットを呼び出し、日本語に翻訳して保存する
#使うときはmain()で指定する
def TranslateDataset():

    translator = Translator()

    df = pd.read_json("data_PreTraining/input/multinli_1.0_train.jsonl", orient='records', lines=True)
    df_choose = df[['gold_label','sentence1','sentence2']].head(10)

    OutputList = []

    for index,row in df_choose.iterrows():
        label = 2
        if row['gold_label'] == "neutral":
            pass
        else:
            if row['gold_label'] == "contradiction":
                label = 0
            elif row['gold_label'] == "entailment":
                label = 1
            else:
                print(index,row)
                print("error2975")
            sentence1_ja = translator.translate(row['sentence1'],dest = "ja").text
            sentence2_ja = translator.translate(row['sentence2'],dest = "ja").text
            OutputList.append([label,sentence1_ja,sentence2_ja])
        
    print(OutputList)

    with open('data_PreTraining/input/multinli_1.0_train_ja_Google.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerows(OutputList)

def TextCollect():
    
    filecount = filecount_sum = 0 #読み込み出力したファイル数のカウント
    linecount = linecount_sum = 0 #読み込み出力した文章数のカウント
    Charcount = Charcount_sum = 0 #読み込み出力した文字数のカウント
    
    outputdir = "data_PreTraining/input/BigData/BigData_" + ver + ".txt"
    outputdir_memo = "output/PreTraining/memo/BigData/BigData_" + ver + "_出力メモ.txt"

    output_file_claer = open(outputdir, 'w')#ファイルの初期化
    output_file_claer.write("")
    output_file_claer.close()

    output_file = open(outputdir, 'a')

    logStr = "" 
    
    #民法から作成したデータも統合

    String = ""
    f = open('data_PreTraining/output/民法/Minpou.txt', 'r') 
    filecount += 1
    for fileline in f:        
        linecount += 1
        Charcount += len(fileline)
        String += fileline
    output_file.write(String)
    logStr += "\n裁判名:民法条文リスト\n"
    logStr += "ファイル数:" + str(filecount) + ", 文章数:" + str(linecount) + ", 文字数:" + str(Charcount) + "\n"
    filecount_sum,linecount_sum,Charcount_sum = filecount + filecount_sum, linecount + linecount_sum ,Charcount + Charcount_sum
    filecount = linecount = Charcount = 0         
    f.close()

    for Search_int in Search_int_list:
        inputdir_base =  "data_PreTraining/output/" + str(Search_dic[Search_int])  + "判例_Text/"

        for Nengou in NengouList: 
            MinYear = 0
            MaxYear = 0
            if Nengou == "昭和":
                MinYear = 22
                MaxYear = 64
            elif Nengou == "平成":
                MinYear = 1
                MaxYear = 30    #31にすると令和1年度とかぶる所がでてきそう
            elif Nengou == "令和":
                MinYear = 1
                MaxYear = 4
            for Year in range(MinYear,MaxYear+1):
                String = ""#一年ごとにStringを書き込む
                for PageNumber in range(1,1000):#ページ番号
                    inputdir = inputdir_base + str(Nengou) + "/" + str(Year) + "/" + str(PageNumber)
                    if not os.path.exists(inputdir):
                        break
                    filename_list = os.listdir (inputdir)
                    if filename_list != []:
                        for filename in filename_list:
                            if MaxLine < linecount_sum + linecount:
                                break
                            if "hanrei.txt" in filename:#この処理がないとlogやbeforeも対象になる
                                f = open(inputdir + "/" + filename, 'r') 
                                filecount += 1
                                for fileline in f:
                                    linecount += 1
                                    Charcount += len(fileline)
                                    String += fileline
                                f.close()
                output_file.write(String)
                if not filecount == 0:
                    logStr += "裁判名:" + Search_dic[Search_int]  + ", 年号:" + Nengou + ", 年:" + str(Year)+ ", ページ番号:" + str(PageNumber) + "\n"
                    logStr += "ファイル数:" + str(filecount) + ", 文章数:" + str(linecount) + ", 文字数:" + str(Charcount) + "\n"
                filecount_sum,linecount_sum,Charcount_sum = filecount + filecount_sum, linecount + linecount_sum ,Charcount + Charcount_sum
                filecount = linecount = Charcount = 0

    logStr += "\nファイル数:" + str(filecount_sum) + ", 文章数:" + str(linecount_sum) + ", 文字数:" + str(Charcount_sum) + "\n"
    
    filecount_sum,linecount_sum,Charcount_sum = filecount + filecount_sum, linecount + linecount_sum ,Charcount + Charcount_sum
    filecount = linecount = Charcount = 0
    String = ""

    NotWikiline = linecount_sum 
    
    if UseWiki and (not UseWiki_same_Minpou or MaxLine > linecount_sum) :#Wikipediaのデータも使用する
        Wiki_file = open('data_PreTraining/input/wiki.txt', 'r') #Fujitaのフォルダ使用可
        for fileline in Wiki_file:
            if NotWikiline < linecount:
                break
            fileline = re.sub("。","。[Maru1948]",fileline)
            fileline = re.sub("\n","",fileline)
            fileline_list = fileline.split("[Maru1948]")
            for fileline_after in fileline_list:
                if fileline_after.count("。") == 1:
                    #括弧が片方のみ入ってるときは無視
                    if fileline_after.count("(") != fileline_after.count(")"):
                        pass
                    elif fileline_after.count("（") != fileline_after.count("）"):
                        pass
                    elif fileline_after.count("「") != fileline_after.count("」"):
                        pass
                    else:
                        linecount += 1
                        Charcount += len(fileline)
                        String += fileline_after + "\n"
    
    logStr += "\nWiki , 文章数:" + str(linecount) + ", 文字数:" + str(Charcount) + "\n"
    filecount_sum,linecount_sum,Charcount_sum = filecount + filecount_sum, linecount + linecount_sum ,Charcount + Charcount_sum
    logStr += "\nファイル数:" + str(filecount_sum) + ", 文章数:" + str(linecount_sum) + ", 文字数:" + str(Charcount_sum) + "\n"
    
    output_file.write(String)
    
    output_file.close()

    log_file = open(outputdir_memo, 'w')
    log_file.write(logStr)
    log_file.close()

if __name__ == "__main__":
    # TranslateDataset()
    TextCollect()
                    