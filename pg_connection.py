import psycopg2 as psg
import psycopg2.extras as ex

class pg_connection():
    def __init__(self):

        try:
            self.con = psg.connect(
                host='localhost', 
                database='tft_db', 
                user = 'admin', 
                password= 'admin'
                )
        except Exception as e:
            print(f"Erro ao conectar: {e}")
    
    def savedMateches(self):
        try:
            cur = self.con.cursor()
            query = 'SELECT max (game_creation) FROM tft.match_status'
            cur.execute(query)

            return cur.fetchall()
        
        except Exception as e:
            return print(f'Fail to query table: {e}')
        
    def insertOnMatchStatus(self, df):
        self.dataframe = df
        tableName = 'match_status'
        batchSise = 5

        if self.dataframe.empty:
            print('DataFrame is empety')
        else:
            maxGameCreation = self.savedMateches()
            axsInsertdf = self.dataframe[self.dataframe['game_creation'] > maxGameCreation]
            
        rows = [tuple(x) for x in axsInsertdf.to_numpy()]
        cols = ','.join(axsInsertdf.columns)

        insert = f'INSERT INTO tft.{tableName} ({cols}) VALUES %s'

        try:
            cur = self.con.cursor()
            pointer = 0
            for i in range(0, len(rows), batchSise):
                batch = rows[i:i + batchSise]
                
                ex.execute_values(cur,insert,batch)
                self.con.commit()
                
                pointer += 1 
                print(f'Insertig batch {pointer} lines {i}')
        except Exception as e:
            print(f'Error to insert {pointer}: {e}')
        

