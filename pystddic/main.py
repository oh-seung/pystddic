import pandas as pd
import numpy as np
from string import capwords
from copy import copy
import psutil
import ray
import pickle
import sys
import os
from tqdm.notebook import tqdm

#################################################################################################################
#################################################################################################################
#################################################################################################################
class wordManage:
    """ 표준단어 관리 클래스 """
    def __init__(self):
        self.englishColumns = ['LogicalWord', 'PhysicalWord', 'LogicalDescription', 'PhysicalDescription', \
                               'EntityClassWord', 'AttributeClassWord', 'wordStandardType', 'synonymousWord']
        self.koreanColumnMapping = {'LogicalWord':'논리명', 'PhysicalWord':'물리약어', 'LogicalDescription':'단어설명', 'PhysicalDescription':'물리전체명칭',\
                                    'EntityClassWord':'엔터티분류어여부', 'AttributeClassWord':'속성분류어여부', 'wordStandardType':'단어유형코드', 'synonymousWord':'동의어'}

        self.wordStorage = pd.DataFrame(None, columns=self.englishColumns)
        
        self.wordVefiryList = {'논리명중복제한':True,
                                '논리명미존재':True,
                                '물리명미존재':True,
                                '물리전체명칭미존재':True,
                                '물리약어중복제한':True,
                                '물리약어길이제한':True,
                                '특수문자사용제한':True,
                                '물리약어대문자변환':True,
                                '물리전체명칭첫글자대문자변환':True,
                              }
        
        self.physicalWordUpperCase = True ### 영문약어는 대문자로만 사용
        self.physicalDescriptionCapWord = True ### 물리전체명칭은 첫글자와 공백 기준 첫글자는 대문자로
        self.PhysicalWordLengthLimit = 10
        self.nonUseSpecialword = "(,),%,@,!,~,$,^,&,*,<,;,/,?,-,_,=,+" ### 
        self.dictionarySync = False

    def multiWordInsert(self, records, **kwags):        
        records = tqdm(records) if 'progress' in kwags.keys() else records
        error_words = []

        for row in records:
            synonymousWord = row['synonymousWord'] if 'synonymousWord' in row.keys() else ""
            try:
                self.wordInsert(LogicalWord=row['LogicalWord'], PhysicalWord=row['PhysicalWord'], \
                                LogicalDescription=row['LogicalDescription'], PhysicalDescription=row['PhysicalDescription'], \
                                EntityClassWord=row['EntityClassWord'], AttributeClassWord=row['AttributeClassWord'], \
                                wordStandardType=row['wordStandardType'], synonymousWord=synonymousWord)
            except:
                _, message, _ = sys.exc_info()
                error_words.append([message, row])

        return None if len(error_words) == 0 else error_words
                
            
    def wordInsert(self, LogicalWord:str, PhysicalWord:str, LogicalDescription:str, PhysicalDescription:str, \
                   EntityClassWord:bool, AttributeClassWord:bool, wordStandardType:str, **kwargs):
        """ 표준단어를 추가함 
             - LogicalWord : 논리단어
             - PhysicalWord : 물리명칭(영문약어) 용어사용시 해당 단어를 조합
             - LogicalDescription : 논리단어에 대한 설명
             - PhysicalDescription : 약어가 아닌 영문 전체 명칭을 정의
             - EntityClassWord : 엔터티 분류어 여부
             - AttributeClassWord : 속성 분류어 여부
             - wordStandardType : 표준단어, 동의어, 금칙어를 지정함
             - synonymousWord : 동의어 단어에 지정된 단어를 매핑
        """
        
        ### 동의어가 있다면 동의어 기록, 없으면 None
        synonymousWord = kwargs['synonymousWord'] if 'synonymousWord' in kwargs.keys() else ""
        ### 단어 셋을 지정
        tempWordSet = {'LogicalWord':LogicalWord, 'PhysicalWord':PhysicalWord, 'LogicalDescription':LogicalDescription, \
         'PhysicalDescription':PhysicalDescription, 'EntityClassWord':EntityClassWord, 'AttributeClassWord':AttributeClassWord, \
         'wordStandardType':wordStandardType, 'synonymousWord':synonymousWord}
        
        ### 표준단어 입력에 대한 기초적인 정제
        tempWordSet = self._wordInsertModification(tempWordSet)
        
        ### 동의어일 경우, 해당 표준단어에 맞게 조정함
        if tempWordSet['wordStandardType'] == '동의어':
            tempWordSet, _ = self._synonymusWordModification(tempWordSet)
        
        ### 체크결과에 오류(True)가 있을때는 오류를 발생시키고, 오류가 없을 경우 데이터 프레임에 입력
        CheckResult = self._wordInsertValidationCheck(tempWordSet)
        if True in CheckResult.values():
            errorMessage = ""
            for key, values in CheckResult.items():
                if values == True:
                    errorMessage += key + ', '
            assert False, 'An error occurred in the word registration. \n LogicalWord:{0}, ErrorMessage:{1}'.format(tempWordSet['LogicalWord'], errorMessage[:-2])
        else:
            self.wordStorage = self.wordStorage.append(tempWordSet, ignore_index=True)
        
        self.dictionarySync = False

            
    def wordQuery(self, **kwargs):
        """ 저장된 표준단어를 요청하는 언어(Language)에 따라 컬럼명을 변경하여 호출함"""
        try:
            if kwargs['language'] == 'Korean':
                return self.wordStorage.rename(columns=self.koreanColumnMapping)
        except:
            return  self.wordStorage
        
        return  self.wordStorage

    def _wordInsertValidationCheck(self, tempWordSet):
        """ 표준단어 추가에 대한 정합성 체크"""
        CheckResult = {}
        if [type(val).__name__ for val in tempWordSet.values()] == ['str', 'str', 'str', 'str', 'bool', 'bool', 'str', 'str']:
            ### 데이터형식 체크 결과
            CheckResult['데이터형식불일치'] = False
            ### 논리명 중복 체크
            LogicalWordCheck = self.wordStorage['LogicalWord'] == tempWordSet['LogicalWord']
            LogicalWordCheck = list(LogicalWordCheck)
            if self.wordVefiryList['논리명중복제한']:
                CheckResult['논리명중복발생'] = True if True in LogicalWordCheck else False
            ### 단어에 특수문자 존재 : (, ), %, @, !, ~, $, ^, &, *, <, ;, /, ?, -, _, =, +
            ### 논리명, 물리명, 물리전체명칭 길이가 0 이상일 경우 
            CheckResult['논리명미존재'] = True if len(tempWordSet['LogicalWord']) == 0 else False
            CheckResult['물리명미존재'] = True if len(tempWordSet['PhysicalWord']) == 0 else False
            CheckResult['물리전체명칭미존재'] = True if len(tempWordSet['PhysicalDescription']) == 0 else False
            
            ### 표준단어에만 해당되는 검증
            if tempWordSet['wordStandardType'] == '표준단어':
                
                PhysicalWordCheck = self.wordStorage['PhysicalWord'] == tempWordSet['PhysicalWord']
                PhysicalWordCheck = list(PhysicalWordCheck)
                ### 물리약어 중복 체크
                if self.wordVefiryList['물리약어중복제한']:
                    CheckResult['물리약어중복발생'] = True if True in PhysicalWordCheck else False        
                ### 영문약어 길이 체크
                if self.wordVefiryList['물리약어길이제한']:
                    CheckResult['물리약어길이제한초과'] = True if len(tempWordSet['PhysicalWord']) > self.PhysicalWordLengthLimit else False
                ### 엔터티분류어, 속성분류어에 Bool값으로 여부 확인
            
            ### 동의어에만 해당하는 체크
            elif tempWordSet['wordStandardType'] == '동의어':
                ### 표준단어 칸이 채워져 있는지 확인
                CheckResult['표준단어공란'] = True if tempWordSet['synonymousWord'] == "" else False
                ### 표준단어가 존재하는지를 확인
                _, stadardWordExist = self._synonymusWordModification(tempWordSet)
                CheckResult['표준단어미존재'] = True if stadardWordExist == False else False
        else:
            CheckResult['데이터형식불일치'] = True

        return CheckResult
    
    def _wordInsertModification(self, tempWordSet):
        """ 입력된 단어에 대한 정비"""
        if [type(val).__name__ for val in tempWordSet.values()] == ['str', 'str', 'str', 'str', 'bool', 'bool', 'str', 'str']:
            ### 1) 물리약어에 대한 대문자 변환
            tempWordSet['PhysicalWord'] = tempWordSet['PhysicalWord'].upper() if self.wordVefiryList['물리약어대문자변환'] == True else tempWordSet['PhysicalWord']
            ### 2) 물리설명에 대해 첫글자, 공백앞 문자 제거
            tempWordSet['PhysicalDescription'] = capwords(tempWordSet['PhysicalDescription']) if self.wordVefiryList['물리전체명칭첫글자대문자변환'] == True else tempWordSet['PhysicalDescription']
            ### 2) 논리명, 물리약어, 논리물리설명에 공백 제거
            tempWordSet['LogicalWord'] = tempWordSet['LogicalWord'].strip()
            tempWordSet['PhysicalWord'] = tempWordSet['PhysicalWord'].strip()
            tempWordSet['LogicalDescription'] = tempWordSet['LogicalDescription'].strip()
            tempWordSet['PhysicalDescription'] = tempWordSet['PhysicalDescription'].strip()
        
        return tempWordSet
    
    def _synonymusWordModification(self, tempWordSet):
        """ 입력된 단어가 동의어일 경우 물리약어 및 설명, 엔터티분류어, 속성분류어 등을 표준단어와 같도록 조정"""
        condition = (self.wordStorage['LogicalWord'] == tempWordSet['synonymousWord']) & (self.wordStorage['wordStandardType'] == '표준단어')
        condition = list(condition)
        stadardWordExist = False
        if True in condition:
            standardWordSet = self.wordStorage[condition].to_dict('records')[0]
            tempWordSet['PhysicalWord']        = standardWordSet['PhysicalWord']
            tempWordSet['LogicalDescription']  = standardWordSet['LogicalDescription']
            tempWordSet['PhysicalDescription'] = standardWordSet['PhysicalDescription']
            tempWordSet['EntityClassWord']     = standardWordSet['EntityClassWord']
            tempWordSet['AttributeClassWord']  = standardWordSet['AttributeClassWord']
            stadardWordExist = True
            
        return tempWordSet, stadardWordExist 
        
    def _dictionarySyncStatusChange(self, Status=False):
        """ 딕셔너리 Sync에 대한 상태를 바꿔줌 """
        self.dictionarySync = Status
        

