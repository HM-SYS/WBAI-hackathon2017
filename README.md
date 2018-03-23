##モデル概要
 今回私たちは、海馬の機能として「エピソード記憶」と「場所細胞」の二点に注目したモデルである。

### エピソード記憶

　エピソード記憶は「いつ・どこで・誰が・なにをした」などの情報から形成される。この情報は五感によって処理された結果であるとした。これよりエピソード記憶は、視覚・聴覚などの感覚情報の処理結果として与えられる特徴ベクトルだとした。また、この特徴ベクトルには感情などからなる価値が付随すると考えた。

### 場所細胞

　エピソード記憶において「どこ」にあたる場所の情報を持たせるために、”Slow Feature Analysis”(SFA)を用いた場所細胞モデルを実装した。[1]

参考　
+- [1](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3725472/)　　

## モジュール概要

+![image](https://user-images.githubusercontent.com/30830112/37825871-a5f31f32-2ed4-11e8-8af1-38c9607f9880.png)



## 学習方法
　SFAを用いて場所細胞モデルを実装させることより、自己位置を推定することができ、過去の経験から価値が高いエピソードを抽出する。抽出したエピソードに紐づく価値をにより行動確率を計算することで行動選択する。
つまり、ある場所(事象)に対して未来の価値の高い行動が選ばれやすくなる仕組みである。


## 環境設定

### Unity Version

Unity: 5.3.4f1

### Python Version
Python 2.7.11

### Other Version
- cd / home/ User name/ hackathon-2017-HM_SYS 
- sh fetch.sh
- cd agent
- pip install –r requirements.txt

### BriCA1 install
- cd/ home/ User name/ BriCA1-devel
- pip install .
- pip freeze

+![image](https://user-images.githubusercontent.com/30830112/37820302-85695f9e-2ec3-11e8-9661-4f8c9c363c8e.png)




