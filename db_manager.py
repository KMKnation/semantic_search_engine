from sqlalchemy import create_engine
import pandas as pd

CREATE_TABLE_STATEMENT = 'CREATE TABLE emails(' \
                         'email_id   INT  NOT NULL,' \
                         'subject VARCHAR (100) NOT NULL,' \
                         'content  TEXT  NOT NULL,' \
                         'cluster  INT,' \
                         'PRIMARY KEY (email_id));'


class DB:
    '''
    Load and store information for working with the Inference Engine,
    and any loaded models.
    '''

    def __init__(self, databsae_path):
        self.engine = create_engine('sqlite:///' + databsae_path)
        # self.engine = create_engine('sqlite:///db/db.sqlite')

    def get_table_names(self):
        # Save the table names to a list: table_names
        table_names = self.engine.table_names()
        return table_names

    def create_table(self, query):
        # Open engine connection: con
        con = self.engine.connect()
        con.execute(query)
        con.close()

    # def get_emails(self):
    #     # Open engine in context manager
    #     # Perform query and save results to DataFrame: df
    #     with self.engine.connect() as con:
    #         rs = con.execute("SELECT * FROM emails")
    #         # df = pd.DataFrame(rs.fetchmany(3))
    #         df = pd.DataFrame(rs.fetchall())
    #         df.columns = rs.keys()
    #
    #     return df

    def get_data(self, query):
        # Execute query and store records in DataFrame: df
        df = pd.read_sql_query(query, self.engine)
        return df

    def execute_query(self, query):
        with self.engine.connect() as con:
            rs = con.execute(query)
            return rs

    def update_email(self, data):
        print(data)
        update_query = "UPDATE emails SET " \
                       "cluster = '" + str(data['cluster']) + "'" \
                                                              " WHERE email_id = '" + str(data['id']) + "';"
        rs = self.execute_query(update_query)
        return rs


    def insert_email(self, data):
        inset_query = "INSERT INTO emails " \
                      "VALUES ('" + str(data['email_id']) + "', '" + data['subject'] + "', '" + data[
                          'content']  + "', '0');"
        # print(inset_query)
        rs = self.execute_query(inset_query)
        return rs

    def get_emails(self, group=None):
        return self.get_data('SELECT * FROM emails WHERE cluster=' + str(group))

    def get_all_emails(self,):
        return self.get_data('SELECT * FROM emails')

# data = {
#     'room_token':'213123ccsd',
#     'contact_info':'mayur@maili.com'
# }


# DB().create_table(CREATE_TABLE_STATEMENT)
# insert_invite(engine,data)
# print(DB().get_invitations())

