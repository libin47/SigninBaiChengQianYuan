sleep 30
curl --location --request POST 'localhost:8080/startAll' \
--header 'Content-Type:application/json' \
--data-raw '{ "top":1, "end":6, "token":"5wUkP4xyKj34RxsOF3EppNTZtEerY0dpnTZBt75ibkc="}'&
curl --location --request POST 'localhost:8080/startAll' \
--header 'Content-Type:application/json' \
--data-raw '{ "top":7, "end":11, "token":"5wUkP4xyKj34RxsOF3EppNTZtEerY0dpnTZBt75ibkc=" }'&
curl --location --request POST 'localhost:8080/startAll' \
--header 'Content-Type:application/json' \
--data-raw '{ "top":12, "end":18, "token":"5wUkP4xyKj34RxsOF3EppNTZtEerY0dpnTZBt75ibkc=" }'&
curl --location --request POST 'localhost:8080/startAll' \
--header 'Content-Type:application/json' \
--data-raw '{ "top":19, "end":25, "token":"5wUkP4xyKj34RxsOF3EppNTZtEerY0dpnTZBt75ibkc=" }'&
curl --location --request POST 'localhost:8080/startAll' \
--header 'Content-Type:application/json' \
--data-raw '{ "top":26, "end":30, "token":"5wUkP4xyKj34RxsOF3EppNTZtEerY0dpnTZBt75ibkc=" }'