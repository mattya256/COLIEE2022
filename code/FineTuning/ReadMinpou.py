#与えられた民法条文を適切な形に変形するクラス

import pickle
import csv
import re
import os

import LegalDataList
import LegalMethod

def main(ver = '0', MinRevCount = 0, ProRevCount = 0, SeqRevCount = 0, ABProCount  = 0 ,UseOkikae = False , DelKakko = False):

    """"
    MinRevCount 民法部分を否定形にするか、0ならそのまま、1なら否定形（自作)
    ProRevCount 問題部分を否定形にするか、0ならそのまま、1なら否定形（自作)
    SeqRevCount 民法と問題の順番を置き替えるべきか、0ならそのまま、1なら入れ替え（ここでは民法部分と問題部分が一緒なので意味なし)
    ABProCount  民法と問題を一部アルファベットに置き替えるか、0ならそのまま、1なら入れ替え
    条番号が記述されているときに、その条文で置き換えるか
    """

    InputMinpouDir = 'data/input/Minpou.txt'#入力となる民法条文のディレクトリ
    OutputDir = 'data/output/TrainData/ver' + ver + '/Min_'+str(MinRevCount)+str(ProRevCount)+str(SeqRevCount)+str(ABProCount) #出力先のディレクトリ
    MinpouDictOutputDir = 'data/output/List/COLIEE_Minpoudict'#民法を辞書化したものを出力するファイルのディレクトリ

    maxlen = 0#文章の文字数の最大、学習のサイズを見るときなどに使用
    maxlendata = ''#最大文字数を持つ文章の内容

    loopcount = 0 # デバック用
    Minpoudict = {}#民法の辞書、条番号をkeyとし、それに含まれる条文のリストをvalueとする
    Minpoudict_Kakugou = {}#民法の"各号"を保存
    Minpoudict_withKou = {}#民法の辞書、条番号+_項番号をkeyとし、それに含まれる条文のリストをvalueとする
    TestCaseList  = []#最終的に出力するリスト
    Tuginikakageru_beforetext = ''
    Tuginikakageru_aftertext = ''
    condition = 0#次に掲げる等で代入を行う際に使用
    KouNum = "1" #項番号を記載

    PreTrainingData = []#PreTrainingの際にも民法条文のデータを使用できるように

    ZyoNum = '0'
    f = open(InputMinpouDir,'r')
    datalist = f.readlines()
    for data in datalist:
        if condition != 0:#次に掲げるにより単なる条文でない場合の処理
            if data.startswith(LegalDataList.KanSujiList[condition]):#「次に掲げる」に関する文章
                data = data.replace(LegalDataList.KanSujiList[condition],'',1)
                data = data.replace('。','')
                condition +=1
            else:#それ以外の文章、次の文章に移っている
                Minpoudict_Kakugou[ZyoNum+"_"+KouNum] = KakugouList
                condition = 0
        BeforeZyoNum = ZyoNum
        data,ZyoNum = LegalMethod.CheckZyoNum(data,ZyoNum)#条番号を取得する,dataを整形する(第何条などの情報を削除)
        if not ( BeforeZyoNum  == ZyoNum ):
            KouNum = "1"
        for smallint,Largenum in LegalDataList.LargeNumDict.items():#"２　組合の業務の決定及び執行は",などの大文字の数字を削除
            if data.startswith(Largenum):
                KouNum = str(smallint)
                data = data[1:]

        if '次に掲げる'  in data or '次の各号に掲げる' in data or '次のとおり' in data:#次に掲げるの処理,詳細は次行
            #1行目　Aは次に掲げる権利を持つ,2行目　人権,三行目 投票権　のようになっているため、一行目を読み飛ばし二行目から代入していく
            #Tuginikakageru_beforetextに "Aは" ,Tuginikakageru_aftertextに "を持つ" を代入する
            findNext = False
            for Next in LegalDataList.NextList:
                if ('次に掲げる'+Next) in data:
                    Tuginikakageru_beforetext = re.split(('次に掲げる'+Next),data)[0]
                    Tuginikakageru_aftertext = re.split(('次に掲げる'+Next),data)[1]
                    findNext=True
            if '次の各号に掲げる' in data:
                Tuginikakageru_beforetext = re.split('次の各号に掲げる',data)[0]
                Tuginikakageru_aftertext = re.split('次の各号に掲げる',data)[1]
                findNext=True
            if '次のとおり' in data:
                Tuginikakageru_beforetext = re.split('次のとおり',data)[0]
                Tuginikakageru_aftertext = re.split('次のとおり',data)[1]
                findNext=True
            if not findNext:
                print('new次に掲げる:'+data)
            condition = 1
            KakugouList = [] #”各号”を保存

        if condition == 1:#何の文章かチェック、「次に掲げる」の文章の時読み飛ばす
            pass
        elif re.search('。',data) or condition != 0:#条文などのとき
            
            if condition !=0:#次に掲げる内の箇条書きの処理
                KakugouList.append(data)
                data = Tuginikakageru_beforetext + data + Tuginikakageru_aftertext
                
            PreTrainingData.append(data)

            if ZyoNum in Minpoudict:#民法辞書を作成、代入や検索の時に使用するために、条番号と条文内容の辞書を作成
                Minpoudict[ZyoNum].append(data)
            else:
                Minpoudict[ZyoNum] = [data]

            if ZyoNum + "_" + KouNum in Minpoudict_withKou:
                Minpoudict_withKou[ZyoNum + "_" + KouNum].append(data)
            else:
                Minpoudict_withKou[ZyoNum + "_" + KouNum] = [data]

            T1 = T2 = data
            #TestCaseList.append(LegalMethod.MakeList(T1, T2, True, MinRevCount, ProRevCount, SeqRevCount, ABProCount))#ここで様々なテストケースを作成する
            
            
            if len(data)>maxlen:
                maxlen = len(data)
                maxlendata = data
        elif re.search('(.*)',data) or re.search('第.章',data) \
        or re.search('第.節',data) or re.search('第.款',data):#()、章、節、款のとき読み飛ばす
            pass
        else:#上記のどれにも当てはまらない時
            print('error20221:'+data)
        loopcount+=1

    #民法そのまま
    with open(MinpouDictOutputDir+ '_Kakugou.csv', 'wb') as fp:
        pickle.dump(Minpoudict_Kakugou, fp)
    
    with open(MinpouDictOutputDir+ '_Read_Kakugou.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerows(Minpoudict_Kakugou.items())

    #民法そのまま
    with open(MinpouDictOutputDir+ '.csv', 'wb') as fp:
        pickle.dump(Minpoudict, fp)
    
    with open(MinpouDictOutputDir+ '_Read.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerows(Minpoudict.items())

    #民法を項単位で分割したもの
    with open(MinpouDictOutputDir+ '_withKou.csv', 'wb') as fp:
        pickle.dump(Minpoudict_withKou, fp)
    
    with open(MinpouDictOutputDir+ '_Read_withKou.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerows(Minpoudict_withKou.items())

    #民法を項単位で分割したもので、条番号を実際の条文で置き換えたもの
    Minpoudict_withKou_Okikae= {}
    for MinpouNum,Minpou in Minpoudict_withKou.items():
        for Minpouline in Minpou:
            data = LegalMethod.ZyoubunOkikaeStart(MinpouNum,Minpouline,Minpoudict_withKou)
            if MinpouNum in Minpoudict_withKou_Okikae:
                Minpoudict_withKou_Okikae[MinpouNum].append(data)
            else:
                Minpoudict_withKou_Okikae[MinpouNum] = [data]

    with open(MinpouDictOutputDir+ '_withKou_Okikae.csv', 'wb') as fp:
        pickle.dump(Minpoudict_withKou_Okikae, fp)
    
    print(MinpouDictOutputDir+ '_withKou_Read_Okikae.csv')
    with open(MinpouDictOutputDir+ '_Read_withKou_Okikae.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerows(Minpoudict_withKou_Okikae.items())

    #ここでテストケースの作成
    if UseOkikae:
        for MinpouNum,Minpou in LegalDataList.Minpoudict_withKou_Okikae_Make.items():#自作の置き替えたものを使用
            for Minpouline in Minpou:
                TestCaseList.append(LegalMethod.MakeList(T1 = Minpouline, T2 = Minpouline,Answer = True,MinRevCount =  MinRevCount, ProRevCount = ProRevCount, SeqRevCount = SeqRevCount, ABProCount = ABProCount , DelKakko_bool =  DelKakko))#ここで様々なテストケースを作成する
        for MinpouNum,Minpou in Minpoudict.items():#20211219置き替えないものも使用
            for Minpouline in Minpou:
                TestCaseList.append(LegalMethod.MakeList(T1 = Minpouline, T2 = Minpouline,Answer = True,MinRevCount =  MinRevCount, ProRevCount = ProRevCount, SeqRevCount = SeqRevCount, ABProCount = ABProCount , DelKakko_bool =  DelKakko))#ここで様々なテストケースを作成する
    else:
        for MinpouNum,Minpou in Minpoudict.items():
            for Minpouline in Minpou:
                TestCaseList.append(LegalMethod.MakeList(T1 = Minpouline, T2 = Minpouline,Answer = True,MinRevCount =  MinRevCount, ProRevCount = ProRevCount, SeqRevCount = SeqRevCount, ABProCount = ABProCount , DelKakko_bool =  DelKakko))#ここで様々なテストケースを作成する

    print("TestCaseList:"+str(len(TestCaseList)))
    OutputList = LegalMethod.MakeOutputList(TestCaseList, MinRevCount, ProRevCount, SeqRevCount, ABProCount)
    print("OutputList:"+str(len(OutputList)))


    #事前学習で使用できるよう前処理後のデータを保存
    #現在の処理は、「。」で区切って改行している
    #括弧内の。は「、」に置き替えている。
    #(の回数で括弧内かを判定しているため、一個でも過不足があるとデータが全てぶれるので注意
    os.makedirs('data/output/TrainData/ver' + ver , exist_ok=True)

    os.makedirs('data_PreTraining/output/民法' , exist_ok=True)
    PreTrainingfile = open('data_PreTraining/output/民法/Minpou.txt','w')
    PreTrainingData_Okikae = ""
    PreTrainingData_Count = 0
    for PreTrainingData_line in PreTrainingData:
        PreTrainingfile.write(PreTrainingData_line+"\n")
    PreTrainingfile.close()

    return OutputDir,OutputList

if __name__ == "__main__":
    OutputDir,OutputList = main(ver = '0')
    with open(OutputDir + '.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerows(OutputList)