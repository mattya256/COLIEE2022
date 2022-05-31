# 過去問から訓練データを作成するクラス

import csv
import re
import pickle
import os

import CompareSentence
import LegalDataList
import LegalMethod

def main(useT1list, year, TrainOrTest , ver = "0", MinRevCount = 0, ProRevCount = 0, SeqRevCount = 0, ABProCount  = 0 , UseOkikae = False , DelKakko = False , Kumiawase = False , SCDictver = "" ,Compare_Count = 10):
    """"
    MinRevCount 民法部分を否定形にするか、0ならそのまま、1なら否定形（自作)
    ProRevCount 問題部分を否定形にするか、0ならそのまま、1なら否定形（自作)
    SeqRevCount 民法と問題の順番を置き替えるべきか、0ならそのまま、1なら入れ替え（ここでは民法部分と問題部分が一緒なので意味なし)
    ABProCount  民法と問題を一部アルファベットに置き替えるか、0ならそのまま、1なら入れ替え
    useT1list = True #T1をリストとして使用する(falseの場合は一文として使用される)
    year = ['H19','H20','H22','H23','H25','H26','H28','H29','R01']
    条番号が記述されているときに、その条文で置き換えるか
    """

    OutputDir = 'data/output/' + TrainOrTest + 'Data/ver'+ ver + '/Pro_'+str(MinRevCount)+str(ProRevCount)+str(SeqRevCount)+str(ABProCount)
    ProbListOutputDir = 'data/output/ProgramTest/ver'+ ver + '/'+TrainOrTest+'_'+str(MinRevCount)+str(ProRevCount)+str(SeqRevCount)+str(ABProCount)
    
    TestCaseList = []#作成した[解答, 条文部分, 問題文]のリスト、最終的にファイルに出力

    condition = 3  # 0は民法条文読み終わり問題読み始め前,1は民法条文読み中,2は問題文読み中,3は問題の途中でない時
    i = 0  # デバック用の数値、ループ回数をカウント

    Answer = None  # 問題の解答がYかNか
    T1 = ''  # 民法条文
    Minpou_T1 = []  # 民法条文一覧から作成した民法条文リストから取得した民法条文のリスト
    T1list = []  # 問題文から読み取った民法条文のリスト
    T2 = ''  # 問題文
    Problist = []  # 問題のリスト、[問題番号、条番号のリスト、条文のリスト、問題、答え]を持つ
    ProbNumber = ''  # 問題番号
    ZyoNumList = [] #問題に関連する条文番号のリスト

    ProbCount = 0 #問題数計測のために使用、前年度までの合計問題数を記録

    ZyoNum = '0'


    for x in year:  # 年ごとにループ
        f = open('data/input/COLIEE2021_traindata/riteval_' + x + '_jp.xml', 'r')
        datalist = f.readlines()
        for data in datalist:
            i += 1
            if 'pair id' in data:  # 問題の解答を抽出
                if condition == 3:
                    if ('Y' in data) and not ('N' in data):
                        Answer = True
                        condition = 0
                    elif ('N' in data) and not ('Y' in data):
                        Answer = False
                        condition = 0
                    else:
                        Answer = True
                        condition = 0
                        print("Answerがありません:"+str(i) + ', ' + data)
                    m = re.search('pair id=(\"|\')[\-HR0-9A-Z]*(\"|\')', data)  # 問題番号の抽出
                    if m:
                        ProbNumber = re.sub('pair id=(\"|\')', '', m.group())
                        ProbNumber = re.sub('(\"|\')', '', ProbNumber)
                    else:
                        print("error4862" + data)
                else:
                    print("error02:"+str(i) + ', ' + data)
            elif '<t1>' in data:  # 民法条文部分のスタート
                if condition == 0:
                    condition = 1
                else:
                    print("error0:"+str(i) + ', ' + data)
            elif '</t1>' in data:  # 民法条文部分の終了
                if condition == 1:
                    condition = 0
                else:
                    print("error1:"+str(i) + ', ' + data)
            elif '<t2>' in data:  # 問題部分のスタート
                if condition == 0:
                    condition = 2
                else:
                    print("error2:"+str(i) + ', ' + data)
            elif '</t2>' in data:  # 問題部分の終了、データの作成
                if condition == 2:
                    condition = 3
                    if Answer != None and T1 != '' and T2 != '':
                        for LargeAB_for in LegalDataList.LARGEAB:#AB問題を記録
                            if LargeAB_for in T2:
                                with open("data/input/LARGEABProb.csv", 'rb') as fp:
                                    LARGEABProb_dic = pickle.load(fp)
                                if not ProbNumber in LARGEABProb_dic:
                                    LARGEABProb_dic[ProbNumber] = True
                                    with open("data/input/LARGEABProb.csv", 'wb') as fp:
                                        pickle.dump(LARGEABProb_dic, fp)
                                break
                        for num in ZyoNumList:#民法条文のリストから、問題文で指定された条文番号に関係する条文のリストのみを抽出
                            if UseOkikae:
                                num_withKou = num + "_1"
                                Minpou_T1 += LegalDataList.Minpoudict_withKou_Okikae_Make[num_withKou]
                                while(True):
                                    num_withKou = re.sub('_.*', '', num_withKou) + "_" + str(int(re.sub('.*_', '', num_withKou)) + 1)
                                    if num_withKou in LegalDataList.Minpoudict_withKou_Okikae_Make:
                                        Minpou_T1 += LegalDataList.Minpoudict_withKou_Okikae_Make[num_withKou]
                                    else:
                                        break
                                Minpou_T1 += LegalDataList.Minpoudict[num]#20211219置き替えないものも追加、20211219_1再度オフに
                            else:
                                Minpou_T1 += LegalDataList.Minpoudict[num]
                        if not useT1list:#問題文の条文をそのまま使うとき(複数条文があった時それらを一つの文として扱う)
                            T1, T2 = LegalMethod.replaceNandU(T1, T2)
                            if TrainOrTest == "Train":#列数を揃えるための処理
                                TestCaseList.append(LegalMethod.MakeList(T1 = T1, T2 = T2 , Answer = Answer, MinRevCount = MinRevCount, ProRevCount = ProRevCount,SeqRevCount =  SeqRevCount, ABProCount = ABProCount ,DelKakko_bool = DelKakko))
                            else:
                                TestCaseList.append(LegalMethod.MakeList(T1 = T1, T2 = T2 , Answer = Answer, MinRevCount = MinRevCount, ProRevCount = ProRevCount,SeqRevCount =  SeqRevCount, ABProCount = ABProCount ,ProbNumber = ProbNumber ,DelKakko_bool = DelKakko))
                        else:#条文のリストをもとに、条文一つに対して一つずつ訓練データを作成する
                            if not Kumiawase:#組み合わせを増やさない
                                for T1line in Minpou_T1:#指定された条文番号に関係する条文のリストについてひとつずつ処理
                                    T1line, T2 = LegalMethod.replaceNandU(T1line, T2)
                                    if TrainOrTest == "Train":#列数を揃えるための処理
                                        TestCaseList.append(LegalMethod.MakeList(T1 = T1line, T2 = T2 , Answer = Answer, MinRevCount = MinRevCount, ProRevCount = ProRevCount,SeqRevCount =  SeqRevCount, ABProCount = ABProCount ,DelKakko_bool = DelKakko))
                                    else:
                                        TestCaseList.append(LegalMethod.MakeList(T1 = T1line, T2 = T2 , Answer = Answer, MinRevCount = MinRevCount, ProRevCount = ProRevCount,SeqRevCount =  SeqRevCount, ABProCount = ABProCount ,ProbNumber = ProbNumber ,DelKakko_bool = DelKakko))
                            else:#組み合わせを増やす
                                Minpou_T1_newlist = [""]#20211219全ての組み合わせで作成
                                Minpou_T1_newlist_2 = [""]
                                for Minpou_T1_count,Minpou_T1_x in enumerate(Minpou_T1):
                                    if TrainOrTest == "Train":#TrainとTestで一問当たりの最大問題数を制限できる。
                                        maxnum = 1000
                                    else:
                                        maxnum = 1000
                                    sublist = []
                                    #if Minpou_T1_count < len(Minpou_T1):置き替え前の民法条文も追加かで切り替え
                                    if UseOkikae:
                                        intWaru = 2
                                    else:
                                        intWaru = 1
                                    #以下のループで全ての民法条文の組み合わせで作成
                                    #置き替えたものと置き替えていないもので組み合わせないように場合分けしている。
                                    if Minpou_T1_count < len(Minpou_T1)/intWaru :#20211219_1置き替え前のもののみ使用ゆえキャンセル
                                        for newlistline in Minpou_T1_newlist:
                                            if len(newlistline) + len(Minpou_T1_x) <= 1000 and len(Minpou_T1_newlist)<maxnum:
                                                sublist.append(newlistline )
                                                sublist.append(newlistline + Minpou_T1_x)
                                            else:
                                                sublist.append(newlistline)
                                        Minpou_T1_newlist = sublist
                                    else:
                                        for newlistline in Minpou_T1_newlist_2:
                                            if len(newlistline) + len(Minpou_T1_x) <= 1000 and len(Minpou_T1_newlist_2)<maxnum:
                                                sublist.append(newlistline )
                                                sublist.append(newlistline + Minpou_T1_x)
                                            else:
                                                sublist.append(newlistline)
                                        Minpou_T1_newlist_2 = sublist
                                Minpou_T1_newlist_2.remove("")
                                Minpou_T1_newlist.extend(Minpou_T1_newlist_2)#置き替え前と置き替え後を結合
                                Minpou_T1_newlist.remove("")
                                results = CompareSentence.CompareSentence(Minpou_T1_newlist,T2,SCDictver)#T2と作成したT1の類似度を比較する
                                Minpou_T1_newlist_save = Minpou_T1_newlist.copy()
                                Minpou_T1_newlist = []
                                ComapreSentenseMax = Compare_Count #最も類似度の高いn件を出力する。
                                ComapreSentenseCount = 0
                                before = ""
                                for idx, distance in results:
                                    if not before == Minpou_T1_newlist_save[idx].strip() and \
                                        (len(Minpou_T1_newlist_save[idx].strip()) + len(T2) < 500 ):
                                        Minpou_T1_newlist.append(Minpou_T1_newlist_save[idx].strip())
                                        ComapreSentenseCount += 1
                                        before = Minpou_T1_newlist_save[idx].strip()
                                    if ComapreSentenseCount >= ComapreSentenseMax:
                                        break

                                if len(Minpou_T1_newlist) == 0:
                                    print("error3875392")
                                for T1line in Minpou_T1_newlist:#指定された条文番号に関係する条文のリストについてひとつずつ処理
                                    T1line, T2 = LegalMethod.replaceNandU(T1line, T2)
                                    if TrainOrTest == "Train":#列数を揃えるための処理
                                        TestCaseList.append(LegalMethod.MakeList(T1 = T1line, T2 = T2 , Answer = Answer, MinRevCount = MinRevCount, ProRevCount = ProRevCount,SeqRevCount =  SeqRevCount, ABProCount = ABProCount ,DelKakko_bool = DelKakko))
                                    else:
                                        TestCaseList.append(LegalMethod.MakeList(T1 = T1line, T2 = T2 , Answer = Answer, MinRevCount = MinRevCount, ProRevCount = ProRevCount,SeqRevCount =  SeqRevCount, ABProCount = ABProCount ,ProbNumber = ProbNumber, DelKakko_bool = DelKakko))
                        Problist.append([ProbNumber, ZyoNumList, Minpou_T1, T1, T2, Answer])
                        ProbNumber = ''
                        ZyoNum = '0'
                        ZyoNumList = []
                        Answer = None
                        Minpou_T1 = []
                        T1 = ''
                        T1list = []
                        T2 = ''
                    else:
                        print("error122:"+str(i) + ', ' + data)
                else:
                    print("error3:"+str(i) + ', ' + data)
            elif condition == 1:  # 民法条文部分の整形、抽出
                data, ZyoNum = LegalMethod.CheckZyoNum(data, ZyoNum)
                if not '0' == ZyoNum and not ZyoNum in ZyoNumList:
                    ZyoNumList.append(ZyoNum)
                T1 += data
                T1list.append(data)
            elif condition == 2:  # 問題文部分の整形、抽出
                T2 += data
            elif '<pair>' in data or '</pair>' in data or 'dataset' in data or 'encoding' in data:
                pass
            else:
                pass
        print(x+":"+str(len(TestCaseList) - ProbCount))
        ProbCount = len(TestCaseList)
    
    print("all:"+str(len(TestCaseList)))
    OutputList = LegalMethod.MakeOutputList(TestCaseList, MinRevCount, ProRevCount, SeqRevCount, ABProCount)
    print("sum:" + str(len(OutputList)))
    os.makedirs('data/output/' + TrainOrTest + 'Data/ver' + ver , exist_ok=True)
    os.makedirs('data/output/ProgramTest/ver' + ver , exist_ok=True)
    with open(ProbListOutputDir + '.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerows(Problist)

    return OutputDir,OutputList
