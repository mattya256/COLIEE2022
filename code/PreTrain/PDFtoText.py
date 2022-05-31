#PDFからTextに変換する。
#前処理も行っている。

import os
from subprocess import call
from pdfminer.high_level import extract_text
import re

Search_dic = {1:"総合", 2:"最高裁判所" , 3:"高等裁判所" , 4:"下級裁判所" , 5:"行政事件" , 6:"労働事件" , 7:"知的財産"}
Search_int_list = [2,3,4,5,6,7] #上のやつに対応、2なら最高裁判所の結果のみを検索
NengouList = ["昭和","平成","令和"]


NotChangeOnly = False #これをTrueにすると、まだ変換していないファイルのみ変換。Falseの場合は全てのファイルを変換。

def TextChange(Str):#PDFが変換されたString型の文字列を適切な形に変形する。
    log = ""
    Str = re.sub("　| ","",Str)#大文字空白,小文字空白を削除
    Str = re.sub("-[ ]?[0-9]+[ ]?-","",Str)#ページ番号の削除
    Str = re.sub("(?:[⑴-⒇⒜-⒵]|\（[0-9|一二三四五六七八九]\）)","",Str)#括弧付き数字の削除
    Str = re.sub("【.*?】","",Str)#【要旨】などの変な括弧をまとめて削除
    Str = re.sub("[①-⑳❶-❿➊-➓㋐-㋾ⓐ-ⓩ]","",Str)#〇付き文字の削除
    Str = re.sub("|○","",Str)#変な文字の削除
    Str = re.sub("[0-9]+","",Str)#半角数字の削除、要検討!
    Str = re.sub(",|，","、",Str)#","と"，"を"、"に置き替える
    # Str = re.sub("。","。\n",Str)#後の分割の際に丸の前で区切れるように
    
    #括弧内の処理,現在は。を[MARU]に
    while(True):#二重括弧の場合などに備え、内側の括弧から順に処理している、一度括弧を別の文字列に置き替え、二度目のループでは二重括弧の外側の括弧を処理する
        Str = re.sub("。\n?\([^\(\)]*?\)","。\n",Str)#。の後の括弧を削除
        Str = re.sub("。\n?\（[^\（\）]*?\）","。\n",Str)
        Str = re.sub("。\n?\「[^\「\」]*?\」","。\n",Str)
        Str = re.sub("(?:\n)+","\n",Str)

        Kakko = re.findall("\([^\(\)]*?\)",Str)#括弧をグループとして抜き出し、括弧内の。を,に置き替える
        Kakko.extend(re.findall("\（[^\（\）]*?\）",Str))
        Kakko.extend(re.findall("\「[^\「\」]*?\」",Str))

        if Kakko == []:
            break
        for Kakkoline in Kakko:
            Kakkoline_after = re.sub("。","{MARU}",Kakkoline)#ここで実際の置き換え
            Kakkoline_after = re.sub("\(",   "{Kakko001}",Kakkoline_after)
            Kakkoline_after = re.sub("\)",   "{Kakko002}",Kakkoline_after)
            Kakkoline_after = re.sub("（",  "{Kakko003}",Kakkoline_after)
            Kakkoline_after = re.sub("）",  "{Kakko004}",Kakkoline_after)
            Kakkoline_after = re.sub("「",  "{Kakko005}",Kakkoline_after)
            Kakkoline_after = re.sub("」",  "{Kakko006}",Kakkoline_after)
            log += "括弧:" + Kakkoline_after + "\n\n"
            Str = Str.replace(Kakkoline , Kakkoline_after)
            # Str = re.sub(Kakkoline,Kakkoline_after,Str)#何故か重かったのでreplaceで代用
    Str = re.sub("{Kakko001}",  "(",   Str)
    Str = re.sub("{Kakko002}",  ")",    Str)
    Str = re.sub("{Kakko003}",  "（",   Str)
    Str = re.sub("{Kakko004}",  "）",   Str)
    Str = re.sub("{Kakko005}",  "「",   Str)
    Str = re.sub("{Kakko006}",  "」",   Str)

    Str = re.sub("(?:\n)+","\n",Str)#空白の行の削除

    beforeStr = ""#変な文字列の前後の文章を削除するために一度保存してからsave
    nextStr = False#同様に、変な文字列の後の文章を削除するためのフラグ
    
    Strlist = Str.split("\n")
    returnStr = ""
    save = ""
    for Strline in Strlist:
        if "。" in Strline:
            while True:
                if len(save + re.sub("。.*","。",Strline)) >= 10:#追加した一文が10文字以上
                    if nextStr == True:
                        nextStr = False
                    else:
                        returnStr += beforeStr
                        beforeStr = save + re.sub("。.*","。",Strline) + "\n"
                else:
                    log += "error2984:" + save + re.sub("。.*","。",Strline)+ "\n"
                    log += "before:" + beforeStr+ "\n"
                    beforeStr = ""
                    nextStr = True
                save = ""
                Strline = re.sub("^.*?。","",Strline)
                if Strline == "":
                    break
                elif "。" in Strline:
                    pass
                else:
                    save += Strline
                    break
        elif len(Strline) >= 10:
            save += Strline
        elif Strline == "主文":#主文前の文章は破棄、要検討
            returnStr = ""
            save = ""
        elif Strline == "理由" or Strline == "事実及び理由":#理由前の文章は破棄、要検討
            returnStr = ""
            save = ""
            pass
        elif Strline == "":
            pass
        else:
            save = ""
            log += "error4649:" + Strline + "\n"#一行内に。がなく、かつ10文字以下の文章
    returnStr += beforeStr


    returnStr = re.sub("(\n)[ア-ンａ-ｚa-z]([^ア-ンａ-ｚa-z])","\\1\\2",returnStr)#文頭の一文字だけのカタカナ、アルファベットの削除
    returnStr = re.sub("(\n)[０-９]+([^０-９項条月日人])","\\1\\2",returnStr)#文頭の一文字だけの数字の削除
    returnStr = re.sub("\n[^\(\)]*?\).*?。\n","\n",returnStr)#(の前に)が来るなど明らかに変な文章の削除
    returnStr = re.sub("\n[^\（\）]*?\）.*?。\n","\n",returnStr)
    returnStr = re.sub("\n[^\「\」]*?\」.*?。\n","\n",returnStr)
    returnStr = re.sub("(?:\n)+","\n",returnStr)
    returnStr = re.sub("(?:^|\n)(?:、|の).*?(\n)","\n",returnStr)
    returnStr = re.sub("(?:^|\n)(?: |　)*(?:[ア-ン]|\(|\)|\（|\）|[0-9]|[０-９]|[一二三四五六七八九])+(?: |　)+","",returnStr)#行頭の不要な単語削除
    returnStr = re.sub("(?:\n)+","\n",returnStr)#空白の行の削除

    returnStr = re.sub("{MARU}","。",returnStr)#最後に[MARU]を”。”に置き替える。
    return returnStr,log

