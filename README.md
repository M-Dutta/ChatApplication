## Running the Application
Make sure that the following is installed
1. Docker
2. docker-compose

This application is containerized and also connects to a postgres database that's containerized
By default, the application runs on `port 8001`  
cd into the base folder and use the following command to start
```
docker-compose up   
# add the -d command for it to run on the background
```

To run tests IN the container, execute the following command
`docker exec -it chatApplication ./manage.py test`

If chatApplication doesn't exist, `docker ps` and replace `chatApplication` use the appropriate name  


# API Info

## Message Endpoints

### **Send Message**

POST `/message/send/{str:receiver_username}`
```bash
Example:
curl -X POST 'http://localhost:8001/message/send/jane.doe' \
-H 'Content-Type: application/json' \
--data-raw '{
    "sender": "john.doe",
    "message" : "Sending to receiver"
}'
# receiver must be a username (string)
# sender must be username (string) 
# Sender and receiver must exist in the database 
    # add user(s) by curl -X POST 'localhost:8001/user/create-user/username
    # (See Add/Create User by username for more info)
# message will be forced into str


Response: json 
{
    "status": "success",
    "date_sent": "2022-01-12T16:15:49+00:00"
}
```
### **Retrieve Messages** sent for a user from another user  

GET `/message/retrieve/` **Content-Type** MUST be `application/x-www-form-urlencoded`
```bash
Example:
curl -L -X GET 'http://localhost:8001/message/retrieve/' \
-H 'Content-Type: application/x-www-form-urlencoded' \
--data-urlencode 'sender=john.doe' \
--data-urlencode 'receiver=jane.doe'

# sender must be a username (string) 
# receiver must be a username (string)
Paginatation: add query param page={int} to see next set of data
Paginatation: add query param per_page={int} to limit # of records returned

'
Response: list[json] (In descending order by date) 
[
    {
        "date_sent": "2022-01-12T16:19:41+00:00",
        "message": "this is a curled message",
    },
    {
        "date_sent": "2022-01-12T15:19:41+00:00",
        "message": "this is another curled message",
    }
]
'
```

### **Retrieve Message** sent by all users  
GET `/message/retrieve/all`
```bash
# messages upto 30 days old are returned by default
# pagination is enabled, and 100 records are returned by per page
Paginatation: add query param page={int} to see next set of data
Paginatation: add query param per_page={int} to limit # of records returned

Example:
curl -X GET 'http://localhost:8001/message/retrieve/all/'

'
Response: list[json] (In descending order by date) 
[
    {
        "sender": "john.doe",
        "date_sent": "2022-01-12T16:19:41+00:00",
        "message": "this is a curled message",
        "receiver": "jane.doe"
    },
    {
        "sender": "bread.dough",
        "date_sent": "2022-01-12T15:19:41+00:00",
        "message": "this is another curled message",
        "receiver": "sandwich.doe"
    }
]
'
```

##User Endpoints

### Add/Create User by username 

`localhost:8001/user/create-user/{str:username{3,18}}`
```bash
curl -X POST 'localhost:8001/user/create-user/test-user'

'
Response: json 
{
    "id": 20,
    "username": "test-user"
}
'
```

### Get User by username 

GET `localhost:8001/user/get-user/{str:username{3,18}}`
```bash
curl -X GET 'localhost:8001/user/get-user/test-user'

'
Response: json 
{
    "id": 20,
    "username": "test-user"
}
'
```

### Get All Users 

GET `localhost:8001/user/all-users/`
```bash
curl -X GET 'localhost:8001/user/all-users/'

'
Response: list[json] 
[
    {
        "id": 1,
        "username": "sender"
    },
    {
        "id": 2,
        "username": "receiver"
    }
'
```

