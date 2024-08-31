# HTTP Web Server
> Simple web server for handling concurrent connections and serving requests written in Python with only standard libraries.

### Usage

```bash
./run.sh
```
Start the web server listening for requests on port `4221`.

## Sending requests

- ### `GET`

  ```curl
  $ curl -v http://localhost:4221/echo/abc
  ```
  
  #### Response
  ```bash
  HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: 3\r\n\r\nabc
  ```

- ### `GET` files

  ```bash
  $ curl -i http://localhost:4221/files/foo
  ```
  
  #### Success Response
  ```bash
  HTTP/1.1 200 OK\r\nContent-Type: application/octet-stream\r\nContent-Length: 14\r\n\r\nHello, World!
  ```
  
  #### Failed Response
  ```bash
  HTTP/1.1 404 Not Found\r\n\r\n
  ```

- ### `POST`

  ```bash
  $ curl -v --data "12345" -H "Content-Type: application/octet-stream" http://localhost:4221/files/file_123
  ```
  
  #### Response
  ```bash
  HTTP/1.1 201 Created\r\n\r\n
  ```

