import os
from enum import Enum

import requests
from dotenv import load_dotenv


class CU_TaskStatus(Enum):
    TO_DO = "TO DO"
    IN_PROGRESS = "IN PROGRESS"
    COMPLETE = "COMPLETE"


class ClickUpClient:
    def __init__(self):
        load_dotenv()
        self.token = os.getenv('CLICKUP_TOKEN')
        self.team_id = os.getenv('CLICKUP_TEAM_ID')
        self.base_url = os.getenv('CLICKUP_ENDPOINT')

    def create_manual_task(self, list_id, attachment, pg_trx_id, description:str = None):
        return self.create_task(list_id=list_id, attachment=attachment, pg_trx_id=pg_trx_id, description=description, task_status=CU_TaskStatus.TO_DO)

    async def create_auto_task(self, list_id, attachments, pg_trx_id, description:str = None):
        tags = ["auto"]
        return await self.create_task(list_id=list_id, attachments=attachments, pg_trx_id=pg_trx_id, description=description, task_status=CU_TaskStatus.IN_PROGRESS, tags=tags)

    async def create_task(self, list_id, attachments, pg_trx_id, description:str=None,
                          task_status:CU_TaskStatus=CU_TaskStatus.TO_DO, tags:[str]=None):
        url = f"{self.base_url}/list/{list_id}/task"

        headers = {
            "Content-Type": "application/json",
            "Authorization": self.token
        }
        query = {
            "custom_task_ids": "true",
            "team_id": self.team_id
        }
        payload = {
            "name": f"{pg_trx_id}",
            "description": f"ID: {pg_trx_id}\n\nDescription: {description}",
            "assignees": [
                 #89657945
            ],
            "status": task_status.value,
            "tags": tags
        }

        response = requests.post(url, json=payload, headers=headers, params=query)
        data = response.json()

        # Attach multiple files
        if attachments and isinstance(attachments, list):
            for attachment in attachments:
                self.add_attachment(data['id'], attachment, True)

        return data

    def add_attachment(self, task_id, attachment, delete_attachment=False):
        url = f"{self.base_url}/task/{task_id}/attachment"
        headers = {
        "Authorization": self.token,
        # "Content-Type": "multipart/form-data"
        }

        if not os.path.exists(attachment):
            raise FileNotFoundError(f"The file {attachment} does not exist.")

        try:
            with open(attachment, 'rb') as file:
                files = {
                    "attachment": (os.path.basename(attachment), file)
                }
                response = requests.post(url, files=files, headers=headers)

            if response.status_code != 200:
                raise Exception(f"Failed to upload attachment: {response.text}")

        # Optionally delete the file
            # if delete_attachment:
            #     os.remove(attachment)

            return response.json()
        except Exception as e:
            print(f"Error uploading attachment: {e}")
            raise
    
    async def update_task_status(self, task_id:str, task_status:CU_TaskStatus=CU_TaskStatus.IN_PROGRESS) -> None:
        url = f"{self.base_url}/task/{task_id}"

        headers = {
            "Content-Type": "application/json",
            "Authorization": self.token
        }
        query = {
            "custom_task_ids": "true",
            "team_id": self.team_id
        }
        payload = {
            "status": task_status.value,
        }

        response = requests.put(url, json=payload, headers=headers, params=query)
    async def update_task_tag(self, task_id, new_tag="manual"):
        tags_url = f"{self.base_url}/task/{task_id}/tag/{new_tag}"
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": self.token,
            "accept": "application/json"
        }
        
        # Fetch the existing tags for the task
        post_response = requests.post(tags_url, headers=headers)
        if post_response.status_code != 200:
            raise Exception(f"Failed to retrieve task {task_id}: {post_response.text}")

        put_respone = requests.put( f"{self.base_url}/task/{task_id}", headers=headers)    
        print(put_respone.status_code)
        
        return post_response.json()
    
    async def update_task_assignee(self, task_id,assignee_id=89657945):
        tags_url = f"{self.base_url}/task/{task_id}"
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": self.token,
            "accept": "application/json"
        }
        payload = {
         "assignees": {
                 "add":[89657945]
        }
        }
        # Fetch the existing tags for the task
        post_response = requests.post(tags_url, headers=headers)
        if post_response.status_code != 200:
            raise Exception(f"Failed to retrieve task {task_id}: {post_response.text}")

        put_respone = requests.put( f"{self.base_url}/task/{task_id}", headers=headers,json=payload)    
        print(put_respone.status_code)
        
        return post_response.json()

CLICKUP_CLIENT = ClickUpClient()