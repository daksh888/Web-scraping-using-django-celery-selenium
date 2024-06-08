from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from celery.result import AsyncResult
from .tasks import scrape_data_for_coins
import json

COIN = ["DUKO", "NOT", "GORILLA"]

class CoinMarketCap(APIView):
    def post(self, request, format=None):
        if not COIN:
            return Response({"error": "No coins provided"}, status=status.HTTP_400_BAD_REQUEST)

        # Call Celery task
        result = scrape_data_for_coins.delay(COIN)

        # Return response with job_id
        return Response({"job_id": result.id}, status=status.HTTP_202_ACCEPTED)
    
    def get(self, request, job_id, format=None):
        # Get the result of the task
        task_result = AsyncResult(job_id)

        # Wait for the task to complete
        while not task_result.ready():
            pass

        # Get the actual result data
        if task_result.successful():
            result_data = task_result.get()
            return Response({"status": "Success", "result": result_data}, status=status.HTTP_200_OK)
        elif task_result.failed():
            error_message = str(task_result.info)
            return Response({"status": "Failure", "error": error_message}, status=status.HTTP_200_OK)
        else:
            return Response({"status": "Pending"}, status=status.HTTP_200_OK)
