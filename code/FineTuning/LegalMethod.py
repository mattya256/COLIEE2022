#複数のクラスで使用する共通のメソッドを管理するクラス

from os import stat_result

import LegalDataList
import re
print("-----------------------------Legalmethod-----------------------------------------------------------------")
MakeHiteikeiOnly = True #Falseのままなら以前のまま,Trueにすると否定形にしたかつYのものは除外(Nを否定形にしたらYになるとは限らないため)

def makeF(data):  # 文章から否定形の文章を作成する
    data = data.replace("\n","")
    data += '\n'
    if True:
        Kakko =  re.search("「.*」",data)
        if Kakko:
            data = re.sub(Kakko.group(),"Kakko1234",data)#括弧を一時削除
        Tadasi = re.search("。ただし[^。]*。\n",data)
        if Tadasi:
            data = re.sub(Tadasi.group(),"。\n",data)#ただしを一次削除
    if not "。\n" in data:
        data = data.replace("\n", "。\n")
    F2 = data
    changed = False
    for Not in LegalDataList.NotList:
        if (Not[0]+"。\n") in data:
            F2 = data.replace((Not[0]+"。\n"), Not[1]+"。")
            changed = True
            break
        elif (Not[1]+"。\n") in data:
            F2 = data.replace((Not[1]+"。\n"), Not[0]+"。")
            changed = True
            break
    if not changed:
        print('error1022:',data)
    if True:
        if Tadasi:
            F2 = re.sub("。\n",Tadasi.group(),F2)
        if Kakko:
            F2 = re.sub("Kakko1234",Kakko.group(),F2)#括弧をもどす
    return F2

def DelKakko(data):
    data = re.sub("（.*）","",data)
    return data

def makeAlphabetical(data):  # 文章の一部をアルファベットや甲告丙に置き替える、匿名問題への貢献を目的
    '''
    最初に出てきた人物名からA,B,Cの順で置き替えたいため、少しややこしい処理になっている
    まず最初のループで人物名を人物名リストに出てきた順番でZ0,Z1,Z2で置き替える
    次のループで文章を最初から読んでいき、Zxが出てくる順番に応じてA,B,Cの順で置き替える
    '''
    count = 0  # 置き替えた回数
    data = data.replace("\n","")
    data += '\n'
    ABPro = data
    Okikae = True #アルファベットに置き替えるか否か、既に匿名問題になっているようなものは置き替えない
    for Alphabet in LegalDataList.LARGEAB:
        if Alphabet in ABPro:
            Okikae = False
    for Name in LegalDataList.PersonList:
        if Name in ABPro and Okikae:
            if (Name+"が") in ABPro or (Name+"を") in ABPro or (Name+"の") in ABPro or (Name+"に") in ABPro or (Name+"は") in ABPro or (Name+"、") in ABPro or (Name+"又") in ABPro:
                ABPro = ABPro.replace(Name, LegalDataList.LARGEAB[-1] + str(count))
                count += 1
            else:
                pass
    data2 = ABPro
    AlphabetCount = 0 #実際に置き替えた回数
    CheckBeforeAlphabet = False #Zを読むとTrueになる,Zの次の数字を読むとFalseに戻り置き替える
    for i in range(len(ABPro)):
        if ABPro[i] == LegalDataList.LARGEAB[-1] and Okikae and not CheckBeforeAlphabet:
            CheckBeforeAlphabet = True
        elif CheckBeforeAlphabet:
            for intcount in reversed(range(99)):
                if intcount >= 10:
                    if (ABPro[i] + ABPro[i+1]) == str(intcount):
                        ABPro = ABPro.replace(LegalDataList.LARGEAB[-1]+str(intcount),LegalDataList.LARGEAB[AlphabetCount])
                        AlphabetCount+=1
                        CheckBeforeAlphabet = False
                        i-=1
                elif ABPro[i] == str(intcount):
                    ABPro = ABPro.replace(LegalDataList.LARGEAB[-1]+str(intcount),LegalDataList.LARGEAB[AlphabetCount])
                    AlphabetCount+=1
                    CheckBeforeAlphabet = False
                    i-=1
        if i>=len(ABPro)-1:
            break
    if CheckBeforeAlphabet:
        print("error298942" + ABPro,data,data2,Okikae)
    ABPro = ABPro.replace('\n', '')
    if count > 1:  # 二カ所以上置き替えていた場合
        return ABPro
    else:
        ABPro = ""
        return ABPro