# PDFからTextに変換する
def PDFtoText():
    # for Nengou in ["昭和","平成","令和"]: 
    for Search_int in Search_int_list:
        inputdir_base =  "data_PreTraining/output/" + str(Search_dic[Search_int])  + "判例_PDF/"
        outputdir_base = "data_PreTraining/output/" + str(Search_dic[Search_int])  + "判例_Text/"
        for Nengou in NengouList:#変更予定
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
                for PageNumber in range(1,1000):#ページ番号

                    inputdir = inputdir_base + str(Nengou) + "/" + str(Year) + "/" + str(PageNumber)#Fujitaのフォルダ使用可
                    outputdir = outputdir_base + str(Nengou) + "/" + str(Year) + "/" + str(PageNumber)
                    if not os.path.exists(inputdir):
                        break
                    
                    filename_list = os.listdir (inputdir)
                    if filename_list != []:
                        os.makedirs(outputdir ,exist_ok = True)
                        for filename in filename_list:
                            if NotChangeOnly and os.path.exists(outputdir + "/" + re.sub(".pdf","",filename) + ".txt"):#変換されていないファイルのみ変換する
                                pass
                            else:#全て変換する
                                textfile = open(outputdir + "/" + re.sub(".pdf","",filename) + ".txt", 'w')#加工後のファイル
                                textfile_before = open(outputdir + "/" + re.sub(".pdf","",filename) + "_before.txt", 'w')#加工前のファイル
                                textfile_log = open(outputdir + "/" + re.sub(".pdf","",filename) + "_log.txt", 'w')#過去の際のlogのファイル
                                filename_input = inputdir + "/" + filename
                                text = extract_text(filename_input)
                                changedtext,log = TextChange(text)
                                textfile_before.write(text)
                                textfile_before.close()
                                textfile_log.write(log)
                                textfile_log.close()
                                textfile.write(changedtext)
                                textfile.close()
                                # exit()
                    memofile = open("output/PreTraining/memo/PDF_to_Text.txt", 'a')
                    memofile.write("裁判所名: " + str(Search_dic[Search_int])  + ", ページ番号:" + str(PageNumber) + ", 年号:" + Nengou + ", 年:" + str(Year) + "\n")
                    memofile.close()
                    print("裁判所名: " + str(Search_dic[Search_int])  + ", ページ番号:" + str(PageNumber) + ", 年号:" + Nengou + ", 年:" + str(Year) + "\n")

if __name__ == "__main__":
    PDFtoText()

