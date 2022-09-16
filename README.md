```python
import pystddic
```

### 표준사전도구 클래스 정의


```python
stddic = pystddic.stddic()
```

### 표준단어 검증 규칙과 CASE 적용 규칙
표준단어 입력 및 수정시 아래 규칙을 적용시킬지 여부를 확인한다.  
 - 검증규칙
     - 논리명중복제한: True
     - 논리명미존재: True
     - 물리명미존재: True
     - 물리전체명칭미존재: True
     - 물리약어중복제한: True
     - 물리약어길이제한: True
     - 물리약어최대길이수: 10
     - 특수문자사용제한: True
     - 사용제한특수문자: (,),%,@,!,~,$,^,&,*,<,>,;,/,?,-,_,=,+,.\,",[,]
 - 자동변환 CASE 규칙
     - 물리약어대문자변환: True
     - 물리전체명칭첫글자대문자변환: True
 
### 표준단어 검증 규칙 변경
'wordManager.wordVefiryRuleChange' 를 통해 검증규칙의 사용여부를 변경할 수 있다


```python
###표준단어 검증 규칙 확인
stddic.wordManager.wordVefiryList
```




    {'논리명중복제한': True,
     '논리명미존재': True,
     '물리명미존재': True,
     '물리전체명칭미존재': True,
     '물리약어중복제한': True,
     '물리약어길이제한': True,
     '특수문자사용제한': True,
     '물리약어대문자변환': True,
     '물리전체명칭첫글자대문자변환': True,
     '물리약어최대길이수': 10,
     '사용제한특수문자': '(,),%,@,!,~,$,^,&,*,<,>,;,/,?,-,_,=,+,.\',",[,]'}




```python
stddic.wordManager.wordVefiryRuleChange(물리전체명칭첫글자대문자변환 = False, 물리약어길이제한=False)
stddic.wordManager.wordVefiryRuleChange(물리약어최대길이수 = 100)
```

    물리전체명칭첫글자대문자변환 : False 으로 변경
    물리약어길이제한 : False 으로 변경
    물리약어최대길이수 : 100 으로 변경
    


```python
stddic.wordManager.wordVefiryList
```




    {'논리명중복제한': True,
     '논리명미존재': True,
     '물리명미존재': True,
     '물리전체명칭미존재': True,
     '물리약어중복제한': True,
     '물리약어길이제한': False,
     '특수문자사용제한': True,
     '물리약어대문자변환': True,
     '물리전체명칭첫글자대문자변환': False,
     '물리약어최대길이수': 100,
     '사용제한특수문자': '(,),%,@,!,~,$,^,&,*,<,>,;,/,?,-,_,=,+,.\',",[,]'}



### 단어사전 조회
단어사전은 'language' 파라메터값에 따라 언어를 지정할 수 있다  
※ 값 출력시에만 사용되며, 다른 메소드 호출시 이용할 수 없다 


```python
stddic.wordManager.wordQuery()
# 또는
#stddic.wordManager.wordQuery(language='Korean')
```




<div>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>LogicalWord</th>
      <th>PhysicalWord</th>
      <th>LogicalDescription</th>
      <th>PhysicalDescription</th>
      <th>EntityClassWord</th>
      <th>AttributeClassWord</th>
      <th>wordStandardType</th>
      <th>synonymousWord</th>
    </tr>
  </thead>
  <tbody>
  </tbody>
</table>
</div>



### DB와의 연동
패키지내 구현대상이 아니며, 다른 환경에서는 아래와 같이 단어 Import 구현한다.


```python
import pyodbc
import pandas as pd

ConnString = 'Driver={driver};SERVER={server};PORT={port};DB={dbname};UID={uid};PWD={pwd};'\
    .format(driver='{Tibero 6 ODBC Driver}', server='127.0.0.1', port='1521', dbname='pystddic', uid='pystddic', pwd='pystddic')
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
"""
df = pd.read_sql(sql, dbconn)

# 엔터티분류어, 속성분류어를 Boolean 값으로 변환함
df['EntityClassWord'] = df['EntityClassWord'].apply(lambda x: True if x == 'Y' else False)
df['AttributeClassWord'] = df['AttributeClassWord'].apply(lambda x: True if x == 'Y' else False)
```