def Kanji_to_Suji(str):  # 漢数字を漢字に変換する(例,二百五十五→255)
    num = 0
    if '百' in str:
        m = re.match('[一|二|三|四|五|六|七|八|九]百', str)
        if m:
            num += LegalDataList.Kanji_Suji_pair[m.group().replace("百", "")]*100
        else:
            num += 100
    if '十' in str:
        m = re.search('[一|二|三|四|五|六|七|八|九]十', str)
        if m:
            num += LegalDataList.Kanji_Suji_pair[m.group().replace("十", "")]*10
        else:
            num += 10
    m = re.match('[一|二|三|四|五|六|七|八|九]', str[-1:])
    if m:
        num += LegalDataList.Kanji_Suji_pair[m.group().replace("十", "")]
    return num

def CheckZyoNum(data,ZyoNum):  # (第一条 債権は...)を[債権は,1]のように返す、numはString型で返却される点に注意、(例,第二百五十五条の二　→　255-2)
    m1 = re.match('第[一|二|三|四|五|六|七|八|九|十|百]+条の[一|二|三|四|五|六|七|八|九|十|百]+', data)
    m2 = re.match('第[一|二|三|四|五|六|七|八|九|十|百]+条', data)
    if m1:
        stringobje = re.sub('第', '', m1.group())
        stringobje = re.sub('条の[一|二|三|四|五|六|七|八|九|十|百]+', '', stringobje)
        num = str(Kanji_to_Suji(stringobje))
        stringobje = re.sub('第.*条の', '', m1.group())
        num = num + '-' + str(Kanji_to_Suji(stringobje))
    elif m2:
        stringobje = re.sub('第', '', m2.group())
        stringobje = re.sub('条', '', stringobje)
        num = str(Kanji_to_Suji(stringobje))
    else:
        num = str(ZyoNum)
    data = re.sub("第[一|二|三|四|五|六|七|八|九|十|百]+条の[一|二|三|四|五|六|七|八|九|十|百]+((\u3000)|( )|(　))","", data)
    data = re.sub("第[一|二|三|四|五|六|七|八|九|十|百]+条((\u3000)|( )|(　))","", data)
    data = re.sub("\u3000","",data)
    data = re.sub("\n","",data)
    return data, num

def replaceNandU(*args):#リスト内の改行をなくす
    list = []
    for arg in args:
        arg = arg.replace("\n", "")
        arg = arg.replace("\u3000", "")
        arg = arg.replace(",","，")
        list.append(arg)
    return list

def MakeList(T1, T2, Answer, MinRevCount, ProRevCount, SeqRevCount, ABProCount,ProbNumber = "" ,DelKakko_bool = False):  # 様々な組み合わせのテストケースを作成する
    dict = {}
    NumString = ""
    if DelKakko_bool:
        T1 = DelKakko(T1)
        T2 = DelKakko(T2)
    for MinRev in range(MinRevCount+1):  # 民法を否定形にするか、0ならそのまま、1なら否定形（自作)
        for ProRev in range(ProRevCount+1):  # 問題文を否定形にするか、0ならそのまま、1なら否定形（自作)
            for SeqRev in range(SeqRevCount+1):  # 民法と問題の順番を置き替えるべきか、0ならそのまま、1なら入れ替え
                for ABPro in range(ABProCount+1): # 民法と問題を一部アルファベットに置き替えるか、0ならそのまま、1なら入れ替え
                    Ronri = True  # 論理が反転するたびにこの値を反転させて正解を維持する
                    NumString = str(MinRev) + str(ProRev) + str(SeqRev) + str(ABPro)
                    if MinRev == 1:#民法を否定形にする
                        TextA = makeF(T1)
                        Ronri = not Ronri
                    else:#民法を否定形にしない(そのまま)
                        TextA = T1
                    if ProRev == 1:#問題を否定形にする
                        TextB = makeF(T2)
                        Ronri = not Ronri
                    else:#問題を否定形にしない（そのまま）
                        TextB = T2
                    if ABPro == 1:#問題を匿名にする(アルファベットにする)
                        ABPro1 = ""
                        ABPro2 = makeAlphabetical(TextB)#問題のみおきかえ
                        if not(ABPro1 == "") and not(ABPro2 == ""):
                            TextA = ABPro1
                            TextB = ABPro2
                        elif not(ABPro1 == "") and (ABPro2 == ""):
                            TextA = ABPro1
                        elif (ABPro1 == "") and not (ABPro2 == ""):
                            TextB = ABPro2
                        else:
                            TextA = ""
                            TextB = ""
                    else:#問題を匿名にしない（そのまま）
                        pass
                    if SeqRev == 1:#問題の順序を入れ替える
                        TextA, TextB = TextB, TextA
                    if Ronri:
                        AnswerNum = int(Answer)
                    else:
                        AnswerNum = int(not Answer)
                    if MakeHiteikeiOnly:#Trueの場合は場合によっては作成しない
                        if (ProRev == 1 or MinRev == 1) and AnswerNum == 1:#(民法か問題文が否定形かつ解答がTrue)でないとき
                            TextA = ""
                            TextB = "" 
                    if ProbNumber == "":
                        dict[NumString] = [AnswerNum, TextA, TextB]
                    else:
                        dict[NumString] = [AnswerNum, TextA, TextB,ProbNumber]    
    return dict

