from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    PushMessageRequest,
    TextMessage
)

ACCESS_TOKEN = "5S3qGtycjYqkl/x+DNdi7LeTo+PODfdSb5dgsneRnmQOPKQSf/sUpGhkOIWxzemONgj8Mk64bDpEuE9cW+iF1hVCwrjGQ4Wl3kTL9oF+DLR90w2FPC/3x/7wlHkseMMCQ6sztwbVshau2ROPh0z+uwdB04t89/1O/w1cDnyilFU="
USER_ID = "U6776a321be1193f406c363388bf45485"

configuration = Configuration(
    access_token=ACCESS_TOKEN
)

with ApiClient(configuration) as api_client:
    line_bot_api = MessagingApi(api_client)

    line_bot_api.push_message(
        PushMessageRequest(
            to=USER_ID,
            messages=[
                TextMessage(
                    text="GitHub Actions通知テスト！"
                )
            ]
        )
    )

print("送信完了")