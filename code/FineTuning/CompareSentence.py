#文章の類似度検索

#以下のサイトを参考に実装しました
#【日本語モデル付き】2020年に自然言語処理をする人にお勧めしたい文ベクトルモデル
#https://qiita.com/sonoisa/items/1df94d0a98cd4f209051#%E6%96%87%E3%83%99%E3%82%AF%E3%83%88%E3%83%AB%E3%81%AE%E8%A8%88%E7%AE%97

from transformers import BertJapaneseTokenizer, BertModel
import torch
import scipy.spatial
import os,pickle

class SentenceBertJapanese:
    print("CompareSentence.pyにてload中、GPU:",os.environ["CUDA_VISIBLE_DEVICES"])
    def __init__(self, model_name_or_path, device=None):
        self.tokenizer = BertJapaneseTokenizer.from_pretrained(model_name_or_path)
        self.model = BertModel.from_pretrained(model_name_or_path)
        self.model.eval()

        if device is None:
            device = "cuda" 
        self.device = torch.device(device)
        self.model.to(device)

    def _mean_pooling(self, model_output, attention_mask):
        token_embeddings = model_output[0] #First element of model_output contains all token embeddings
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)

    @torch.no_grad()
    def encode(self, sentences, batch_size=8):
        all_embeddings = []
        iterator = range(0, len(sentences), batch_size)
        for batch_idx in iterator:
            batch = sentences[batch_idx:batch_idx + batch_size]

            encoded_input = self.tokenizer.batch_encode_plus(batch, padding="longest", 
                                           truncation=True, return_tensors="pt").to(self.device)
            model_output = self.model(**encoded_input)
            sentence_embeddings = self._mean_pooling(model_output, encoded_input["attention_mask"]).to('cpu')

            all_embeddings.extend(sentence_embeddings)

        # return torch.stack(all_embeddings).numpy()
        return torch.stack(all_embeddings)

#初期ロード
model = SentenceBertJapanese("sonoisa/sentence-bert-base-ja-mean-tokens")

def CompareSentence(sentences,query,SCDictver):
    ProbDict = {}#問題の辞書、一度比較した問題を再度比較しないように(Keyは問題のString,Valueは結果のリスト)
    ProbDictfile = 'data/output/List/CompareSentence/' + SCDictver
    os.makedirs(ProbDictfile, exist_ok=True)
    ProbDictfile = 'data/output/List/CompareSentence/' + SCDictver +"CS.txt"

    if not os.path.exists(ProbDictfile):
        with open(ProbDictfile, "w+") as f:
            pass

    if os.path.getsize(ProbDictfile) > 0:   
        with open(ProbDictfile, 'rb') as fp:
            ProbDict = pickle.load(fp)
    if query in ProbDict :
        return ProbDict[query]
    else:
        query = [query]
        sentence_vectors = model.encode(sentences)

        query_embeddings = model.encode(query).numpy()

        log = ""
        for Q, query_embedding in zip(query, query_embeddings):
            distances = scipy.spatial.distance.cdist([query_embedding], sentence_vectors, metric="cosine")[0]

            results = zip(range(len(distances)), distances)
            results = sorted(results, key=lambda x: x[1])

            log += ("\n======================\n")
            log += ("Query:" + Q)
            count = 0
            count2 = 0#同じものを出力しないように
            before = ""
            for idx, distance in results:
                if before != sentences[idx].strip():
                    if count2 < 3 or count + 3 >= len(results):
                        log += "\n" + str(count) + ":" + (sentences[idx].strip() +  "(Score:" + str((distance / 2)) + ")" )
                    before = (sentences[idx].strip())
                    count2 += 1
                    count += 1
                else:
                    count += 1
        f = open("output/PreTraining/memo/comapre.txt","a")
        f.write(log)
        f.close()

        ProbDict[query[0]] = (results)
        with open(ProbDictfile, 'wb') as fp:
            pickle.dump(ProbDict, fp)
        return results

if __name__ == "__main__":
    CompareSentence( ['前条の場合のほか、組合員は、死亡によって脱退する。','前条の場合のほか、組合員は、除名によって脱退する。', '脱退した組合員の持分は、その出資の種類を問わず、金銭で払い戻すことができる。',  '前条の場合のほか、組合員は、死亡によって脱退する。前条の場合のほか、組合員は、除名によって脱退する。','前条の場合のほか、組合員は、除名によって脱退する。脱退の時にまだ完了していない事項については、その完了後に計算をすることができる。', '前条の場合のほか、組合員は、除名によって脱退する。脱退した組合員の持分は、その出資の種類を問わず、金銭で払い戻すことができる。',  '前条の場合のほか、組合員は、死亡によって脱退する。前条の場合のほか、組合員は、除名によって脱退する。脱退した組合員の持分は、その出資の種類を問わず、金銭で払い戻すことができる。']  , "組合員は，除名された場合であっても，持分の払戻しを受けることができる。","test")