def MakeOutputList(TestCaseList, MinRevCount, ProRevCount, SeqRevCount, ABProCount):
    OutputList = []
    for x in TestCaseList:
        for MinRev in range(MinRevCount+1):  # 民法を否定形にするか、0ならそのまま、1なら否定形（自作)
            for ProRev in range(ProRevCount+1):  # 問題文を否定形にするか、0ならそのまま、1なら否定形（自作)
                for SeqRev in range(SeqRevCount+1):  # 民法と条文の順番を置き替えるべきか、0ならそのまま、1なら入れ替え
                    for ABPro in range(ABProCount+1): # 民法と問題を一部アルファベットに置き替えるか、0ならそのまま、1なら入れ替え
                        NumString = str(MinRev) + str(ProRev) + str(SeqRev) + str(ABPro)
                        if (not(x[NumString][1] == "") and not(x[NumString][2] == "")):#アルファベットに置き替えてない問題はnullになっている、重複しないための処理
                            OutputList.append(x[NumString])
    return OutputList

def ListSort(dir):#リストを記載したファイルを、文字列の長いものから順番になるようソートする
    List = []
    Listfile = open(dir, 'r')
    Listline = Listfile
    for line in Listline:
        line = line.replace("\n", "")
        List.append(line)
    List.sort(reverse=True, key=len)
    with open(dir,'w') as f:
        for Name in List:
            Name = Name + '\n'
            f.write(Name)

