#裁判例をサイトからpdfでダウンロードする(以下のサイト)
#https://www.courts.go.jp/app/hanrei_jp/search1
#スクレイピングを行うため、情報の使用、サイトへの負荷へ注意する。
# sleepをなくすとサイトへの負荷が大きくなり違法になりかねないので注意。

from bs4 import BeautifulSoup
import urllib.request as req
import urllib
import os
import time
import re
from urllib.parse import urljoin
from urllib.parse import urlparse
import urllib.request

from TextCollect import Search_int_list

Search_dic = {1:"総合", 2:"最高裁判所" , 3:"高等裁判所" , 4:"下級裁判所" , 5:"行政事件" , 6:"労働事件" , 7:"知的財産"}
Search_int_list = [2] #上のやつに対応、2なら最高裁判所の結果のみを検索
NengouList = ["平成"]

def DownloadPDF(URL,Search_int,Nengou,Year,PageNumber):#判例のpdf保存
    download = True#Falseの時はpdfのダウンロードをしない、動作確認用

    target_dir = "data_PreTraining/output/" + str(Search_dic[Search_int]) + "判例_PDF/" + str(Nengou) + "/" + str(Year) + "/" + str(PageNumber)#保存先の指定
    
    p = urlparse(URL)#URLの日本語でエラーが出るので回避するための処理
    query = urllib.parse.quote_plus(p.query, safe='=&')
    URL = '{}://{}{}{}{}{}{}{}{}'.format(
        p.scheme, p.netloc, p.path,
        ';' if p.params else '', p.params,
        '?' if p.query else '', query,
        '#' if p.fragment else '', p.fragment)

    res = req.urlopen(URL)
    soup = BeautifulSoup(res, "html.parser")
    result = soup.select("a[href]")

    pdflist = [] 
    for x in result:#pdfの名前を検索
        x = str(x)
        if "pdf" in x:
            pdfname = re.search("\".*?pdf\"",x)
            if not pdfname == None:
                pdflist.append(pdfname.group()[1:-1])

    if pdflist == []:
        return False

    abs_dbpdf_list = []#相対パスを絶対パスに変換
    for relative in pdflist:
        temp_url = urljoin(URL, relative)
        abs_dbpdf_list.append(temp_url)
    
    # print(abs_dbpdf_list)

    filename_list = []#ファイル名を取得
    for target in abs_dbpdf_list:
        temp_list = target.split("/")
        filename_list.append(temp_list[len(temp_list)-1])

    savepath_list = []
    for filename in filename_list:
        savepath_list.append(os.path.join(target_dir, filename))

    if download:
        os.makedirs(target_dir ,exist_ok = True)
        for (pdflink, savepath) in zip(abs_dbpdf_list, savepath_list):#保存(2秒間隔にしているのはサイトに負荷をかけないように)
            urllib.request.urlretrieve(pdflink, savepath)
            time.sleep(5)#サイトへの負荷考慮のため重要,2秒までは減らしてもいいかも
            
    print("保存完了")
    return True

def main():
    # for Nengou in ["昭和","平成","令和"]:]
    for Search_int in Search_int_list:
        for Nengou in NengouList:#変更予定
            MinYear = 0
            MaxYear = 0
            if Nengou == "昭和":
                MinYear = 22
                MaxYear = 64
            elif Nengou == "平成":
                MinYear = 1   
                MaxYear = 30   
            elif Nengou == "令和":
                MinYear = 1
                MaxYear = 4
            for Year in range(MinYear,MaxYear+1):
                PageNumber_Minrange = 1
                PagaNumber_Maxreange = 1000
                if Nengou == "平成":
                    if Year == 21:
                        PageNumber_Minrange = 36
                        pass
                for PageNumber in range(PageNumber_Minrange,PagaNumber_Maxreange):#ページ番号
                    time.sleep(2)
                    URL = "hogehoge"#念のため隠しております。

                    print("裁判所名:" + str(Search_dic[Search_int]) + ", ページ番号:" + str(PageNumber) + ", 年号:" + Nengou + ", 年:" + str(Year) +"\n")
                    print("URL:" + URL +"\n")
                    if DownloadPDF(URL,Search_int,Nengou,Year,PageNumber) == False:
                        print("保存失敗")
                        break
                f = open("output/PreTraining/memo/DownloadPDF_" + str(Search_dic[Search_int]) + "_進行状況.txt", 'a')
                f.write("裁判所名:" + str(Search_dic[Search_int]) + ", ページ番号:" + str(PageNumber) + ", 年号:" + Nengou + ", 年:" + str(Year) + "\n")
                f.close()

if __name__ == "__main__":
    main()