#################################################################################################################
#################################################################################################################
#################################################################################################################

class stdDicMultiProcessing:
    """ 형태소분석 병렬 처리를 위한 별도 클래스 """
    def __init__(self):
        self.rayInit = False
        
    def _listSplit(self, arr):
        """ 병렬개수에 맞춰 분할하기"""
        ret_arr = [ [] for _ in range(self.MultiProcessCount)]
        for i, val in enumerate(arr):
            ret_arr[i % self.MultiProcessCount].append(val)
        return ret_arr

    def MultiProcessingInit(self):
        """ 병렬처리 모듈 Run """
        self.MultiProcessCount = psutil.cpu_count(logical=False)
        ray.init(num_cpus=self.MultiProcessCount, ignore_reinit_error=True)
        self.rayInit = True

    def MultiProcessingShutdown(self):
        """ 병렬처리 모듈 Shutdown """
        self.MultiProcessCount = psutil.cpu_count(logical=False)
        ray.shutdown()
        
    def _termParsingMultiProcessing(self, termList, wordStorage):
        """ 병렬처리를 위한 처리 함수 """
        if not self.rayInit:
            self.MultiProcessingInit()
        partTermList = self._listSplit(termList)
        
        @ray.remote
        def _tempTermParsing(partTermList):
            finalResults = list()
            termParser = termParse()
            termParser._wordStorageSet(wordStorage)
            for term in partTermList:
                finalResult = termParser._termParsing(term)
                finalResults.append(finalResult)
            return finalResults
        
        a = [_tempTermParsing.remote(partTermList[i]) for i in range(self.MultiProcessCount)]
        _result = ray.get(a)
        
        result = []
        for partResult in _result:
            result += partResult
        
        return result