def Mcheck(ZyoNum,match,Minpoudict_withKou,SaveZyoNum):#前条、第xx条など検索したいフレーズを入れると"123"など条番号のStringで返す
    match = re.sub(LegalDataList.Tuika_Seiki,"",match)
    m1 = re.search(LegalDataList.ZyouSitei_Seiki, match)
    m2 = re.search(LegalDataList.KouSitei_Seiki, match)
    if m1:
        stringobje = re.sub('^第', '', match)
        stringobje = re.sub('条(の[一|二|三|四|五|六|七|八|九|十|百]+)?(第[一|二|三|四|五|六|七|八|九|十|百]+項)?', '', stringobje)
        
        if stringobje == ("前"):#前条の場合、条文番号-1をしたものを条文として扱う
            m_Zyo = re.search(".*-.*_.*",ZyoNum)
            if m_Zyo:
                ZenZyo = re.sub('_.*', '', m_Zyo.group())
                ZenZyo2 = re.sub('.*-', '', ZenZyo)
                if int(ZenZyo2)-1 == 1:
                    num = re.sub('-.*', '', m_Zyo.group())
                else:
                    num = re.sub('-.*', '', m_Zyo.group()) + "-" + str(int(ZenZyo2)-1)
            else:
                num = str(int(re.sub("_.*","",ZyoNum))-1)
        elif stringobje == ("次"):#前条の場合、条文番号-1をしたものを条文として扱う
            if "-" in ZyoNum:
                Part_Zyo = re.sub('-.*', '', ZyoNum)
                Part_Aida = re.sub('_.*', '', ZyoNum)
                Part_Aida = re.sub('.*-', '', Part_Aida)
            else:
                Part_Zyo = re.sub('_.*', '', ZyoNum)
                Part_Aida = ""
            Part_Kou = re.sub('.*_', '', ZyoNum)
            if not Part_Aida == "":
                num = Part_Zyo + "-" + str(int(Part_Aida)+1)
            else:
                num = Part_Zyo + "-2"
            if not ((num + "_1") in Minpoudict_withKou):
                num = str(int(Part_Zyo) + 1)
        elif stringobje == ("同"):#同条の場合、saveしてあるものを条文として扱う
            if not SaveZyoNum == "":
                num = re.sub("_.*","",SaveZyoNum)
            else:
                print("error937953",stringobje)
        else:
            num = str(Kanji_to_Suji(stringobje))#ここで何条か確認
        m3 = re.search('(前|同|第'+ stringobje+')条(の[一|二|三|四|五|六|七|八|九|十|百]+)', match)
        if m3:
            stringobje = re.sub('第.*条の', '', m3.group())
            num = num + '-' + str(Kanji_to_Suji(stringobje))#ここで「三十三条の二」のような「の二」部分を確認
        m4 = re.search('(前|同|第[一|二|三|四|五|六|七|八|九|十|百]+)条(の[一|二|三|四|五|六|七|八|九|十|百]+)?(第[一|二|三|四|五|六|七|八|九|十|百]+項)', match)
        if m4:
            stringobje = re.sub('(前|同|第[一|二|三|四|五|六|七|八|九|十|百]+)条(の[一|二|三|四|五|六|七|八|九|十|百]+)?第', '', m4.group())
            stringobje = re.sub('項', '', stringobje)
            num = num + '_' + str(Kanji_to_Suji(stringobje))#ここで「三十三条第三項」のような「第三項」部分を確認
    elif m2:#'((前([一|二|三|四|五|六|七|八|九|十|百]+)?|同|第[一|二|三|四|五|六|七|八|九|十|百]+)項)'
            m5 = re.search('前([一|二|三|四|五|六|七|八|九|十|百]+)?項', match)
            m6 = re.search('第[一|二|三|四|五|六|七|八|九|十|百]+項', match)
            m7 = re.search('同項',m2.group())
            if m5:
                stringobje = re.sub('前', '', match)
                stringobje = re.sub('項', '', stringobje)
                if not stringobje == "":
                    stringKou =  str(Kanji_to_Suji(stringobje))
                    intKou = int(re.sub(".*_","",ZyoNum))
                    num = re.sub("_.*","",ZyoNum)+"_" + str(intKou-int(stringKou))
                else:
                    intKou = int(re.sub(".*_","",ZyoNum))
                    num = re.sub("_.*","",ZyoNum)+"_"+str(intKou-1)
            elif m6:
                stringobje = re.sub('第', '', match)
                stringobje = re.sub('項', '', stringobje)
                stringKou =  str(Kanji_to_Suji(stringobje))
                num = re.sub("_.*","",ZyoNum) + "_" + stringKou
            elif m7:
                if not SaveZyoNum == "":
                    num = re.sub("_.*","",SaveZyoNum)
                else:
                    print("error93792453")
    else:
        print("error92853")
    if not "_" in num:
        num = num + "_1"
    return num

OkikaeList = []
def ZyoubunOkikaeStart(ZyoNum,data,Minpoudict_withKou) :
    saikicount = 0 #無限ループ対策の変数
    global OkikaeList 
    OkikaeList = []#既に呼び出された条文のリスト"
    return ZyoubunOkikae(ZyoNum,data,Minpoudict_withKou,saikicount)

