#事前学習を行う。

#以下のサイトを参考に実装しました。
#huggingface / transformersを使って日本語BERTの事前学習を実施してオリジナルな言語モデルを作ってみる
#https://qiita.com/m__k/items/6f71ab3eca64d98ec4fc

from sentencepiece import SentencePieceTrainer
from transformers import AlbertTokenizer, PreTrainedModel
from transformers import BertConfig
from transformers import BertForMaskedLM
from transformers import LineByLineTextDataset
from transformers import DataCollatorForLanguageModeling
from transformers import TrainingArguments
from transformers import Trainer
from transformers import T5Tokenizer,RobertaForMaskedLM,BertJapaneseTokenizer,AlbertTokenizer
from transformers import DummyObject, requires_backends
import os

PreTraining_bool    = True      #事前学習を行うか

Usecltohoku_tonizer = False    #これをTrueにするとcl_tohokuのtokenizerを使用する,Falseの時は自作のもの
if Usecltohoku_tonizer:
    MakeTokenizer_bool  = False #Tokenizerの学習をするか
else:
    MakeTokenizer_bool  = True

ver = "20220311_onlyHanrei_original"

input_dir = "data_PreTraining/input/BigData/BigData_" + ver + ".txt"
drive_dir = "data_PreTraining/modelList/model_" + ver + "/"

os.makedirs(drive_dir , exist_ok=True)

def MekeTokenizer():#tokenizerを学習する
    print("Maketokenizer")
    SentencePieceTrainer.Train(
        '--input=' + input_dir + ', --model_prefix=' + drive_dir + 'Hanrei_sentencepiece '\
        '--character_coverage=0.9995 '\
        '--vocab_size=32000 '\
        '--pad_id=3 '\
        '--add_dummy_prefix=False'
    )

def load_tokenizer():
    if Usecltohoku_tonizer:
        tokenizer = BertJapaneseTokenizer.from_pretrained('cl-tohoku/bert-base-japanese-whole-word-masking', mecab_kwargs={"mecab_dic": "ipadic", "mecab_option": None})
    else:
        tokenizer = AlbertTokenizer.from_pretrained(drive_dir + 'Hanrei_sentencepiece.model', keep_accents=True)
    tokenizer.save_pretrained(drive_dir)
    return tokenizer

#BERTモデルの設定、事前学習まで行う
def BERT_setting():
    print("bert_setting")
    tokenizer = load_tokenizer()
    print("bert_config")
    config = BertConfig(#vocab_size=32003
        vocab_size=32010,\
        num_hidden_layers=12, \
        intermediate_size=768, \
        num_attention_heads=12
    )
    print("bert_model")
    model = BertForMaskedLM(config)
    print("bert_dataset")
    dataset = LineByLineTextDataset(
        tokenizer=tokenizer,
        file_path=input_dir,
        block_size=512, # tokenizerのmax_length
    )
    print("bert_datacollar")
    data_collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer,
        mlm=True,
        mlm_probability= 0.15
    )
    print("bert_trainarg")
    training_args = TrainingArguments(
        output_dir= drive_dir ,
        overwrite_output_dir=True,
        num_train_epochs=10,
        per_device_train_batch_size=32,
        save_steps=10000,
        save_total_limit=2,
        prediction_loss_only=True
    )
    print("bert_trainer")
    trainer = Trainer(
        model=model,
        args=training_args,
        data_collator=data_collator,
        train_dataset=dataset
    )
    print("bert_train")
    trainer.train()
    trainer.save_model(drive_dir)

def BERT_Test():
    from transformers import pipeline

    tokenizer = load_tokenizer()
    model = BertForMaskedLM.from_pretrained(drive_dir)

    fill_mask = pipeline(
        "fill-mask",
        model=model,
        tokenizer=tokenizer
    )

    MASK_TOKEN = tokenizer.mask_token
    #原判決は，要旨次のとおり説示した。
    text = '''
    原判決は，要旨次のとおり{}した。
    '''.format(MASK_TOKEN)
    print(fill_mask(text))

if __name__ == "__main__":
    #tokenizerを学習する
    if MakeTokenizer_bool:
        MekeTokenizer()

    #Tokenizerのテスト
    tokenizer = load_tokenizer()
    text = "被告人が荷物の中身をどのように認識していたにしても，ＡにＢ宅を荷物の送付先として紹介した者として，荷物の回収の依頼を受けるのは不自然であるとはいえないし，その依頼を受けたら，回収に向けた行動を取るのも当たり前であって，Ａから催促の電話を受けて，複数回にわたり，電話がないＢ宅に配達の有無を確認するのも不自然な行動ではない。"
    print(tokenizer.tokenize(text))

    #BERTの設定、事前学習まで行う
    if PreTraining_bool:
        BERT_setting()

    # #事前学習で作成されたモデルのテスト
    BERT_Test()