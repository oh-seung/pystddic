### 패키지 import


```python
import pystddic
```

### 표준사전도구 정의


```python
stddic = pystddic.stddic()
```

### 표준단어 Import
> 다량 적재(multiWordInsert), 단일건 적재(wordInsert)가 제공됩니다. <br>
> 다량 적재의 경우, 단어별로 dictionary형태이어야 하며, 단일건의 적재되는 메소드의 매개변수와 같은 명칭이어야 합니다. <br>


```python
import pandas as pd
df = pd.read_csv('단어목록.csv')

df = df[['LogicalWord', 'PhysicalWord', 'LogicalDescription','PhysicalDescription', 'EntityClassWord', 'AttributeClassWord', 'wordStandardType']]
df.head(5)
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
      <th>LogicalWord</th>
      <th>PhysicalWord</th>
      <th>LogicalDescription</th>
      <th>PhysicalDescription</th>
      <th>EntityClassWord</th>
      <th>AttributeClassWord</th>
      <th>wordStandardType</th>
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
    </tr>
  </tbody>
</table>
</div>




```python
### 다량의 단어 적재(multiWordInsert)
stddic.wordManager.multiWordInsert(df.to_dict('records'), progress=True) 
```


      0%|          | 0/5094 [00:00<?, ?it/s]



```python
### 단일건 적재(wordInsert)
stddic.wordManager.wordInsert(LogicalWord='등록차량', PhysicalWord='RGCAR', LogicalDescription='차량이 등록되었다는 복합 단어', \
                              PhysicalDescription='Car Regist', EntityClassWord=False, AttributeClassWord=False, \
                              wordStandardType='표준단어')
```

### 적재된 단어 사전 조회
> language 매개변수에 표시된 언어(English, Korean)에 따라 컬럼명을 표시합니다.


```python
stddic.wordManager.wordQuery().head(5)
# 또는
stddic.wordManager.wordQuery(language='Korean').head(5)
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
  </tbody>
</table>
</div>



### 단어사전 저장, 불러오기


```python
# 저장할 경로 지정
stddic.dictionaryPath(r'dicsave\\')
```


```python
# 저장하기
stddic.dictionarySave('stddic_20220831.dump')
```


```python
# 불러오기
stddic.dictionaryLoad('stddic_20220831.dump')
```

### 형태소분석


```python
import pyodbc
import pandas as pd

ConnString = 'Driver={driver};SERVER={server};PORT={port};DB={dbname};UID={uid};PWD={pwd};'\
    .format(driver='{Tibero 6 ODBC Driver}', server='10.7.141.84', port='1521', dbname='DATAWARE', uid='dtwareadm', pwd='Encore##5868')
dbconn = pyodbc.connect(ConnString, timeout=5)
```


