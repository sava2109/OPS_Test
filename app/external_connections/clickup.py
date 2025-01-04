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

    async def create_auto_task(self, list_id, attachment, pg_trx_id, description:str = None):
        tags = ["auto"]
        return await self.create_task(list_id=list_id, attachment=attachment, pg_trx_id=pg_trx_id, description=description, task_status=CU_TaskStatus.IN_PROGRESS, tags=tags)

    async def create_task(self, list_id, attachment, pg_trx_id, description:str=None,
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

        if attachment and attachment != "":
            self.add_attachment(data['id'], attachment, True)

        return data

    def add_attachment(self, task_id, attachment, delete_attachment=False):
        url = f"{self.base_url}/task/{task_id}/attachment"
        headers = {
            "Authorization": self.token
        }
        file = {
            "attachment": (attachment, open(attachment, 'rb'))
        }

        response = requests.post(url, files=file, headers=headers)

        if delete_attachment:
            os.remove(attachment)

        return response.json()

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
    async def update_task_tag(self, task_id, new_tag="Manual"):
        url = f"{self.base_url}/task/{task_id}"

        headers = {
            "Content-Type": "application/json",
            "Authorization": self.token
        }

        # Fetch the existing tags for the task
        get_response = requests.get(url, headers=headers)
        if get_response.status_code != 200:
            raise Exception(f"Failed to retrieve task {task_id}: {get_response.text}")

        task_data = get_response.json()
        existing_tags = task_data.get("tags", [])

        # Add the new tag if it's not already in the tags
        if new_tag not in existing_tags:
            existing_tags.append(new_tag)

        # Update the task with the modified tags
        payload = {
            "tags": existing_tags
        }
        response = requests.put(url, json=payload, headers=headers)
        if response.status_code != 200:
            raise Exception(f"Failed to update task {task_id}: {response.text}")

        return response.json()

CLICKUP_CLIENT = ClickUpClient()