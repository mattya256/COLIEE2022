#様々なリストを管理するクラス

import pickle
import re

Test_Setting_CountList = ["UseBert","UseAttention","TrainYear","T1list_train","T1list_test","MinRev","ProRev","SeqRev","MakeAlpha","Okikae","DelKakko","Kumiawase","UseMyBert","UseEntailmentDatset"]

KanSujiList=['零','一','二','三','四','五','六','七','八','九','十','十一','十二','十三','十四','十五','十六','十七','十八','十九','二十','二十一','二十二','二十三','二十四','二十五']#漢数字のリスト

Kanji_Suji_pair={'零':0, '一':1, '二':2, '三':3, '四':4, '五':5, '六':6, '七':7, '八':8, '九':9 }#漢数字と数字のペアリスト

#LargeNumList = ['１','２','３','４','５','６','７','８','９']#大文字の数字のリスト
LargeNumDict = {1:'１',2:'２',3:'３',4:'４',5:'５',6:'６',7:'７',8:'８',9:'９'}#大文字の数字の辞書

LARGEAB = ["Ａ","Ｂ","Ｃ","Ｄ","Ｅ","Ｆ","Ｇ","Ｈ","Ｉ","Ｊ","Ｋ","Ｌ","Ｍ","Ｎ","Ｏ","Ｐ","Ｑ","Ｒ","Ｓ","Ｔ","Ｕ","Ｖ","Ｗ","Ｘ","Ｙ","Ｚ"]#問題文中の人物名を確認する際に使用

#"次に掲げる"の後に出てくる単語のリスト(例として次に掲げる原因)、第何条に規定するxxの時も使用
#Nextlist = ['場合', '事由', '事項', 'とき', '時', 'もの' ,'ところ', '行為', '区分', '者', '方式', '錯誤', '事実', '原因', '債務', '要件', '順序', '書面','催告','責任','権利','死亡','期間','規定','追認','合意','書面','公正証書','申し込み','広告','意思表示','不適合','委任','組合員','組合','目録','権限','公示','義務','期日','仲裁合意','意思表示','和解']
NextList = []
NextListfile = open('data/input/NextList.txt', 'r')
NextListline = NextListfile.readlines()
for line in NextListline:
    NextList.append(re.sub("\n","",line))

OkikaeNextListTest=["の規定","の審判","と同様","の期間内"]
OkikaeNextList=["の規定","の審判","と同様","の期間内"]
for x in NextList:
    OkikaeNextList.append("の"+x)
    OkikaeNextList.append("の定める"+x)
    OkikaeNextList.append("に掲げる"+x)
    OkikaeNextList.append("に定める"+x)
    OkikaeNextList.append("において"+x)
    OkikaeNextList.append("に規定する"+x)
OkikaeNextList.sort(reverse=True, key=len)

ZyouSitei_Seiki = '(?:(?:前|次|同|第[一|二|三|四|五|六|七|八|九|十|百]+)条(?:の[一|二|三|四|五|六|七|八|九|十|百]+)?(?:第[一|二|三|四|五|六|七|八|九|十|百]+項)?)'
KouSitei_Seiki = '(?:(?:前(?:[一|二|三|四|五|六|七|八|九|十|百]+)?|同|第[一|二|三|四|五|六|七|八|九|十|百]+)項)'
Tuika_Seiki = '(?:前段|後段|各号|ただし書|まで|第.号)'
Zyou_Kou_Seiki = '(?:' + ZyouSitei_Seiki + '|' + KouSitei_Seiki + ')' + Tuika_Seiki + '?'#第一条、前項、第三条の二第一項など様々な条番号指定をとれる正規表現
Setuzoku_Seiki_List = ["から","及び","又は","並びに","、"]
Setuzoku_Seiki = '(?:'
for count,x in enumerate(Setuzoku_Seiki_List):
    Setuzoku_Seiki += x
    if count + 1 != len(Setuzoku_Seiki_List):
        Setuzoku_Seiki += '|'
Setuzoku_Seiki += ')'

NotList = []#肯定系と否定形のセットのリスト(例、{働く、働かない})
NotListfile = open('data/input/NotList.txt', 'r')
NotListline = NotListfile.readlines()
for line in NotListline:
    NotList.append(line.replace('\n', '').split('、'))

PersonList = []#人物名のリスト(売主、買主)
PersonListfile = open('data/input/PersonList.txt', 'r')
PersonListline = PersonListfile
for line in PersonListline:
    line = line.replace("\n", "")
    PersonList.append(line)

Minpoudict = {}#民法の辞書、条文番号と条文（リスト）で構成
Minpoudictfile = 'data/output/List/COLIEE_Minpoudict.csv'

with open(Minpoudictfile, 'rb') as fp:
    Minpoudict = pickle.load(fp)

Minpoudict_Kakugou = {}#民法の"各号"に関する情報のみを記載
Minpoudict_Kakugoufile = 'data/output/List/COLIEE_Minpoudict_Kakugou.csv'

with open(Minpoudict_Kakugoufile, 'rb') as fp:
    Minpoudict_Kakugou = pickle.load(fp)

Minpoudict_withKou = {}#民法の辞書、条文番号と条文（リスト）で構成
Minpoudict_withKoufile = 'data/output/List/COLIEE_Minpoudict_withKou.csv'

with open(Minpoudict_withKoufile, 'rb') as fp:
    Minpoudict_withKou = pickle.load(fp)

Minpoudict_withKou_Okikae_Make = {}#民法の辞書、条文番号と条文（リスト）で構成,自作
Minpoudict_withKou_Okikae_Make_file = open("data/input/Fin_COLIEE_Minpoudict_Read_withKou_Okikae_MakeByFujita.csv", 'r' ,  encoding='utf-8')
Minpoudict_withKou_Okikae_Makline = Minpoudict_withKou_Okikae_Make_file.readlines()
for line in Minpoudict_withKou_Okikae_Makline:
    line = re.sub("\[|\]|\\n|\"|\'","",line)
    for count,x in enumerate(line.split(",")):
        if count == 0:
            key = x
        elif count == 1:
            list = [x]
        else:
            list.append(x)
    Minpoudict_withKou_Okikae_Make[key] = list
