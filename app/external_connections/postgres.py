import os, psycopg2
from datetime import datetime
from dotenv import load_dotenv

class PostgresApiKey:
    def __init__(self, pg_id: int = None, pg_api_key: str = None):
        self.pg_id = pg_id
        self.pg_api_key = pg_api_key

class PostgresShop:
    def __init__(self, id: int = None, merchant_name: str = None, shop_name: str = None,
                 management_chat_id: int = None, finance_chat_id: int = None, support_chat_id: int = None, notification_chat_id: int = None,
                 pg_api_key_id: int = None):
        self.id = id
        self.merchant_name = merchant_name
        self.shop_name = shop_name
        self.management_chat_id = management_chat_id
        self.finance_chat_id = finance_chat_id
        self.support_chat_id = support_chat_id
        self.notification_chat_id = notification_chat_id
        self.pg_api_key_id = pg_api_key_id

class PostgresProvider:
    def __init__(self, id: int = None, provider_name: str = None, terminal_name:str = None, terminal_index: int = None,
                 cu_list_id: str = None, support_chat_id: int = None):
        self.id = id
        self.provider_name = provider_name
        self.terminal_name = terminal_name
        self.terminal_index = terminal_index
        self.cu_list_id = cu_list_id
        self.support_chat_id = support_chat_id

class PostgresTicketRequest:
    def __init__(self, id: int = None, shop_id: int = None, shop_message_id: int = None,
                 provider_id: int = None, provider_message_id: int = None,
                 pg_id: int = None, trx_id: str = None,
                 cu_task_id: str = None,
                 closed: bool = None, manual: bool = None,
                 created_at: datetime = None, message_full_text:str = None):
        self.id = id
        self.shop_id = shop_id
        self.provider_id = provider_id
        self.pg_id = pg_id
        self.trx_id = trx_id
        self.cu_task_id = cu_task_id
        self.provider_message_id = provider_message_id
        self.shop_message_id = shop_message_id
        self.closed = closed
        self.manual = manual
        self.created_at = created_at
        self.message_full_text = message_full_text

