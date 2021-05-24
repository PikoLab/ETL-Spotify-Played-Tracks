# ETL for Personal Spotify Played Tracks


### 1. Purpose 
Build personal played trackes database by extracting data through Spotify API every day! 

### 2. ETL Process

```
Step1: Extract Data through Spotify API(https://developer.spotify.com/console/get-recently-played/)

Step2-1:Transform data from json object to pandas datafram

Step2-2: Check data validation
1. check df.empty
2. null values
3. primary key constraint
4. data for yesterday

Step3: Load data to sql database
```

### 3. Packages Used
```python
import requests
import pandas as pd 
import sqlalchemy
import sqlite3
from datetime import datetime
import datetime
```


