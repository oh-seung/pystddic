Standard Dictionary Management

```python
import pystddic
```

### 표준사전도구 정의


```python
stddic = pystddic.stddic()
```

### 단어사전 조회


```python
stddic.wordManager.wordQuery()
# 또는
stddic.wordManager.wordQuery(language='Korean')
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>논리명</th>
      <th>물리약어</th>
      <th>단어설명</th>
      <th>물리전체명칭</th>
      <th>엔터티분류어여부</th>
      <th>속성분류어여부</th>
      <th>단어유형코드</th>
      <th>동의어</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>현금</td>
      <td>CASH</td>
      <td>어음·증서·채권 따위에 대하여) 실지로 통용되는 화폐</td>
      <td>Cash</td>
      <td>False</td>
      <td>False</td>
      <td>표준단어</td>
      <td></td>
    </tr>
    <tr>
      <th>1</th>
      <td>현대커머셜</td>
      <td>HCMC</td>
      <td>현대커머셜주식회사(현대 상용 캐피탈)</td>
      <td>Hyundai Commercial</td>
      <td>False</td>
      <td>False</td>
      <td>표준단어</td>
      <td></td>
    </tr>
    <tr>
      <th>2</th>
      <td>형식</td>
      <td>FMT</td>
      <td>사물이 존재하고 있을 때 외부로 나타나 있는 모양</td>
      <td>Formality</td>
      <td>False</td>
      <td>False</td>
      <td>표준단어</td>
      <td></td>
    </tr>
    <tr>
      <th>3</th>
      <td>혜택</td>
      <td>BNFT</td>
      <td>자연이나 문명이나 단체 등이 사람에게 베푸는 이로움이나 이익</td>
      <td>Benefit</td>
      <td>False</td>
      <td>False</td>
      <td>표준단어</td>
      <td></td>
    </tr>
    <tr>
      <th>4</th>
      <td>확정</td>
      <td>DCSN</td>
      <td>일이 확실히 정해지는 것. 또는, 일을 확실히 정하는 것</td>
      <td>Decision</td>
      <td>False</td>
      <td>False</td>
      <td>표준단어</td>
      <td></td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>5092</th>
      <td>일사</td>
      <td>SLRN</td>
      <td>양의 복사 에너지가 땅에 닿았을 때의 세기</td>
      <td>Solar Insolation</td>
      <td>False</td>
      <td>False</td>
      <td>표준단어</td>
      <td></td>
    </tr>
    <tr>
      <th>5093</th>
      <td>인포테인먼트</td>
      <td>INFT</td>
      <td>인포메이션과 오락적인 요소를 말하는 엔터테인먼트 합성어\nEX) 차량용 인포테인먼트...</td>
      <td>Infoentertainment</td>
      <td>False</td>
      <td>False</td>
      <td>표준단어</td>
      <td></td>
    </tr>
    <tr>
      <th>5094</th>
      <td>세대주</td>
      <td>HOH</td>
      <td>한 가구를 이끄는 주가 되는 사람.</td>
      <td>Head Of Household</td>
      <td>False</td>
      <td>False</td>
      <td>표준단어</td>
      <td></td>
    </tr>
    <tr>
      <th>5095</th>
      <td>도움말</td>
      <td>HELP</td>
      <td>응용 프로그램의 기능 사용에 관한 설명이나 지시 사항을 디스크에 기억시켜 놓은 것</td>
      <td>Help</td>
      <td>False</td>
      <td>False</td>
      <td>표준단어</td>
      <td></td>
    </tr>
    <tr>
      <th>5096</th>
      <td>등록차량</td>
      <td>RGCAR</td>
      <td>값이 녜, 아녜여 확인</td>
      <td>Car Regist</td>
      <td>False</td>
      <td>False</td>
      <td>표준단어</td>
      <td></td>
    </tr>
  </tbody>
</table>
<p>5097 rows × 8 columns</p>
</div>



### DB와의 연동
#### 패키지내 구현대상이 아니며, 다른 환경에서는 아래와 같이 단어 Import 구현


```python
import pyodbc
import pandas as pd

ConnString = 'Driver={driver};SERVER={server};PORT={port};DB={dbname};UID={uid};PWD={pwd};'\
    .format(driver='{Tibero 6 ODBC Driver}', server='10.7.141.84', port='1521', dbname='DATAWARE', uid='dtwareadm', pwd='Encore##5868')
dbconn = pyodbc.connect(ConnString, timeout=5)

