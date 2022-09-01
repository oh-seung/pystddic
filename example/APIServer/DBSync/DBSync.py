### 10초마다 DB와 연동될 수 있도록 작성

import pystddic
import cx_Oracle
import threads 


class stddic_sync(pystddic.stddic):
  def __init__(self):
    super().__init__()
    
  def _dbConnection(self):
    """ DB와의 접속 처리 """
    pass
  
  def _dbSync(self):
    """ 데이터를 DB와 10초마다 연동 """
    pass 
    
  def _dataQuery(self):
    """ 데이터를 호출 """
    return wordSet
    
  
  def _dataCheck(self):
    """ 신규로 발생된 데이터가 있는지 체크 """
    return False