### 단어 입력
- single Insert 시 아래 예제 참조
    - 아래 파라메터의 데이터 형식을 맞게 입력해햐 한다.
    - 검증규칙에 맞지 않거나, 데이터 형식이 다른 경우 오류가 발생한다.
- multi Insert 시 df에 표시된 컬럼에 맞춰 데이터 입력
    - 값 입력시 리스트(list)내 딕셔너리(dict) 형태로 입력해야 한다.
    - 딕셔너리에 key는 단일건 입력시 사용된 파라메터의 명칭과 동일해야 한다.
    - 검증규칙에 맞지 않거나, 데이터 형식이 다른 경우, 오류 발생건이 다량일 수 있어 오류대상건을 return 한다.
    
입력된 값의 확인은 wordManager.wordQuery() 를 통해 확인할 수 있다.


```python
# single Insert
stddic.wordManager.wordInsert(LogicalWord='등록차량', PhysicalWord='RGCAR', LogicalDescription='값이 녜, 아녜여 확인', \
                              PhysicalDescription='Car Regist', EntityClassWord=False, AttributeClassWord=False, \
                              wordStandardType='표준단어')
```


```python
# multi Insert 
stddic.wordManager.multiWordInsert(df.to_dict('records'), progress=True, replace=True) #, 
```
    [[AssertionError('An error occurred in the word registration. \n LogicalWord:비율, ErrorMessage:물리약어중복발생'),
      {'LogicalWord': '비율',
       'PhysicalWord': 'RT',
       'LogicalDescription': '둘 이상의 수를 비교하여 나타낼 때,그중 한 개의 수를 기준으로 하여 나타낸 다른 수의 비교 값',
       'PhysicalDescription': 'Ratio',
       'EntityClassWord': False,
       'AttributeClassWord': True,
       'wordStandardType': '표준단어'}],
     [AssertionError('An error occurred in the word registration. \n LogicalWord:구름저항, ErrorMessage:물리약어중복발생'),
      {'LogicalWord': '구름저항',
       'PhysicalWord': 'RR',
       'LogicalDescription': '구르는 타이어는 항상 도로면으로부터 저항을 받게 되는데, 트럭에 짐을 적재한 상태에서 타이어는 눌려서 형상이 찌그러진다.\n부드러운 표면을 가진 비포장 도로 상에서 타이어는 표면에 내려앉아 타이어 앞에 작은 경사를 이루는데, 이들이 구름 저항을 구성한다.\n트럭의 중량이 크면 클수록, 도로 재질이 부드러우면 부드러울수록 구름 저항(Rr)은 비례적으로 더 커진다.',
       'PhysicalDescription': 'Rolling Resistance',
       'EntityClassWord': False,
       'AttributeClassWord': False,
       'wordStandardType': '표준단어'}]]




```python
stddic.wordManager.wordQuery().head(5)
```




<div>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>LogicalWord</th>
      <th>PhysicalWord</th>
      <th>LogicalDescription</th>
      <th>PhysicalDescription</th>
      <th>EntityClassWord</th>
      <th>AttributeClassWord</th>
      <th>wordStandardType</th>
      <th>synonymousWord</th>
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
  </tbody>
</table>
</div>



### 단어 수정
- 단어 수정 조건은 LogicalWord 같은 단어에 대해서 수정한다.
- dictionary 형태로 사용해야 하며, LogicalWord이외의 값이 수정된다(※ 다른 값은 유지)
- 검증규칙은 Insert와 동일하게 유지된다.


```python
wordSet = {'LogicalWord':'현금', 'PhysicalWord':'HOHO'}
stddic.wordManager.wordUpdate(wordSet)
```

    word change complete.
    {'LogicalWord': '현금', 'PhysicalWord': 'HOHO', 'LogicalDescription': '어음·증서·채권 따위에 대하여) 실지로 통용되는 화폐', 'PhysicalDescription': 'Cash', 'EntityClassWord': False, 'AttributeClassWord': False, 'wordStandardType': '표준단어', 'synonymousWord': ''}
    