class Postgres:
    def __init__(self):
        load_dotenv()
        self.db_params = {
            'dbname': os.getenv('ESQL_MAIN_DB'),
            'user': os.getenv('ESQL_USER'),
            'password': os.getenv('ESQL_PASS'),
            'host': os.getenv('ESQL_HOST'),
            'port': os.getenv('ESQL_PORT')
        }
        self.db_params_keys = {
            'dbname': os.getenv('ESQL_KEYS_DB'),
            'user': os.getenv('ESQL_USER'),
            'password': os.getenv('ESQL_PASS'),
            'host': os.getenv('ESQL_HOST'),
            'port': os.getenv('ESQL_PORT')
        }
        self.conn= None
        self.conn_keys = None
    def _get_connection(self):
        if self.conn is None or self.conn.closed:
            self.conn = psycopg2.connect(**self.db_params)
        return self.conn
    def _get_connection_keys(self):
        if self.conn_keys is None or self.conn_keys.closed:
            self.conn_keys = psycopg2.connect(**self.db_params_keys)
        return self.conn_keys

    def _close_connection(self):
        if self.conn and not self.conn.closed:
            self.conn.close()
            self.conn = None
    def _close_connection_keys(self):
        if self.conn_keys and not self.conn_keys.closed:
            self.conn_keys.close()
            self.conn_keys = None
    
    def create_shop(self, merchant_name:str, shop_name:str, support_chat_id:int, pg_api_key:int) -> None:
        
        conn = self._get_connection()

        cur = conn.cursor()

        query = """
                INSERT INTO shops (merchant_name, shop_name, support_chat_id, pg_api_key_id)
                VALUES (%s, %s, %s, %s);
                """
        cur.execute(query, (merchant_name, shop_name, support_chat_id, pg_api_key))

        conn.commit()
        cur.close()
        return
    
    def get_shops_by_support_chat_id(self, support_chat_id:int) -> list[PostgresShop] | None:
        
        conn = self._get_connection()

        cur = conn.cursor()

        query = "SELECT * FROM shops WHERE support_chat_id = %s"
        cur.execute(query, (support_chat_id,))

        result = cur.fetchall()

        cur.close()
        print(f"chat: {support_chat_id}, res: {result}")
        if result == None:
            return None

        shops = []
        for row in result:
            shop = PostgresShop(id=row[0],
                                merchant_name=row[1],
                                shop_name=row[2],
                                management_chat_id=row[3],
                                finance_chat_id=row[4],
                                support_chat_id=row[5],
                                notification_chat_id=row[6],
                                pg_api_key_id=row[7])
            shops.append(shop)

        return shops
    
    def get_shop_by_id(self, shop_id:int) -> PostgresShop | None:
        
        conn = self._get_connection()
        cur = conn.cursor()

        query = "SELECT * FROM shops WHERE id = %s"
        cur.execute(query, (shop_id,))

        result = cur.fetchall()

        cur.close()
        

        if result == None:
            return None

        for row in result:
            shop = PostgresShop(id=row[0],
                                merchant_name=row[1],
                                shop_name=row[2],
                                management_chat_id=row[3],
                                finance_chat_id=row[4],
                                support_chat_id=row[5],
                                notification_chat_id=row[6],
                                pg_api_key_id=row[7])
            return shop

    def create_shop_api_key(self, shop_name:str, pg_id:int, pg_api_key:str) -> None:
        
        conn = self._get_connection_keys()

        cur = conn.cursor()

        query = """
                INSERT INTO shop_keys (shop_name, pg_id, pg_api_key)
                VALUES (%s, %s, %s);
                """
        cur.execute(query, (shop_name, pg_id, pg_api_key))

        conn.commit()
        cur.close()
        

        return
    
    def get_shop_api_key(self, shop_key_ref:int) -> PostgresApiKey | None:
        
        conn = self._get_connection_keys()

        cur = conn.cursor()

        query = "SELECT * FROM shop_keys WHERE id = %s"
        cur.execute(query, (shop_key_ref,))

        result = cur.fetchall()

        cur.close()
        

        if result == None:
            return None

        for row in result:
            answer = PostgresApiKey(row[2], # pg_id
                                    row[3] # pg_api_key
                                    )
            return answer

    def create_provider(self, provider_name:str, terminal_name:str, terminal_index:int, cu_list_id:str, support_chat_id:int) -> None:
        
        conn = self._get_connection()

        cur = conn.cursor()

        query = """
                INSERT INTO providers (provider_name, terminal_name, terminal_index, cu_list_id, support_chat_id)
                VALUES (%s, %s, %s, %s, %s);
                """
        cur.execute(query, (provider_name, terminal_name, terminal_index, cu_list_id, support_chat_id))

        conn.commit()
        cur.close()
        

        return
    
    def get_provider_by_terminal_index(self, terminal_index:int) -> PostgresProvider | None:
        
        conn = self._get_connection()

        cur = conn.cursor()

        query = "SELECT * FROM providers WHERE terminal_index = %s"
        cur.execute(query, (terminal_index,))

        result = cur.fetchall()

        cur.close()
        

        if result == None:
            return None

        for row in result:
            provider = PostgresProvider(id=row[0],
                                        provider_name=row[1],
                                        terminal_name=row[2],
                                        terminal_index=row[3],
                                        cu_list_id=row[4],
                                        support_chat_id=row[5])
            return provider

    def create_new_ticket_request(self, trx_id: str, shop_data: PostgresShop, shop_mes_id: int, provider_data: PostgresProvider,
                             provider_mes_id: int, cu_task_id: str,
                             is_manual_ticket: bool, message_full_text: str) -> bool:
        conn = self._get_connection()
        cur = conn.cursor()

        query = """
        INSERT INTO ticket_test (shop_id, shop_support_message_id, 
        provider_id, provider_support_message_id, 
        trx_id, cu_task_id, 
        closed, manual, message_full_text, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """
        cur.execute(query, (shop_data.id, shop_mes_id,
                            provider_data.id, provider_mes_id,
                            trx_id, cu_task_id,
                            False, is_manual_ticket, message_full_text, datetime.now()))

        conn.commit()
        cur.close()
        

        return True
    
    def get_all_tickets_v2(self) -> list[PostgresTicketRequest] | None:
        
        conn = self._get_connection()

        cur = conn.cursor()

        query = "SELECT * FROM ticket_test "
        cur.execute(query)

        result = cur.fetchall()

        cur.close()
        

        if result == None:
            return None

        tickets = []
        for row in result:
            ticket = PostgresTicketRequest(id=row[0],
                                           shop_id=row[1],
                                           shop_message_id=row[2],
                                           provider_id=row[3],
                                           provider_message_id=row[4],
                                           trx_id=row[5],
                                           cu_task_id=row[6],
                                           closed=row[7],
                                           manual=row[8],
                                           message_full_text=row[9],
                                           created_at=row[10])
            tickets.append(ticket)
        return tickets
    
    def get_all_tickets(self, closed: bool) -> list[PostgresTicketRequest] | None:
        
        conn = self._get_connection()

        cur = conn.cursor()

        query = "SELECT * FROM tickets WHERE closed = %s"
        cur.execute(query, (closed,))

        result = cur.fetchall()

        cur.close()
        

        if result == None:
            return None

        tickets = []
        for row in result:
            ticket = PostgresTicketRequest(id=row[0],
                                           shop_id=row[1],
                                           shop_message_id=row[2],
                                           provider_id=row[3],
                                           provider_message_id=row[4],
                                           trx_id=row[5],
                                           cu_task_id=row[6],
                                           closed=row[7],
                                           manual=row[8],
                                           message_full_text=row[9],
                                           created_at=row[10])
            tickets.append(ticket)

        return tickets

    def close_ticket(self, ticked_id, closed: bool) -> None:
        
        conn = self._get_connection()
        cur = conn.cursor()
        query = """
        UPDATE tickets
        SET closed = %s
        WHERE id = %s;
        """

        cur.execute(query, (closed, ticked_id))
        conn.commit()

        cur.close()
        

        return True

    def delete_old_ticket(self,ticket_id) -> None:
        
        conn = self._get_connection()
        cur = conn.cursor()
        query = """
			DELETE FROM ticket_test
			WHERE id = %s;
        """

        cur.execute(query, (ticket_id,))
        conn.commit()

        cur.close()
        

        return True

    def get_provider_by_terminal_name(self, terminal_name:int) -> PostgresProvider | None:
        
        conn = self._get_connection()

        cur = conn.cursor()

        query = "SELECT * FROM providers WHERE terminal_name = %s"
        cur.execute(query, (terminal_name,))

        result = cur.fetchall()

        cur.close()
        

        if result == None:
            return None

        return result[0][3] if result else None
    
    def activate_ticket_manual_tag(self, ticket_id) -> bool:
        conn = self._get_connection()
        cur = conn.cursor()
        
        try:
            query = """
                UPDATE ticket_test
                SET manual = true
                WHERE id = %s
                RETURNING id;
            """

            cur.execute(query, (ticket_id,))
            updated_row = cur.fetchone()
            conn.commit()
            
            success = updated_row is not None
            return success

        except Exception as e:
            conn.rollback()
            raise e
        
        finally:
            cur.close()
            conn.close()
        
    def __del__(self):
        """Ensure the connection is closed when the object is deleted."""
        self._close_connection()
        self._close_connection_keys()

POSTGRES = Postgres()