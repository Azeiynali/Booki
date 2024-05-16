## add message
method: **POST** <br />
route : `/api/addMessage`<br />
[with referer check](./referer.md)
- data
- content
- PIN (a pin for Security with MD5 hash)

## delete message
method: **DELETE**<br />
route : `/api/delMessage`<br />
[with referer check](./referer.md)
- date
- mess_id (message id)
- PIN

## user valid
description: for user checking, when send just username, return the username is exists of no, but when send username and password, the user is login
method: **POST**<br />
route : `/api/userValid`<br />
limit : 4 req per minute<br />
[with referer check](./referer.md)
- username
- password (optional)

## add post
method: **POST**<br />
route : `/api/add`<br />
limit : 5 req per minute<br />
[with referer check](./referer.md)
- img
- content
- group

## delete post
method: **DELETE**<br />
route : `/api/delete`<br />
[with referer check](./referer.md)
- post_id

## upload avatar
method: **POST**<br />
route : `/api/uploadavatar`<br />
- file (type: file)

## add user
method: **PUT**<br />
route : `/api/adduser`<br />
limit : 1 req per hour 
- username
- password
- gender
- city
- country
- avatar
- bio

## follow
method: **PUT**<br />
route : `/api/addfollow`<br />
- user_id

## unfollow
method: **DELETE**<br />
route : `/api/delfollow`<br />
- user_id

## edit
description: for user details edit
method: **POST**<br />
route : `/api/edit`<br />
limit : 4 req per minute
- username (optional)
- password (optional)
- bio (optional)
- country (optional)
- city (optional)
- avatar (optional)

and some other...