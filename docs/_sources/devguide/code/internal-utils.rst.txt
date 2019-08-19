Códigos utilitátios internos
============================


HttpClient
-----------

Esse é um cliente que deve ser usado em todos os momentos em que qualquer código precisar fazer
uma requisição HTTP/HTTPS.

Caso alguma funcionalidade necessária para fazer o request ainda não esteja disponível nesse client, idealmente temos que adicionar suporte.

A ideia desse client é que algumas confogirações já estejam sempre feitas, como por exemplo timeout da conexão TCP e do request HTTP.


.. autoclass:: asgard.http.client.HttpClient
  :noindex:
  :members:
  :private-members:
