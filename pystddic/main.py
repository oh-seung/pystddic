import pandas as pd
import pickle
from tqdm.notebook import tqdm

from .wordManage import *
from .domainManage import *
from .termParse import *


class stddic:
    def __init__(self):
        self.wordManager = wordManage()
        self.termParser = termParse()
        self.domainManager = domainManage()
            
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
