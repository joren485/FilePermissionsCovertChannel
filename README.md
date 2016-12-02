# FilePermissionsCovertChannel

### What does it do?
This program allows two users to communicate a hidden message.
It does this by changing the file permissions of a file in /tmp/.
An ASCII character is 8 bits long. The owner, group and other permissions of a file are 3 bits each, thus 9 bits total.
By changing 8 (actually 7) bits of those 9 permission bits, we are able to write a full character. 
If we base64 encode the message first, we have less and better readable characters.
For synchronization we flip the owner read bit every character. 

#### Sender
1. base64 encode the message
2. Create the file
3. Wait for the receiver to signal.
4. For every character in the base64 encoded message change the permissions, change the permissions of the file accordingly.
5. Set the owner read bit to `the index of the current character in the message % 2`. 
6. Wait 1 second and go to step 3.
7. Write a '|' to signal the end of the message.
8. Remove the file.

#### Receiver
1. Signal that we are ready to read the message by writing a '1' into the file.
2. Read the permissions until an '|' character is found.  
3. If the owner read bit is not `the index of the current character in the read message % 2`, decode the permissions to a char. Go to step 2. 
4. base64 decode the message. 

### How to use it?
User1:
`python3 client.py w --message "test_message"`

User2
`python3 client.py r`