```python
# 형태소분석할 대상 호출
termList = ['최초등록시스템유형코드', '최초등록자아이디', '최초등록일시', '최종수정시스템유형코드', '최종수정자아이디', '최종수정일시', '고객관리번호', '가입신청번호', '법인가입자번호', '고객유형코드', '회원신청유형코드', '계약번호', '레드멤버스보유차종코드', 'ALP카드유형코드', '모집채널코드', '모집인지점코드', '모집인명', '모집인사원번호', '접수일시', '최초등록일시', '최초등록자아이디', '최종수정일시', '최종수정자아이디', '가입신청번호', '상호명', '사업자등록번호', '법인등록번호', '고객유형코드', '대표자명', '직장우편번호', '직장주소', '직장상세주소', '직장건물관리번호', '직장전화지역통신사번호', '직장전화앞자리번호', '직장전화뒷자리번호', '담당자전화지역통신사번호', '담당자전화앞자리번호', '담당자전화뒷자리번호', '담당자휴대폰전화지역통신사번호', '담당자휴대폰전화앞자리번호', '담당자휴대폰전화뒷자리번호', '담당자이메일주소', '담당자직장명', '담당자부서명', '담당자직위명', '담당자명', '회원신청유형코드', '계약번호', '해약여부', '차대번호', '레드멤버스보유차종코드', '보유차종년월', '차량번호', '카드수령유형코드', 'DM수신여부', 'SMS수신여부', '마일리지SMS수신여부', '이메일수신여부', 'DM수신유형코드', '개인정보수집활용동의여부', '서류징구여부', '고객사인여부', 'ALP안내문수령채널코드', '카드신청유형코드', 'ALP카드유형코드', '현대카드번호', '모집채널코드', '모집인지점코드', '모집인명', '모집인사원번호', '접수일시', '현대카드신청서번호', '최초등록일시', '최초등록자아이디', '최종수정일시', '최종수정자아이디', '카드수령우편번호', '카드수령지주소', '카드수령지상세주소', '카드수령지건물관리번호', '회원고유번호', '직장참고주소', '카드수령지참고주소', '텔레마케팅수신동의여부', '광고성정보수신동의여부', '사업자등록번호', '상호명', '법인등록번호', '고객가입경로코드', '회원가입일시', '회원고유번호', '고객관리번호', '고객유형코드', '법인상태코드', '법인업체유형코드', '영리고객유형코드', '업체코드', '업종명', '대표자명', '업태명', '종목명', '법인사업자명', '직장우편번호', '직장주소', '직장상세주소', '직장주소수정일시', '직장주소수정시스템코드', '직장주소수정사원번호', '직장건물관리번호', '직장전화지역통신사번호', '직장전화앞자리번호', '직장전화뒷자리번호', '직장전화번호수정일시', '직장전화번호수정시스템코드', '직장전화번호수정사원번호', '기타전화지역통신사번호', '기타전화앞자리번호', '기타전화뒷자리번호', '담당자명', '담당자부서명', '담당자직위명', '담당자전화지역통신사번호', '담당자전화앞자리번호', '담당자전화뒷자리번호', '담당자휴대폰전화지역통신사번호', '담당자휴대폰전화앞자리번호', '담당자휴대폰전화뒷자리번호', '담당자이메일주소', '카드수령유형코드', 'DM수신여부', 'SMS수신여부', '마일리지SMS수신여부', '이메일수신여부', 'DM수신유형코드', '개인정보수집활용동의여부', '등록시스템유형코드', '최초등록자아이디', '최초등록일시', '수정시스템유형코드', '최종수정자아이디', '최종수정일시', '카드수령우편번호', '카드수령지주소', '카드수령지상세주소', '카드수령지건물관리번호', '고객식별번호', '직장참고주소', '카드수령지참고주소', '제휴사연계고객CI번호', '텔레마케팅수신동의여부', '광고성정보수신동의여부', '사업자등록번호', '수신유형코드', '수신여부', '최종수정시스템유형코드', '최종수정자아이디', '최종수정일시', '사업자등록번호', '회원고유번호', '수정이전대표자명', '수정이후대표자명', '최종수정시스템유형코드', '최종수정자아이디', '최종수정일시', '사업자등록번호', '수정이전법인번호', '수정이후법인번호', '최종수정시스템유형코드', '최종수정자아이디', '최종수정일시', '사업자등록번호', '수정이전상호명', '수정이후상호명', '최종수정시스템유형코드', '최종수정자아이디', '최종수정일시', '사업자등록번호', '법인전화번호유형코드', '법인전화지역통신사번호', '법인전화앞자리번호', '법인전화뒷자리번호', '최종수정시스템유형코드', '최종수정자아이디', '최종수정일시', '카드수령지유형코드', '최종수정시스템유형코드', '최종수정일시', '최종수정자아이디', '회원고유번호', '최신회원가입신청서번호', '카드요청유형코드', '회원고유번호', '고객관리번호', '카드수령자명', '직위명', '부서명', '배송방법코드', '발급요청카드수', '연락처유형코드', '연락처전화지역통신사번호', '연락처전화앞자리번호', '연락처전화뒷자리번호', '카드수령지유형코드', '카드수령지우편번호', '카드수령지주소', '카드수령지상세주소', '카드수령지참고주소', '카드수령지건물관리번호', '발급요청채널코드', '모집인지점코드', '모집인사원번호', '최초등록일시', '최초등록자아이디', '최종수정일시', '최종수정자아이디', 'ALP카드유형코드', '송수신문순번', '등록순번', '송수신문유형코드', '카드브랜드코드', '기준일시', '마일리지회원번호', '회원명', '카드수령유형코드', '자택주소우편번호', '자택주소', '자택상세주소', '직장우편번호', '직장주소', '직장상세주소', '최초등록일시', '최초등록자아이디', '최종수정일시', '최종수정자아이디', '회원고유번호', '자택참고주소', '직장참고주소', '자택건물관리번호', '직장건물관리번호', '요청번호', '마일리지회원번호암호화', '발송아이디', '회원고유번호', '고객관리번호', '회원명', '기본우편번호', '기본주소', '기본상세주소', '기본참고주소', '요청유형코드', '요청주소유형코드', '요청우편번호', '요청주소', '요청상세주소', '요청참고주소', '배송방법코드', '요청사유내용', '요청일시', '요청사원번호', '처리상태코드', '처리사유내용', '접수일시', '접수사원번호', '최초등록일시', '최초등록자아이디', '최종수정일시', '최종수정자아이디', '기본주소유형코드', '기본배송유형코드', '송수신문순번', '등록순번', '송수신문유형코드', '카드브랜드코드', '기준일시', '마일리지회원번호암호화', '반송일시', '반송사유코드', '사유내용', '최초등록일시', '최초등록자아이디', '최종수정일시', '최종수정자아이디', '회원고유번호', '배송방법유형코드', '송수신문순번', '등록순번', '송수신문유형코드', '카드브랜드코드', '기준일시', '마일리지회원번호암호화', '반송일시', '반송사유코드', '사유내용', '최초등록일시', '최초등록자아이디', '최종수정일시', '최종수정자아이디', '회원고유번호', '사업자등록번호', '주소유형코드', '우편번호', '과거도로명주소', '상세주소', '최종수정시스템유형코드', '최종수정자아이디', '최종수정일시', '건물관리번호', '참고주소', '사업자등록번호', '수정사업자등록번호', '고객관리번호', '수정고객관리번호', '작업설명내용', '최종수정자아이디', '최종수정일시', '상세내용', '사업자등록번호', '수정이전담당자명', '수정이후담당자명', '최종수정시스템유형코드', '최종수정자아이디', '최종수정일시', '회원고유번호', '담당자전화지역통신사번호', '담당자전화앞자리번호', '담당자전화뒷자리번호', '담당자이메일주소', '담당자휴대폰전화지역통신사번호', '담당자휴대폰전화앞자리번호', '담당자휴대폰전화뒷자리번호', '담당자부서명', '담당자직위명', '담당자명', '작업년월일', '탈퇴처리유형코드', '회원고유번호', '상태코드', '작업테이블번호', '작업테이블명', '작업수', '스팅어멤버십회원명', '수신자주소', '생년월일년월일', '성별코드', '전담정비업체코드', '사용여부', '최초등록자아이디', '최초등록일시', '최종수정자아이디', '최종수정일시', '휴대폰전화번호', '수정일시', '신청년월일', '신청순번', '마일리지서비스아이디', '마일리지가맹점아이디', '신청유형코드', '법인통장여부', '신청내용', '진행상태코드', '신청자명', '관리자코멘트내용', '최초등록자아이디', '최초등록일시', '최종수정자아이디', '최종수정일시', '마일리지거래관리번호', '마일리지아이디', '마일리지약어명', '사인관리번호', '가맹점아이디', '가맹점주문번호', '영업소코드', '마일리지승인금액', '마일리지승인금액사인내용', '마일리지승인상태코드', '수집일시', '수집상태코드', '미사용식별값', '회원명', '영업소담당자명', '제휴사승인번호', '제휴사승인일시', '최초등록자아이디', '최초등록일시', '최종수정자아이디', '최종수정일시', '고객생년월일번호', '제휴사연계본인확인값', '마일리지아이디', '가맹점상태코드', '가맹점상태수정일시', '가맹점상태수정사유코드', '가맹점오픈일시', '마일리지명', '가맹점폐쇄일시', '마일리지약어명', '마일리지가맹점아이디', '외부마일리지여부', '세금계산서사업자등록번호', '정산대상사업자등록번호', '마일리지수수료조건아이디', '최초등록자아이디', '최초등록일시', '최종수정자아이디', '최종수정일시', '승인거래정산유형코드', '입출금유형코드', '납부자번호', '청구서발송유형코드', '연속연체수', '누적연체수', '서비스유지여부', '불량가맹점여부', '부가가치세포함여부', '가맹점수기지급여부', '불량가맹점등록일시', '불량가맹점등록사유내용', '협력업체동의번호', '가입신청번호', '상용차량여부', '협력업체코드', '제3자정보제공동의여부', '필수여부', '최초등록자아이디', '최초등록일시', '최종수정자아이디', '최종수정일시', '회원고유번호', '제휴사연계본인확인값', '최초등록일시', '최초등록자아이디', '탈퇴채널코드', '탈퇴일시', '탈퇴처리사원번호', '고객관리번호', '회원가입일시', '사업자등록번호', '이메일유형코드', '이메일주소', '최종수정시스템유형코드', '최종수정자아이디', '최종수정일시', '사업자등록번호', '상호명', '법인등록번호', '고객가입경로코드', '회원가입일시', '회원고유번호', '고객유형코드', '법인상태코드', '배송방법유형코드', '송수신문순번', '등록순번', '송수신문유형코드', '카드브랜드코드', '마일리지회원번호암호화', 'ALP카드발송결과코드', 'ALP카드수령일시', 'ALP카드수취인관계코드', '반송사유코드', 'ALP카드배송업체명', '수취인명', '회원고유번호', '마일리지회원번호암호화', '사인관리번호', '카드발행일시', '카드발행명세수집시작일시', '카드발행명세수집마감일시', '카드발행명세수집마감예정일시', '정산상태코드', '정산유형코드', '카드발행집계일시', '카드발행가맹점아이디', '카드발행유형코드', '청구지급번호', '최초등록자아이디', '최초등록일시', '최종수정자아이디', '최종수정일시', '카드발행가맹점아이디', '가맹점상태코드', '가맹점상태수정일시', '가맹점상태수정사유코드', '가맹점오픈일시', '가맹점폐쇄일시', '세금계산서사업자등록번호', '정산대상사업자등록번호', '마일리지수수료조건아이디', '최초등록자아이디', '최초등록일시', '최종수정자아이디', '최종수정일시', '승인거래정산유형코드', '입출금유형코드', '납부자번호', '청구서발송유형코드', '연속연체수', '누적연체수', '서비스유지여부', '불량가맹점여부', '부가가치세포함여부', '가맹점수기지급여부', '불량가맹점등록일시', '불량가맹점등록사유내용', '카드발행신청번호', '가입신청번호', '카드번호', '가계구성원관계코드', '발행사유코드', '발행진행상태코드', '카드반송유형코드', 'ALP카드신청일시', 'ALP카드유형코드', '현대카드번호', '카드발행일시', '회원고유번호', '카드별마일리지변동번호', '마일리지회원번호암호화', '마일리지거래관리번호', '회원고유번호', '가맹점주문번호', '마일리지정보수정일시', '거래유형코드', '변동마일리지금액', '변동이후현재마일리지금액', '변동이후가용마일리지금액', '금액사인내용', '마일리지수집처리여부', '원거래번호', '마일리지본사분담금액', '제휴사분담금액', '취소여부', '마일리지가맹점아이디', '최초등록자아이디', '최초등록일시', '최종수정자아이디', '최종수정일시', '가용화년월일', '가용화여부', '분실접수번호', '카드번호', '분실일시', '분실사유코드', '분실접수일시', '분실접수채널코드', '연락처전화번호', '최초등록일시', '최초등록자아이디', '회원고유번호', '마일리지회원번호암호화', '배송메모내용', '최초등록자아이디', '최초등록일시', '최종수정자아이디', '최종수정일시', '차대번호', '분실접수번호', '카드번호', '재발행사유코드', '재발행신청일시', '채널유형코드', '카드수령우편번호', '카드수령지주소', '카드수령지상세주소', 'ALP카드유형코드', '현대카드번호', '카드발행일시', '최초등록일시', '최초등록자아이디', '건물관리번호', '카드수령유형코드', '배송유형코드', '회원고유번호', '카드수령지참고주소', '고객유형코드', '요청자명', '요청일시', '수령자명', '연락처전화지역통신사번호', '연락처전화앞자리번호', '연락처전화뒷자리번호', '커리큘럼번호', '참고주소', '건물관리번호', '입력시스템유형코드', '입력사원번호', '입력일시', '채널유형코드', '최종수정사원번호', '최종수정일시', '담당사원번호', '조직유형코드', '조직코드', '카마스터명', '호칭명', '직군코드', '직무코드', '직위코드', '직급코드', '사원여부', '퇴직여부', '퇴직년월일', '퇴직사유내용', '인사부서코드', '입력시스템유형코드', '입력사원번호', '입력일시', '채널유형코드', '최종수정사원번호', '최종수정일시', '고객생년월일번호암호화', '조직유형코드', '조직코드', '전화번호', '팩스전화번호', '도로명주소우편번호', '도로명주소', '도로명상세주소', '참고주소', '건물관리번호', '입력시스템유형코드', '입력사원번호', '입력일시', '채널유형코드', '최종수정사원번호', '최종수정일시', '조직유형코드', '조직코드', '상용업체유형코드', '상위단계조직코드', '조직구분명', '부서장사원번호', '지점판촉그룹코드', '지점평가그룹코드', '인사부서코드', '야간정비가능여부', '종료여부', '차량점검대행가능코드', '해지년월일', '출장정비서비스가능코드', '입력시스템유형코드', '입력사원번호', '입력일시', '채널유형코드', '최종수정사원번호', '최종수정일시', '이벤트번호', '이벤트명', '이벤트유형코드', '발행계획타임스탬프', '시작타임스탬프', '종료타임스탬프', '경품지급방법코드', '미사용속성값7', '이벤트대표이미지값', '위치정보내용', '이벤트URL주소', '이벤트내용L', '승인자아이디', '이벤트적용아이디', '이벤트상태코드', '이벤트활성화상태코드', '이벤트템플릿번호', '최초등록자아이디', '최초등록타임스탬프', '최종수정자아이디', '최종수정타임스탬프', '취소타임스탬프', '실제발행타임스탬프', '이벤트코드', '승인거부사유내용', '승인타임스탬프', '재확인타임스탬프', '접두사명', '배경칼라값', '차종코드', '등록자부서명', '등록사원번호', '등록자명', '반응형태여부', '이벤트코드명', 'CRM이벤트번호', '일자이내순서', '신규상태년월일', '실제발행취소타임스탬프', '임직원제한여부', '이벤트참가휴대폰파일명', '이벤트참가휴대폰전화번호수', '최소연령', '방문자수', '등록자수', '룰렛허용여부', '룰렛폰트명', '룰렛폰트크기', '룰렛폰트칼라값', '룰렛당첨율', '브랜드번호', '룰렛메시지내용', '당첨메시지내용', '낙첨메시지내용', '이벤트템플릿번호', '템플릿명', '템플릿설명내용', '템플릿유형코드', '템플릿내용L', '상태코드', '최초등록자아이디', '최초등록타임스탬프', '최종수정자아이디', '최종수정타임스탬프', '복사템플릿번호', '배경칼라값', '브랜드번호', '이벤트템플릿브랜드번호', '이벤트템플릿번호', '브랜드번호', '최초등록자아이디', '최초등록타임스탬프', '최종수정자아이디', '최종수정타임스탬프', '이벤트배정번호', '이벤트번호', '사용자아이디', '데이터상태코드', '최초등록자아이디', '최초등록타임스탬프', '최종수정자아이디', '최종수정타임스탬프', '이벤트컨텐츠번호', '이벤트번호', '이벤트템플릿번호', '이벤트내용L', '최초등록자아이디', '최초등록타임스탬프', '최종수정자아이디', '최종수정타임스탬프', '페이지번호', '반응형태여부', '페이지라벨명', '이벤트데이터번호', '필드명', '필드내용L', '필드CRM코드', '이벤트번호', '최초등록자아이디', '최초등록타임스탬프', '최종수정자아이디', '최종수정타임스탬프', '이벤트참고번호', '고정컬럼여부', '필수여부', '이벤트삭제번호', '이벤트명', '이벤트유형코드', '발행계획타임스탬프', '시작타임스탬프', '경품지급방법코드', '미사용속성값7', '이벤트대표이미지값', '위치정보내용', '이벤트URL주소', '이벤트내용L', '승인자아이디', '이벤트적용아이디', '이벤트상태코드', '이벤트활성화상태코드', '이벤트템플릿번호', '최초등록자아이디', '최초등록타임스탬프', '최종수정자아이디', '최종수정타임스탬프', '발행취소타임스탬프', '실제발행타임스탬프', '이벤트코드', '승인거부사유내용', '승인타임스탬프', '재확인타임스탬프', '접두사명', '배경칼라값', '차종코드', '등록자부서명', '등록사원번호', '등록자명', '반응형태여부', '이벤트코드명', 'CRM이벤트번호', '일자이내순서', '신규상태년월일', '실제발행취소타임스탬프', '임직원제한여부', '이벤트참가휴대폰파일명', '이벤트참가휴대폰전화번호수', '최소연령', '룰렛허용여부', '룰렛폰트명', '룰렛폰트크기', '룰렛폰트칼라값', '룰렛당첨율', '브랜드번호', '방문자수', '등록자수', '이벤트번호', '룰렛메시지내용', '당첨메시지내용', '낙첨메시지내용', '이벤트매체번호', '이벤트번호', '매체번호', '이벤트매체상태코드', '최초등록자아이디', '최초등록타임스탬프', '최종수정자아이디', '최종수정타임스탬프', '이벤트컨텐츠번호', '이벤트설문번호', '이벤트번호', '질문번호', '발송상태코드', '최초등록자아이디', '최초등록타임스탬프', '최종수정자아이디', '최종수정타임스탬프', '파일번호', '참고유형명', '파일명', '이벤트참고번호', '삭제유형코드', '호출URL주소', '경품번호', '이벤트번호', '매체번호', '상품페이지URL주소', '경품순위', '경품명', '경품수량', '경품설명내용', '경품상태코드', '최초등록자아이디', '최초등록타임스탬프', '최종수정자아이디', '최종수정타임스탬프', '룰렛순번', '룰렛칼라값', '이벤트당첨여부', '경품번호', '이벤트번호', '경품명', '룰렛칼라값', '룰렛순번', '최초등록자아이디', '최초등록타임스탬프', '최종수정자아이디', '최종수정타임스탬프', '경품상태코드', '매체번호', '파일업로드유형코드', '카테고리코드', '비공개업로드여부', '파일명', '파일URL주소', '대체사진경로주소', '매체설명내용', '파일확장자명', '업로드파일크기', '서버경로주소', '매체상태코드', '최초등록자아이디', '최초등록타임스탬프', '최종수정자아이디', '최종수정타임스탬프', '썸네일URL주소', '메뉴번호', '메뉴명', '메뉴URL주소', '메뉴설명내용', '정렬순서', '사이트유형코드', '메뉴아이디', '최초등록자아이디', '최초등록타임스탬프', '최종수정자아이디', '최종수정타임스탬프', '시작타임스탬프', '종료타임스탬프', '메시지발송번호', '메시지템플릿번호', '최초등록자아이디', '최초등록타임스탬프', '최종수정자아이디', '최종수정타임스탬프', '방문자이벤트번호', '메시지번호', '발송자번호', '발송휴대폰전화번호', '메시지컨텐츠내용', '공지사항첨부파일번호', '공지사항번호',\
            '매체번호', '데이터상태코드', '최초등록자아이디', '최초등록타임스탬프', '최종수정자아이디', '최종수정타임스탬프', '권한번호', '역할번호', '메뉴번호', '권한코드', '최초등록자아이디', '최초등록타임스탬프', '최종수정자아이디', '최종수정타임스탬프', '역할번호', '역할명', '역할설명내용', '데이터상태코드', '최초등록자아이디', '최초등록타임스탬프', '최종수정자아이디', '최종수정타임스탬프', '하위약관번호', '약관번호', '약관코드', '약관버전명', '컨텐츠내용L', '데이터상태코드', '최초등록자아이디', '최초등록타임스탬프', '최종수정자아이디', '최종수정타임스탬프', '약관제목명', '동의문구내용', '통합CRM연동상태코드', '필수동의여부', '약관순번', '설문답변번호', '설문질문번호', '답변내용', '최초등록타임스탬프', '답변고객내용', '설문순번', '기타입력내용', '응답자아이디', '설문질문번호', '질문내용', '질문유형명', '최초등록타임스탬프', '방문자이벤트번호', '설문순번', '질문번호', '종료타임스탬프', '주소코드', '주소명', '주소단계코드', '시스템유형코드', 'EAI전송년월일', 'EAI순번', '담당사원번호', '직장전화번호', '담당자휴대폰전화번호', '자택전화번호', '우선이메일유형코드', '이메일주소1', '이메일주소2', '이메일주소3', '주소기재유형코드', '도로명주소우편번호', '도로명주소', '도로명상세주소', '참고주소', '건물관리번호', '입력시스템유형코드', '입력사원번호', '입력일시', '채널유형코드', '최종수정사원번호', '최종수정일시', 'EAI처리일시', 'EAI결과유형코드', 'EAI메시지내용', '시스템적용일시', '시스템적용여부', '미적용메시지내용', '시스템유형코드', 'EAI전송년월일', 'EAI순번', '담당사원번호', '조직유형코드', '조직코드', '카마스터명', '호칭명', '직군코드', '직무코드', '직위코드', '직급코드', '사원여부', '퇴직여부', '퇴직년월일', '퇴직사유내용']
```


```python
# 1건씩 형태소 분석
stddic.termParsing(termList[500])
```




    {'logicalParsingResult': '[서비스][유지][여부]',
     'physicalName': 'SVC_UPK_YN',
     'termSplitResult': '서비스;유지;여부;',
     'attributeClassWord': '여부',
     'attributeClassUseResult': True,
     'nonstandardWords': '',
     'synonymousWords': '',
     'termRegistration': False}




```python
### 병렬처리 방법(Multi Processing)
# 1) 병렬처리 엔진 (1번만 켜놓으면 됨)
stddic.termParser.MultiProcessingInit()
```

    2022-09-01 12:33:48,088	INFO services.py:1456 -- View the Ray dashboard at [1m[32mhttp://127.0.0.1:8265[39m[22m
    


```python
# 2) 분석할 대상을 전달
# parallel [True, False]에 따라 병렬처리인지, 싱글처리인지 구분됨
result = stddic.multiTermParsing(termList, parallel=True)
```


```python
# 2) 병렬처리 엔진 Shutdown
stddic.termParser.MultiProcessingShutdown()
```
