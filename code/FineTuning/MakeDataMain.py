#学習データの作成、訓練、テストまでまとめて行う。

import ReadMinpou
import ReadBeforeProblem
import COLIEE_TextPairClassification
import UseEntailmentDataset
import LegalDataList
# import COLIEE_Attention
import csv
import os
import pickle

cuda_num = 2

def main_loop():
    Compare_Count = 5 #上位何件を比較するか
    StartPoint = 0 #プログラムが途中で止まった場合の再開用
    ver = 2
    nowver = "BERT/20220401/"
    original_ver = nowver + str(ver)
    allyear = ['H18','H19','H20','H21','H22','H23','H24','H25','H26','H27','H28','H29','H30','R01']#これまでの全ての問題データ

    TestCount = 5 #それぞれ何回ずつテストをするか

    TestList = [[]]   #0:UseBERT,1:UseAttention,2:TestYear(list),3:UseT1list_train,4:UseT1list_test,
                      #5MinRevCount,6:ProRevCount,7:SeqRevCount,8:ABProCount9:UseOkikae,10:TestCount
    TestList_Setting = ["","","","","","","","","","","","","",""]#20211219_1
    TestList_Setting[0] = [True]#[True,False] #UseBERTList
    TestList_Setting[1] = [False]#UseAttentionList
    Test_Year_List_List = [[['H18','H19'],['H20','H21']],[['H22','H23'],['H24','H25']],[['H26','H27'],['H28','H29'],['H30','R01']]]#これまでの全ての問題データ
    TestList_Setting[2] = Test_Year_List_List[ver]
    TestList_Setting[3] = [True]#[False,True]#UseT1list_train_List
    TestList_Setting[4] = [True]#[False,True]#UseT1list_test_List
    TestList_Setting[5] = [0] #MinRevCount# 民法を否定形にするか、0ならそのまま、1なら否定形（自作)
    TestList_Setting[6] = [1]#[0,1]#ProRevCount # 問題文を否定形にするか、0ならそのまま、1なら否定形（自作)
    TestList_Setting[7] = [0]#[0,1]#SeqRevCount # 民法と問題の順番を置き替えるべきか、0ならそのまま、1なら入れ替え
    TestList_Setting[8] = [1]#[0,1]#ABProCount # 民法と問題を一部アルファベットに置き替えるか、0ならそのまま、1なら入れ替え
    TestList_Setting[9] = [True]#[True,False]#UseOkikae
    TestList_Setting[10] = [False]#[True,False]#delKakko括弧を削除するか20211219_1
    TestList_Setting[11] = [True]#[True,False]#組み合わせを増やすか
    TestList_Setting[12] = [True]#[Ture,False]#自分で事前学習したモデルを使うかどうか
    TestList_Setting[13] = [False]#[True,False]#既存の含意関係のデータセットを使用するかどうか
    for settingline in TestList_Setting:
        TestList_Save = []
        for TestList_Youso in TestList:
            for setting in settingline:
                if setting == "T3":
                    setting = TestList_Youso[3]
                if setting == "T3_break":
                    if TestList_Youso[3]:
                        setting = 1
                    else:
                        break
                TestList_Youso_append = TestList_Youso.copy()
                TestList_Youso_append.append(setting)
                TestList_Save.append(TestList_Youso_append)
        TestList = TestList_Save
    print("TestList",TestList)
    print("lenTestList",len(TestList))
    
    Result_dic = {}
    if os.path.exists('data/output/ProgramTest/ver' + original_ver  + '/Result_dic.csv'):
        with open('data/output/ProgramTest/ver' + original_ver  + '/Result_dic.csv', 'rb') as fp:
            Result_dic = pickle.load(fp)
    loopcount = 0
    for Test in TestList:
        for count in range(TestCount):
            if loopcount >= StartPoint:
                ver = original_ver + "/" + str(int(loopcount/10) * 10) + "/" + str(int(loopcount))#数値に意味はない、出力先ディレクトリを分けて分かりやすくするため
                log = ""
                for x_log , y_log in enumerate(Test):
                    log += LegalDataList.Test_Setting_CountList[x_log] + ":" + str(y_log) +"\n"
                useBERT      =  Test[0]
                useAttention =  Test[1] #BERTがFalseのときのみ実行
                Testyear =     Test[2]#訓練に使うデータ
                useT1list_train =Test[3] #T1をリストとして使用する(falseの場合は一文として使用される)
                useT1list_test = Test[4]
                Trainyear = list(set(allyear) - set(Testyear))
                MinRevCount =   Test[5] # 民法を否定形にするか、0ならそのまま、1なら否定形（自作)
                ProRevCount =   Test[6] # 問題文を否定形にするか、0ならそのまま、1なら否定形（自作)
                SeqRevCount =   Test[7] # 民法と問題の順番を置き替えるべきか、0ならそのまま、1なら入れ替え
                ABProCount  =   Test[8] # 民法と問題を一部アルファベットに置き替えるか、0ならそのまま、1なら入れ替え
                UseOkikae   =   Test[9] # 置き替えた文章を用いるか
                DelKakko    =   Test[10]#括弧を削除するか20211219_1
                Kumiawase   =   Test[11]#組み合わせを増やすか
                useMybert   =   Test[12]#自分で事前学習したモデルを使うかどうか
                useEntailmentDataset    = Test[13]#既存の含意関係のデータセットを使うかどうか
                OutputListMin = []
                print('\033[32m'+'民法をもとに訓練データの作成'+'\033[0m')
                OutputDirMin,OutputListMin = ReadMinpou.main(ver = ver ,  MinRevCount = MinRevCount , ProRevCount = ProRevCount , SeqRevCount = 0 , ABProCount = ABProCount, UseOkikae = UseOkikae ,DelKakko = DelKakko)#順番入れ替えは意味をなさないので0
                print('\033[32m'+'過去問をもとに訓練データの作成'+'\033[0m')
                OutputDirProTra,OutputListProTra = ReadBeforeProblem.main(useT1list = useT1list_train, year = Trainyear, TrainOrTest = "Train" , ver = ver , MinRevCount = MinRevCount , ProRevCount = ProRevCount ,  SeqRevCount = SeqRevCount , ABProCount = ABProCount ,UseOkikae = UseOkikae , DelKakko = DelKakko,Kumiawase = Kumiawase,SCDictver = original_ver,Compare_Count = Compare_Count)#訓練データの作成
                OutputListMin.extend(OutputListProTra)

                if useEntailmentDataset:#既存の含意関係のデータセットを訓練データに使用する
                    print('\033[32m'+'既存のデータセットをもとに訓練データの作成'+'\033[0m')
                    OutputListMin.extend(UseEntailmentDataset.UseEntailmentdataset())
            
                with open(OutputDirProTra + '_Min.csv', 'w') as f:
                    writer = csv.writer(f)
                    writer.writerows(OutputListMin)
                print('\033[32m'+'過去問をもとに検証データの作成'+'\033[0m')
                OutputDirProTest,OutputListProTest = ReadBeforeProblem.main(useT1list = useT1list_test,year =  Testyear ,TrainOrTest = "Test" , ver = ver , MinRevCount = 0 , ProRevCount = 0 , SeqRevCount = 0 , ABProCount = 0 , UseOkikae = UseOkikae , DelKakko =DelKakko,Kumiawase = Kumiawase,SCDictver = original_ver,Compare_Count = Compare_Count)#検証データの作成
                with open(OutputDirProTest + '.csv', 'w') as f:
                    writer = csv.writer(f)
                    writer.writerows(OutputListProTest)
                print(OutputDirProTra + '_Min.csv', OutputDirProTest + '.csv', cuda_num)
                if useBERT:
                    Retrun_log, Return_Resultlog = COLIEE_TextPairClassification.main(OutputDirProTra + '_Min.csv', OutputDirProTest + '.csv', ver , useMybert , cuda_num )

                log += Retrun_log
                Result_dic[loopcount] = Return_Resultlog 
                Result_dic[loopcount]["ver"] = Test
                os.makedirs('data/output/ProgramTest/ver' + ver , exist_ok=True)
                with open('data/output/ProgramTest/ver' + ver + '/log.csv', 'w') as f:
                    f.write(log)
                loopcount += 1
                
                os.makedirs('data/output/ProgramTest/ver' + original_ver , exist_ok=True)
                with open('data/output/ProgramTest/ver' + original_ver  + '/Result_dic.csv', 'wb') as fp:
                    pickle.dump(Result_dic, fp)
                with open('data/output/ProgramTest/ver' + original_ver + '/Result_dic_read.csv', 'w') as f:
                    writer = csv.writer(f)
                    writer.writerows(Result_dic.items())
            else:
                loopcount += 1


if __name__ == "__main__":
    main_loop()    