def ZyoubunOkikae(ZyoNum,data,Minpoudict_withKou,saikicount):#文章内で指定された条文を置き替える(例,"第百上の...前項が..." → "[第百条]の...[前項]が...)
    global OkikaeList
    if data in OkikaeList:
        return ZyoNum#要検討
    else:
        OkikaeList.append(data)
    saikicount += 1#この関数が呼び出された回数をカウント
    this_saikicount = saikicount
    if this_saikicount>10: #一回の置き換えで10回以上呼び出されたら中止
        return "error242344"
    loopcount = 0#この関数ないで置き換え処理がループしすぎないかカウント
    SaveZyoNum=ZyoNum #直前に出た条番号を記録、「第一条...のとき、同条第二項のとき...」のようなときに使用
    while(True):#dataに出現する条番号を一つずつ置き替える、1ループにつき一つ置き替え
        numlist = []#条番号の集合、「から」などで複数指定されている場合のためにリスト
        Reigai = re.search('民事執行法|借地借家法|同法|仲裁法|債務者は、譲渡制限の意思表示がされた金銭の給付を目的とする債権が譲渡|前項の場合において、相殺をする債権者の有する債権がその負担する', data)#民事執行法第三条などは抽出できないのでpass
        if Reigai:
            #print(data)
            break
        match = re.search(LegalDataList.Zyou_Kou_Seiki + "((" + LegalDataList.Setuzoku_Seiki + LegalDataList.Zyou_Kou_Seiki+")+)?", data)
        String = ""
        if match:
            if re.search(LegalDataList.Setuzoku_Seiki,match.group()):#一度に指定する条番号が二つ以上の時
                data_Setuzoku = match.group()
                for Setuzokuline in LegalDataList.Setuzoku_Seiki_List:
                    data_Setuzoku = re.sub("(?<=" + Setuzokuline + ")","魑魅魍魎",data_Setuzoku)#一度、や。の後にキーワードを挿入し
                BunkatuList_Setuzoku = re.split("魑魅魍魎",data_Setuzoku)#挿入したキーワードを用いて分割を行う
                SaveA = False #前条第三項から第五項のような場合のため場合分け、要検討
                SaveB = False #「から」が前の文章に含まれていたかを保存
                num = "" #「から」の場合に前の条文をSave
                for multimatch in BunkatuList_Setuzoku: 
                    multimatch_After = re.sub(LegalDataList.Setuzoku_Seiki , "", multimatch)
                    if SaveA:
                        num1 = Mcheck(num,multimatch_After,Minpoudict_withKou,num)
                        pass
                    else:
                        num1 = Mcheck(ZyoNum,multimatch_After,Minpoudict_withKou,SaveZyoNum)
                        pass
                    if SaveB:
                        while(True):#ここで一つ目に指定された条文から二つ目に指定された条文までの間の条文をリスト化する
                            num = re.sub('_.*', '', num) + "_" + str(int(re.sub('.*_', '', num)) + 1)
                            Part_Zyo="0"
                            if num in Minpoudict_withKou:
                                pass
                            else:
                                if "-" in num:
                                    Part_Zyo = re.sub('-.*', '', num)
                                    Part_Aida = re.sub('_.*|.*-', '', num)
                                else:
                                    Part_Zyo = re.sub('_.*', '', num)
                                    Part_Aida = ""
                                Part_Kou = re.sub('.*_', '', ZyoNum)
                                if not Part_Aida == "":
                                    num = Part_Zyo + "-" + str(int(Part_Aida)+1) +"_1"
                                else:
                                    num = Part_Zyo + "-2_1" 
                                if num  in Minpoudict_withKou:
                                    pass
                                else:
                                    num = str(int(Part_Zyo) + 1) +"_1"
                                    if num  in Minpoudict_withKou:
                                        pass
                            if num == num1:
                                break
                            else:
                                numlist.append(num)
                            if int(re.sub('-.*', '', re.sub('-.*', '', num)))>int(re.sub('-.*', '', re.sub('-.*', '', num1))):
                                print("\nerror387583","\nZyoNum:",ZyoNum,"\ndata:",data,"\nnum:",num,"\nnum1,num2:",num1,num1)
                                break
                    if "条" in multimatch and "項" in multimatch:#前条第三項から第五項のような場合のため場合分け、要検討
                        SaveA = True
                    else:
                        SaveA = False
                    if re.search('から',multimatch):
                        SaveB = True
                    else:
                        SaveB = False
                    numlist.append(num1)
                    num = num1
            else:#条番号が一つのとき
                numlist.append(Mcheck(ZyoNum,match.group(),Minpoudict_withKou,SaveZyoNum))
            String = match.group()
            m_Tuika = re.search(LegalDataList.Tuika_Seiki, match.group())#前段、後段、各号、ただし書などの情報を抽出
        else:
            break
        Koudata = ""
        for numcount in range(len(numlist)):#複数条番号指定されている場合のためにループ処理
            if numlist[numcount] =="876-9_1":#登録されていない条番号
                Koudata = "「存在しない条」"
            else:
                for Kou in Minpoudict_withKou[numlist[numcount]]:#項が指定されない場合どうするか検討
                    if saikicount > 10:
                        print("error262825")
                        break
                    if m_Tuika and m_Tuika.group() == "ただし書":#「第九条ただし書」などの場合はただし書部分のみを参照
                        _,_,Kou = MakeInfo(Kou)
                    elif m_Tuika and m_Tuika.group() == "各号":#「第九条ただし書」などの場合はただし書部分のみを参照
                        Kou = ""
                        for count,Kakugou in enumerate(LegalDataList.Minpoudict_Kakugou[numlist[numcount]]):
                            Kou += Kakugou
                            if not count + 1 == len(LegalDataList.Minpoudict_Kakugou[numlist[numcount]]):
                                Kou += "」、「"
                    for Yousocount,Youso in enumerate(LegalDataList.OkikaeNextList):#ここで置き換えを行う
                        if match.group()+Youso in data or match.group() +"本文" + Youso in data:#現在条文の次のワードを検索
                            if "者" in Youso:#者に関するデータの場合は人物名のみを代入
                                _,Youso_PersonList,_ = MakeInfo(Kou)
                                Kou = ''
                                for count,x in enumerate(Youso_PersonList):
                                    Kou += x
                                    if not count + 1 == len(Youso_PersonList):
                                        Kou += "、"
                                else:#それ以外の場合は無視
                                    pass
                            break
                    Koudata += "「"  + ZyoubunOkikae(numlist[numcount],Kou,Minpoudict_withKou,saikicount) + "」"    
                    if m_Tuika and m_Tuika.group() == "各号":#「第九条ただし書」などの場合はただし書部分のみを参照
                        break#次に掲げるなどで文章が長くなりすぎる場合に備えて最初の一文のみ参照、要検討
        for Yousocount,Youso in enumerate(LegalDataList.OkikaeNextList):#ここで置き換えを行う
            if match.group()+Youso in data or match.group() +"本文" + Youso in data:#現在条文の次のワードを検索
                if "者" in Youso:#者に関するデータの場合は人物名のみを代入
                    data = re.sub( String+"(?:本文)?" + Youso,  Koudata , data,1)
                else:#それ以外の場合は無視
                    data = re.sub( String+"(?:本文)?",  Koudata  , data,1)
                break
            if Yousocount + 1 == len(LegalDataList.OkikaeNextList):
                if match.group() in data or match.group() +"本文" in data:    
                    data = re.sub(String+"(?:本文)?",  Koudata  , data,1)
                else:
                    print(ZyoNum,String,data,"error68786",match)
        loopcount+=1
        
        if loopcount>10:
            print("error9752975::"+ZyoNum)
            break
        if len(numlist)>0:
            SaveZyoNum = numlist[-1]#要検討
    return data