sql = """SELECT DIC_LOG_NM AS "LogicalWord"
     , DIC_PHY_NM AS "PhysicalWord"
     , DIC_DESC AS "LogicalDescription"
     , DIC_PHY_FLL_NM AS "PhysicalDescription"
     , ENT_CLSS_YN AS "EntityClassWord"
     , ATTR_CLSS_YN AS "AttributeClassWord"
     , '표준단어' AS "wordStandardType"
FROM 운표준단어기본 A
WHERE AVAL_END_DT = '99991231235959'
AND STANDARD_YN = 'Y' 
AND DIC_LOG_NM NOT IN ('율', '구름저항')
"""
df = pd.read_sql(sql, dbconn)

# 엔터티분류어, 속성분류어를 Boolean 값으로 변환함
df['EntityClassWord'] = df['EntityClassWord'].apply(lambda x: True if x == 'Y' else False)
df['AttributeClassWord'] = df['AttributeClassWord'].apply(lambda x: True if x == 'Y' else False)
```

### 단어사전 Insert
> 1) Multi Insert 시 df에 표시된 컬럼에 맞춰 데이터 입력 <br>
> 2) 단일건 Insert 시 아래 예제 참조


```python
# Multi Insert 
stddic.wordManager.multiWordInsert(df.to_dict('records'), progress=True) 
```


      0%|          | 0/5096 [00:00<?, ?it/s]



```python
# 단일건 Insert
stddic.wordManager.wordInsert(LogicalWord='등록차량', PhysicalWord='RGCAR', LogicalDescription='값이 녜, 아녜여 확인', PhysicalDescription='Car Regist', \
EntityClassWord=False, AttributeClassWord=False, wordStandardType='표준단어')
```

### 단어사전 저장, 불러오기


```python
# 저장할 경로 지정
stddic.dictionaryPath(r'dicsave\\')
```


```python
# 저장하기
stddic.dictionarySave('stddic_20220831.dump')
```

    Dictionary Dump file 저장 완료
    


```python
# 불러오기
stddic.dictionaryLoad('stddic_20220831.dump')
```

    Dictionary Dump file 호출 완료
    

### 형태소분석


```python
# 형태소분석할 대상 호출
sql = """SELECT 후보한글컬럼명
FROM 운컬럼기본
WHERE 자산화여부 = 'Y'
AND 후보한글컬럼명 IS NOT NULL """

termdf = pd.read_sql(sql, dbconn)
termList = termdf['후보한글컬럼명'].tolist()[0:1000]
```


```python
# 1건씩 형태소 분석
stddic.termParsing(termList[0])
```




    {'logicalParsingResult': '[최초][등록][시스템][유형][코드]',
     'physicalName': 'VBG_RGST_SYS_TYPE_CD',
     'termSplitResult': '최초;등록;시스템;유형;코드;',
     'attributeClassWord': '코드',
     'attributeClassUseResult': True,
     'nonstandardWords': '',
     'synonymousWords': '',
     'termRegistration': False}




```python
### 병렬처리 방법(Multi Processing)
# 1) 병렬처리 엔진 (1번만 켜놓으면 됨)
stddic.termParser.MultiProcessingInit()
```

    2022-08-31 10:08:25,148	INFO worker.py:963 -- Calling ray.init() again after it has already been called.
    


```python
# 2) 분석할 대상을 전달
# parallel [True, False]에 따라 병렬처리인지, 싱글처리인지 구분됨
result = stddic.multiTermParsing(termList, parallel=True)
```

    2022-08-31 10:08:53,844	INFO services.py:1456 -- View the Ray dashboard at [1m[32mhttp://127.0.0.1:8265[39m[22m
    


```python
# 2) 병렬처리 엔진 Shutdown
stddic.termParser.MultiProcessingShutdown()
```

## 반영(변경)해야할 기능
> 1) Multi Insert시 전체에 문제가 없을때 반영하기. 단어사전 백업하고 오류 발생하면 복원시키기 <br>
> 2) 형태소 분석시 Dictionary Sync 변수 만들어, 데이터 반영 횟수 줄이기 <br>
> 3) Multi 형태소 분석시, 중복되는 단어는 한번만 파싱할 수 있도록 변경 <br>
> 4) 형태소 분석의 결과에 리스트 형태 전달 또는 결과값(dictionary)에 추가하기


## 신규 구현할 기능
> 1) 비표준 단어 집계 <br>

## 별도 제공할 문서
> 1) API 구현 <br>
> 2) 준실시간 데이터 연동


```python

```
