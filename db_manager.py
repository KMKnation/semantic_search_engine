from sqlalchemy import create_engine
import pandas as pd

CREATE_TABLE_STATEMENT = 'CREATE TABLE emails(' \
                         'email_id   INT  NOT NULL,' \
                         'subject VARCHAR (50)      NOT NULL,' \
                         'content  VARCHAR (200)   NOT NULL,' \
                         'cluster  INT,' \
                         'PRIMARY KEY (email_id));'

class DB:
    '''
    Load and store information for working with the Inference Engine,
    and any loaded models.
    '''

    def __init__(self):
        self.engine = create_engine('sqlite:///db/db.sqlite')

    def get_table_names(self):
        # Save the table names to a list: table_names
        table_names = self.engine.table_names()
        return table_names

    def create_table(self, query):
        # Open engine connection: con
        con = self.engine.connect()
        con.execute(query)
        con.close()

    def get_emails(self):
        # Open engine in context manager
        # Perform query and save results to DataFrame: df
        with self.engine.connect() as con:
            rs = con.execute("SELECT * FROM emails")
            # df = pd.DataFrame(rs.fetchmany(3))
            df = pd.DataFrame(rs.fetchall())
            df.columns = rs.keys()

        return df

    def get_data(self, query):
        # Execute query and store records in DataFrame: df
        df = pd.read_sql_query(query, self.engine)
        return df

    def execute_query(self, query):
        with self.engine.connect() as con:
            rs = con.execute(query)
            return rs

    def update_email(self, data):
        update_query = "UPDATE emails SET " \
                       "cluster = '"+str(data['cluster'])+"'" \
                       " WHERE email_id = " + str(data['id']) + ";"
        rs = self.execute_query(update_query)
        return rs


    def insert_email(self, data):
        if not 'email_id' in data.keys():
            resultDf = self.get_data('SELECT * FROM emails')
            inset_query = "INSERT INTO emails " \
                          "VALUES ('" + str(len(resultDf)) + "', '" + data['subject'] + "', '" + data['content'] + "', '0');"
            print(inset_query)
            rs = self.execute_query(inset_query)
            return rs
        else:
            resultDf = self.get_data('SELECT * FROM emails WHERE email_id=' + data['email_id'])
            update_query = "UPDATE emails SET cluster = '" + data['cluster'] + "' WHERE email_id = " + data['email_id'] + ";"
            if (len(resultDf) > 0):
                rs = self.execute_query(update_query)
                return rs
            else:
                print('NO email record FOUND!!')
                return None

    def get_invitations(self, id=None):
        if id == None:
            return self.get_data('SELECT * FROM emails')
        else:
            return self.get_data('SELECT * FROM emails WHERE email_id=' + str(id))

# data = {
#     'room_token':'213123ccsd',
#     'contact_info':'mayur@maili.com'
# }


# DB().create_table(CREATE_TABLE_STATEMENT)
# insert_invite(engine,data)
# print(DB().get_invitations())
