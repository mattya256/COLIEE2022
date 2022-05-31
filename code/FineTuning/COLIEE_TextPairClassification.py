#SimpleTransformersの使用は以下のサイトを参考にしました。
#Simple Transformers 入門 (1) - テキスト分類 , npaka , 2020/10/3
#https://note.com/npaka/n/nfe2436ea5301

from simpletransformers.classification import ClassificationModel
import pandas as pd
import logging
import csv
import re
import os
import pickle
from transformers import T5Tokenizer,BertJapaneseTokenizer

modeldir = "model_20220311_onlyHanrei_original"

def main(train_dir , eval_dir , ver , useMybert , cuda_num = 0 ):

    #tokenizerの設定
    usebert = True#Falseのときrobert
    if usebert:
        if useMybert:#注意!!
            tokenizer = BertJapaneseTokenizer.from_pretrained('cl-tohoku/bert-base-japanese-whole-word-masking', mecab_kwargs={"mecab_dic": "ipadic", "mecab_option": None})
            Str_tokenizer = 'cl-tohoku/bert-base-japanese-whole-word-masking'
            # tokenizer = AlbertTokenizer.from_pretrained('data_PreTraining/modelList/' + modeldir, keep_accents=True)
            # Str_tokenizer = 'data_PreTraining/modelList/'
        else:
            tokenizer = BertJapaneseTokenizer.from_pretrained('cl-tohoku/bert-base-japanese-whole-word-masking', mecab_kwargs={"mecab_dic": "ipadic", "mecab_option": None})
            Str_tokenizer = 'cl-tohoku/bert-base-japanese-whole-word-masking'
    else:
        tokenizer = T5Tokenizer.from_pretrained("rinna/japanese-roberta-base")
        tokenizer.do_lower_case = True  # due to some bug of tokenizer config loading

    #モデル設定
    if usebert:
        if useMybert:
            model_type='bert'
            model_name='data_PreTraining/modelList/' + modeldir
        else:
            model_type='bert'
            model_name='cl-tohoku/bert-base-japanese-whole-word-masking'
    else:
        model_type='roberta'
        model_name='rinna/japanese-roberta-base'#20211220_1

    Resultlog={}
    log = ""
    ResultOutputDir = 'data/output/ProgramTest/ver' + ver + '/Result.csv'
    ModelOutputDir = 'outputs' +"/" + ver
    os.makedirs(ModelOutputDir,exist_ok = True)

    # ログの設定(いらないかも?)
    logging.basicConfig(level=logging.INFO)
    transformers_logger = logging.getLogger("transformers")
    transformers_logger.setLevel(logging.WARNING)

    # 学習データの作成
    train_data_withNumber  = pd.read_csv(train_dir,header = None).values.tolist()
    train_data = []
    train_t = 0
    train_f = 0
    for x in train_data_withNumber:
        if len(x[1]) + len(x[2]) <= 500:
            train_t +=1
            train_data.append([x[0],x[1],x[2]])
        else:
            train_f +=1
    train_df = pd.DataFrame(train_data, columns=['labels', 'text_a', 'text_b'])
    print(train_df,len(train_df))
    print(train_t,train_f)
    log += ("\n訓練データ有効:"+str(train_t)+",無効:"+str(train_f))

    # 評価データの作成
    train_t = 0
    train_f = 0
    eval_data_withNumber = pd.read_csv(eval_dir,header = None).values.tolist()

    for eval_data_del in (reversed(eval_data_withNumber)):
        if len(eval_data_del[1]) + len(eval_data_del[2]) <= 500:
            train_t +=1
        else:
            eval_data_withNumber.remove(eval_data_del)
            train_f +=1
    eval_data = []
    for x in eval_data_withNumber:
        eval_data.append([x[0],x[1],x[2]])
            
    eval_df = pd.DataFrame(eval_data, columns=['labels', 'text_a', 'text_b'])
    print(eval_df,len(eval_df))
    print(train_t,train_f)
    log += ("\n評価データ有効:"+str(train_t)+",無効:"+str(train_f))

    # 学習引数
    train_args={
        'cache_dir' : "cache_dir/" + ver +"/" ,
        'output_dir' : ModelOutputDir + '/model',
        'reprocess_input_data': True,
        'overwrite_output_dir': True,
        'num_train_epochs': 6,
        'max_seq_length': 512,
        'save_eval_checkpoints': False,
        'save_steps': 100000,
        'save_model_every_epoch': False,
        'train_batch_size': 32
    }

    # モデルの作成
    model = ClassificationModel(model_type, model_name, tokenizer_type=tokenizer, num_labels=2, use_cuda=True,
                                args=train_args)

    print(train_df.head())

    # 学習
    model.train_model(train_df, eval_df=eval_df, output_dir = ModelOutputDir + '/train')

    print("train_dir:",train_dir,"eval_dir:",eval_dir)
    print("trainargs:",train_args)
    print("model_type:",model_type,"model_name:",model_name)
    log += ("model_type:" + str(model_type) + "\nmodel_name:"+ str(model_name) + "\ntokenizer:" + str(Str_tokenizer))

    #結果の出力
    OutputLineList = []#このリストに登録した情報がResultファイルに出力される

    PredictList = []#民法条文と問題文のリストを登録、これをモデルに渡して推論を行う
    for x in eval_data_withNumber:
        PredictList.append([x[1],x[2]])#データ作成

    predictions, raw_outputs = model.predict(PredictList)#推論

    predictionsList = predictions.tolist()#0or1のモデルが推論した解答
    raw_outputsList = raw_outputs.tolist()#確信度,例:[-1.4111328125, 1.572265625]
    Answer_Dict = {}#問題番号をkeyに辞書を作成、中身のリストは[実際の解答,推論の解答,確信度のリスト,民法条文,問題文]
    for outputcount,x in enumerate(eval_data_withNumber):
        if x[3] in Answer_Dict:
            Answer_Dict[x[3]].append([x[0],predictionsList[outputcount],raw_outputsList[outputcount],x[1],x[2]])
        else:
            Answer_Dict[x[3]] = [[x[0],predictionsList[outputcount],raw_outputsList[outputcount],x[1],x[2]]]
        OutputLineList.append([x[3],x[0],predictionsList[outputcount],raw_outputsList[outputcount],x[1],x[2]])

    #------------------------------------------------------------------------------------------------------------
    #与えられた結果と比較を行わない純粋な解答を作成
    Majority_Dict_Ans = {}
    Confidence_max_Dict_Ans = {}
    Confidence_sum_Dict_Ans = {}
    #現在は以下の三つが全てTrueを想定
    Majority_vote_Ans = True #問題ごとの最終的な解答を多数決で行う
    Confidence_Max_Ans = True #問題ごとの最終的な解答を、最も確信度に差があるものを最終的な解答とする
    Confidence_Sum_Ans = True #問題ごとの最終的な解答を、確信度の合計から最終的な解答を求める

    #注意:TrueCount,FalseCountは予測がYやNと答えた回数を記録するもの
    #TrueCountSum,FalseCountSumとTCount,FCountは予測が正しかったか正しくなかったかをカウントするもの

    for Probnum_Ans , AnswerInfo_Ans in Answer_Dict.items():#問題番号ごとに最終的な解答を出力
        TrueCount_Ans = FalseCount_Ans = 0
        Confidence_M_Ans = 0
        False_Confidence_Sum_Ans = 0.0
        True_Confidence_Sum_Ans = 0.0
        if len(AnswerInfo_Ans) > 1:#問題文が複数の条文を参照しているとき(解答が定まらない時)
            if Majority_vote_Ans:#多数決で解答を行う
                for AnswerInfo_inlist_Ans in AnswerInfo_Ans:#問題が複数の条文を参照するとき、その条文ごとに処理
                    if AnswerInfo_inlist_Ans[1] == 1:
                        TrueCount_Ans += 1
                    else:
                        FalseCount_Ans += 1
                if TrueCount_Ans > FalseCount_Ans:
                    Majority_Dict_Ans[Probnum_Ans] = 1
                else:
                    Majority_Dict_Ans[Probnum_Ans] = 0
            else:#多数決を行わない場合は何もしない
                pass
            if Confidence_Max_Ans:#最も確信度に差があるものを最終的な解答とする
                for AnswerInfo_inlist_Ans in AnswerInfo_Ans:
                    if abs(AnswerInfo_inlist_Ans[2][0] - AnswerInfo_inlist_Ans[2][1]) > Confidence_M_Ans:#確信度の差が最大の時解答を変更
                        Confidence_M_Ans = abs(AnswerInfo_inlist_Ans[2][0] - AnswerInfo_inlist_Ans[2][1])
                        if AnswerInfo_inlist_Ans[2][1] > AnswerInfo_inlist_Ans[2][0]:#推論結果はTrue
                            Confidence_max_Dict_Ans[Probnum_Ans] = 1
                        else:#推論結果はFalse
                            Confidence_max_Dict_Ans[Probnum_Ans] = 0
            else:#確信度差を使わない場合はpass
                pass
            if Confidence_Sum_Ans:#確信度を合計し最終的な解答を行う
                for AnswerInfo_inlist_Ans in AnswerInfo_Ans:
                    False_Confidence_Sum_Ans += AnswerInfo_inlist_Ans[2][0]
                    True_Confidence_Sum_Ans += AnswerInfo_inlist_Ans[2][1]
                if True_Confidence_Sum_Ans > False_Confidence_Sum_Ans:#推論結果はTrue
                    Confidence_sum_Dict_Ans[Probnum_Ans] = 1
                else:#推論結果はFalse
                    Confidence_sum_Dict_Ans[Probnum_Ans] = 0
            else:#確信度合計を使わない場合はpass
                pass
        else:#その問題が一つの 民法条文しか参照していない時
            if AnswerInfo_Ans[0][1] == 1:#解答が正しいか
                Majority_Dict_Ans[Probnum_Ans] = 1
                Confidence_max_Dict_Ans[Probnum_Ans] = 1
                Confidence_sum_Dict_Ans[Probnum_Ans] = 1
            else:
                Majority_Dict_Ans[Probnum_Ans] = 0
                Confidence_max_Dict_Ans[Probnum_Ans] = 0
                Confidence_sum_Dict_Ans[Probnum_Ans] = 0
    
    os.makedirs("data/output/Answer_2022/ver" + ver,exist_ok=True)
    with open("data/output/Answer_2022/ver" + ver + "/Majority.csv" , 'wb') as fp:
        pickle.dump(Majority_Dict_Ans, fp)
    
    f =  open("data/output/Answer_2022/ver" + ver + "/Majority_Read.txt" , 'w')
    for Probnum_Ans , Answer_Ans in Majority_Dict_Ans.items():
        f.write(str(Probnum_Ans) + "," + str(Answer_Ans) + "\n")
    f.close()

    with open("data/output/Answer_2022/ver" + ver + "/Confidence_max.csv" , 'wb') as fp:
        pickle.dump(Confidence_max_Dict_Ans, fp)
    
    f =  open("data/output/Answer_2022/ver" + ver + "/Confidence_max_Read.txt" , 'w')
    for Probnum_Ans , Answer_Ans in Confidence_max_Dict_Ans.items():
        f.write(str(Probnum_Ans) + "," + str(Answer_Ans) + str("\n"))
    f.close()

    with open("data/output/Answer_2022/ver" + ver + "/Confidence_sum.csv" , 'wb') as fp:
        pickle.dump(Confidence_sum_Dict_Ans, fp)
    
    f =  open("data/output/Answer_2022/ver" + ver + "/Confidence_sum_Read.txt" , 'w')
    for Probnum_Ans , Answer_Ans in Confidence_sum_Dict_Ans.items():
        f.write(str(Probnum_Ans) + "," + str(Answer_Ans) + str("\n"))
    f.close()


    #-------------------------------------------------------------------------------------------------------------
    
    #現在は以下の三つが全てTrueを想定
    Majority_vote = True #問題ごとの最終的な解答を多数決で行う
    Confidence_Max = True #問題ごとの最終的な解答を、最も確信度に差があるものを最終的な解答とする
    Confidence_Sum = True #問題ごとの最終的な解答を、確信度の合計から最終的な解答を求める
    #要素が三個の配列になっているのは、上記三つの解答を個別に保存できるように
    Tcount = [0,0,0] #「問題ごとの最終的な解答」のTrueの数
    Fcount = [0,0,0] #「問題ごとの最終的な解答」のFalseの数、上と合わせて問題数と一致するはず
    TrueCountSum = 0 # 「項ごと」のTrueの数
    FalseCountSum = 0 # 「項ごと」のFalseの数

    #注意:TrueCount,FalseCountは予測がYやNと答えた回数を記録するもの
    #TrueCountSum,FalseCountSumとTCount,FCountは予測が正しかったか正しくなかったかをカウントするもの

    for Probnum , AnswerInfo in Answer_Dict.items():#問題番号ごとに最終的な解答を出力
        Answer = ["","",""] #問題の解答,"True"or"False"
        TrueCount = FalseCount = 0
        Confidence_M = 0
        False_Confidence_Sum = 0.0
        True_Confidence_Sum = 0.0
        if len(AnswerInfo) > 1:#問題文が複数の条文を参照しているとき(解答が定まらない時)
            if Majority_vote:#多数決で解答を行う
                for AnswerInfo_inlist in AnswerInfo:#問題が複数の条文を参照するとき、その条文ごとに処理
                    if AnswerInfo_inlist[0] == AnswerInfo_inlist[1]:
                        TrueCountSum+=1
                    else:
                        FalseCountSum+=1
                    if AnswerInfo_inlist[1] == 1:
                        TrueCount += 1
                    else:
                        FalseCount += 1
                if TrueCount > FalseCount:
                    if AnswerInfo_inlist[0] == 1:
                        Answer[0] = True
                    else:
                        Answer[0] = False
                        TrueCount,FalseCount = FalseCount,TrueCount
                else:
                    if AnswerInfo_inlist[0] == 0:
                        Answer[0] = True
                        TrueCount,FalseCount = FalseCount,TrueCount
                    else:
                        Answer[0] = False
            else:#多数決を行わない場合は適当な解答を代入
                Answer[0] = True
            if Confidence_Max:#最も確信度に差があるものを最終的な解答とする
                for AnswerInfo_inlist in AnswerInfo:
                    if abs(AnswerInfo_inlist[2][0] - AnswerInfo_inlist[2][1]) > Confidence_M:#確信度の差が最大の時解答を変更
                        Confidence_M = abs(AnswerInfo_inlist[2][0] - AnswerInfo_inlist[2][1])
                        if AnswerInfo_inlist[2][1] > AnswerInfo_inlist[2][0]:#推論結果はTrue
                            if AnswerInfo_inlist[0] == 1:#実際の解答もTrue
                                Answer[1] = True
                            else:
                                Answer[1] = False
                        else:#推論結果はFalse
                            if AnswerInfo_inlist[0] == 0:#実際の解答もFalse
                                Answer[1] = True
                            else:
                                Answer[1] = False
            else:#確信度差を使わない場合は適当な解答を代入
                Answer[1] = True
            if Confidence_Sum:#確信度を合計し最終的な解答を行う
                for AnswerInfo_inlist in AnswerInfo:
                    False_Confidence_Sum += AnswerInfo_inlist[2][0]
                    True_Confidence_Sum += AnswerInfo_inlist[2][1]
                if True_Confidence_Sum > False_Confidence_Sum:#推論結果はTrue
                    if AnswerInfo_inlist[0] == 1:#実際の解答もTrue
                        Answer[2] = True
                    else:
                        Answer[2] = False
                else:#推論結果はFalse
                    if AnswerInfo_inlist[0] == 0:#実際の解答もFalse
                        Answer[2] = True
                    else:
                        Answer[2] = False
            else:#確信度合計を使わない場合は適当な解答を代入
                Answer[2] = True
        else:#その問題が一つの 民法条文しか参照していない時
            if AnswerInfo[0][0] == AnswerInfo[0][1]:#解答が正しいか
                Answer[0] = Answer[1] = Answer[2] = True
                TrueCount += 1
                TrueCountSum += 1
            else:
                Answer[0] = Answer[1] = Answer[2] = False
                FalseCount += 1
                FalseCountSum += 1
        for count,Ans in enumerate(Answer):
            if Ans:
                Tcount[count] += 1
            else:
                Fcount[count] += 1
        if Majority_vote:
            OutputLineList.append(["\n0,多数決:",Probnum,Answer[0],TrueCount,FalseCount])
            Resultlog[Probnum+":0"] = [Answer[0],TrueCount,FalseCount]
        if Confidence_Max:
            OutputLineList.append(["1,確信差:",Probnum,Answer[1],Confidence_M])
            Resultlog[Probnum+":1"] = [Answer[1],Confidence_M]
        if Confidence_Sum:
            OutputLineList.append(["2,確信計:",Probnum,Answer[2],False_Confidence_Sum,True_Confidence_Sum])
            Resultlog[Probnum+":2"] = [Answer[2],False_Confidence_Sum,True_Confidence_Sum]
    os.makedirs('data/output/ProgramTest/ver' + ver ,exist_ok = True)
    with open(ResultOutputDir,'w') as f:
        writer = csv.writer(f)
        writer.writerows(OutputLineList)
    
    if Majority_vote:
        log += ("\n-----<多数決>-----")
        log += ("\n正答数:" + str(Tcount[0]) + "\n誤答数:" + str(Fcount[0]) + "\n正答率" + str(float(Tcount[0]/(Tcount[0]+Fcount[0]))))
        Resultlog["多数決"] = [Tcount[0],Fcount[0],float(Tcount[0]/(Tcount[0]+Fcount[0]))]
    if Confidence_Max:
        log += ("\n-----<最大確信度>-----")
        log += ("\n正答数:" + str(Tcount[1]) + "\n誤答数:"+ str(Fcount[1]) + "\n正答率" + str(float(Tcount[1]/(Tcount[1]+Fcount[1]))))
        Resultlog["最大確信度"] = [Tcount[1],Fcount[1],float(Tcount[1]/(Tcount[1]+Fcount[1]))]
    if Confidence_Sum:
        log += ("\n-----<確信度合計>-----")
        log += ("\n正答数:" + str(Tcount[2]) + "\n誤答数:" + str(Fcount[2]) + "\n正答率" + str(float(Tcount[2]/(Tcount[2]+Fcount[2]))))
        Resultlog["確信度合計"] = [Tcount[2],Fcount[2],float(Tcount[2]/(Tcount[2]+Fcount[2]))]
    if Majority_vote:
        log += ("\nTと答えた数(項単位):" + str(TrueCountSum) + "\nFと答えた数(項単位):" + str(FalseCountSum) + "\n正答率" + str(float(TrueCountSum/(TrueCountSum+FalseCountSum))))
        Resultlog["合計"] = [TrueCountSum,FalseCountSum,float(TrueCountSum/(TrueCountSum+FalseCountSum))]
    print(log)
    
    Output_Excel_dic = {}
    Output_Excel_dic[0] = [["多数決"]] 
    Output_Excel_dic[1] = [["最大確信度"]] 
    Output_Excel_dic[2] = [["確信度差"]] 
    for x,y in Resultlog.items():
        if not (x =="合計" or x =="多数決" or x ==  "確信度合計" or x =="最大確信度"):
            ProbNum = [re.sub(":.","",x)]
            ProbNum.extend(y)
            Output_Excel_dic[int(x[-1])].append(ProbNum)

    os.makedirs("data/output/Answer/ver" + ver , exist_ok=True)
    for count in range(3):
        with open("data/output/Answer/ver" + ver + "/" + str(count) + ".csv" ,'w') as f:
            writer = csv.writer(f)
            writer.writerows(Output_Excel_dic[count])

    return log,Resultlog