def PersonList_in_data(data):#dataから人物名のリストを抽出
    PersonData = []
    for PersonName in LegalDataList.PersonList:
        if PersonName in data:
            PersonData.append(PersonName)
    return PersonData

def BunsyoBunkatu(data):#文字列を"、"や"。"で分割してリストで返却する
    BunkatuList = []
    data = re.sub("(?<=、|,|。)","Keyword1234",data)#一度、や。の後にキーワードを挿入し
    BunkatuList = re.split("Keyword1234",data)#挿入したキーワードを用いて分割を行う
    if BunkatuList[-1] == "":
        del BunkatuList[-1]
    else:
        print("error295224",BunkatuList)
    return BunkatuList

def MakeInfo(data):#String文字列のdataから人物名、時、場所などの情報を抽出する
    BunkatuList = BunsyoBunkatu(data)
    PersonList = PersonList_in_data(data)
    Tadasigaki = ""
    if "ただし" in data:
        match = re.search("ただし.*",data)
        Tadasigaki = match.group()
        Tadasigaki = re.sub("ただし、","",Tadasigaki)
    return BunkatuList,PersonList,Tadasigaki

if __name__ == "__main__":
    print("method")
    aaa = "法律上の原因なく他人の財産又は労務によって利益を受け、そのために他人に損失を及ぼした者（以下この章において「受益者」という。）は、その利益の存する限度において、これを返還する義務を負う。"
    print(DelKakko(aaa))