### 단어 삭제
- 값은 dictionary 형태로 전달해야 하며, 조건이 여러개인 경우 모두 만족하는(논리연산자:and) 데이터가 삭제된다.
- 'or' 조건이 필요한 경우, 반복하여 호출하면 가능하다.


```python
#deleteCondition = {'AttributeClassWord':True}
deleteCondition = {'LogicalWord':'확정'}
stddic.wordManager.wordDelete(deleteCondition)
```

    deleted word: 확정
    

### 단어사전 저장, 불러오기
- 단어사전에 대해 저장 및 불러오기가 가능하다


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
    

## 형태소분석


```python
# 형태소분석할 대상 호출
sql = """SELECT 후보한글컬럼명
FROM 운컬럼기본
WHERE 자산화여부 = 'Y'
AND 후보한글컬럼명 IS NOT NULL """

termdf = pd.read_sql(sql, dbconn)
termList = termdf['후보한글컬럼명'].tolist()[0:1000]
```

### 용어에 대한 형태소 분석 (메소드 termParsing)
- 결과값 설명
    - logicalParsingResult : 요청된 단어를 단어사전 기반으로 분할한다. 표준은 대괄호([]), 비표준은 (%%), 동의어는 중괄호({})로 감싸진다.
    - physicalName: 분할된 단어를 기반으로 물리약어를 조합하여 생성된 명칭이다.
    - termSplitResult: 표준, 비표준 구분없이 단어를 분할한 정보
    - attributeClassWord: 사용된 속성분류어가 표시된다.
    - attributeClassUseResult: 속성분류어가 사용되었는지를 표시한다.
    - nonstandardWords: 비표준 단어가 기재된다.
    - synonymousWords: 동의어 단어가 기재된다.
    - termOriginalName: 분석을 요청한 원본 단어를 기재한다.
    - termRegisterValidationCheck: 분석을 요청한 용어에 문제가 없는지 표시한다(문제가 없을 경우:True, 문제가 있을 경우:False)
    - termRegistration: 현재 관리하고 있는 용어에 등록되어 있는지 표시한다.(※ 현재 미지원)


```python
stddic.termParsing('대리점고객유형대리점수1')
```




    {'logicalParsingResult': '[대리점][고객][유형][대리점][수]',
     'physicalName': 'AGEN_CSMR_TYPE_AGEN_CNT',
     'termSplitResult': '대리점;고객;유형;대리점;수;',
     'attributeClassWord': '수',
     'attributeClassUseResult': True,
     'nonstandardWords': '',
     'synonymousWords': '',
     'termOriginalName': '대리점고객유형대리점수1',
     'termRegisterValidationCheck': True,
     'termRegistration': False}



### 용어에 대한 병렬처리
- 대량의 용어에 대해 형태소 분석이 필요할 경우, 병렬처리 패키지인 'ray'를 활용한다.
- 해당 컴퓨터의 Physical Cpu 개수만큼 병렬로 처리되니 주의해야 한다.
- 병렬처리가 필요 없을 경우, 매개변수 parallel을 False로 하면 된다.


```python
### 병렬처리 방법(Multi Processing)
# 1) 병렬처리 엔진 (1번만 켜놓으면 됨)
stddic.termParser.MultiProcessingInit()
```

    2022-09-16 16:26:34,499	INFO services.py:1456 -- View the Ray dashboard at [1m[32mhttp://127.0.0.1:8265[39m[22m
    


```python
import time
stime = time.time()

result = stddic.multiTermParsing(termList, parallel=True)
print(time.time()- stime)
```

    3.5339479446411133
    


```python
stime = time.time()

result = stddic.multiTermParsing(termList, parallel=False)
print(time.time()- stime)
```

    8.815149068832397
    


```python
# 2) 병렬처리 엔진 Shutdown
stddic.termParser.MultiProcessingShutdown()
```