#################################################################################################################
#################################################################################################################
#################################################################################################################

class termParse(stdDicMultiProcessing):
    """ 단어사전을 활용하여 용어에 대한 형태소 분석 """    
        
    def _wordStorageSet(self, wordStorage):
        """ 용어 형태소분석을 위한 단어사전을 지정 """
        self.wordStorage = wordStorage
        
    def _attributeClassCheck(self, termParsingResult):
        """ 속성분류어 체크 """
        attrclsword = self.wordStorage[self.wordStorage['AttributeClassWord']]['LogicalWord'].tolist()
        
        termParsingResult.reverse()
        attributeClassWord, attributeClassResult = "", False
        tempAttributeClassWord = ""
        for word, _, _, _, _, _ in termParsingResult:
            tempAttributeClassWord = word + tempAttributeClassWord

            if tempAttributeClassWord in attrclsword:
                attributeClassWord, attributeClassResult = copy(tempAttributeClassWord), True
                
        return attributeClassWord, attributeClassResult
    
    def _numericSplit(self, term:str):
        """ 논리명의 끝 숫자를 제거 """
        parsterm = term[::-1]

        numericWord = ''
        for i, s in enumerate(parsterm):
            if s.isdigit() == True:
                numericWord += s
            elif s.isdigit() == False:
                term = term[0:len(term)-i]
                break

        return term, numericWord

    def _wordListCreation(self, term):
        """ 용어를 구성할 수 있는 단어 목록을 생성 """
        wordList = list()
        termLength = len(term)
        
        ### 만들어 질 수 있는 단어의 형태로 모두 잘라냄
        for i in range(1, termLength + 1):
            for j in range(termLength - i + 1):
                wordList.append(term[j:i+j])
        
        KeyWordList = self.wordStorage['LogicalWord'].tolist()
        ### 단어의 위치를 등록.
        termWordList = []
        for word in wordList:
            wordSearchResult = False
            if word in KeyWordList:
                wordSearchResult = True
                _, PhysicalWord, _, _, _, _, wordStandardType, synonymousWord = \
                    self.wordStorage[self.wordStorage['LogicalWord'] == word].values[0]

            for i in range(termLength - len(word) + 1):
                result = term.startswith(word, i)
                if result == True:
                    if wordSearchResult == True:
                        termWordList.append([word, PhysicalWord, i, i+ len(word), wordStandardType, synonymousWord])
                    elif wordSearchResult == False and len(word) == 1:
                        termWordList.append([word, "", i, i+ len(word), '비표준', word])
                            
                        
        termWordList = pd.DataFrame(termWordList, columns=['논리명', '물리약어', '시작위치', '종료위치', '단어유형', '표준단어'])
        termWordList = termWordList.drop_duplicates().sort_values(['시작위치', '종료위치']).to_numpy()
        return termWordList
    
    def _termCartessianProduct(self, term, termWordList):
        ### 단어 조합으로 만들 수 있는 경우의 수를 생성
        termParsingList = list()

        for i in range(len(term)):
            MatchList = termWordList[termWordList[:, 2] == i]
            if i == 0:
                #표준단어나 임시단어가 존재할 경우, 비표준단어 시작은 제거
                if (MatchList[:, 4] == '표준단어').tolist().count(True) > 0 or (MatchList[:, 4] == '임시단어').tolist().count(True) > 0:
                    MatchList = MatchList[MatchList[:, 4] != '비표준']
                for MatchRow in MatchList:
                    termParsingList.append(MatchRow)                    
            elif i > 0:
                NewParsingList = list()
                for i, ParsingCol in enumerate(termParsingList):
                    for j, MatchRow in enumerate(MatchList):
                        if ParsingCol[-3] == MatchRow[2]:
                            NParsingCol = np.append(ParsingCol, MatchRow)
                            NewParsingList.append(NParsingCol)
                        else:
                            NewParsingList.append(ParsingCol)

                termParsingList = copy(NewParsingList)
        return termParsingList
        
    def _nonStandardwordCleansing(self, termParsingList):
        """비표준 단어에 대한 연결된 결과를 만듬 """
        newTermParsingList = []
        for ParsingPatterm in termParsingList:
            ### 비표준단어를 서로 연결하는 로직
            ParsingPatterm = ParsingPatterm.reshape(-1, 6)
            NonParsWord = ""
            ParsingResult = []
            bef_e = 0
            for word, phwd, s, e, gb, stdwd in ParsingPatterm:
                if gb != '비표준':
                    ParsingResult.append([word, phwd, s, e, gb, stdwd])
                else:
                    if s > bef_e or s == 0:
                        NonParsWord = word
                        NonParsresult = [word, '', s, e, gb, stdwd]

                    elif s == bef_e:
                        NonParsresult = copy(ParsingResult[-1])
                        s, e = NonParsresult[2], NonParsresult[3]+1
                        del ParsingResult[-1]
                        NonParsWord = NonParsWord + word
                        NonParsresult = [NonParsWord, '', s, e, gb, NonParsWord]

                    ParsingResult.append(NonParsresult)
                    bef_e = copy(e)
            newTermParsingList.append(np.array(ParsingResult))
        return newTermParsingList
    
        return termParsingList
    
    def _bestParsingPicking(self, termParsingList):
        """ 가장 좋은 단어의 구성을 찾음 """
        attrclsword = self.wordStorage[self.wordStorage['AttributeClassWord']]['LogicalWord'].tolist()
        
        NewParsingList = []
        for i, ParsingData in enumerate(termParsingList):
            ParsingDataSummary = {'행번호':0, '속성분류어사용여부':'N', '표준단어':0, '동의어':0, '비표준':0, '비표준길이합':0, '임시동의어':0, '임시단어':0}
            ParsingDataSummary['비표준길이합'] = sum([len(word) for word in ParsingData[ParsingData[:, 4] == '비표준'][:, 0]])
            
            k, v = np.unique(ParsingData[:, 4], return_counts=True)
            
            for j, key in enumerate(k):
                ParsingDataSummary[key] = v[j]

            ParsingDataSummary['속성분류어사용여부'] = 'Y' if ParsingData[-1][0] in attrclsword else 'N'

            ParsingDataSummary['행번호'] = i
            NewParsingList.append(ParsingDataSummary)

        df = pd.DataFrame(NewParsingList).fillna(0)
        df['표준동의어합'] = df['동의어'] + df['표준단어']
        
        ## 형태소분석 조건중 우선 순위 지정
        #### 1) 속성분류어 사용
        #### 2) 비표준 단어의 길이가 적어야 한다.
        #### 3) 표준단어와 동의어 사용 갯수가 적어야 한다.
        #### 4) 동의어 사용 횟수가 적어야 한다.

        df = df.sort_values(by=['속성분류어사용여부', '비표준길이합','표준동의어합', '동의어'], ascending=[False, True, True, True])
        idx = df.head(1).reset_index()['index'][0]
        bestParsingResult = termParsingList[idx]
        bestParsingResult = bestParsingResult.reshape(-1, 6).tolist()
        return bestParsingResult
    
    def _ParsingResultConcat(self, bestParsingResult):
        """ 가장 좋은단어의 구성을 결과로 연결하고, 요약함 """
        logicalTermParsingResult, physicalTermParsingResult = "", ""
        
        finalResult = {"logicalParsingResult":"",
                       "physicalName":"",
                       "termSplitResult":"",
                       "attributeClassWord":"",
                       "attributeClassUseResult":False,
                       "nonstandardWords":"",
                       "synonymousWords":"",
                       "termOriginalName":"",
                       "termRegistration":False}
        
        for i, (LogicalWord, PhysicalWord, _, _, wordStandardType, synonymousWord) in enumerate(bestParsingResult):
            finalResult['termSplitResult'] += LogicalWord + ';'
            
            if wordStandardType == '표준단어':
                finalResult['logicalParsingResult'] += "[" + LogicalWord + "]"
            
            elif wordStandardType == '동의어':
                finalResult['logicalParsingResult'] += "{" + synonymousWord + "}"
                finalResult['synonymousWords'] += LogicalWord + ";"
                
            elif wordStandardType == '비표준':
                finalResult['logicalParsingResult'] += "%" + LogicalWord + "%"
                
                finalResult['nonstandardWords'] += LogicalWord + ";"                
                
            if wordStandardType == '표준단어' or wordStandardType == '동의어':
                finalResult['physicalName'] += PhysicalWord if i == 0 else '_' + PhysicalWord
            else:
                finalResult['physicalName'] += '%' + LogicalWord + '%' if i == 0 else '_%' + LogicalWord + '%'
                
        finalResult["attributeClassWord"], finalResult["attributeClassUseResult"] = self._attributeClassCheck(bestParsingResult)
        
        return finalResult
    
    def _termParsing(self, term):
        """ 단어 동기화가 필요함 """
        term, numericWord = self._numericSplit(term)
        termWordList = self._wordListCreation(term)
        termParsingList = self._termCartessianProduct(term, termWordList)
        termParsingList = self._nonStandardwordCleansing(termParsingList)
        bestParsingResult = self._bestParsingPicking(termParsingList)
        finalResult = self._ParsingResultConcat(bestParsingResult)
        finalResult["termOriginalName"] = term
        
        return finalResult
    
