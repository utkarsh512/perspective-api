# How to use
The script allows the user to make call to Perspective API for computing scores for some texts on various attributes supported by the API. 
```python3
from caller import Caller

API_KEY = 'Your API Key'
QPS = 1  # Query per second limit for client, default is 1
         # but could be increased by making a request 

api = Caller(API_KEY, QPS)

text = 'And, you call me dumb.... Dude!'
result = api.score(text) # {attribute: score} dictionary
```
