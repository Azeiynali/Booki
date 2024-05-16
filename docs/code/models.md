## Users
- username
- gems (gem counter)
- password
- avatar (avatar picture link)
- date (register date)
- registered (a boolean to if the user get register message)
- country 
- city
- tags (keywords of biography)
- salt (a salt for password hashing)
- bio
- gender
- posts 
- messages 
- notifications 
- comments

## Notifications
- content
- date
- seened (if the user seen this notif)
- user_id

## Posts
- img (link)
- date
- content
- tags (keywords of content - with hashtags and AI keyword finder)
- description
- group
- comments
- user_id

## Messages
- date
- content
- user_id

## Follows
*save the followers and followings*
- follower (id > integer)
- followed (id > integer)

## Likes
*save the liker user and liked post*
- liker (id > integer)
- liked (id > integer)

## RecoveryCodes
*save account Recovery Codes*
- date
- code
- name
- user_id

## Comment
- date
- content
- user_id
- post_id