#################################################################################################################
#################################################################################################################
#################################################################################################################

class stddic:
    def __init__(self):
        self.wordManager = wordManage()
        self.termParser = termParse()
            
    def multiTermParsing(self, termList, **kwargs):
        """ 병렬처리 """
        parallel = kwargs['parallel'] if 'parallel' in kwargs.keys() else False
        
        if parallel:
            results = self.termParser._termParsingMultiProcessing(termList, self.wordManager.wordStorage)            
        else:
            if self.wordManager.dictionarySync == False:
                self.termParser._wordStorageSet(self.wordManager.wordStorage)
                self.wordManager.dictionarySync = True
            results = list()
            for term in termList:
                result = self.termParser._termParsing(term)
                results.append(result)
        
        return results
    
    def termParsing(self, term):
        """ 용어를 단어 기준으로 파싱함 """
        if self.wordManager.dictionarySync == False:
            self.termParser._wordStorageSet(self.wordManager.wordStorage)
            self.wordManager.dictionarySync = True

        result = self.termParser._termParsing(term)
        
        return result
    
    def dictionaryPath(self, filePath):
        """ 딕셔너리를 저장하고 불러들일 경로 지정 """
        self.filePath = filePath
    
    def dictionarySave(self, filename):
        fullFilePath = self.filePath + filename
        with open(fullFilePath, 'wb') as fw:
            pickle.dump(self.wordManager.wordStorage, fw)
        print('Dictionary Dump file 저장 완료')
        
    def dictionaryLoad(self, filename):
        """ 단어 사전 로드 """
        fullFilePath = self.filePath + filename
        with open(fullFilePath, 'rb') as fr:
            self.wordManager.wordStorage = pickle.load(fr)
        print('Dictionary Dump file 호출 완료')

    def nonStandardWordExtraction(self, termList):
        """ 사전에 정의되지 않은 단어를 추출함 """
        ParsingResult = self.multiTermParsing(termList, parallel=True)
        ParsingResultDf = pd.DataFrame(ParsingResult)
        
        ### 비표준단어 목록 추출(Unique)
        nonstandardWordList = []
        for nonstandardWords in ParsingResultDf['nonstandardWords']:
            nonstandardWords = nonstandardWords[:-1].split(";")
            if len(nonstandardWords) > 0 and nonstandardWords[0] != '':
                nonstandardWordList += [word.strip() for word in nonstandardWords]
        nonstandardWordList = list(set(nonstandardWordList))
        nonstandardWordList.sort()
        
        results = []
        replaceWords = [':', '(', ')', '[', ']'] ###해당 단어가 포함되어 있으면 치환함, 오류 처리용
        skipWords = ['.', '?', ''] ### 해당단어는 검색하지 않음
        
        ## 해당단어를 포함하고 있는 용어를 찾음
        for word in nonstandardWordList:
            cnt = 0
            if word not in skipWords:
                orgword = word
                for replaceWord in replaceWords:
                    word = word.replace(replaceWord , '\\'+replaceWord)
                word = "%" + word + "%"
                useTerms = list(set(ParsingResultDf[ParsingResultDf['logicalParsingResult'].str.contains(word)]['termOriginalName'].tolist()))
                useTerms = ", ".join(useTerms)
                if useTerms != '':
                    results.append([orgword, useTerms, len(useTerms)])
                    
        results = pd.DataFrame(results, columns=['비표준단어명', '비표준단어사용용어목록', '사용건수']).sort_values(by=['사용건수'], ascending=False)
        
        return results
