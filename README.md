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



```python
# 2) 병렬처리 엔진 Shutdown
stddic.termParser.MultiProcessingShutdown()
```
